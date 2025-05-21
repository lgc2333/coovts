from typing import Annotated, ClassVar

from pydantic import BaseModel, Field

from ..registry import response_model


@response_model
class APIErrorResponse(BaseModel):
    msg_t: ClassVar[str] = "APIError"
    error_id: Annotated[int, Field(alias="errorID")]
    message: str
