from asyncio import Future, wait_for
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


@dataclass
class ResponseInfo[M: BaseModel]:
    model: type[M]
    future: Future[M] = field(default_factory=Future)


class RequestManager:
    def __init__(self, id_counter_max: int = 2147483647) -> None:
        self.id_counter_max = id_counter_max

        self.id_counter = 0
        self.id_signals: dict[str, ResponseInfo] = {}

    def has_id(self, req_id: str) -> bool:
        return req_id in self.id_signals

    def acquire_request(self, req_id: str, model: type[BaseModel]):
        if self.id_counter in self.id_signals:
            raise RuntimeError("ID already in use")
        self.id_signals[req_id] = ResponseInfo(model=model)

    def acquire_next_request(self, model: type[BaseModel]) -> str:
        if self.id_counter >= self.id_counter_max:
            self.id_counter = 0
        self.id_counter += 1
        id_str = str(self.id_counter)
        self.acquire_request(id_str, model)
        return id_str

    async def wait_response(
        self,
        req_id: str,
        timeout: float | None = 30,  # noqa: ASYNC109
        pop: bool = True,
    ) -> Any:
        if timeout == 0:
            timeout = None
        try:
            return await wait_for(self.id_signals[req_id].future, timeout)
        finally:
            if pop and self.has_id(req_id):
                self.pop(req_id)

    def pop(self, req_id: str) -> ResponseInfo:
        return self.id_signals.pop(req_id)

    def reset(self) -> None:
        self.id_counter = 0
        signals = self.id_signals.copy()
        self.id_signals.clear()
        for signal in signals.values():
            signal.future.cancel()
