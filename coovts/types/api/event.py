from typing import Any

from pydantic import BaseModel

from ..shared import with_request_model_config, with_response_model_config


@with_request_model_config
class EventSubscriptionRequest(BaseModel):
    event_name: str
    subscribe: bool
    config: Any


@with_response_model_config
class EventSubscriptionResponse(BaseModel):
    subscribed_event_count: int
    subscribed_events: list[str]
