from typing import Annotated, Literal

from pydantic import Field

from ..shared import VTSBaseModel

type FadeMode = Literal[
    "linear",
    "easeIn",
    "easeOut",
    "easeBoth",
    "overshoot",
    "zip",
]
type AngleRelativeTo = Literal[
    "RelativeToWorld",
    "RelativeToCurrentItemRotation",
    "RelativeToModel",
    "RelativeToPinPosition",
]
type SizeRelativeTo = Literal["RelativeToWorld", "RelativeToCurrentItemSize"]
type VertexPinType = Literal["Provided", "Center", "Random"]
type ItemSortSplitPoint = Literal["Unchanged", "UseArtMeshID"]
type ItemSortFrontOrder = Literal["Unchanged", "UseArtMeshID", "UseSpecialID"]
type ItemSortBackOrder = Literal["Unchanged", "UseArtMeshID", "UseSpecialID"]


class ItemPinInfo(VTSBaseModel):
    model_id: Annotated[str, Field(alias="modelID")] = ""
    art_mesh_id: Annotated[str, Field(alias="artMeshID")] = ""
    angle: float
    size: float
    vertex_id1: Annotated[int, Field(alias="vertexID1")] = 0
    vertex_id2: Annotated[int, Field(alias="vertexID2")] = 0
    vertex_id3: Annotated[int, Field(alias="vertexID3")] = 0
    vertex_weight1: float = 0
    vertex_weight2: float = 0
    vertex_weight3: float = 0


class ItemInstanceInfo(VTSBaseModel):
    file_name: str
    instance_id: Annotated[str, Field(alias="instanceID")]
    order: int
    type: str
    censored: bool
    flipped: bool
    locked: bool
    smoothing: float
    framerate: float
    frame_count: int
    current_frame: int
    pinned_to_model: bool
    pinned_model_id: Annotated[str, Field(alias="pinnedModelID")]
    pinned_art_mesh_id: Annotated[str, Field(alias="pinnedArtMeshID")]
    group_name: str
    scene_name: str
    from_workshop: bool


class ItemFileInfo(VTSBaseModel):
    file_name: str
    type: str
    loaded_count: int


class UnloadedItem(VTSBaseModel):
    instance_id: Annotated[str, Field(alias="instanceID")]
    file_name: str


class ItemMoveResult(VTSBaseModel):
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    success: bool
    error_id: Annotated[int, Field(alias="errorID")]


class ItemListRequest(VTSBaseModel):
    include_available_spots: bool = False
    include_item_instances_in_scene: bool = False
    include_available_item_files: bool = False
    only_items_with_file_name: str | None = None
    only_items_with_instance_id: Annotated[
        str | None,
        Field(alias="onlyItemsWithInstanceID"),
    ] = None


class ItemListResponse(VTSBaseModel):
    items_in_scene_count: int
    total_items_allowed_count: int
    can_load_items_right_now: bool
    available_spots: list[int] = []
    item_instances_in_scene: list[ItemInstanceInfo] = []
    available_item_files: list[ItemFileInfo] = []


class ItemLoadRequest(VTSBaseModel):
    file_name: str
    position_x: float
    position_y: float
    size: float
    rotation: float
    fade_time: float = 0.5
    order: int
    fail_if_order_taken: bool = False
    smoothing: float = 0
    censored: bool = False
    flipped: bool = False
    locked: bool = False
    unload_when_plugin_disconnects: bool = True
    custom_data_base64: str = ""
    custom_data_ask_user_first: bool = True
    custom_data_skip_asking_user_if_whitelisted: bool = True
    custom_data_ask_timer: float = -1


class ItemLoadResponse(VTSBaseModel):
    instance_id: Annotated[str, Field(alias="instanceID")]
    file_name: str


class ItemUnloadRequest(VTSBaseModel):
    unload_all_in_scene: bool = False
    unload_all_loaded_by_this_plugin: bool = False
    allow_unloading_items_loaded_by_user_or_other_plugins: bool = True
    instance_ids: Annotated[list[str], Field(alias="instanceIDs")] = []
    file_names: list[str] = []


class ItemUnloadResponse(VTSBaseModel):
    unloaded_items: list[UnloadedItem]


class ItemAnimationControlRequest(VTSBaseModel):
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    framerate: float = -1
    frame: int = -1
    brightness: float = -1
    opacity: float = -1
    set_auto_stop_frames: bool = False
    auto_stop_frames: list[int] = []
    set_animation_play_state: bool = False
    animation_play_state: bool = True


class ItemAnimationControlResponse(VTSBaseModel):
    frame: int
    animation_playing: bool


class ItemMoveInfo(VTSBaseModel):
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    time_in_seconds: float
    fade_mode: FadeMode = "linear"
    position_x: float = -1000
    position_y: float = -1000
    size: float = -1000
    rotation: float = -1000
    order: int = -1000
    set_flip: bool = False
    flip: bool = False
    user_can_stop: bool = True


class ItemMoveRequest(VTSBaseModel):
    items_to_move: list[ItemMoveInfo]


class ItemMoveResponse(VTSBaseModel):
    moved_items: list[ItemMoveResult]


class ItemPinRequest(VTSBaseModel):
    pin: bool
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    angle_relative_to: AngleRelativeTo = "RelativeToWorld"
    size_relative_to: SizeRelativeTo = "RelativeToWorld"
    vertex_pin_type: VertexPinType = "Center"
    pin_info: ItemPinInfo | None = None
    """The pin position, needed only to pin an item; an unpin (`pin=False`) carries none."""


class ItemPinResponse(VTSBaseModel):
    is_pinned: bool
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    item_file_name: str


class ItemSortRequest(VTSBaseModel):
    """Sort and pin an item between the layers of the main model.

    The three mode fields decide how `split_at`, `within_model_order_front` and
    `within_model_order_back` are read: `Unchanged` leaves the matching position alone, so its
    value field is ignored.
    """

    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    front_on: bool = False
    back_on: bool = False
    set_split_point: ItemSortSplitPoint
    set_front_order: ItemSortFrontOrder
    set_back_order: ItemSortBackOrder
    split_at: str | None = None
    within_model_order_front: str | None = None
    within_model_order_back: str | None = None


class ItemSortResponse(VTSBaseModel):
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    model_loaded: bool
    model_id: Annotated[str, Field(alias="modelID")]
    model_name: str
    loaded_model_had_requested_front_layer: bool
    loaded_model_had_requested_back_layer: bool
