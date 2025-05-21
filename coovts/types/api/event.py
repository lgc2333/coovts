from typing import Any, ClassVar

from pydantic import BaseModel

from ..registry import request_model, response_model


@request_model
class EventSubscriptionRequest(BaseModel):
    msg_t: ClassVar[str] = "EventSubscriptionRequest"
    event_name: str
    subscribe: bool
    config: Any


@response_model
class EventSubscriptionResponse(BaseModel):
    msg_t: ClassVar[str] = "EventSubscriptionResponse"
    subscribed_event_count: int
    subscribed_events: list[str]
