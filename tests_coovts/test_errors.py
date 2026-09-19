"""Tests for the exception surface in `coovts.errors`."""

from coovts.errors import (
    APIError,
    AuthenticationFailedError,
    NetworkError,
    RequestError,
    RequestTimeout,
    ValidationError,
    VTSError,
)
from coovts.types.api import APIErrorResponse, AuthenticationResponse


def test_every_error_type_is_a_vts_error() -> None:
    """Every exception the package raises derives from `VTSError`."""
    error_types = [
        VTSError,
        RequestError,
        APIError,
        NetworkError,
        RequestTimeout,
        ValidationError,
        AuthenticationFailedError,
    ]

    for error_type in error_types:
        assert issubclass(error_type, VTSError)


def test_request_timeout_is_also_a_builtin_timeout() -> None:
    """`RequestTimeout` is catchable as both a `RequestError` and a builtin `TimeoutError`."""
    assert issubclass(RequestTimeout, RequestError)
    assert issubclass(RequestTimeout, TimeoutError)


def test_api_error_str_carries_the_id_and_the_message() -> None:
    """`APIError` renders the error ID and the message VTS answered with."""
    error = APIError(APIErrorResponse(error_id=7, message="Unknown messageType: Foo"))

    assert str(error) == "[7] Unknown messageType: Foo"


def test_authentication_failed_error_str_is_the_reason_vts_gave() -> None:
    """`AuthenticationFailedError` renders exactly the reason from the response."""
    error = AuthenticationFailedError(
        AuthenticationResponse(authenticated=False, reason="Plugin was denied."),
    )

    assert str(error) == "Plugin was denied."


def test_validation_error_carries_the_raw_data_and_the_model() -> None:
    """`ValidationError` keeps the payload it could not validate and the model it tried."""
    error = ValidationError(b"not a frame", APIErrorResponse)

    assert error.raw == b"not a frame"
    assert error.model is APIErrorResponse


def test_network_error_is_a_vts_error_and_a_request_error() -> None:
    """A dropped connection is a `VTSError` on the request-error branch of the hierarchy."""
    assert issubclass(NetworkError, VTSError)
    assert issubclass(NetworkError, RequestError)
