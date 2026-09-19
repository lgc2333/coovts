"""Wire-shape tests for the auth models of `coovts.types.api`."""

import json

from coovts.types.api import (
    AuthenticationRequest,
    AuthenticationResponse,
    AuthenticationTokenRequest,
    AuthenticationTokenResponse,
)

TOKEN = "adcd-123-ef09-some-token-string-abcd"  # noqa: S105


def test_documented_token_request_dumps_the_wire_shape() -> None:
    """A token request carries both names and the optional icon, which is null when unset."""
    assert json.loads(
        AuthenticationTokenRequest(
            plugin_name="My Cool Plugin",
            plugin_developer="My Name",
        ).model_dump_json(),
    ) == {
        "pluginName": "My Cool Plugin",
        "pluginDeveloper": "My Name",
        "pluginIcon": None,
    }

    assert json.loads(
        AuthenticationTokenRequest(
            plugin_name="My Cool Plugin",
            plugin_developer="My Name",
            plugin_icon="iVBORw0.........KGgoA=",
        ).model_dump_json(),
    ) == {
        "pluginName": "My Cool Plugin",
        "pluginDeveloper": "My Name",
        "pluginIcon": "iVBORw0.........KGgoA=",
    }


def test_documented_token_response_decodes() -> None:
    """The documented token response decodes `authenticationToken` into the python field."""
    response = AuthenticationTokenResponse.model_validate(
        {"authenticationToken": TOKEN},
    )

    assert response.authentication_token == TOKEN
    assert json.loads(response.model_dump_json()) == {
        "authenticationToken": TOKEN,
    }


def test_documented_authentication_request_dumps_the_wire_shape() -> None:
    """An authentication request carries both names and the token under their aliases."""
    assert json.loads(
        AuthenticationRequest(
            plugin_name="My Cool Plugin",
            plugin_developer="My Name",
            authentication_token=TOKEN,
        ).model_dump_json(),
    ) == {
        "pluginName": "My Cool Plugin",
        "pluginDeveloper": "My Name",
        "authenticationToken": TOKEN,
    }


def test_documented_authentication_response_decodes() -> None:
    """The documented response decodes `authenticated` and `reason`, for success and denial."""
    response = AuthenticationResponse.model_validate(
        {
            "authenticated": True,
            "reason": "Token valid. The plugin is authenticated for the duration of this session.",
        },
    )

    assert response.authenticated is True
    assert (
        response.reason
        == "Token valid. The plugin is authenticated for the duration of this session."
    )

    denied = AuthenticationResponse.model_validate(
        {"authenticated": False, "reason": "Token invalid."},
    )

    assert denied.authenticated is False
    assert denied.reason == "Token invalid."
