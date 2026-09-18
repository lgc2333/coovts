from typing import Annotated, Any

from pydantic import BaseModel, Field, field_serializer

from ..api.art_mesh import ArtMeshHit, ArtMeshHitInfo, Point2D
from ..api.model import ModelPosition
from ..shared import with_request_model_config, with_response_model_config


@with_request_model_config
class TestEventConfig(BaseModel):
    __test__ = False
    """Not a pytest test class: `Test` is part of VTS's test event name."""

    test_message_for_event: str


@with_response_model_config
class TestEventData(BaseModel):
    __test__ = False
    """Not a pytest test class: `Test` is part of VTS's test event name."""

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
    ignore_hotkeys_triggered_by_api: Annotated[
        bool,
        Field(alias="ignoreHotkeysTriggeredByAPI"),
    ] = False


@with_response_model_config
class HotkeyTriggeredEventData(BaseModel):
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
    hotkey_name: str
    hotkey_action: str
    hotkey_file: str
    hotkey_triggered_by_api: Annotated[bool, Field(alias="hotkeyTriggeredByAPI")]
    model_id: Annotated[str, Field(alias="modelID")]
    model_name: str
    is_live2d_item: bool


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
class ModelOutlineEventData(BaseModel):
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    convex_hull: list[Point2D]
    convex_hull_center: Point2D
    window_size: Point2D


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
        Field(alias="itemInstanceIDs"),
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


@with_request_model_config
class ModelAnimationEventConfig(BaseModel):
    ignore_live2d_items: bool = False
    ignore_idle_animations: bool = False


@with_response_model_config
class ModelAnimationEventData(BaseModel):
    animation_event_type: str
    animation_event_time: float
    animation_event_data: str
    animation_name: str
    animation_length: float
    is_idle_animation: bool
    model_id: Annotated[str | None, Field(alias="modelID")] = None
    model_name: str
    is_live2d_item: bool


@with_request_model_config
class BackgroundChangedEventConfig(BaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#background-changed"""


@with_response_model_config
class BackgroundChangedEventData(BaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#background-changed"""

    background_name: str
    """Name as shown in the background list, typically the file name without its extension."""


@with_request_model_config
class ModelConfigChangedEventConfig(BaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#model-config-modified"""


@with_response_model_config
class ModelConfigChangedEventData(BaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#model-config-modified"""

    model_id: Annotated[str, Field(alias="modelID")]
    model_name: str
    hotkey_config_changed: bool
    """`True` when the changed setting is related to hotkeys."""


@with_request_model_config
class PostProcessingEventConfig(BaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#post-processing-event"""


@with_response_model_config
class PostProcessingEventData(BaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#post-processing-event"""

    current_on_state: bool
    current_preset: str


@with_request_model_config
class ExpressionToggledEventConfig(BaseModel):
    """Only available on the public beta branch of VTube Studio.

    https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#expression-activateddeactivated-event
    """

    send_all_active_states_on_subscription: bool
    ignore_live2d_items: bool


@with_response_model_config
class ExpressionToggledEventData(BaseModel):
    """Only available on the public beta branch of VTube Studio.

    https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#expression-activateddeactivated-event
    """

    model_id: Annotated[str, Field(alias="modelID")]
    model_name: str
    is_live2d_item: bool
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    """Empty string for the main model."""
    just_loaded: bool
    """`True` for the full state snapshot sent right after subscribing or loading a model."""
    expression_file: str
    expression_name: str
    active: bool


@with_request_model_config
class ArtMeshTrackingPointConfig(BaseModel):
    """One point to track in an `ArtMeshTrackingEventConfig` payload."""

    tracking_point_id: Annotated[str, Field(alias="trackingPointID")]
    """Id assigned by the plugin, echoed back by the event."""
    art_mesh_coords: ArtMeshHitInfo
    """Barycentric coordinates, same shape the `ModelClickedEvent` returns."""
    visualize: bool
    """Draws a debug circle at the tracked position in VTube Studio."""

    @field_serializer("art_mesh_coords")
    def serialize_art_mesh_coords(self, value: ArtMeshHitInfo) -> dict[str, Any]:
        """Send the shared `ArtMeshHitInfo` with its wire aliases (`modelID`, `artMeshID`)."""
        return value.model_dump(by_alias=True)


@with_response_model_config
class ArtMeshTrackingPoint(BaseModel):
    """One found point in an `ArtMeshTrackingEventData` payload."""

    tracking_point_id: Annotated[str, Field(alias="trackingPointID")]
    art_mesh_visible: bool
    """`False` when the ArtMesh is faded out; position, rotation and size stay valid."""
    position: Point2D
    """VTS coordinates, `-1` to `1`; outside means the point is off-screen."""
    rotation: float
    """World-space degrees, `0` to `360`."""
    size: float
    """In VTS coordinate units based on the window height."""


@with_request_model_config
class ArtMeshTrackingEventConfig(BaseModel):
    """Only available on the public beta branch of VTube Studio.

    https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#track-custom-point-on-artmesh-event
    """

    frequency: int
    """Events per second, `1` to `60`."""
    tracking_points: list[ArtMeshTrackingPointConfig]


@with_response_model_config
class ArtMeshTrackingEventData(BaseModel):
    """Only available on the public beta branch of VTube Studio.

    https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#track-custom-point-on-artmesh-event
    """

    model_loaded: bool
    model_id: Annotated[str, Field(alias="modelID")]
    """Empty string when no model is loaded."""
    window_size: Point2D
    subscribed_points_count: int
    found_points_count: int
    event_counter: int
    """Starts at `0` on subscribe, gains `1` per event, resets on re-subscribe."""
    tracking_points: list[ArtMeshTrackingPoint]
    """Only the points that were found, the missing ones are omitted."""


@with_request_model_config
class ArtMeshRef(BaseModel):
    """One ArtMesh to track in an `ArtMeshOutlineEventConfig` payload."""

    model_id: Annotated[str, Field(alias="modelID")]
    art_mesh_id: Annotated[str, Field(alias="artMeshID")]


@with_response_model_config
class ArtMeshOutlineRing(BaseModel):
    """One boundary ring of an ArtMesh outline."""

    points: list[float]
    """Flat 40 floats: 20 interleaved x/y pairs exactly as the wire sends them, so this
    stays a list of floats instead of 20 `Point2D`s."""


@with_response_model_config
class ArtMeshOutline(BaseModel):
    """One found ArtMesh in an `ArtMeshOutlineEventData` payload."""

    art_mesh_id: Annotated[str, Field(alias="artMeshID")]
    art_mesh_visible: bool
    """`False` when the ArtMesh is faded out; the outline points stay valid."""
    outline_count: int
    """Number of boundary rings, disconnected mesh islands add rings."""
    outline_area: float
    """Approximate combined ring area in VTS units, `4` is about a whole screen."""
    outline_points: list[ArtMeshOutlineRing]
    """One ring per boundary."""


@with_request_model_config
class ArtMeshOutlineEventConfig(BaseModel):
    """Only available on the public beta branch of VTube Studio.

    https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#track-artmesh-outline-event
    """

    frequency: int
    """Events per second, `1` to `30`."""
    art_meshes: list[ArtMeshRef]


@with_response_model_config
class ArtMeshOutlineEventData(BaseModel):
    """Only available on the public beta branch of VTube Studio.

    https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#track-artmesh-outline-event
    """

    model_loaded: bool
    model_id: Annotated[str, Field(alias="modelID")]
    """Empty string when no model is loaded."""
    window_size: Point2D
    subscribed_art_mesh_count: int
    found_art_mesh_count: int
    event_counter: int
    """Starts at `0` on subscribe, gains `1` per event, resets on re-subscribe."""
    art_mesh_outlines: list[ArtMeshOutline]
    """Only the ArtMeshes that were found, the missing ones are omitted."""
