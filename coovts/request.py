from asyncio import Future, wait_for
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel

from .errors import APIError, NetworkError, RequestTimeout, ValidationError
from .types.api import APIErrorResponse


@dataclass
class PendingRequest[M: BaseModel]:
    req_id: str
    model: type[M] | None = None
    future: Future[M] = field(default_factory=Future)

    def resolve(self, raw: str | bytes, data: Any, *, is_error: bool) -> None:
        model: type[BaseModel] | None = APIErrorResponse if is_error else self.model
        try:
            result = (
                data if model is None else model.model_validate(data, by_alias=True)
            )
        except Exception as e:
            err = ValidationError(raw, model)
            err.__cause__ = e
            self.future.set_exception(err)
            return

        if is_error:
            if TYPE_CHECKING:
                assert isinstance(result, APIErrorResponse)
            self.future.set_exception(APIError(result))
        else:
            self.future.set_result(cast("M", result))

    async def result(self, timeout: float | None = None) -> M:  # noqa: ASYNC109
        if timeout == 0:
            timeout = None
        try:
            return await wait_for(self.future, timeout)
        except TimeoutError as e:
            raise RequestTimeout(f"Request timed out after {timeout} seconds") from e


class RequestManager:
    def __init__(self, id_counter_max: int = 2147483647) -> None:
        self.id_counter_max = id_counter_max

        self.id_counter = 0
        self.pending: dict[str, PendingRequest] = {}

    def _next_id(self) -> str:
        if self.id_counter >= self.id_counter_max:
            self.id_counter = 0
        self.id_counter += 1
        while (req_id := str(self.id_counter)) in self.pending:
            self.id_counter += 1
        return req_id

    def start[M: BaseModel](self, model: type[M] | None = None) -> PendingRequest[M]:
        """Register a request that is waiting for its response."""
        pending = PendingRequest(self._next_id(), model)
        self.pending[pending.req_id] = pending
        return pending

    def take(self, req_id: str) -> PendingRequest | None:
        """Remove and return the request registered under `req_id`, if any."""
        return self.pending.pop(req_id, None)

    def discard(self, req_id: str) -> None:
        """Forget a request nobody is waiting for anymore."""
        self.pending.pop(req_id, None)

    def reset(self, pending_error: str | None = None) -> None:
        """Forget every pending request, failing the ones still waiting if asked to."""
        self.id_counter = 0
        pending = self.pending.copy()
        self.pending.clear()
        for request in pending.values():
            if request.future.done():
                continue
            if pending_error is None:
                request.future.cancel()
            else:
                request.future.set_exception(NetworkError(pending_error))
