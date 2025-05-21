from typing import ClassVar

from pydantic import BaseModel

from ..registry import request_model, response_model, response_param_model


@response_param_model
class CapturePartColor(BaseModel):
    active: bool
    color_r: int
    color_g: int
    color_b: int


@request_model
class SceneColorOverlayInfoRequest(BaseModel):
    msg_t: ClassVar[str] = "SceneColorOverlayInfoRequest"


@response_model
class SceneColorOverlayInfoResponse(BaseModel):
    msg_t: ClassVar[str] = "SceneColorOverlayInfoResponse"
    active: bool
    items_included: bool
    is_window_capture: bool
    base_brightness: int
    color_boost: int
    smoothing: int
    color_overlay_r: int
    color_overlay_g: int
    color_overlay_b: int
    color_avg_r: int
    color_avg_g: int
    color_avg_b: int
    left_capture_part: CapturePartColor
    middle_capture_part: CapturePartColor
    right_capture_part: CapturePartColor
