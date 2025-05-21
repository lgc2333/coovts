from typing import Any, ClassVar

from pydantic import BaseModel

from ..registry import (
    event_config_model,
    request_model,
    response_model,
    response_param_model,
)


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


@event_config_model
class TestEventConfig(BaseModel):
    msg_t: ClassVar[str] = "TestEvent"
    test_message_for_event: str


@response_model
class TestEventData(BaseModel):
    msg_t: ClassVar[str] = "TestEvent"
    your_test_message: str
    counter: int


@event_config_model
class ModelLoadedEventConfig(BaseModel):
    msg_t: ClassVar[str] = "ModelLoadedEvent"
    model_id: list[str] | None = None


@response_model
class ModelLoadedEventData(BaseModel):
    msg_t: ClassVar[str] = "ModelLoadedEvent"
    model_loaded: bool
    model_name: str
    model_id: str


@event_config_model
class TrackingStatusChangedEventConfig(BaseModel):
    msg_t: ClassVar[str] = "TrackingStatusChangedEvent"


@response_model
class TrackingStatusChangedEventData(BaseModel):
    msg_t: ClassVar[str] = "TrackingStatusChangedEvent"
    face_found: bool
    left_hand_found: bool
    right_hand_found: bool


@event_config_model
class HotkeyTriggeredEventConfig(BaseModel):
    msg_t: ClassVar[str] = "HotkeyTriggeredEvent"
    only_for_action: str | None = None
    ignore_hotkeys_triggered_by_api: bool = False


@response_model
class HotkeyTriggeredEventData(BaseModel):
    msg_t: ClassVar[str] = "HotkeyTriggeredEvent"
    hotkey_id: str
    hotkey_name: str
    hotkey_action: str
    hotkey_file: str
    hotkey_triggered_by_api: bool
    model_id: str
    model_name: str
    is_live2d_item: bool


@event_config_model
class ModelMovedEventConfig(BaseModel):
    msg_t: ClassVar[str] = "ModelMovedEvent"


@response_param_model
class ModelPosition(BaseModel):
    position_x: float
    position_y: float
    size: float
    rotation: float


@response_model
class ModelMovedEventData(BaseModel):
    msg_t: ClassVar[str] = "ModelMovedEvent"
    model_id: str
    model_name: str
    model_position: ModelPosition


@event_config_model
class ModelOutlineEventConfig(BaseModel):
    msg_t: ClassVar[str] = "ModelOutlineEvent"
    draw: bool = False


@response_param_model
class Point2D(BaseModel):
    x: float
    y: float


@response_model
class ModelOutlineEventData(BaseModel):
    msg_t: ClassVar[str] = "ModelOutlineEvent"
    model_name: str
    model_id: str
    convex_hull: list[Point2D]
    convex_hull_center: Point2D
    window_size: Point2D


@event_config_model
class ModelClickedEventConfig(BaseModel):
    msg_t: ClassVar[str] = "ModelClickedEvent"
    only_clicks_on_model: bool = True


@response_model
class ArtMeshHitInfo(BaseModel):
    model_id: str
    art_mesh_id: str
    angle: float
    size: float
    vertex_id1: int
    vertex_id2: int
    vertex_id3: int
    vertex_weight1: float
    vertex_weight2: float
    vertex_weight3: float


@response_param_model
class ArtMeshHit(BaseModel):
    art_mesh_order: int
    is_masked: bool
    hit_info: ArtMeshHitInfo


@response_model
class ModelClickedEventData(BaseModel):
    msg_t: ClassVar[str] = "ModelClickedEvent"
    model_loaded: bool
    loaded_model_id: str
    loaded_model_name: str
    model_was_clicked: bool
    mouse_button_id: int
    click_position: Point2D
    window_size: Point2D
    clicked_art_mesh_count: int
    art_mesh_hits: list[ArtMeshHit]


@event_config_model
class ItemEventConfig(BaseModel):
    msg_t: ClassVar[str] = "ItemEvent"
    item_instance_ids: list[str] | None = None
    item_file_names: list[str] | None = None


@response_model
class ItemEventData(BaseModel):
    msg_t: ClassVar[str] = "ItemEvent"
    item_event_type: str
    item_instance_id: str
    item_file_name: str
    item_position: Point2D


@event_config_model
class Live2DCubismEditorConnectedEventConfig(BaseModel):
    msg_t: ClassVar[str] = "Live2DCubismEditorConnectedEvent"


@response_model
class Live2DCubismEditorConnectedEventData(BaseModel):
    msg_t: ClassVar[str] = "Live2DCubismEditorConnectedEvent"
    trying_to_connect: bool
    connected: bool
    should_send_parameters: bool
