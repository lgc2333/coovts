"""Wire-shape tests for the art_mesh models of `coovts.types.api`."""

import json

from coovts.types.api import (
    ArtMeshAtPositionRequest,
    ArtMeshAtPositionResponse,
    ArtMeshGroup,
    ArtMeshHitInfo,
    ArtMeshListRequest,
    ArtMeshListResponse,
    ArtMeshMatcher,
    ArtMeshSelectionRequest,
    ArtMeshSelectionResponse,
    ColorData,
    ColorTintRequest,
    ColorTintResponse,
    Point2D,
)


def test_documented_art_mesh_list_response_decodes() -> None:
    """The example response from the reference docs decodes into two ArtMesh groups."""
    response = ArtMeshListResponse.model_validate(
        {
            "modelLoaded": True,
            "numberOfArtMeshNames": 5,
            "numberOfArtMeshTags": 2,
            "artMeshNames": [
                "ArtMesh1",
                "ArtMesh2",
                "HairFront1",
                "HairFront2",
                "SomeArtMesh",
            ],
            "artMeshTags": ["my_tag", "SomeOtherTag"],
            "numberOfArtMeshGroups": 2,
            "artMeshGroups": [
                {
                    "groupID": "5c1dc47c3b7447efa3cdd1bca56f4c27",
                    "groupName": "Model Hair",
                    "numberOfArtMeshesInGroup": 2,
                    "artMeshNames": ["hair_1", "hair_2"],
                },
                {
                    "groupID": "2ed325b7d3dd4f92af8dbc1c47cd3143",
                    "groupName": "empty_group_test",
                    "numberOfArtMeshesInGroup": 0,
                    "artMeshNames": [],
                },
            ],
        },
    )

    assert response.model_loaded is True
    assert response.number_of_art_mesh_names == 5
    assert response.number_of_art_mesh_tags == 2
    assert response.art_mesh_names == [
        "ArtMesh1",
        "ArtMesh2",
        "HairFront1",
        "HairFront2",
        "SomeArtMesh",
    ]
    assert response.art_mesh_tags == ["my_tag", "SomeOtherTag"]
    assert response.number_of_art_mesh_groups == 2
    assert len(response.art_mesh_groups) == 2
    assert [group.group_id for group in response.art_mesh_groups] == [
        "5c1dc47c3b7447efa3cdd1bca56f4c27",
        "2ed325b7d3dd4f92af8dbc1c47cd3143",
    ]
    assert [group.group_name for group in response.art_mesh_groups] == [
        "Model Hair",
        "empty_group_test",
    ]
    assert [
        group.number_of_art_meshes_in_group for group in response.art_mesh_groups
    ] == [2, 0]
    assert response.art_mesh_groups[0].art_mesh_names == ["hair_1", "hair_2"]
    assert response.art_mesh_groups[1].art_mesh_names == []


def test_art_mesh_group_dumps_exactly_the_wire_shape() -> None:
    """A group serializes its ID alias plus the camelCase fields, with no extra keys."""
    assert json.loads(
        ArtMeshGroup(
            group_id="5c1dc47c3b7447efa3cdd1bca56f4c27",
            group_name="Model Hair",
            number_of_art_meshes_in_group=2,
            art_mesh_names=["hair_1", "hair_2"],
        ).model_dump_json(),
    ) == {
        "groupID": "5c1dc47c3b7447efa3cdd1bca56f4c27",
        "groupName": "Model Hair",
        "numberOfArtMeshesInGroup": 2,
        "artMeshNames": ["hair_1", "hair_2"],
    }


def test_empty_list_messages_keep_their_empty_wire_shape() -> None:
    """A list request has no payload and a group-less list response keeps empty defaults."""
    assert json.loads(ArtMeshListRequest().model_dump_json()) == {}

    assert json.loads(
        ArtMeshListResponse(
            model_loaded=False,
            number_of_art_mesh_names=0,
            number_of_art_mesh_tags=0,
            art_mesh_names=[],
            art_mesh_tags=[],
        ).model_dump_json(),
    ) == {
        "modelLoaded": False,
        "numberOfArtMeshNames": 0,
        "numberOfArtMeshTags": 0,
        "artMeshNames": [],
        "artMeshTags": [],
        "numberOfArtMeshGroups": 0,
        "artMeshGroups": [],
    }


def test_color_tint_request_and_response_wire_shapes() -> None:
    """The documented tint example validates into python fields and dumps its aliases."""
    request = ColorTintRequest.model_validate(
        {
            "colorTint": {
                "colorR": 255,
                "colorG": 150,
                "colorB": 0,
                "colorA": 255,
                "mixWithSceneLightingColor": 1,
            },
            "artMeshMatcher": {
                "tintAll": False,
                "artMeshNumber": [1, 3, 5],
                "nameExact": ["eye_white_left", "eye_white_right"],
                "nameContains": ["mouth"],
                "tagExact": [],
                "tagContains": ["MyTag"],
                "artMeshGroupIDExact": ["5c1dc47c3b7447efa3cdd1bca56f4c27"],
            },
        },
    )

    assert (
        request.color_tint.color_r,
        request.color_tint.color_g,
        request.color_tint.color_b,
        request.color_tint.color_a,
    ) == (255, 150, 0, 255)
    assert request.color_tint.mix_with_scene_lighting_color == 1.0
    assert request.art_mesh_matcher.art_mesh_number == [1, 3, 5]
    assert request.art_mesh_matcher.name_contains == ["mouth"]
    assert request.art_mesh_matcher.art_mesh_group_id_exact == [
        "5c1dc47c3b7447efa3cdd1bca56f4c27",
    ]

    assert json.loads(request.model_dump_json())["artMeshMatcher"] == {
        "tintAll": False,
        "artMeshNumber": [1, 3, 5],
        "nameExact": ["eye_white_left", "eye_white_right"],
        "nameContains": ["mouth"],
        "tagExact": [],
        "tagContains": ["MyTag"],
        "artMeshGroupIDExact": ["5c1dc47c3b7447efa3cdd1bca56f4c27"],
    }

    built = ColorTintRequest(
        color_tint=ColorData(color_r=255, color_g=150, color_b=0, color_a=255),
        art_mesh_matcher=ArtMeshMatcher(art_mesh_group_id_exact=["g1"]),
    )

    assert json.loads(built.model_dump_json()) == {
        "colorTint": {
            "colorR": 255,
            "colorG": 150,
            "colorB": 0,
            "colorA": 255,
            "mixWithSceneLightingColor": 1.0,
        },
        "artMeshMatcher": {
            "tintAll": False,
            "artMeshNumber": [],
            "nameExact": [],
            "nameContains": [],
            "tagExact": [],
            "tagContains": [],
            "artMeshGroupIDExact": ["g1"],
        },
    }

    response = ColorTintResponse.model_validate({"matchedArtMeshes": 3})

    assert response.matched_art_meshes == 3


def test_art_mesh_selection_request_and_response_wire_shapes() -> None:
    """Selection defaults pass through as null/zero and the response keeps both ID lists."""
    assert json.loads(
        ArtMeshSelectionRequest(
            text_override="This text is shown over the ArtMesh selection list.",
            help_override="This text is shown when the user presses the ? button.",
            requested_art_mesh_count=5,
            active_art_meshes=["D_BODY_00", "D_ARM_R_05"],
        ).model_dump_json(),
    ) == {
        "textOverride": "This text is shown over the ArtMesh selection list.",
        "helpOverride": "This text is shown when the user presses the ? button.",
        "requestedArtMeshCount": 5,
        "activeArtMeshes": ["D_BODY_00", "D_ARM_R_05"],
    }

    response = ArtMeshSelectionResponse.model_validate(
        {
            "success": True,
            "activeArtMeshes": ["D_BROW_00", "D_EYE_BALL_03"],
            "inactiveArtMeshes": ["D_EAR_06", "D_BODY_00", "D_ARM_R_05"],
        },
    )

    assert response.success is True
    assert response.active_art_meshes == ["D_BROW_00", "D_EYE_BALL_03"]
    assert response.inactive_art_meshes == ["D_EAR_06", "D_BODY_00", "D_ARM_R_05"]


def test_documented_art_mesh_at_position_wire_shapes() -> None:
    """The documented hit example decodes, and a hit info round-trips its ID aliases."""
    assert json.loads(
        ArtMeshAtPositionRequest(x=0.3, y=-0.67, visualize=2.5).model_dump_json(),
    ) == {"x": 0.3, "y": -0.67, "visualize": 2.5}

    response = ArtMeshAtPositionResponse.model_validate(
        {
            "modelLoaded": True,
            "loadedModelID": "d87b771d2902473bbaa0226d03ef4754",
            "loadedModelName": "Akari",
            "modelWasHit": True,
            "checkedPosition": {"x": 0.3, "y": -0.67},
            "windowSize": {"x": 2268, "y": 1243},
            "artMeshHitCount": 2,
            "artMeshHits": [
                {
                    "artMeshOrder": 0,
                    "isMasked": False,
                    "hitInfo": {
                        "modelID": "d87b771d2902473bbaa0226d03ef4754",
                        "artMeshID": "hair_right6",
                        "angle": 130.80455017089844,
                        "size": 1.0,
                        "vertexID1": 80,
                        "vertexID2": 76,
                        "vertexID3": 75,
                        "vertexWeight1": 0.4725686013698578,
                        "vertexWeight2": 0.07506437599658966,
                        "vertexWeight3": 0.45236700773239136,
                    },
                },
                {
                    "artMeshOrder": 1,
                    "isMasked": True,
                    "hitInfo": {
                        "modelID": "d87b771d2902473bbaa0226d03ef4754",
                        "artMeshID": "face_skin",
                        "angle": 63.90638732910156,
                        "size": 1.0,
                        "vertexID1": 75,
                        "vertexID2": 71,
                        "vertexID3": 70,
                        "vertexWeight1": 0.3965734839439392,
                        "vertexWeight2": 0.06637920439243317,
                        "vertexWeight3": 0.5370473265647888,
                    },
                },
            ],
        },
    )

    assert response.model_loaded is True
    assert response.loaded_model_id == "d87b771d2902473bbaa0226d03ef4754"
    assert response.loaded_model_name == "Akari"
    assert response.model_was_hit is True
    assert isinstance(response.checked_position, Point2D)
    assert (response.checked_position.x, response.checked_position.y) == (0.3, -0.67)
    assert (response.window_size.x, response.window_size.y) == (2268, 1243)
    assert response.art_mesh_hit_count == 2
    assert [(hit.art_mesh_order, hit.is_masked) for hit in response.art_mesh_hits] == [
        (0, False),
        (1, True),
    ]

    hit_info = response.art_mesh_hits[0].hit_info

    assert (hit_info.model_id, hit_info.art_mesh_id) == (
        "d87b771d2902473bbaa0226d03ef4754",
        "hair_right6",
    )
    assert (hit_info.vertex_id1, hit_info.vertex_id2, hit_info.vertex_id3) == (
        80,
        76,
        75,
    )
    assert json.loads(hit_info.model_dump_json()) == {
        "modelID": "d87b771d2902473bbaa0226d03ef4754",
        "artMeshID": "hair_right6",
        "angle": 130.80455017089844,
        "size": 1.0,
        "vertexID1": 80,
        "vertexID2": 76,
        "vertexID3": 75,
        "vertexWeight1": 0.4725686013698578,
        "vertexWeight2": 0.07506437599658966,
        "vertexWeight3": 0.45236700773239136,
    }
    assert (
        ArtMeshHitInfo.model_validate(json.loads(hit_info.model_dump_json()))
        == hit_info
    )
