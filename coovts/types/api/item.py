from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, Field

from ..registry import (
    request_model,
    request_param_model,
    response_model,
    response_param_model,
)

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


@request_param_model
class ItemPinInfo(BaseModel):
    model_id: Annotated[str, Field(alias="modelID")] = ""
    art_mesh_id: Annotated[str, Field(alias="artMeshID")] = ""
    angle: float
    size: float
    vertex_id1: int = 0
    vertex_id2: int = 0
    vertex_id3: int = 0
    vertex_weight1: float = 0
    vertex_weight2: float = 0
    vertex_weight3: float = 0


@response_param_model
class ItemInstanceInfo(BaseModel):
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


@response_param_model
class ItemFileInfo(BaseModel):
    file_name: str
    type: str
    loaded_count: int


@response_param_model
class UnloadedItem(BaseModel):
    instance_id: Annotated[str, Field(alias="instanceID")]
    file_name: str


@response_param_model
class ItemMoveResult(BaseModel):
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    success: bool
    error_id: Annotated[int, Field(alias="errorID")]


@request_model
class ItemListRequest(BaseModel):
    msg_t: ClassVar[str] = "ItemListRequest"
    include_available_spots: bool = False
    include_item_instances_in_scene: bool = False
    include_available_item_files: bool = False
    only_items_with_file_name: str | None = None
    only_items_with_instance_id: str | None = None


@response_model
class ItemListResponse(BaseModel):
    msg_t: ClassVar[str] = "ItemListResponse"
    items_in_scene_count: int
    total_items_allowed_count: int
    can_load_items_right_now: bool
    available_spots: list[int] = []
    item_instances_in_scene: list[ItemInstanceInfo] = []
    available_item_files: list[ItemFileInfo] = []


@request_model
class ItemLoadRequest(BaseModel):
    msg_t: ClassVar[str] = "ItemLoadRequest"
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


@response_model
class ItemLoadResponse(BaseModel):
    msg_t: ClassVar[str] = "ItemLoadResponse"
    instance_id: Annotated[str, Field(alias="instanceID")]
    file_name: str

    class Response(BaseModel):
        msg_t: ClassVar[str] = "ItemLoadResponse"
        instance_id: Annotated[str, Field(alias="instanceID")]
        file_name: str


@request_model
class ItemUnloadRequest(BaseModel):
    msg_t: ClassVar[str] = "ItemUnloadRequest"
    unload_all_in_scene: bool = False
    unload_all_loaded_by_this_plugin: bool = False
    allow_unloading_items_loaded_by_user_or_other_plugins: bool = True
    instance_ids: Annotated[list[str], Field(alias="instanceIDs")] = []
    file_names: list[str] = []


@response_model
class ItemUnloadResponse(BaseModel):
    msg_t: ClassVar[str] = "ItemUnloadResponse"
    unloaded_items: list[UnloadedItem]


@request_model
class ItemAnimationControlRequest(BaseModel):
    msg_t: ClassVar[str] = "ItemAnimationControlRequest"
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    framerate: float = -1
    frame: int = -1
    brightness: float = -1
    opacity: float = -1
    set_auto_stop_frames: bool = False
    auto_stop_frames: list[int] = []
    set_animation_play_state: bool = False
    animation_play_state: bool = True


@response_model
class ItemAnimationControlResponse(BaseModel):
    msg_t: ClassVar[str] = "ItemAnimationControlResponse"
    frame: int
    animation_playing: bool


class ItemMoveInfo(BaseModel):
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


@request_model
class ItemMoveRequest(BaseModel):
    msg_t: ClassVar[str] = "ItemMoveRequest"
    items_to_move: list[ItemMoveInfo]


@response_model
class ItemMoveResponse(BaseModel):
    msg_t: ClassVar[str] = "ItemMoveResponse"
    moved_items: list[ItemMoveResult]


@request_model
class ItemPinRequest(BaseModel):
    msg_t: ClassVar[str] = "ItemPinRequest"
    pin: bool
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    angle_relative_to: AngleRelativeTo = "RelativeToWorld"
    size_relative_to: SizeRelativeTo = "RelativeToWorld"
    vertex_pin_type: VertexPinType = "Center"
    pin_info: ItemPinInfo


@response_model
class ItemPinResponse(BaseModel):
    msg_t: ClassVar[str] = "ItemPinResponse"
    is_pinned: bool
    item_instance_id: Annotated[str, Field(alias="itemInstanceID")]
    item_file_name: str
