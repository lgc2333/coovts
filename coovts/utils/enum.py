# ruff: noqa: ARG004 -- the `_generate_next_value_` hook has to keep the base's parameter names
from enum import StrEnum


class RawStrEnum(StrEnum):
    """A `StrEnum` whose `auto()` values are the member names, not their lowercased form."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name
