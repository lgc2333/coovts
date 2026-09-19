"""Wire-shape tests for the ndi models of `coovts.types.api`."""

import json

from coovts.types.api import NDIConfigRequest, NDIConfigResponse

DOCUMENTED_NDI_PAYLOAD = {
    "setNewConfig": True,
    "ndiActive": True,
    "useNDI5": True,
    "useCustomResolution": True,
    "customWidthNDI": 1024,
    "customHeightNDI": 512,
}


def test_documented_config_response_decodes() -> None:
    """The example NDI config response decodes into the python field names."""
    response = NDIConfigResponse.model_validate(DOCUMENTED_NDI_PAYLOAD)

    assert response.set_new_config is True
    assert response.ndi_active is True
    assert response.use_ndi5 is True
    assert response.use_custom_resolution is True
    assert response.custom_width_ndi == 1024
    assert response.custom_height_ndi == 512


def test_documented_config_request_dumps_the_wire_shape() -> None:
    """An NDI config request built from python names re-emits the documented keys."""
    request = NDIConfigRequest(
        set_new_config=True,
        ndi_active=True,
        use_ndi5=True,
        use_custom_resolution=True,
        custom_width_ndi=1024,
        custom_height_ndi=512,
    )

    assert json.loads(request.model_dump_json()) == DOCUMENTED_NDI_PAYLOAD


def test_config_request_defaults_are_serialised() -> None:
    """A read-only NDI request still carries the full documented default payload."""
    assert json.loads(NDIConfigRequest(set_new_config=False).model_dump_json()) == {
        "setNewConfig": False,
        "ndiActive": True,
        "useNDI5": True,
        "useCustomResolution": True,
        "customWidthNDI": -1,
        "customHeightNDI": -1,
    }


def test_config_request_accepts_wire_aliases() -> None:
    """The abbreviated NDI aliases are accepted on the way in as well as out."""
    request = NDIConfigRequest.model_validate(
        {
            "setNewConfig": True,
            "ndiActive": False,
            "useNDI5": False,
            "useCustomResolution": False,
            "customWidthNDI": 256,
            "customHeightNDI": 256,
        },
    )

    assert request.use_ndi5 is False
    assert request.custom_width_ndi == 256
    assert request.custom_height_ndi == 256


def test_documented_config_payload_round_trips() -> None:
    """The documented NDI payload survives a validate/dump cycle unchanged."""
    response = NDIConfigResponse.model_validate(DOCUMENTED_NDI_PAYLOAD)

    assert json.loads(response.model_dump_json()) == DOCUMENTED_NDI_PAYLOAD
