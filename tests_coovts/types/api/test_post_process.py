"""Wire-shape tests for the post process models of `coovts.types.api`."""

import json

from coovts.types.api import (
    ConfigValue,
    PostProcessingListRequest,
    PostProcessingListResponse,
    PostProcessingUpdateRequest,
)


def test_documented_list_response_payload_decodes() -> None:
    """The example list response from the reference docs decodes into the expected models."""
    response = PostProcessingListResponse.model_validate(
        {
            "postProcessingSupported": True,
            "postProcessingActive": True,
            "canSendPostProcessingUpdateRequestRightNow": True,
            "restrictedEffectsAllowed": False,
            "presetIsActive": True,
            "activePreset": "some_effects_preset_3",
            "presetCount": 70,
            "activeEffectCount": 5,
            "effectCountBeforeFilter": 29,
            "configCountBeforeFilter": 258,
            "effectCountAfterFilter": 4,
            "configCountAfterFilter": 31,
            "postProcessingEffects": [
                {
                    "internalID": "color_grading",
                    "enumID": "ColorGrading",
                    "explanation": "Color grading",
                    "effectIsActive": False,
                    "effectIsRestricted": False,
                    "configEntries": [
                        {
                            "internalID": "color_grading-strength",
                            "enumID": "ColorGrading_Strength",
                            "explanation": "Effect on/off",
                            "type": "Float",
                            "activationConfig": True,
                            "floatValue": 0.0,
                            "floatMin": 0.0,
                            "floatMax": 1.0,
                            "floatDefault": 0.0,
                            "intValue": 0,
                            "intMin": 0,
                            "intMax": 0,
                            "intDefault": 0,
                            "colorValue": "",
                            "colorDefault": "",
                            "colorHasAlpha": False,
                            "boolValue": False,
                            "boolDefault": False,
                            "stringValue": "",
                            "stringDefault": "",
                            "sceneItemValue": "",
                            "sceneItemDefault": "",
                        },
                    ],
                },
            ],
            "postProcessingPresets": [
                "My Cool Preset",
                "some_effects_preset_1",
                "some_effects_preset_2",
                "some_effects_preset_3",
            ],
        },
    )

    assert response.preset_is_active is True
    assert response.active_preset == "some_effects_preset_3"
    effect = response.post_processing_effects[0]
    assert effect.effect_is_restricted is False
    assert effect.config_entries[0].internal_id == "color_grading-strength"
    assert effect.config_entries[0].activation_config is True
    assert response.post_processing_presets[0] == "My Cool Preset"


def test_documented_config_entry_dumps_the_wire_shape() -> None:
    """A `Float` config entry round-trips to its full documented wire dict."""
    entry = (
        PostProcessingListResponse.model_validate(
            {
                "postProcessingSupported": True,
                "postProcessingActive": False,
                "canSendPostProcessingUpdateRequestRightNow": False,
                "restrictedEffectsAllowed": False,
                "presetIsActive": False,
                "activePreset": "",
                "presetCount": 0,
                "activeEffectCount": 0,
                "effectCountBeforeFilter": 1,
                "configCountBeforeFilter": 1,
                "effectCountAfterFilter": 1,
                "configCountAfterFilter": 1,
                "postProcessingEffects": [
                    {
                        "internalID": "color_grading",
                        "enumID": "ColorGrading",
                        "explanation": "Color grading",
                        "effectIsActive": False,
                        "effectIsRestricted": False,
                        "configEntries": [
                            {
                                "internalID": "color_grading-strength",
                                "enumID": "ColorGrading_Strength",
                                "explanation": "Effect on/off",
                                "type": "Float",
                                "activationConfig": True,
                                "floatValue": 0.0,
                                "floatMin": 0.0,
                                "floatMax": 1.0,
                                "floatDefault": 0.0,
                                "intValue": 0,
                                "intMin": 0,
                                "intMax": 0,
                                "intDefault": 0,
                                "colorValue": "",
                                "colorDefault": "",
                                "colorHasAlpha": False,
                                "boolValue": False,
                                "boolDefault": False,
                                "stringValue": "",
                                "stringDefault": "",
                                "sceneItemValue": "",
                                "sceneItemDefault": "",
                            },
                        ],
                    },
                ],
            },
        )
        .post_processing_effects[0]
        .config_entries[0]
    )

    assert json.loads(entry.model_dump_json()) == {
        "internalID": "color_grading-strength",
        "enumID": "ColorGrading_Strength",
        "explanation": "Effect on/off",
        "type": "Float",
        "activationConfig": True,
        "floatValue": 0.0,
        "floatMin": 0.0,
        "floatMax": 1.0,
        "floatDefault": 0.0,
        "intValue": 0,
        "intMin": 0,
        "intMax": 0,
        "intDefault": 0,
        "colorValue": "",
        "colorDefault": "",
        "colorHasAlpha": False,
        "boolValue": False,
        "boolDefault": False,
        "stringValue": "",
        "stringDefault": "",
        "sceneItemValue": "",
        "sceneItemDefault": "",
    }


def test_bare_list_request_emits_the_wire_shape() -> None:
    """A default list request fills both arrays and applies no effect filter."""
    assert json.loads(PostProcessingListRequest().model_dump_json()) == {
        "fillPostProcessingPresetsArray": True,
        "fillPostProcessingEffectsArray": True,
        "effectIDFilter": [],
    }


def test_config_value_dumps_the_wire_shape() -> None:
    """A config value emits `configID` and keeps its value as a string."""
    value = ConfigValue(config_id="Backlight_Strength", config_value="0.8")

    assert json.loads(value.model_dump_json()) == {
        "configID": "Backlight_Strength",
        "configValue": "0.8",
    }


def test_documented_update_request_built_from_field_names() -> None:
    """The documented update request round-trips from python field names to the wire dict."""
    request = PostProcessingUpdateRequest(
        post_processing_on=True,
        set_post_processing_values=True,
        post_processing_fade_time=1.3,
    )
    request.post_processing_values.append(
        ConfigValue(config_id="Backlight_Strength", config_value="0.8"),
    )

    assert json.loads(request.model_dump_json()) == {
        "postProcessingOn": True,
        "setPostProcessingPreset": False,
        "setPostProcessingValues": True,
        "presetToSet": "",
        "postProcessingFadeTime": 1.3,
        "setAllOtherValuesToDefault": True,
        "usingRestrictedEffects": False,
        "randomizeAll": False,
        "randomizeAllChaosLevel": 0.0,
        "postProcessingValues": [
            {"configID": "Backlight_Strength", "configValue": "0.8"},
        ],
    }


def test_bare_update_request_emits_empty_values() -> None:
    """A bare update request only requires `postProcessingOn` and no config values."""
    assert json.loads(
        PostProcessingUpdateRequest(post_processing_on=True).model_dump_json()
    ) == {
        "postProcessingOn": True,
        "setPostProcessingPreset": False,
        "setPostProcessingValues": False,
        "presetToSet": "",
        "postProcessingFadeTime": 0.0,
        "setAllOtherValuesToDefault": True,
        "usingRestrictedEffects": False,
        "randomizeAll": False,
        "randomizeAllChaosLevel": 0.0,
        "postProcessingValues": [],
    }
