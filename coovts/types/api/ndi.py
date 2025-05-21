from typing import Annotated

from pydantic import BaseModel, Field

from ..shared import with_request_model_config, with_response_model_config


@with_request_model_config
class NDIConfigRequest(BaseModel):
    set_new_config: bool
    ndi_active: bool = True
    use_ndi5: bool = True
    use_custom_resolution: bool = True
    custom_width_ndi: Annotated[int, Field(alias="customWidthNDI")] = -1
    custom_height_ndi: Annotated[int, Field(alias="customHeightNDI")] = -1


@with_response_model_config
class NDIConfigResponse(BaseModel):
    set_new_config: bool
    ndi_active: bool
    use_ndi5: bool
    use_custom_resolution: bool
    custom_width_ndi: Annotated[int, Field(alias="customWidthNDI")]
    custom_height_ndi: Annotated[int, Field(alias="customHeightNDI")]
