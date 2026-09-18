"""Permission models of the VTube Studio API.

https://github.com/DenchiSoft/VTubeStudio/blob/master/Permissions/README.md
"""

from typing import Literal

from pydantic import BaseModel

from ..shared import with_request_model_config, with_response_model_config

type PermissionName = Literal["LoadCustomImagesAsItems", "ControlNDISettings"]
"""Permission names upstream documents today.

The reference list ends with "more to come", so no field is narrowed to this alias: every
permission name on the wire stays a plain `str`.
"""


@with_request_model_config
class PermissionRequest(BaseModel):
    """Request a permission for this plugin, or only list the ones it already has."""

    requested_permission: str = ""
    """Permission to request; an empty string asks for the list without a user popup"""


@with_response_model_config
class PermissionInfo(BaseModel):
    """One permission VTube Studio offers, with the grant state of the asking plugin."""

    name: str
    """Permission name, see `PermissionName`"""
    granted: bool
    """Whether this plugin currently has that permission"""


@with_response_model_config
class PermissionResponse(BaseModel):
    """All permissions VTube Studio offers, and how a requested permission was answered."""

    grant_success: bool = False
    """Whether the user granted the permission.

    A real VTube Studio answers a list-only request with `grantSuccess: false`, so the field is
    always present and a plain `bool` covers both the listing and the answering shape.
    """
    requested_permission: str = ""
    """Name of the permission the user just answered about.

    The permission this response is about, not the plugin's grants; empty when only the list was
    requested. Only `permissions` tells which permissions this plugin currently has.
    """
    permissions: list[PermissionInfo] = []
    """Every permission VTube Studio offers, granted or not.

    Only this array can be read to learn which permissions this plugin currently has.
    """
