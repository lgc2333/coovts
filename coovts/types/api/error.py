from typing import Annotated

from pydantic import BaseModel, Field

from ..shared import with_response_model_config


@with_response_model_config
class APIErrorResponse(BaseModel):
    error_id: Annotated[int, Field(alias="errorID")]
    message: str
