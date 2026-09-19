from typing import Annotated

from pydantic import Field

from ..api.art_mesh import ArtMeshHit, ArtMeshHitInfo, Point2D
from ..api.model import ModelPosition
from ..shared import VTSBaseModel


class TestEventConfig(VTSBaseModel):
    # Not a pytest test class: `Test` is part of VTS's test event name.
    __test__ = False

    test_message_for_event: str = ""
    """The string VTS echoes back; empty when omitted, as upstream's optional field allows."""


class TestEventData(VTSBaseModel):
    __test__ = False

    your_test_message: str
    counter: int


class ModelLoadedEventConfig(VTSBaseModel):
    model_id: Annotated[list[str] | None, Field(alias="modelID")] = None


class ModelLoadedEventData(VTSBaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]


class TrackingStatusChangedEventConfig(VTSBaseModel):
    pass


class TrackingStatusChangedEventData(VTSBaseModel):
    face_found: bool
    left_hand_found: bool
    right_hand_found: bool


class HotkeyTriggeredEventConfig(VTSBaseModel):
    only_for_action: str | None = None
    ignore_hotkeys_triggered_by_api: Annotated[
        bool,
        Field(alias="ignoreHotkeysTriggeredByAPI"),
    ] = False


class HotkeyTriggeredEventData(VTSBaseModel):
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
    hotkey_name: str
    hotkey_action: str
    hotkey_file: str
    hotkey_triggered_by_api: Annotated[bool, Field(alias="hotkeyTriggeredByAPI")]
    model_id: Annotated[str, Field(alias="modelID")]
    model_name: str
    is_live2d_item: bool


class ModelMovedEventConfig(VTSBaseModel):
    pass


class ModelMovedEventData(VTSBaseModel):
    model_id: Annotated[str, Field(alias="modelID")]
    model_name: str
    model_position: ModelPosition


class ModelOutlineEventConfig(VTSBaseModel):
    draw: bool = False


class ModelOutlineEventData(VTSBaseModel):
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    convex_hull: list[Point2D]
    convex_hull_center: Point2D
    window_size: Point2D


class ModelClickedEventConfig(VTSBaseModel):
    only_clicks_on_model: bool = True


class ModelClickedEventData(VTSBaseModel):
    model_loaded: bool
    loaded_model_id: Annotated[str, Field(alias="loadedModelID")]
    loaded_model_name: str
    model_was_clicked: bool
    mouse_button_id: Annotated[int, Field(alias="mouseButtonID")]
    click_position: Point2D
    window_size: Point2D
    clicked_art_mesh_count: int
    art_mesh_hits: list[ArtMeshHit]


class ItemEventConfig(VTSBaseModel):
    item_instance_ids: Annotated[
        list[str] | None,
        Field(alias="itemInstanceIDs"),
    ] = None
    item_file_names: list[str] | None = None


class ItemEventData(VTSBaseModel):
    item_event_type: str
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    item_file_name: str
    item_position: Point2D


class Live2DCubismEditorConnectedEventConfig(VTSBaseModel):
    pass


class Live2DCubismEditorConnectedEventData(VTSBaseModel):
    trying_to_connect: bool
    connected: bool
    should_send_parameters: bool


class ModelAnimationEventConfig(VTSBaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#animation-event-triggered"""

    ignore_live2d_items: bool = False
    ignore_idle_animations: bool = False


class ModelAnimationEventData(VTSBaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#animation-event-triggered"""

    animation_event_type: str
    animation_event_time: float
    animation_event_data: str
    animation_name: str
    animation_length: float
    is_idle_animation: bool
    model_id: Annotated[str | None, Field(alias="modelID")] = None
    model_name: str
    is_live2d_item: bool


class BackgroundChangedEventConfig(VTSBaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#background-changed"""


class BackgroundChangedEventData(VTSBaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#background-changed"""

    background_name: str
    """Name as shown in the background list, typically the file name without its extension."""


class ModelConfigChangedEventConfig(VTSBaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#model-config-modified"""


class ModelConfigChangedEventData(VTSBaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#model-config-modified"""

    model_id: Annotated[str, Field(alias="modelID")]
    model_name: str
    hotkey_config_changed: bool
    """`True` when the changed setting is related to hotkeys."""


class PostProcessingEventConfig(VTSBaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#post-processing-event"""


class PostProcessingEventData(VTSBaseModel):
    """https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#post-processing-event"""

    current_on_state: bool
    current_preset: str


class ExpressionToggledEventConfig(VTSBaseModel):
    """Only available on the public beta branch of VTube Studio.

    https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#expression-activateddeactivated-event
    """

    send_all_active_states_on_subscription: bool = False
    ignore_live2d_items: bool = False


class ExpressionToggledEventData(VTSBaseModel):
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


class ArtMeshTrackingPointConfig(VTSBaseModel):
    """One point to track in an `ArtMeshTrackingEventConfig` payload."""

    tracking_point_id: Annotated[str, Field(alias="trackingPointID")]
    """Id assigned by the plugin, echoed back by the event."""
    art_mesh_coords: ArtMeshHitInfo
    """Barycentric coordinates, same shape the `ModelClickedEvent` returns."""
    visualize: bool
    """Draws a debug circle at the tracked position in VTube Studio."""


class ArtMeshTrackingPoint(VTSBaseModel):
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


class ArtMeshTrackingEventConfig(VTSBaseModel):
    """Only available on the public beta branch of VTube Studio.

    https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#track-custom-point-on-artmesh-event
    """

    frequency: int
    """Events per second, `1` to `60`."""
    tracking_points: list[ArtMeshTrackingPointConfig]


class ArtMeshTrackingEventData(VTSBaseModel):
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


class ArtMeshRef(VTSBaseModel):
    """One ArtMesh to track in an `ArtMeshOutlineEventConfig` payload."""

    model_id: Annotated[str, Field(alias="modelID")]
    art_mesh_id: Annotated[str, Field(alias="artMeshID")]


class ArtMeshOutlineRing(VTSBaseModel):
    """One boundary ring of an ArtMesh outline."""

    points: list[float]
    """Flat 40 floats: 20 interleaved x/y pairs exactly as the wire sends them, so this
    stays a list of floats instead of 20 `Point2D`s."""


class ArtMeshOutline(VTSBaseModel):
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


class ArtMeshOutlineEventConfig(VTSBaseModel):
    """Only available on the public beta branch of VTube Studio.

    https://github.com/DenchiSoft/VTubeStudio/blob/master/Events/README.md#track-artmesh-outline-event
    """

    frequency: int
    """Events per second, `1` to `30`."""
    art_meshes: list[ArtMeshRef]


class ArtMeshOutlineEventData(VTSBaseModel):
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
