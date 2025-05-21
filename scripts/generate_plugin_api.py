from pathlib import Path

from pydantic import BaseModel

from coovts.types import api, event, get_api_response_model, get_message_type
from coovts.types.shared import get_event_name

FILE_HEAD = """\
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from types import EllipsisType
from typing import Any, Literal, overload

from pydantic import BaseModel

from . import api, event

type _Deco[**P, R] = Callable[[Callable[P, R]], Callable[P, R]]
type _Co[T] = Coroutine[Any, Any, T]

class PluginAPI(ABC):
    @abstractmethod
    async def _call_api(
        self,
        data: Any,
        *,
        message_type: str | None = None,
        response_model: type[BaseModel] | None | EllipsisType = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> Any: ...
    @abstractmethod
    def _handle_event[T: BaseModel](
        self,
        event_data_model: type[T],
        event_name: str | None = None,
    ) -> _Deco[[T], _Co[Any]]: ...

    # region builtin apis
"""

API_TEMPLATE = """
    @overload
    async def call_api(
        self,
        data: api.{req},
        *,
        message_type: Literal["{msg_t}"] = ...,
        response_model: type[api.{resp}] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.{resp}: ..."""

API_REST = """

    # endregion

    @overload
    async def call_api[M: BaseModel](
        self,
        data: BaseModel,
        *,
        message_type: str | None = None,
        response_model: type[M],
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> M: ...
    @overload
    async def call_api(
        self,
        data: BaseModel,
        *,
        message_type: str | None = None,
        response_model: None = None,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> dict[str, Any]: ...
    # otherwise message_type is required
    @overload
    async def call_api[M: BaseModel](
        self,
        data: Any,
        *,
        message_type: str,
        response_model: type[M],
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> M: ...
    @overload
    async def call_api(
        self,
        data: Any,
        *,
        message_type: str,
        response_model: None = None,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> dict[str, Any]: ...
"""

EVENT_HEAD = """
    # region builtin events
"""

EVENT_TEMPLATE = """
    @overload
    def handle_event[T: event.{model}](
        self,
        event_data_model: type[T],
        event_name: Literal["{name}"] = ...,
    ) -> _Deco[[T], _Co[Any]]: ..."""

EVENT_TAIL = """

    # endregion

    @overload
    def handle_event[T: BaseModel](
        self,
        event_data_model: type[T],
        event_name: str | None = None,
    ) -> _Deco[[T], _Co[Any]]: ...
"""

PYI_PATH = Path(__file__).parent.parent / "coovts" / "types" / "plugin_api.pyi"

with PYI_PATH.open("w", encoding="u8") as f:
    f.write(FILE_HEAD)
    for name, model in api.__dict__.items():
        if not name.endswith("Request"):
            continue
        assert issubclass(model, BaseModel)
        f.write(
            API_TEMPLATE.format(
                req=model.__name__,
                msg_t=get_message_type(model),
                resp=get_api_response_model(model).__name__,
            ),
        )
    f.write(API_REST)

    f.write(EVENT_HEAD)
    for name, model in event.__dict__.items():
        if not name.endswith("EventData"):
            continue
        assert issubclass(model, BaseModel)
        f.write(
            EVENT_TEMPLATE.format(
                name=get_event_name(model),
                model=model.__name__,
            ),
        )
    f.write(EVENT_TAIL)
