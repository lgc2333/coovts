"""Builders for the VTube Studio frames a test feeds to, or reads from, the fake."""

import json
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .plugin_fake import FakeConnection


class SentFrame(TypedDict):
    """The envelope fields a test inspects on an outbound frame."""

    requestID: str | None
    messageType: str
    data: dict[str, object]


def envelope(
    message_type: str,
    data: object,
    request_id: str | None = None,
) -> str:
    """Build one VTube Studio frame for the fake connection to deliver."""
    return json.dumps(
        {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "timestamp": 1,
            "requestID": request_id,
            "messageType": message_type,
            "data": data,
        },
    )


def sent_frame(connection: "FakeConnection", index: int) -> SentFrame:
    """Decode the frame the plugin sent at `index`."""
    return json.loads(connection.sent[index])


REAL_FRAMES_PATH = Path(__file__).with_name("real_frames.json")


@cache
def _captured_frames() -> tuple[dict[str, str], ...]:
    """Frames a real VTube Studio sent, verbatim; see the note inside the file."""
    return tuple(json.loads(REAL_FRAMES_PATH.read_text(encoding="u8"))["frames"])


def real_frame(message_type: str) -> str:
    """One frame a real VTube Studio sent, byte for byte."""
    for frame in _captured_frames():
        if frame["messageType"] == message_type:
            return frame["raw"]
    raise KeyError(message_type)


def real_payload(message_type: str) -> dict[str, object]:
    """The `data` object of that captured frame."""
    return json.loads(real_frame(message_type))["data"]


def real_error_frame(error_id: int) -> str:
    """The `APIError` frame a real VTube Studio sent for `error_id`."""
    for frame in _captured_frames():
        data = json.loads(frame["raw"])["data"]
        if isinstance(data, dict) and data.get("errorID") == error_id:
            return frame["raw"]
    raise KeyError(error_id)


def real_error_payload(error_id: int) -> dict[str, object]:
    """The `data` object of that captured error frame."""
    return json.loads(real_error_frame(error_id))["data"]
