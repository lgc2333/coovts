"""Wire-shape tests for `coovts.types.event`, driven by frames a real VTube Studio sent
and by payloads copied from the VTube Studio events documentation."""

import json

from coovts.types import api, event
from coovts.types.api import ArtMeshHitInfo, ModelPosition, Point2D
from coovts.types.shared import BaseResponse, get_event_name

from ...utils.frames import real_frame, real_payload

NEW_EVENT_STEMS = (
    "BackgroundChanged",
    "ModelConfigChanged",
    "PostProcessing",
    "ExpressionToggled",
    "ArtMeshTracking",
    "ArtMeshOutline",
)

HAIR_RIGHT6_OUTLINE_POINTS = [
    0.1421,
    0.3812,
    0.1388,
    0.3901,
    0.134,
    0.3964,
    0.1271,
    0.4003,
    0.1198,
    0.4014,
    0.1124,
    0.3994,
    0.1062,
    0.3947,
    0.1019,
    0.3878,
    0.1001,
    0.38,
    0.1011,
    0.3722,
    0.1048,
    0.3654,
    0.1109,
    0.3604,
    0.1182,
    0.3578,
    0.1259,
    0.3578,
    0.1331,
    0.3602,
    0.1391,
    0.3649,
    0.1429,
    0.3717,
    0.1443,
    0.3794,
    0.1421,
    0.3812,
]

FACE_SKIN_OUTLINE_POINTS = [
    0.0191,
    0.4451,
    0.0088,
    0.4502,
    -0.0021,
    0.4511,
    -0.0127,
    0.4476,
    -0.0214,
    0.4403,
    -0.0264,
    0.4303,
    -0.0271,
    0.4193,
    -0.0236,
    0.4089,
    -0.0163,
    0.4008,
    -0.0064,
    0.3961,
    0.0044,
    0.3953,
    0.0148,
    0.3985,
    0.0233,
    0.4054,
    0.0284,
    0.4151,
    0.0294,
    0.4259,
    0.0262,
    0.4362,
    0.0191,
    0.4451,
]

ART_MESH_TRACKING_EVENT_PAYLOAD: dict[str, object] = {
    "modelLoaded": True,
    "modelID": "d87b771d2902473bbaa0226d03ef4754",
    "windowSize": {"x": 1920, "y": 1080},
    "subscribedPointsCount": 2,
    "foundPointsCount": 2,
    "eventCounter": 147,
    "trackingPoints": [
        {
            "trackingPointID": "Tracked Point on Hair",
            "artMeshVisible": True,
            "position": {"x": 0.142, "y": 0.381},
            "rotation": 217.4,
            "size": 0.073,
        },
        {
            "trackingPointID": "Some other tracked point 1234",
            "artMeshVisible": False,
            "position": {"x": 0.019, "y": 0.445},
            "rotation": 94.1,
            "size": 0.051,
        },
    ],
}

ART_MESH_OUTLINE_EVENT_PAYLOAD: dict[str, object] = {
    "modelLoaded": True,
    "modelID": "d87b771d2902473bbaa0226d03ef4754",
    "windowSize": {"x": 1920, "y": 1080},
    "subscribedArtMeshCount": 2,
    "foundArtMeshCount": 2,
    "eventCounter": 147,
    "artMeshOutlines": [
        {
            "artMeshID": "hair_right6",
            "artMeshVisible": True,
            "outlineCount": 1,
            "outlineArea": 0.0842,
            "outlinePoints": [{"points": HAIR_RIGHT6_OUTLINE_POINTS}],
        },
        {
            "artMeshID": "face_skin",
            "artMeshVisible": True,
            "outlineCount": 1,
            "outlineArea": 0.2341,
            "outlinePoints": [{"points": FACE_SKIN_OUTLINE_POINTS}],
        },
    ],
}


def test_real_test_event_frame_decodes() -> None:
    """The `TestEvent` payload VTS sent decodes into its data model."""
    data = event.TestEventData.model_validate(real_payload("TestEvent"), by_alias=True)

    assert data.your_test_message == "coovts probe"
    assert data.counter == 560


def test_real_model_moved_event_uses_the_shared_position_model() -> None:
    """A real `ModelMovedEvent` decodes into the same `ModelPosition` the API side declares."""
    data = event.ModelMovedEventData.model_validate(
        real_payload("ModelMovedEvent"),
        by_alias=True,
    )

    assert data.model_id == "6248f9ba0edc401c96de072a3350de3f"
    assert data.model_name == "饼干寻"
    assert type(data.model_position) is ModelPosition
    assert data.model_position.position_x == 0.07763361930847168
    assert data.model_position.rotation == 358.4307861328125
    assert data.model_position.size == -65.87860870361328


def test_real_model_outline_event_frame_decodes() -> None:
    """A real 15 FPS `ModelOutlineEvent` decodes with its hull, center and window size."""
    data = event.ModelOutlineEventData.model_validate(
        real_payload("ModelOutlineEvent"),
        by_alias=True,
    )

    assert len(data.convex_hull) == 12
    assert data.convex_hull[0].x == 0.018246205523610115
    assert data.convex_hull_center.y == 0.22207362949848175
    assert (data.window_size.x, data.window_size.y) == (1440, 800)


def test_real_event_frames_carry_an_id_that_is_not_ours() -> None:
    """Events arrive with VTS's own 32-hex id, so they can never resolve a pending request."""
    envelope = BaseResponse.model_validate_json(real_frame("TestEvent"), by_alias=True)

    assert envelope.message_type == "TestEvent"
    assert envelope.request_id == "4513064a63b54cb6ab77a4eb1f5d471d"
    assert not envelope.request_id.isdigit()


def test_documented_events_name_the_wire_event() -> None:
    """Each documented event and its config sibling name the same `*Event` messageType."""
    for stem in NEW_EVENT_STEMS:
        event_name = stem + "Event"
        data_model = getattr(event, stem + "EventData")
        config_model = getattr(event, stem + "EventConfig")

        assert get_event_name(data_model) == event_name
        assert get_event_name(config_model) == event_name


def test_pytest_does_not_collect_the_test_event_wire_models() -> None:
    """The `Test*` wire models opt out of pytest's class collection despite their name."""
    assert event.TestEventConfig.__test__ is False
    assert event.TestEventData.__test__ is False


def test_documented_background_changed_payload_decodes() -> None:
    """The documented `BackgroundChangedEvent` payload decodes into its data model."""
    data = event.BackgroundChangedEventData.model_validate(
        {"backgroundName": "my_cool_background"},
        by_alias=True,
    )

    assert data.background_name == "my_cool_background"


def test_documented_model_config_changed_payload_decodes() -> None:
    """The documented `ModelConfigChangedEvent` payload decodes into its data model."""
    data = event.ModelConfigChangedEventData.model_validate(
        {
            "modelID": "UniqueIDToIdentifyThisModelBy",
            "modelName": "My Cool Model",
            "hotkeyConfigChanged": True,
        },
        by_alias=True,
    )

    assert data.model_id == "UniqueIDToIdentifyThisModelBy"
    assert data.model_name == "My Cool Model"
    assert data.hotkey_config_changed is True


def test_documented_post_processing_payload_decodes() -> None:
    """The documented `PostProcessingEvent` payload decodes into its data model."""
    data = event.PostProcessingEventData.model_validate(
        {
            "currentOnState": True,
            "currentPreset": "my_preset",
        },
        by_alias=True,
    )

    assert data.current_on_state is True
    assert data.current_preset == "my_preset"


def test_documented_expression_toggled_payload_decodes() -> None:
    """The documented `ExpressionToggledEvent` payload decodes into its data model."""
    data = event.ExpressionToggledEventData.model_validate(
        {
            "modelID": "d8ee771d2909873b1aa0226d03ef4f51",
            "modelName": "Akari",
            "isLive2DItem": False,
            "itemInstanceID": "",
            "justLoaded": False,
            "expressionFile": "EyesCry.exp3.json",
            "expressionName": "EyesCry",
            "active": True,
        },
        by_alias=True,
    )

    assert data.model_id == "d8ee771d2909873b1aa0226d03ef4f51"
    assert data.model_name == "Akari"
    assert data.is_live2d_item is False
    assert data.item_instance_id == ""
    assert data.just_loaded is False
    assert data.expression_file == "EyesCry.exp3.json"
    assert data.expression_name == "EyesCry"
    assert data.active is True


def test_documented_art_mesh_tracking_payload_decodes() -> None:
    """The documented `ArtMeshTrackingEvent` payload decodes into its data model."""
    data = event.ArtMeshTrackingEventData.model_validate(
        ART_MESH_TRACKING_EVENT_PAYLOAD,
        by_alias=True,
    )

    assert data.model_loaded is True
    assert data.model_id == "d87b771d2902473bbaa0226d03ef4754"
    assert (data.window_size.x, data.window_size.y) == (1920, 1080)
    assert (data.subscribed_points_count, data.found_points_count) == (2, 2)
    assert data.event_counter == 147

    tracked, missing = data.tracking_points
    assert tracked.tracking_point_id == "Tracked Point on Hair"
    assert tracked.art_mesh_visible is True
    assert type(tracked.position) is Point2D
    assert (tracked.position.x, tracked.position.y) == (0.142, 0.381)
    assert (tracked.rotation, tracked.size) == (217.4, 0.073)
    assert missing.tracking_point_id == "Some other tracked point 1234"
    assert missing.art_mesh_visible is False


def test_documented_art_mesh_outline_payload_decodes() -> None:
    """The documented `ArtMeshOutlineEvent` payload decodes into its data model."""
    data = event.ArtMeshOutlineEventData.model_validate(
        ART_MESH_OUTLINE_EVENT_PAYLOAD,
        by_alias=True,
    )

    assert data.model_loaded is True
    assert data.model_id == "d87b771d2902473bbaa0226d03ef4754"
    assert (data.window_size.x, data.window_size.y) == (1920, 1080)
    assert (data.subscribed_art_mesh_count, data.found_art_mesh_count) == (2, 2)
    assert data.event_counter == 147

    hair, face = data.art_mesh_outlines
    assert hair.art_mesh_id == "hair_right6"
    assert (hair.outline_count, hair.outline_area) == (1, 0.0842)
    assert hair.outline_points[0].points == HAIR_RIGHT6_OUTLINE_POINTS
    assert face.art_mesh_id == "face_skin"
    assert (face.outline_count, face.outline_area) == (1, 0.2341)
    assert face.outline_points[0].points == FACE_SKIN_OUTLINE_POINTS


def test_outline_ring_keeps_all_forty_numbers_flat() -> None:
    """A 20-point ring stays a flat list of 40 numbers instead of becoming `Point2D`s."""
    points = [index / 100 for index in range(40)]

    data = event.ArtMeshOutlineEventData.model_validate(
        {
            "modelLoaded": True,
            "modelID": "m1",
            "windowSize": {"x": 1920, "y": 1080},
            "subscribedArtMeshCount": 1,
            "foundArtMeshCount": 1,
            "eventCounter": 0,
            "artMeshOutlines": [
                {
                    "artMeshID": "hair_right6",
                    "artMeshVisible": True,
                    "outlineCount": 1,
                    "outlineArea": 0.5,
                    "outlinePoints": [{"points": points}],
                },
            ],
        },
        by_alias=True,
    )

    ring = data.art_mesh_outlines[0].outline_points[0]

    assert ring.points == points
    assert len(ring.points) == 40


def test_art_mesh_tracking_config_serializes_to_the_documented_wire_shape() -> None:
    """A tracking subscription goes out with the documented aliases, nested hit info included."""
    config = event.ArtMeshTrackingEventConfig.model_validate(
        {
            "frequency": 30,
            "tracking_points": [
                {
                    "tracking_point_id": "Tracked Point on Hair",
                    "art_mesh_coords": {
                        "modelID": "d87b771d2902473bbaa0226d03ef4754",
                        "artMeshID": "hair_right6",
                        "vertexID1": 80,
                        "vertexID2": 76,
                        "vertexID3": 75,
                        "vertexWeight1": 0.4725686013698578,
                        "vertexWeight2": 0.07506437599658966,
                        "vertexWeight3": 0.45236700773239136,
                        "angle": 0.0,
                        "size": 1.0,
                    },
                    "visualize": False,
                },
            ],
        },
        by_alias=True,
    )
    request = api.EventSubscriptionRequest(
        event_name="ArtMeshTrackingEvent",
        subscribe=True,
        config=config,
    )

    assert type(config.tracking_points[0].art_mesh_coords) is ArtMeshHitInfo

    payload = json.loads(request.model_dump_json())["config"]

    assert payload == {
        "frequency": 30,
        "trackingPoints": [
            {
                "trackingPointID": "Tracked Point on Hair",
                "artMeshCoords": {
                    "modelID": "d87b771d2902473bbaa0226d03ef4754",
                    "artMeshID": "hair_right6",
                    "vertexID1": 80,
                    "vertexID2": 76,
                    "vertexID3": 75,
                    "vertexWeight1": 0.4725686013698578,
                    "vertexWeight2": 0.07506437599658966,
                    "vertexWeight3": 0.45236700773239136,
                    "angle": 0.0,
                    "size": 1.0,
                },
                "visualize": False,
            },
        ],
    }


def test_art_mesh_outline_config_serializes_to_the_documented_wire_shape() -> None:
    """The outline config is built from field names and sent with the documented aliases."""
    config = event.ArtMeshOutlineEventConfig.model_validate(
        {
            "frequency": 15,
            "art_meshes": [
                {
                    "model_id": "d87b771d2902473bbaa0226d03ef4754",
                    "art_mesh_id": "hair_right6",
                },
            ],
        },
    )

    payload = json.loads(config.model_dump_json())

    assert payload == {
        "frequency": 15,
        "artMeshes": [
            {
                "modelID": "d87b771d2902473bbaa0226d03ef4754",
                "artMeshID": "hair_right6",
            },
        ],
    }
