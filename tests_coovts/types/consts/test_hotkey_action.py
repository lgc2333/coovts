"""Unit tests for the transcribed hotkey actions."""

from coovts.types.consts import HotkeyAction


def test_members_compare_equal_to_the_wire_strings() -> None:
    """`hotkeyAction`, `onlyForAction` and `HotkeyInfo.type` carry the member name as a string."""
    assert HotkeyAction.TriggerAnimation == "TriggerAnimation"
    assert HotkeyAction.ToggleExpression == "ToggleExpression"
    assert HotkeyAction.ChangeVTSModel == "ChangeVTSModel"


def test_unset_is_a_string_member_although_upstream_declares_it_as_minus_one() -> None:
    """Upstream's `-1` sentinel has no string form, so the member carries its own name."""
    assert HotkeyAction.Unset.value == "Unset"
    assert isinstance(HotkeyAction.Unset, str)
