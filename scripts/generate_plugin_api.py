from pathlib import Path

from pydantic import BaseModel

from coovts.types import api, get_api_response_model, get_message_type

FILE_HEAD = """\
from abc import ABC, abstractmethod
from types import EllipsisType
from typing import Any, overload

from pydantic import BaseModel

from . import api

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

    # region builtin apis
"""

API_TEMPLATE = """
    @overload
    async def call_api(
        self,
        data: api.{req},
        *,
        message_type: str = "{msg_t}",
        response_model: type[api.{resp}] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.{resp}: ..."""

API_REST = """

    # endregion

    # if data is a model, we consider it has msg_t class var
    # so message_type is optional
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

PYI_PATH = Path(__file__).parent.parent / "coovts" / "types" / "plugin_api.pyi"

with PYI_PATH.open("w", encoding="u8") as f:
    f.write(FILE_HEAD)

    for name, model in api.__dict__.items():
        if not name.endswith("Request"):
            continue

        print(f"Generating {name} API")
        assert issubclass(model, BaseModel)

        f.write(
            API_TEMPLATE.format(
                req=model.__name__,
                msg_t=get_message_type(model),
                resp=get_api_response_model(model).__name__,
            ),
        )

    f.write(API_REST)
