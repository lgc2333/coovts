"""Wire-shape tests for `coovts.types.event`, driven by frames a real VTube Studio sent."""

from coovts.types import event
from coovts.types.api import ModelPosition
from coovts.types.shared import BaseResponse

from ...utils.frames import real_frame, real_payload


def test_real_test_event_frame_decodes() -> None:
    """The `TestEvent` payload VTS sent decodes into its data model."""
    data = event.TestEventData.model_validate(real_payload("TestEvent"))

    assert data.your_test_message == "coovts probe"
    assert data.counter == 560


def test_real_model_moved_event_uses_the_shared_position_model() -> None:
    """A real `ModelMovedEvent` decodes into the same `ModelPosition` the API side declares."""
    data = event.ModelMovedEventData.model_validate(real_payload("ModelMovedEvent"))

    assert data.model_id == "6248f9ba0edc401c96de072a3350de3f"
    assert data.model_name == "饼干寻"
    assert type(data.model_position) is ModelPosition
    assert data.model_position.position_x == 0.07763361930847168
    assert data.model_position.rotation == 358.4307861328125
    assert data.model_position.size == -65.87860870361328


def test_real_model_outline_event_frame_decodes() -> None:
    """A real 15 FPS `ModelOutlineEvent` decodes with its hull, center and window size."""
    data = event.ModelOutlineEventData.model_validate(real_payload("ModelOutlineEvent"))

    assert len(data.convex_hull) == 12
    assert data.convex_hull[0].x == 0.018246205523610115
    assert data.convex_hull_center.y == 0.22207362949848175
    assert (data.window_size.x, data.window_size.y) == (1440, 800)


def test_real_event_frames_carry_an_id_that_is_not_ours() -> None:
    """Events arrive with VTS's own 32-hex id, so they can never resolve a pending request."""
    envelope = BaseResponse.model_validate_json(real_frame("TestEvent"))

    assert envelope.message_type == "TestEvent"
    assert envelope.request_id == "4513064a63b54cb6ab77a4eb1f5d471d"
    assert not envelope.request_id.isdigit()
