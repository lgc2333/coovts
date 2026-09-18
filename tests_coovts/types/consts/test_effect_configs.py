"""Unit tests for the transcribed post-processing effect config IDs."""

from coovts.types.consts import EffectConfigs


def test_members_compare_equal_to_the_wire_strings() -> None:
    """`configID` and `EffectConfigEntry.enumID` carry the member name as a string."""
    assert EffectConfigs.ColorGrading_Strength == "ColorGrading_Strength"
    assert EffectConfigs.Vhs_NoiseGrain == "Vhs_NoiseGrain"
    assert EffectConfigs.ModelGlitch_StrengthLiquify == "ModelGlitch_StrengthLiquify"
