"""Unit tests for the transcribed raw key table."""

from coovts.types.consts import RestrictedRawKey


def test_members_are_the_windows_virtual_key_codes() -> None:
    """The members transcribe upstream's `ushort` table, so they compare equal to the codes."""
    assert RestrictedRawKey.LeftMouseButton == 0x01
    assert RestrictedRawKey.Tab == 0x09
    assert RestrictedRawKey.A == 0x41
    assert RestrictedRawKey.F24 == 0x87
    assert RestrictedRawKey.Alt == 0xA4
