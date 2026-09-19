import asyncio
import base64
from collections.abc import Callable, Iterable, Iterator
from enum import Enum, auto
from pathlib import Path
from types import CoroutineType, EllipsisType
from typing import TYPE_CHECKING, Any, overload, override

import websockets as ws
from pydantic import BaseModel
from websockets.exceptions import WebSocketException

from .errors import APIError, AuthenticationFailedError, NetworkError
from .event import EventRegistration, EventSubscriptionRegistry, RawEventRegistration
from .request import RequestManager
from .types import (
    BaseRequest,
    BaseResponse,
    get_api_response_model,
    get_message_type,
)
from .types.api import (
    AuthenticationRequest,
    AuthenticationTokenRequest,
    EventSubscriptionRequest,
    EventSubscriptionResponse,
)
from .types.consts import ErrorID
from .types.plugin_api import PluginAPI

if TYPE_CHECKING:
    from asyncio import Task

type C[T] = CoroutineType[Any, Any, T]

type ConnectingHandler = Callable[[], C[Any]]
type ConnectedHandler = Callable[[], C[Any]]
type ConnectFailedHandler = Callable[[Exception], C[Any]]
type ConnectionClosedHandler = Callable[[Exception], C[Any]]
type DisconnectFailedHandler = Callable[[Exception], C[Any]]
type ParseDataErrorHandler = Callable[[str | bytes, Exception], C[Any]]
type AuthenticationTokenGotHandler = Callable[[str], C[Any]]
type AuthenticatedHandler = Callable[[], C[Any]]
type AuthenticationFailedHandler = Callable[[Exception], C[Any]]
type HandlerRunFailedHandler = Callable[[Exception], C[Any]]
type SubscribeFailedHandler = Callable[[EventRegistration, Exception], C[Any]]
type RecvRawHandler = Callable[[str | bytes], C[Any]]
type BeforeSendRawHandler = Callable[[str], C[Any]]

DEFAULT_ENDPOINT = "ws://localhost:8001"
CONNECTION_LOST_MESSAGE = "Connection to VTube Studio was lost"

_FATAL_AUTH_ERROR_IDS: frozenset[ErrorID] = frozenset(
    {
        ErrorID.APIAccessDeactivated,
        ErrorID.JSONInvalid,
        ErrorID.APINameInvalid,
        ErrorID.APIVersionInvalid,
        ErrorID.TokenRequestDenied,
        ErrorID.TokenRequestPluginNameInvalid,
        ErrorID.TokenRequestDeveloperNameInvalid,
        ErrorID.TokenRequestPluginIconInvalid,
        ErrorID.AuthenticationTokenMissing,
        ErrorID.AuthenticationPluginNameMissing,
        ErrorID.AuthenticationPluginDeveloperMissing,
    },
)
"""Authentication refusals that retrying cannot fix. Plugin stops when VTS answers these."""


class Hook[T]:
    """Registers the handlers of one lifecycle hook."""

    def __init__(self) -> None:
        self._handlers: list[T] = []

    def __call__(self, handler: T) -> T:
        self._handlers.append(handler)
        return handler

    def __iter__(self) -> Iterator[T]:
        return iter(self._handlers)


def start_handler_task[R](
    coro: C[R],
    running: "set[Task[Any]] | None" = None,
) -> "Task[R]":
    """Start one handler task, and keep it in `running` for as long as it lives."""
    task = asyncio.create_task(coro)
    if running is not None:
        running.add(task)
        task.add_done_callback(running.discard)
    return task


def dispatch_handlers_inner[**P, R](
    handlers: Iterable[Callable[P, C[R]]],
    run_failed_handlers: Iterable[HandlerRunFailedHandler] | None = None,
    running: "set[Task[Any]] | None" = None,
    *args: P.args,
    **kwargs: P.kwargs,
) -> list["Task[R | Exception]"]:
    async def run_task(f: Callable[P, C[R]]) -> R | Exception:
        try:
            return await f(*args, **kwargs)
        except Exception as e:
            if run_failed_handlers:
                dispatch_handlers_inner(run_failed_handlers, None, running, e)
            return e

    return [start_handler_task(run_task(x), running) for x in handlers]


class PluginState(Enum):
    STOPPED = auto()
    DISCONNECTED = auto()
    CONNECTING = auto()
    AUTHENTICATING = auto()
    AUTHENTICATED = auto()


class Plugin(PluginAPI):
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

        self.on_connecting: Hook[ConnectingHandler] = Hook()
        self.on_connected: Hook[ConnectedHandler] = Hook()
        self.on_connect_failed: Hook[ConnectFailedHandler] = Hook()
        self.on_connection_closed: Hook[ConnectionClosedHandler] = Hook()
        self.on_disconnect_failed: Hook[DisconnectFailedHandler] = Hook()
        self.on_parse_data_error: Hook[ParseDataErrorHandler] = Hook()
        self.on_authentication_token_got: Hook[AuthenticationTokenGotHandler] = Hook()
        self.on_authenticated: Hook[AuthenticatedHandler] = Hook()
        self.on_authenticate_failed: Hook[AuthenticationFailedHandler] = Hook()
        self.on_handler_run_failed: Hook[HandlerRunFailedHandler] = Hook()
        self.on_subscribe_failed: Hook[SubscribeFailedHandler] = Hook()
        self.on_recv_raw: Hook[RecvRawHandler] = Hook()
        self.on_before_send_raw: Hook[BeforeSendRawHandler] = Hook()

        self.client: ws.ClientConnection | None = None
        self._stopped = True
        self.req_manager = RequestManager()
        self.subscriptions = EventSubscriptionRegistry(self._send_subscription)

        self._state = PluginState.STOPPED
        self._recv_task: Task | None = None
        self._run_task: Task | None = None
        self._handler_tasks: set[Task[Any]] = set()
        # Bumped by every disconnect, so a receive loop can tell its session is over.
        self._session = 0
        self._connect_lock = asyncio.Lock()
        # Set while a socket is up, and when the run ends, so a waiter cannot hang.
        self._connected = asyncio.Event()

    @staticmethod
    def prepare_icon(icon: str | bytes | Path) -> str:
        if isinstance(icon, Path):
            icon = icon.read_bytes()
        if isinstance(icon, bytes):
            icon = base64.b64encode(icon).decode()
        return icon

    @property
    def state(self) -> PluginState:
        return self._state

    @overload
    def handle_event[T: BaseModel](
        self,
        event_data_model: type[T],
    ) -> EventRegistration[T]: ...
    @overload
    def handle_event(self, event_data_model: str) -> RawEventRegistration: ...
    def handle_event(
        self,
        event_data_model: type[BaseModel] | str,
    ) -> EventRegistration[Any] | RawEventRegistration:
        """Register a handler for an event without subscribing to it; decorate with the result.

        An event named by its wire name is not decoded, so its handlers get the raw payload.
        """
        registration = self.subscriptions.registration(event_data_model)
        if isinstance(event_data_model, str):
            return RawEventRegistration(registration)
        return registration

    @override
    def _subscribe_event(
        self,
        event_data_model: type[BaseModel] | str,
        config: Any = None,
    ) -> EventRegistration[Any] | RawEventRegistration:
        registration = self.subscriptions.subscribe(event_data_model, config)
        if isinstance(event_data_model, str):
            return RawEventRegistration(registration)
        return registration

    async def _send_subscription(
        self,
        request: EventSubscriptionRequest,
    ) -> EventSubscriptionResponse:
        return await self.call_api(request)

    def dispatch_handlers[**P, R](
        self,
        handlers: Iterable[Callable[P, C[R]]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> list["Task[R | Exception]"]:
        return dispatch_handlers_inner(
            handlers,
            self.on_handler_run_failed,
            self._handler_tasks,
            *args,
            **kwargs,
        )

    def ensure_client(self) -> ws.ClientConnection:
        if not self.client:
            raise NetworkError("Not connected to VTube Studio")
        return self.client

    def _handle_raw(self, raw: str | bytes) -> None:
        self.dispatch_handlers(self.on_recv_raw, raw)

        try:
            resp = BaseResponse.model_validate_json(raw)
        except Exception as e:
            self.dispatch_handlers(self.on_parse_data_error, raw, e)
            return

        if resp.request_id and (pending := self.req_manager.take(resp.request_id)):
            pending.resolve(
                raw,
                resp.data,
                is_error=resp.message_type == APIError.message_type,
            )

        registration = self.subscriptions.get(resp.message_type)
        if registration is None:
            return

        # One decode per model, in handler order: a frame that does not decode is reported once.
        decoded: dict[type[BaseModel], Any] = {}
        for data_model in dict.fromkeys(
            model for model, _ in registration.handlers if model is not None
        ):
            try:
                decoded[data_model] = data_model.model_validate(resp.data)
            except Exception as e:
                self.dispatch_handlers(self.on_parse_data_error, raw, e)

        for data_model, handler in registration.handlers:
            if data_model is None:
                self.dispatch_handlers([handler], resp.data)
            elif data_model in decoded:
                self.dispatch_handlers([handler], decoded[data_model])

    async def _recv(self, client: ws.ClientConnection):
        self._handle_raw(await client.recv())

    async def _recv_loop(self, client: ws.ClientConnection, session: int) -> None:
        """Receive frames until the socket fails, or until this session is dropped.

        A cancellation from a session that is already replaced ends the loop quietly, so the run
        awaiting it survives (ADR-0019).
        """
        try:
            while True:
                await self._recv(client)
        except asyncio.CancelledError:
            if self._session == session:
                raise
            return
        except Exception as e:
            if self._session != session:
                return
            self.client = None
            self._state = (
                PluginState.STOPPED if self._stopped else PluginState.DISCONNECTED
            )
            self.req_manager.reset(CONNECTION_LOST_MESSAGE)
            self.dispatch_handlers(self.on_connection_closed, e)
            try:
                await asyncio.sleep(self.reconnect_delay)
            except asyncio.CancelledError:
                if self._session == session:
                    raise
                return

    async def _disconnect(self, pending_error: str | None):
        client = self.client
        task = self._recv_task
        self.client = None
        self._recv_task = None
        # Whatever is receiving now belongs to a past session, and must end quietly.
        self._session += 1
        self._connected.clear()
        self._state = PluginState.STOPPED if self._stopped else PluginState.DISCONNECTED
        self.req_manager.reset(pending_error)
        try:
            if client and (client.close_code is None):
                await client.close()
        finally:
            if task and (not task.done()):
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

    async def reconnect(self, *, wait_connect: bool = False) -> None:
        """Ask for a fresh session; a run in progress opens it, otherwise this call connects.

        Never raises while a run is in progress, and `wait_connect` waits for the new socket, not
        for authentication.
        """
        if not self._connect_lock.locked():
            if self._run_task and (not self._run_task.done()):
                try:
                    async with self._connect_lock:
                        await self._disconnect(CONNECTION_LOST_MESSAGE)
                except Exception as e:
                    # The session is dropped either way; only the close failed to say so.
                    self.dispatch_handlers(self.on_disconnect_failed, e)
            else:
                await self._open_session()

        if wait_connect:
            await self._connected.wait()

    async def _open_session(self):
        """Connect to the endpoint and start receiving; the run in progress calls this."""
        async with self._connect_lock:
            await self._disconnect(CONNECTION_LOST_MESSAGE)

            self._state = PluginState.CONNECTING
            self.dispatch_handlers(self.on_connecting)
            try:
                client = await ws.connect(self.endpoint)
            except BaseException:
                self._state = (
                    PluginState.STOPPED if self._stopped else PluginState.DISCONNECTED
                )
                raise

            self.client = client
            self._state = PluginState.AUTHENTICATING
            self.dispatch_handlers(self.on_connected)
            task = asyncio.create_task(self._recv_loop(client, self._session))
            self._recv_task = task
            self._connected.set()
            return task

    async def stop(self):
        self._stopped = True
        if self._run_task:
            self._run_task.cancel()
            await asyncio.gather(self._run_task, return_exceptions=True)
        try:
            # Sweep after the disconnect (a drop landing here dispatches handlers), and even when
            # the close refuses.
            await self._disconnect(None)
        finally:
            handler_tasks = tuple(self._handler_tasks)
            for task in handler_tasks:
                task.cancel()
            await asyncio.gather(*handler_tasks, return_exceptions=True)
            self._handler_tasks.clear()
            self._run_task = None

    async def _resubscribe(self) -> None:
        """Re-send every declared subscription, which a new session does not remember."""
        for registration in self.subscriptions:
            if registration.config is None:
                continue
            try:
                await self.subscriptions.send(registration)
            except Exception as e:
                self.dispatch_handlers(self.on_subscribe_failed, registration, e)

    async def _run(self):
        self._stopped = False
        self._state = PluginState.DISCONNECTED
        self._connected.clear()

        try:
            while True:
                try:
                    task = await self._open_session()
                except Exception as e:
                    self.dispatch_handlers(self.on_connect_failed, e)
                    await asyncio.sleep(self.reconnect_delay)
                    continue

                session = self._session
                try:
                    await self.authenticate()
                except Exception as e:
                    if self._session != session:
                        # The session was dropped while authenticating: not a refusal to report.
                        continue
                    self.dispatch_handlers(self.on_authenticate_failed, e)
                    if (
                        isinstance(e, APIError)
                        and e.data.error_id in _FATAL_AUTH_ERROR_IDS
                    ):
                        self._stopped = True
                    try:
                        await self._disconnect(CONNECTION_LOST_MESSAGE)
                    except Exception as disconnect_error:
                        self.dispatch_handlers(
                            self.on_disconnect_failed,
                            disconnect_error,
                        )
                    if self._stopped:
                        break
                    await asyncio.sleep(self.reconnect_delay)
                    continue

                await task
        finally:
            self._connected.set()

    def run(self):
        if self._run_task and not self._run_task.done():
            raise RuntimeError("Already running")
        self._run_task = asyncio.create_task(self._run())
        return self._run_task

    @overload
    async def send_request[M: BaseModel](
        self,
        request: BaseRequest,
        response_model: type[M],
        api_timeout: float | EllipsisType | None = ...,
    ) -> M: ...
    @overload
    async def send_request(
        self,
        request: BaseRequest,
        response_model: type[BaseModel] | None = None,
        api_timeout: float | EllipsisType | None = ...,
    ) -> dict[str, Any]: ...
    async def send_request(
        self,
        request: BaseRequest,
        response_model: type[BaseModel] | None = None,
        api_timeout: float | EllipsisType | None = ...,
    ) -> Any:
        req_timeout = self.api_timeout if api_timeout is ... else api_timeout

        client = self.ensure_client()
        pending = self.req_manager.start(response_model)
        request.request_id = pending.req_id

        payload = request.model_dump_json()
        self.dispatch_handlers(self.on_before_send_raw, payload)
        try:
            try:
                await client.send(payload)
            except (WebSocketException, OSError) as e:
                raise NetworkError(CONNECTION_LOST_MESSAGE) from e
            return await pending.result(req_timeout)
        finally:
            self.req_manager.discard(pending.req_id)

    @override
    async def _call_api(
        self,
        data: Any,
        *,
        message_type: str | None = None,
        response_model: type[BaseModel] | EllipsisType | None = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | EllipsisType | None = ...,
    ) -> Any:
        req_timeout = self.api_timeout if api_timeout is ... else api_timeout

        if not message_type:
            if not isinstance(data, BaseModel):
                raise TypeError(
                    "'message_type' is required when 'data' is not a model",
                )
            message_type = get_message_type(data)

        if response_model is ...:
            if not isinstance(data, BaseModel):
                raise TypeError(
                    "'response_model' is required when 'data' is not a model",
                )
            response_model = get_api_response_model(data)

        request = BaseRequest(
            api_name=api_name,
            api_version=api_version,
            message_type=message_type,
            data=data,
        )
        return await self.send_request(
            request,
            response_model=response_model,
            api_timeout=req_timeout,
        )

    async def authenticate(self):
        if self._state is PluginState.AUTHENTICATED:
            return

        if not self.authentication_token:
            token_data = await self.call_api(
                AuthenticationTokenRequest(
                    plugin_name=self.plugin_name,
                    plugin_developer=self.plugin_developer,
                    plugin_icon=self.plugin_icon,
                ),
            )
            self.authentication_token = token_data.authentication_token
            self.dispatch_handlers(
                self.on_authentication_token_got,
                token_data.authentication_token,
            )

        data = await self.call_api(
            AuthenticationRequest(
                plugin_name=self.plugin_name,
                plugin_developer=self.plugin_developer,
                authentication_token=self.authentication_token,
            ),
        )
        if not data.authenticated:
            self.authentication_token = None
            raise AuthenticationFailedError(data)
        self._state = PluginState.AUTHENTICATED
        await self._resubscribe()
        self.dispatch_handlers(self.on_authenticated)
