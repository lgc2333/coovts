import argparse
import difflib
import sys
from itertools import islice
from pathlib import Path

from pydantic import BaseModel

from coovts.types import (
    api,
    event,
    get_api_response_model,
    get_event_config_model,
    get_message_type,
)

FILE_HEAD = """\
from abc import ABC, abstractmethod
from types import EllipsisType
from typing import Any, Literal, overload

from pydantic import BaseModel

from ..event import EventRegistration, RawEventRegistration
from . import api, event

class PluginAPI(ABC):
    @abstractmethod
    async def _call_api(
        self,
        data: Any,
        *,
        message_type: str | None = None,
        response_model: type[BaseModel] | EllipsisType | None = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | EllipsisType | None = ...,
    ) -> Any: ...
    @abstractmethod
    def _subscribe_event(
        self,
        event_data_model: type[BaseModel] | str,
        config: Any = None,
    ) -> EventRegistration[Any] | RawEventRegistration: ...

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
        api_timeout: float | EllipsisType | None = ...,
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
        api_timeout: float | EllipsisType | None = ...,
    ) -> M: ...
    # an omitted response_model is derived from the payload's resp_m / resp_t, or from the
    # Request -> Response convention, so it still answers with a model; only an explicit None
    # asks for the raw response body
    @overload
    async def call_api(
        self,
        data: BaseModel,
        *,
        message_type: str | None = None,
        response_model: EllipsisType = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | EllipsisType | None = ...,
    ) -> BaseModel: ...
    @overload
    async def call_api(
        self,
        data: BaseModel,
        *,
        message_type: str | None = None,
        response_model: None = None,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | EllipsisType | None = ...,
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
        api_timeout: float | EllipsisType | None = ...,
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
        api_timeout: float | EllipsisType | None = ...,
    ) -> dict[str, Any]: ...
"""

SUBSCRIPTION_HEAD = """
    # region builtin event subscriptions
"""

SUBSCRIPTION_TEMPLATE = """
    @overload
    def subscribe_event(
        self,
        event_data_model: type[event.{data}],
        config: event.{config}{optional},
    ) -> EventRegistration[event.{data}]: ..."""

SUBSCRIPTION_TAIL = """

    # endregion

    @overload
    def subscribe_event[T: BaseModel](
        self,
        event_data_model: type[T],
        config: Any | None,
    ) -> EventRegistration[T]: ...
    @overload
    def subscribe_event(
        self,
        event_data_model: str,
        config: Any | None = None,
    ) -> RawEventRegistration: ...
"""

ROOT = Path(__file__).parent.parent
PYI_PATH = ROOT / "coovts" / "types" / "plugin_api.pyi"
REFERENCES_PATH = ROOT / "docs" / "references.md"


def event_data_models() -> tuple[type[BaseModel], ...]:
    """The event data models the stub's event surface is generated from."""
    models = []
    for name, model in event.__dict__.items():
        if not name.endswith("EventData"):
            continue
        assert issubclass(model, BaseModel), f"{name} is not a pydantic model"
        models.append(model)
    return tuple(models)


def render() -> str:
    """Build the whole stub as a string."""
    parts = [FILE_HEAD]
    for name, model in api.__dict__.items():
        if not name.endswith("Request"):
            continue
        assert issubclass(model, BaseModel), f"{name} is not a pydantic model"
        parts.append(
            API_TEMPLATE.format(
                req=model.__name__,
                msg_t=get_message_type(model),
                resp=get_api_response_model(model).__name__,
            ),
        )
    parts.append(API_REST)

    events = event_data_models()
    parts.append(SUBSCRIPTION_HEAD)
    for model in events:
        config_model = get_event_config_model(model)
        # Only a config with a required field has to be passed: every other one can be built
        # from its own defaults, so `subscribe_event` accepts its absence.
        optional = (
            ""
            if any(field.is_required() for field in config_model.model_fields.values())
            else " | None = None"
        )
        parts.append(
            SUBSCRIPTION_TEMPLATE.format(
                data=model.__name__,
                config=config_model.__name__,
                optional=optional,
            ),
        )
    parts.append(SUBSCRIPTION_TAIL)
    return "".join(parts)


def stats() -> str:
    """Describe the surface the stub is generated from."""
    api_models = [
        value
        for value in api.__dict__.values()
        if isinstance(value, type) and issubclass(value, BaseModel)
    ]
    requests = [name for name in api.__dict__ if name.endswith("Request")]
    events = event_data_models()
    event_models = [
        name for name in event.__dict__ if name.endswith(("EventData", "EventConfig"))
    ]
    return (
        f"{len(requests)} call_api overloads (plus {API_REST.count('@overload')} generic ones) "
        f"from {len(api_models)} api models, "
        f"{len(events)} subscribe_event overloads (plus 1 generic one and 1 by event name) from "
        f"{len(event_models)} event models"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the typed PluginAPI stub.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift instead of writing the stub",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="render and report the covered surface without writing the stub",
    )
    args = parser.parse_args()

    content = render()
    print(stats())
    print(
        f"these counts are recorded in {REFERENCES_PATH.relative_to(ROOT).as_posix()}; "
        "update it when they change",
    )

    if args.check:
        current = PYI_PATH.read_text(encoding="u8") if PYI_PATH.exists() else ""
        if current == content:
            print(f"{PYI_PATH.name} is up to date")
            return 0
        diff = difflib.unified_diff(
            current.splitlines(keepends=True),
            content.splitlines(keepends=True),
            fromfile=f"{PYI_PATH} (on disk)",
            tofile=f"{PYI_PATH} (generated)",
        )
        print("".join(islice(diff, 40)), end="")
        print(f"{PYI_PATH.name} is out of date, run `poe gen-api`", file=sys.stderr)
        return 1

    if args.dry_run:
        return 0

    tmp_path = PYI_PATH.with_name(f"{PYI_PATH.name}.tmp")
    tmp_path.write_text(content, encoding="u8", newline="\n")
    tmp_path.replace(PYI_PATH)
    print(f"wrote {PYI_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
