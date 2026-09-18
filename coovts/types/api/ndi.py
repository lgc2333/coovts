from typing import Annotated

from pydantic import Field

from ..shared import VTSBaseModel


class NDIConfigRequest(VTSBaseModel):
    set_new_config: bool
    ndi_active: bool = True
    use_ndi5: Annotated[bool, Field(alias="useNDI5")] = True
    use_custom_resolution: bool = True
    custom_width_ndi: Annotated[int, Field(alias="customWidthNDI")] = -1
    custom_height_ndi: Annotated[int, Field(alias="customHeightNDI")] = -1


class NDIConfigResponse(VTSBaseModel):
    set_new_config: bool
    ndi_active: bool
    use_ndi5: Annotated[bool, Field(alias="useNDI5")]
    use_custom_resolution: bool
    custom_width_ndi: Annotated[int, Field(alias="customWidthNDI")]
    custom_height_ndi: Annotated[int, Field(alias="customHeightNDI")]
