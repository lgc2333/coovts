from typing import Any

from ..shared import VTSBaseModel


class EventSubscriptionRequest(VTSBaseModel):
    event_name: str
    subscribe: bool
    config: Any


class EventSubscriptionResponse(VTSBaseModel):
    subscribed_event_count: int
    subscribed_events: list[str]
