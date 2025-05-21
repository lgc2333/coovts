from pydantic import BaseModel

from ..shared import with_request_model_config, with_response_model_config


@with_request_model_config
class ConfigValue(BaseModel):
    config_id: str
    config_value: str


@with_response_model_config
class EffectConfigEntry(BaseModel):
    internal_id: str
    enum_id: str
    explanation: str
    type: str
    activation_config: bool
    float_value: float
    float_min: float
    float_max: float
    float_default: float
    int_value: int
    int_min: int
    int_max: int
    int_default: int
    color_value: str
    color_default: str
    color_has_alpha: bool
    bool_value: bool
    bool_default: bool
    string_value: str
    string_default: str
    scene_item_value: str
    scene_item_default: str


@with_response_model_config
class PostProcessingEffect(BaseModel):
    internal_id: str
    enum_id: str
    explanation: str
    effect_is_active: bool
    effect_is_restricted: bool
    config_entries: list[EffectConfigEntry]


@with_request_model_config
class PostProcessingListRequest(BaseModel):
    fill_post_processing_presets_array: bool = True
    fill_post_processing_effects_array: bool = True
    effect_id_filter: list[str] = []


@with_response_model_config
class PostProcessingListResponse(BaseModel):
    post_processing_supported: bool
    post_processing_active: bool
    can_send_post_processing_update_request_right_now: bool
    restricted_effects_allowed: bool
    preset_is_active: bool
    active_preset: str
    preset_count: int
    active_effect_count: int
    effect_count_before_filter: int
    config_count_before_filter: int
    effect_count_after_filter: int
    config_count_after_filter: int
    post_processing_effects: list[PostProcessingEffect] = []
    post_processing_presets: list[str] = []


@with_request_model_config
class PostProcessingUpdateRequest(BaseModel):
    post_processing_on: bool
    set_post_processing_preset: bool = False
    set_post_processing_values: bool = False
    preset_to_set: str = ""
    post_processing_fade_time: float = 0.0
    set_all_other_values_to_default: bool = True
    using_restricted_effects: bool = False
    randomize_all: bool = False
    randomize_all_chaos_level: float = 0.0
    post_processing_values: list[ConfigValue] = []


@with_response_model_config
class PostProcessingUpdateResponse(BaseModel):
    post_processing_active: bool
    preset_is_active: bool
    active_preset: str
    active_effect_count: int
