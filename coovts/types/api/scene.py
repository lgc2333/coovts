from typing import Annotated, ClassVar

from pydantic import BaseModel, Field

from ..registry import request_model, response_model


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
    color_overlay_r: Annotated[int, Field(alias="colorOverlayR")]
    color_overlay_g: Annotated[int, Field(alias="colorOverlayG")]
    color_overlay_b: Annotated[int, Field(alias="colorOverlayB")]
    color_avg_r: Annotated[int, Field(alias="colorAvgR")]
    color_avg_g: Annotated[int, Field(alias="colorAvgG")]
    color_avg_b: Annotated[int, Field(alias="colorAvgB")]
    left_capture_part: CapturePartColor
    middle_capture_part: CapturePartColor
    right_capture_part: CapturePartColor
