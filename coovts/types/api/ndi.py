from typing import Annotated, ClassVar

from pydantic import BaseModel, Field

from ..registry import request_model, response_model


@request_model
class NDIConfigRequest(BaseModel):
    msg_t: ClassVar[str] = "NDIConfigRequest"
    set_new_config: bool
    ndi_active: bool = True
    use_ndi5: bool = True
    use_custom_resolution: bool = True
    custom_width_ndi: Annotated[int, Field(alias="customWidthNDI")] = -1
    custom_height_ndi: Annotated[int, Field(alias="customHeightNDI")] = -1


@response_model
class NDIConfigResponse(BaseModel):
    msg_t: ClassVar[str] = "NDIConfigResponse"
    set_new_config: bool
    ndi_active: bool
    use_ndi5: bool
    use_custom_resolution: bool
    custom_width_ndi: Annotated[int, Field(alias="customWidthNDI")]
    custom_height_ndi: Annotated[int, Field(alias="customHeightNDI")]
