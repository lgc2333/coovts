from typing import Annotated, Any

from cookit.pyd import model_with_model_config
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

request_model_config = ConfigDict(
    alias_generator=to_camel,
    validate_by_alias=False,
    serialize_by_alias=True,
)
response_model_config = ConfigDict(
    alias_generator=to_camel,
)


with_request_model_config = model_with_model_config(request_model_config)
with_response_model_config = model_with_model_config(response_model_config)


@with_request_model_config
class BaseRequest(BaseModel):
    api_name: str = "VTubeStudioPublicAPI"
    api_version: str = "1.0"
    request_id: Annotated[str | None, Field(alias="requestID")] = None
    message_type: str
    data: Any


@with_response_model_config
class BaseResponse(BaseModel):
    api_name: str
    api_version: str = "1.0"
    timestamp: int
    """13 digits"""
    request_id: Annotated[str | None, Field(alias="requestID")]
    message_type: str
    data: Any


def get_api_response_model(model: type[BaseModel] | BaseModel) -> type[BaseModel]:
    if not isinstance(model, type):
        model = type(model)

    if resp_m := getattr(model, "resp_m", None):
        if issubclass(resp_m, BaseModel):
            return resp_m
        raise TypeError(f"Model's 'resp_m' should be a BaseModel, not {type(resp_m)}")

    from . import api

    if resp_t := getattr(model, "resp_t", None):
        if not isinstance(resp_t, str):
            raise TypeError(f"Model's 'resp_t' should be a str, not {type(resp_t)}")
        if resp_m := getattr(api, resp_t, None):
            return resp_m
        raise ValueError(f"Model's resp_t '{resp_t}' not found in api module")

    if model.__name__.endswith("Request"):
        resp_t = f"{model.__name__[:-7]}Response"
        if resp_t and (resp_m := getattr(api, resp_t, None)):
            return resp_m

    raise ValueError(
        f"Cannot find suitable response model for {model}, please define manually",
    )


def get_message_type(model: type[BaseModel] | BaseModel) -> str:
    if not isinstance(model, type):
        model = type(model)
    if msg_t := getattr(model, "msg_t", None):
        if isinstance(msg_t, str):
            return msg_t
        raise TypeError(f"Model's 'msg_t' should be a str, not {type(msg_t)}")
    return model.__name__


def get_event_name(model: type[BaseModel] | BaseModel) -> str:
    if not isinstance(model, type):
        model = type(model)
    if msg_t := getattr(model, "msg_t", None):
        if isinstance(msg_t, str):
            return msg_t
        raise TypeError(f"Model's 'msg_t' should be a str, not {type(msg_t)}")
    if model.__name__.endswith("EventData"):
        return model.__name__[:-4]
    raise ValueError(
        f"Cannot find suitable event name for {model}, please define manually",
    )
