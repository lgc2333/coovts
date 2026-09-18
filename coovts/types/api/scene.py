from ..shared import VTSBaseModel


class CapturePartColor(VTSBaseModel):
    active: bool
    color_r: int
    color_g: int
    color_b: int


class SceneColorOverlayInfoRequest(VTSBaseModel):
    pass


class SceneColorOverlayInfoResponse(VTSBaseModel):
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
