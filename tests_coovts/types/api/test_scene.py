"""Wire-shape tests for the scene models of `coovts.types.api`."""

import json

from coovts.types.api import (
    CapturePartColor,
    SceneColorOverlayInfoRequest,
    SceneColorOverlayInfoResponse,
)


def test_documented_response_payload_decodes() -> None:
    """The example response from the reference docs decodes into the expected models."""
    response = SceneColorOverlayInfoResponse.model_validate(
        {
            "active": True,
            "itemsIncluded": True,
            "isWindowCapture": False,
            "baseBrightness": 16,
            "colorBoost": 35,
            "smoothing": 6,
            "colorOverlayR": 206,
            "colorOverlayG": 150,
            "colorOverlayB": 153,
            "colorAvgR": 237,
            "colorAvgG": 157,
            "colorAvgB": 162,
            "leftCapturePart": {
                "active": True,
                "colorR": 243,
                "colorG": 231,
                "colorB": 234,
            },
            "middleCapturePart": {
                "active": True,
                "colorR": 230,
                "colorG": 83,
                "colorB": 89,
            },
            "rightCapturePart": {
                "active": False,
                "colorR": 235,
                "colorG": 95,
                "colorB": 101,
            },
        },
    )

    assert response.color_overlay_r == 206
    assert response.color_avg_g == 157
    assert response.left_capture_part.color_r == 243
    assert response.right_capture_part.active is False


def test_capture_part_dumps_the_wire_shape() -> None:
    """A capture part emits its `colorR`/`colorG`/`colorB` aliases."""
    part = CapturePartColor(active=True, color_r=243, color_g=231, color_b=234)

    assert json.loads(part.model_dump_json()) == {
        "active": True,
        "colorR": 243,
        "colorG": 231,
        "colorB": 234,
    }


def test_response_decodes_and_redumps_nested_capture_parts() -> None:
    """The nested capture parts survive a wire decode and re-emit their aliases."""
    response = SceneColorOverlayInfoResponse.model_validate(
        {
            "active": True,
            "itemsIncluded": True,
            "isWindowCapture": False,
            "baseBrightness": 16,
            "colorBoost": 35,
            "smoothing": 6,
            "colorOverlayR": 206,
            "colorOverlayG": 150,
            "colorOverlayB": 153,
            "colorAvgR": 237,
            "colorAvgG": 157,
            "colorAvgB": 162,
            "leftCapturePart": {
                "active": True,
                "colorR": 243,
                "colorG": 231,
                "colorB": 234,
            },
            "middleCapturePart": {
                "active": True,
                "colorR": 230,
                "colorG": 83,
                "colorB": 89,
            },
            "rightCapturePart": {
                "active": False,
                "colorR": 235,
                "colorG": 95,
                "colorB": 101,
            },
        },
    )

    assert json.loads(response.left_capture_part.model_dump_json()) == {
        "active": True,
        "colorR": 243,
        "colorG": 231,
        "colorB": 234,
    }


def test_bare_request_emits_the_wire_shape() -> None:
    """The scene color overlay read carries an empty payload."""
    assert json.loads(SceneColorOverlayInfoRequest().model_dump_json()) == {}
