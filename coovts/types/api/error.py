from typing import Annotated

from pydantic import Field

from ..shared import VTSBaseModel


class APIErrorResponse(VTSBaseModel):
    error_id: Annotated[int, Field(alias="errorID")]
    message: str
