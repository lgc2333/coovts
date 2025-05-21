from typing import Annotated

from pydantic import BaseModel, Field

from ..shared import with_request_model_config, with_response_model_config


@with_request_model_config
class TestEventConfig(BaseModel):
    test_message_for_event: str


@with_response_model_config
class TestEventData(BaseModel):
    your_test_message: str
    counter: int


@with_request_model_config
class ModelLoadedEventConfig(BaseModel):
    model_id: Annotated[list[str] | None, Field(alias="modelID")] = None


@with_response_model_config
class ModelLoadedEventData(BaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]


@with_request_model_config
class TrackingStatusChangedEventConfig(BaseModel):
    pass


@with_response_model_config
class TrackingStatusChangedEventData(BaseModel):
    face_found: bool
    left_hand_found: bool
    right_hand_found: bool


@with_request_model_config
class HotkeyTriggeredEventConfig(BaseModel):
    only_for_action: str | None = None
    ignore_hotkeys_triggered_by_api: bool = False


@with_response_model_config
class HotkeyTriggeredEventData(BaseModel):
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
    hotkey_name: str
    hotkey_action: str
    hotkey_file: str
    hotkey_triggered_by_api: bool
    model_id: Annotated[str, Field(alias="modelID")]
    model_name: str
    is_live2d_item: bool


@with_response_model_config
class ModelPosition(BaseModel):
    position_x: float
    position_y: float
    size: float
    rotation: float


@with_request_model_config
class ModelMovedEventConfig(BaseModel):
    pass


@with_response_model_config
class ModelMovedEventData(BaseModel):
    model_id: Annotated[str, Field(alias="modelID")]
    model_name: str
    model_position: ModelPosition


@with_request_model_config
class ModelOutlineEventConfig(BaseModel):
    draw: bool = False


@with_response_model_config
class Point2D(BaseModel):
    x: float
    y: float


@with_response_model_config
class ModelOutlineEventData(BaseModel):
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    convex_hull: list[Point2D]
    convex_hull_center: Point2D
    window_size: Point2D


@with_response_model_config
class ArtMeshHitInfo(BaseModel):
    model_id: Annotated[str, Field(alias="modelID")]
    art_mesh_id: Annotated[str, Field(alias="artMeshID")]
    angle: float
    size: float
    vertex_id1: Annotated[int, Field(alias="vertexID1")]
    vertex_id2: Annotated[int, Field(alias="vertexID2")]
    vertex_id3: Annotated[int, Field(alias="vertexID3")]
    vertex_weight1: float
    vertex_weight2: float
    vertex_weight3: float


@with_response_model_config
class ArtMeshHit(BaseModel):
    art_mesh_order: int
    is_masked: bool
    hit_info: ArtMeshHitInfo


@with_request_model_config
class ModelClickedEventConfig(BaseModel):
    only_clicks_on_model: bool = True


@with_response_model_config
class ModelClickedEventData(BaseModel):
    model_loaded: bool
    loaded_model_id: Annotated[str, Field(alias="loadedModelID")]
    loaded_model_name: str
    model_was_clicked: bool
    mouse_button_id: Annotated[int, Field(alias="mouseButtonID")]
    click_position: Point2D
    window_size: Point2D
    clicked_art_mesh_count: int
    art_mesh_hits: list[ArtMeshHit]


@with_request_model_config
class ItemEventConfig(BaseModel):
    item_instance_ids: Annotated[
        list[str] | None,
        Field(alias="item_instance_ids"),
    ] = None
    item_file_names: list[str] | None = None


@with_response_model_config
class ItemEventData(BaseModel):
    item_event_type: str
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    item_file_name: str
    item_position: Point2D


@with_request_model_config
class Live2DCubismEditorConnectedEventConfig(BaseModel):
    pass


@with_response_model_config
class Live2DCubismEditorConnectedEventData(BaseModel):
    trying_to_connect: bool
    connected: bool
    should_send_parameters: bool
