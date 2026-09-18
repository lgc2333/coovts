"""`Plugin.prepare_icon`: turning bytes or a file into the platform's icon form."""

import base64
from pathlib import Path

from coovts.plugin import Plugin


def test_prepare_icon_encodes_bytes_and_paths(tmp_path: Path) -> None:
    """An icon passes through as text, and bytes or a file path become base64."""
    raw = b"\x89PNG\r\n"
    encoded = base64.b64encode(raw).decode()

    assert (
        Plugin.prepare_icon("data:image/png;base64,abc") == "data:image/png;base64,abc"
    )
    assert Plugin.prepare_icon(raw) == encoded

    icon_file = tmp_path / "icon.png"
    icon_file.write_bytes(raw)
    assert Plugin.prepare_icon(icon_file) == encoded
