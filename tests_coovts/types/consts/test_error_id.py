"""Unit tests for the transcribed VTube Studio error IDs."""

from coovts.types.consts import ErrorID


def test_members_compare_equal_to_the_wire_integers() -> None:
    """`errorID` is an integer on the wire, so a parsed response can be matched by member."""
    assert ErrorID.TokenRequestDenied == 50
    assert ErrorID.RequestRequiresAuthetication == 8
    assert ErrorID.EventSubscriptionRequestEventTypeUnknown == 950


def test_event_config_errors_sit_at_their_offset_above_event_offset() -> None:
    """Event-subscription errors are `EVENT_OFFSET` plus the offset upstream gives them."""
    assert ErrorID.EVENT_OFFSET == 100000
    assert ErrorID.Event_ArtMeshTrackingEvent_FrequencyInvalid == 100151
    assert ErrorID.Event_ArtMeshOutlineEvent_ArtMeshesInvalid == 100200


def test_an_offset_zero_member_is_an_alias_of_event_offset() -> None:
    """Upstream's `EVENT_OFFSET + 0` member shares its value, so Python folds it into an alias."""
    assert ErrorID.Event_TestEvent_TestMessageTooLong is ErrorID.EVENT_OFFSET
    assert "Event_TestEvent_TestMessageTooLong" in ErrorID.__members__
