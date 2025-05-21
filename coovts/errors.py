from typing import TYPE_CHECKING, ClassVar, override

from .types.api import APIErrorResponse, AuthenticationResponse

if TYPE_CHECKING:
    from pydantic import BaseModel


class VTSError(Exception):
    pass


class RequestError(VTSError):
    pass


class APIError(RequestError):
    message_type: ClassVar[str] = "APIError"

    def __init__(self, data: APIErrorResponse) -> None:
        self.data = data

    @override
    def __str__(self) -> str:
        return f"[{self.data.error_id}] {self.data.message}"


class NetworkError(RequestError):
    pass


class ValidationError(RequestError):
    def __init__(
        self,
        raw: str | bytes,
        model: type["BaseModel"] | None = None,
    ) -> None:
        self.raw = raw
        self.model = model

    def __str__(self) -> str:
        return f"Returned data cannot validate to {self.model and self.model.__name__}"


class AuthenticationFailedError(RequestError):
    def __init__(self, data: AuthenticationResponse) -> None:
        self.data = data

    @override
    def __str__(self) -> str:
        return self.data.reason
