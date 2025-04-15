import asyncio
import base64
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from types import CoroutineType, EllipsisType
from typing import TYPE_CHECKING, Any

import websockets as ws
from cookit.loguru import warning_suppress
from pydantic import BaseModel

from .errors import APIError, AuthenticationFailedError, ValidationError
from .request import RequestManager
from .types.request import (
    AuthenticationRequestData,
    AuthenticationTokenRequestData,
    BaseRequest,
)
from .types.response import (
    APIErrorResponseData,
    AuthenticationResponseData,
    AuthenticationTokenResponseData,
    BaseResponse,
)
from .utils import run_sync

if TYPE_CHECKING:
    from asyncio import Task

type C[T] = CoroutineType[Any, Any, T]

type ConnectingHandler = Callable[[], C[Any]]
type ConnectedHandler = Callable[[], C[Any]]
type ConnectFailedHandler = Callable[[Exception], C[Any]]
type ConnectionClosedHandler = Callable[[Exception], C[Any]]
type ParseDataErrorHandler = Callable[[str | bytes, Exception], C[Any]]
type AuthenticationTokenGotHandler = Callable[[str], C[Any]]
type AuthenticatedHandler = Callable[[], C[Any]]
type AuthenticationFailedHandler = Callable[[Exception], C[Any]]
type HandlerRunFailedHandler = Callable[[Exception], C[Any]]
type RecvRawHandler = Callable[[str | bytes], C[Any]]
type BeforeSendRawHandler = Callable[[str], C[Any]]

DEFAULT_ENDPOINT = "ws://localhost:8001"


@dataclass
class EventHandlerInfo[T: BaseModel]:
    model: type[T]
    handler: Callable[[T], Any]


def dispatch_handlers[**P, R](
    handlers: list[Callable[P, C[R]]],
    run_failed_handlers: list[HandlerRunFailedHandler] | None = None,
    *args: P.args,
    **kwargs: P.kwargs,
) -> list["Task[R | Exception]"] | None:
    async def run_task(f: Callable[P, C[R]]) -> R | Exception:
        try:
            return await f(*args, **kwargs)
        except Exception as e:
            if run_failed_handlers:
                dispatch_handlers(run_failed_handlers, None, e)
            return e

    return [asyncio.create_task(run_task(x)) for x in handlers]


class PluginState(Enum):
    STOPPED = auto()
    DISCONNECTED = auto()
    CONNECTING = auto()
    AUTHENTICATING = auto()
    AUTHENTICATED = auto()


class Plugin:
    def __init__(
        self,
        plugin_name: str,
        plugin_developer: str,
        plugin_icon: str | bytes | Path | None = None,
        authentication_token: str | None = None,
        endpoint: str = DEFAULT_ENDPOINT,
        api_timeout: float | None = 30,
        reconnect_delay: float = 5,
    ) -> None:
        self.plugin_name = plugin_name
        self.plugin_developer = plugin_developer
        self.plugin_icon = self.prepare_icon(plugin_icon) if plugin_icon else None
        self.authentication_token = authentication_token
        self.endpoint = endpoint
        self.api_timeout = api_timeout
        self.reconnect_delay = reconnect_delay

        self.connecting_handlers: list[ConnectingHandler] = []
        self.connected_handlers: list[ConnectedHandler] = []
        self.connect_failed_handlers: list[ConnectFailedHandler] = []
        self.connection_closed_handlers: list[ConnectionClosedHandler] = []
        self.parse_data_error_handlers: list[ParseDataErrorHandler] = []
        self.authentication_token_got_handlers: list[AuthenticationTokenGotHandler] = []
        self.authenticated_handlers: list[AuthenticatedHandler] = []
        self.authenticate_failed_handlers: list[AuthenticationFailedHandler] = []
        self.handler_run_failed_handlers: list[HandlerRunFailedHandler] = []
        self.recv_raw_handlers: list[RecvRawHandler] = []
        self.before_send_raw_handlers: list[BeforeSendRawHandler] = []
        self.event_handlers: dict[str, list[EventHandlerInfo]] = {}

        self.client: ws.ClientConnection | None = None
        self.connecting = False
        self.authenticated = False
        self.stopped = True
        self.req_manager = RequestManager()

        self._recv_task: Task | None = None
        self._run_task: Task | None = None

    @staticmethod
    def prepare_icon(icon: str | bytes | Path) -> str:
        if isinstance(icon, Path):
            icon = icon.read_bytes()
        if isinstance(icon, bytes):
            icon = base64.b64encode(icon).decode()
        return icon

    @property
    def state(self) -> PluginState:
        if self.client:
            if self.authenticated:
                return PluginState.AUTHENTICATED
            return PluginState.AUTHENTICATING
        if self.connecting:
            return PluginState.CONNECTING
        return PluginState.DISCONNECTED

    def on_connecting[T: ConnectingHandler](self, handler: T) -> T:
        self.connecting_handlers.append(handler)
        return handler

    def on_connected[T: ConnectedHandler](self, handler: T) -> T:
        self.connected_handlers.append(handler)
        return handler

    def on_connect_failed[T: ConnectFailedHandler](self, handler: T) -> T:
        self.connect_failed_handlers.append(handler)
        return handler

    def on_connection_closed[T: ConnectionClosedHandler](self, handler: T) -> T:
        self.connection_closed_handlers.append(handler)
        return handler

    def on_parse_data_error[T: ParseDataErrorHandler](self, handler: T) -> T:
        self.parse_data_error_handlers.append(handler)
        return handler

    def on_authentication_token_got[T: AuthenticationTokenGotHandler](
        self,
        handler: T,
    ) -> T:
        self.authentication_token_got_handlers.append(handler)
        return handler

    def on_authenticated[T: AuthenticatedHandler](self, handler: T) -> T:
        self.authenticated_handlers.append(handler)
        return handler

    def on_authenticate_failed[T: AuthenticationFailedHandler](self, handler: T) -> T:
        self.authenticate_failed_handlers.append(handler)
        return handler

    def on_handler_run_failed[T: HandlerRunFailedHandler](self, handler: T) -> T:
        self.handler_run_failed_handlers.append(handler)
        return handler

    def on_recv_raw[T: RecvRawHandler](self, handler: T) -> T:
        self.recv_raw_handlers.append(handler)
        return handler

    def on_before_send_raw[T: BeforeSendRawHandler](self, handler: T) -> T:
        self.before_send_raw_handlers.append(handler)
        return handler

    def on_event[T: BaseModel, H: Callable[[BaseModel], Any]](
        self,
        event_name: str,
        model: type[T],
        handler: H,
    ) -> H:
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(EventHandlerInfo(model, handler))
        return handler

    def dispatch_handlers[**P, R](
        self,
        handlers: list[Callable[P, C[R]]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> list["Task[R | Exception]"] | None:
        return dispatch_handlers(
            handlers,
            self.handler_run_failed_handlers,
            *args,
            **kwargs,
        )

    def ensure_client(self):
        if not self.client:
            raise RuntimeError("Client is not connected")
        return self.client

    async def _recv(self, client: ws.ClientConnection):
        raw = await client.recv()
        self.dispatch_handlers(self.recv_raw_handlers, raw)

        try:
            resp = BaseResponse.model_validate_json(raw)
        except Exception as e:
            self.dispatch_handlers(self.parse_data_error_handlers, raw, e)
            return

        instance_cache: dict[type[BaseModel], BaseModel] = {}

        def validate_data[T: BaseModel](model: type[T]) -> T:
            if model not in instance_cache:
                data = model.model_validate(resp.data)
                instance_cache[model] = data
            else:
                data = instance_cache[model]
            return data

        is_err = resp.message_type == APIError.message_type

        if resp.request_id and self.req_manager.has_id(resp.request_id):
            fut = self.req_manager.pop(resp.request_id)
            try:
                data = validate_data(APIErrorResponseData if is_err else fut.model)
            except Exception as e:
                err = ValidationError(raw, fut.model)
                err.__cause__ = e
                self.dispatch_handlers([run_sync(fut.future.set_exception)], err)
            else:
                if is_err:
                    self.dispatch_handlers(
                        [run_sync(fut.future.set_exception)],
                        APIError(data),
                    )
                else:
                    self.dispatch_handlers([run_sync(fut.future.set_result)], data)

        if resp.message_type in self.event_handlers:
            for handler_info in self.event_handlers[resp.message_type]:
                try:
                    data = validate_data(handler_info.model)
                except Exception as e:
                    self.dispatch_handlers(self.parse_data_error_handlers, raw, e)
                else:
                    self.dispatch_handlers([handler_info.handler], data)

    async def _recv_loop(self, client: ws.ClientConnection):
        while True:
            try:
                await self._recv(client)
            except Exception as e:
                self.client = None
                self.authenticated = False
                self.dispatch_handlers(self.connection_closed_handlers, e)
                await asyncio.sleep(self.reconnect_delay)
                break

    async def _disconnect(self):
        client = self.client
        task = self._recv_task
        self.client = None
        self._recv_task = None
        self.connecting = False
        self.authenticated = False
        self.req_manager.reset()
        self.req_manager = RequestManager()
        if client and (client.close_code is None):
            await client.close()
        if task and (not task.done()):
            task.cancel()

    async def reconnect(self):
        await self._disconnect()

        if self.connecting:
            raise RuntimeError("Already connecting")

        self.connecting = True
        self.dispatch_handlers(self.connecting_handlers)
        try:
            self.client = await ws.connect(self.endpoint)
        finally:
            self.connecting = False

        self.dispatch_handlers(self.connected_handlers)
        self._recv_task = asyncio.create_task(self._recv_loop(self.client))
        return self._recv_task

    async def stop(self):
        self.stopped = True
        await self._disconnect()
        if self._run_task:
            self._run_task.cancel()
        self._run_task = None

    async def _run(self):
        if not self.stopped:
            return
        self.stopped = False

        while not self.stopped:
            try:
                task = await self.reconnect()
            except Exception as e:
                if self.stopped:
                    break
                self.dispatch_handlers(self.connect_failed_handlers, e)
                await asyncio.sleep(self.reconnect_delay)
                continue

            try:
                await self.authenticate()
            except Exception as e:
                if self.stopped:
                    break
                self.dispatch_handlers(self.authenticate_failed_handlers, e)
                with warning_suppress("Disconnect failed"):
                    await self._disconnect()
                await asyncio.sleep(self.reconnect_delay)
                continue

            await task

    async def run(self):
        if self._run_task and not self._run_task.done():
            raise RuntimeError("Already running")
        self._run_task = asyncio.create_task(self._run())
        return self._run_task

    async def call_api[M: BaseModel](
        self,
        message_type: str,
        response_data_model: type[M],
        data: Any = None,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> M:
        req_timeout = self.api_timeout if api_timeout is ... else api_timeout

        client = self.ensure_client()
        req_id = self.req_manager.acquire_next_request(response_data_model)
        request = BaseRequest(
            api_name=api_name,
            api_version=api_version,
            request_id=req_id,
            message_type=message_type,
            data=data,
        )
        payload = request.model_dump_json()
        self.dispatch_handlers(self.before_send_raw_handlers, payload)
        await client.send(payload)
        return await self.req_manager.wait_response(req_id, req_timeout, pop=True)

    async def authenticate(self):
        if self.authenticated:
            return

        if not self.authentication_token:
            token_data = await self.call_api(
                "AuthenticationTokenRequest",
                AuthenticationTokenResponseData,
                AuthenticationTokenRequestData(
                    plugin_name=self.plugin_name,
                    plugin_developer=self.plugin_developer,
                    plugin_icon=self.plugin_icon,
                ),
            )
            self.authentication_token = token_data.authentication_token
            self.dispatch_handlers(
                self.authentication_token_got_handlers,
                token_data.authentication_token,
            )

        data = await self.call_api(
            "AuthenticationRequest",
            AuthenticationResponseData,
            AuthenticationRequestData(
                plugin_name=self.plugin_name,
                plugin_developer=self.plugin_developer,
                authentication_token=self.authentication_token,
            ),
        )
        if not data.authenticated:
            self.authentication_token = None
            raise AuthenticationFailedError(data)
        self.authenticated = True
        self.dispatch_handlers(self.authenticated_handlers)
