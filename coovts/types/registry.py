from cookit.pyd import model_with_model_config
from pydantic import BaseModel

from .shared import request_model_config, response_model_config


class APIDataModelCollector:
    def __init__(self):
        self.data: dict[str, type[BaseModel]] = {}

    def __call__[T: type[BaseModel]](self, model: T) -> T:
        if not hasattr(model, "msg_t"):
            raise ValueError("Model must have a 'msg_t' attribute")
        msg_t = getattr(model, "msg_t", None)
        if not isinstance(msg_t, str):
            raise TypeError("Model's 'msg_t' attribute must be a string")
        if msg_t in self.data:
            raise ValueError(f"Model with msg_t '{msg_t}' already exists")
        self.data[msg_t] = model
        return model


models = APIDataModelCollector()
event_configs = APIDataModelCollector()


def request_model[T: type[BaseModel]](m: T) -> T:
    return models(model_with_model_config(request_model_config)(m))


def response_model[T: type[BaseModel]](m: T) -> T:
    return models(model_with_model_config(response_model_config)(m))


def event_config_model[T: type[BaseModel]](m: T) -> T:
    return event_configs(model_with_model_config(request_model_config)(m))


request_param_model = model_with_model_config(request_model_config)
response_param_model = model_with_model_config(response_model_config)
