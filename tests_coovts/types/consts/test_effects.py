"""Unit tests for the transcribed post-processing effect IDs."""

from coovts.types.consts import Effects


def test_members_compare_equal_to_the_wire_strings() -> None:
    """`effectIDFilter` and `PostProcessingEffect.enumID` carry the member name as a string."""
    assert Effects.ColorGrading == "ColorGrading"
    assert Effects.Ascii == "Ascii"
    assert Effects.ModelGlitch == "ModelGlitch"
