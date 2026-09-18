from .utils.frames import real_error_frame, real_error_payload


async def test_start_allocates_distinct_requests() -> None:
    """Two started requests get distinct ids and are taken back by their id."""
    from coovts.request import RequestManager

    manager = RequestManager()

    first = manager.start()
    second = manager.start()

    assert first.req_id != second.req_id
    assert manager.take(first.req_id) is first
    assert manager.take(second.req_id) is second
    assert manager.pending == {}


async def test_start_skips_in_flight_id_on_wrap() -> None:
    """A wrapping counter never reuses the id of a request still pending."""
    from coovts.request import RequestManager

    manager = RequestManager(id_counter_max=1)

    first = manager.start()
    second = manager.start()

    assert first.req_id != second.req_id


async def test_take_returns_none_for_unknown_id() -> None:
    """Taking an id that was never started yields `None`."""
    from coovts.request import RequestManager

    manager = RequestManager()

    assert manager.take("42") is None


async def test_discard_forgets_request_without_touching_future() -> None:
    """Discarding drops the request but leaves its future unresolved."""
    from coovts.request import RequestManager

    manager = RequestManager()
    pending = manager.start()

    manager.discard(pending.req_id)

    assert pending.req_id not in manager.pending
    assert not pending.future.done()


async def test_reset_cancels_pending_futures() -> None:
    """A bare reset cancels every waiting future and restarts the id counter."""
    from coovts.request import RequestManager

    manager = RequestManager()
    first = manager.start()
    second = manager.start()

    manager.reset()

    assert manager.pending == {}
    assert first.future.cancelled()
    assert second.future.cancelled()
    assert manager.start().req_id == "1"


async def test_reset_with_message_fails_pending_futures() -> None:
    """A reset with a message fails every waiting future with a `NetworkError`."""
    from coovts.errors import NetworkError
    from coovts.request import RequestManager

    manager = RequestManager()
    pending = manager.start()

    manager.reset("connection closed")

    assert manager.pending == {}
    error = pending.future.exception()
    assert isinstance(error, NetworkError)
    assert str(error) == "connection closed"


async def test_reset_skips_request_whose_future_already_settled() -> None:
    """A reset leaves an already resolved future alone instead of failing it again."""
    from coovts.request import RequestManager
    from coovts.types.api import ModelLoadResponse

    manager = RequestManager()
    pending = manager.start(ModelLoadResponse)
    response = ModelLoadResponse.model_validate({"modelID": "m1"}, by_alias=True)
    pending.future.set_result(response)

    manager.reset("connection closed")

    assert manager.pending == {}
    assert pending.future.result() is response
    assert pending.future.exception() is None


async def test_resolve_sets_validated_model_on_future() -> None:
    """A successful payload resolves the future to the validated model instance."""
    from coovts.request import PendingRequest
    from coovts.types.api import ModelLoadResponse

    pending = PendingRequest("1", ModelLoadResponse)

    pending.resolve('{"modelID": "m1"}', {"modelID": "m1"}, is_error=False)

    result = pending.future.result()
    assert isinstance(result, ModelLoadResponse)
    assert result.model_id == "m1"


async def test_resolve_fails_future_on_payload_that_cannot_validate() -> None:
    """An undecodable payload fails the future with the library `ValidationError`."""
    from pydantic import ValidationError as PydanticValidationError

    from coovts.errors import ValidationError
    from coovts.request import PendingRequest
    from coovts.types.api import ModelLoadResponse

    pending = PendingRequest("1", ModelLoadResponse)
    raw = '{"modelID": 123}'

    pending.resolve(raw, {"modelID": 123}, is_error=False)

    error = pending.future.exception()
    assert isinstance(error, ValidationError)
    assert error.raw == raw
    assert error.model is ModelLoadResponse
    assert isinstance(error.__cause__, PydanticValidationError)
    assert "ModelLoadResponse" in str(error)


async def test_resolve_error_payload_fails_future_with_api_error() -> None:
    """An error frame VTS really sent fails the future with an `APIError` holding its id."""
    from coovts.errors import APIError
    from coovts.request import PendingRequest
    from coovts.types.api import ModelLoadResponse

    pending = PendingRequest("1", ModelLoadResponse)
    raw = real_error_frame(50)

    pending.resolve(raw, real_error_payload(50), is_error=True)

    error = pending.future.exception()
    assert isinstance(error, APIError)
    assert error.data.error_id == 50
    assert error.data.message == "User denied authentication request for your plugin."
    assert "50" in str(error)
    assert "denied" in str(error)
