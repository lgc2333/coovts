"""Wire-shape tests for the model models of `coovts.types.api`."""

import json

from coovts.types.api import (
    AvailableModelsRequest,
    AvailableModelsResponse,
    CurrentModelRequest,
    CurrentModelResponse,
    ModelLoadRequest,
    ModelLoadResponse,
    MoveModelRequest,
    MoveModelResponse,
)


def test_documented_current_model_response_decodes() -> None:
    """The example current-model response decodes, nested position included."""
    response = CurrentModelResponse.model_validate(
        {
            "modelLoaded": True,
            "modelName": "My Currently Loaded Model",
            "modelID": "UniqueIDToIdentifyThisModelBy",
            "vtsModelName": "Model.vtube.json",
            "vtsModelIconName": "ModelIconPNGorJPG.png",
            "live2DModelName": "Model.model3.json",
            "modelLoadTime": 3021,
            "timeSinceModelLoaded": 419903,
            "numberOfLive2DParameters": 29,
            "numberOfLive2DArtmeshes": 136,
            "hasPhysicsFile": True,
            "numberOfTextures": 2,
            "textureResolution": 4096,
            "modelPosition": {
                "positionX": -0.1,
                "positionY": 0.4,
                "rotation": 9.33,
                "size": -61.9,
            },
        },
    )

    assert response.model_id == "UniqueIDToIdentifyThisModelBy"
    assert response.number_of_live2d_parameters == 29
    assert response.number_of_live2d_artmeshes == 136
    assert response.model_position.position_x == -0.1
    assert response.model_position.size == -61.9
    assert json.loads(response.model_dump_json())["modelPosition"] == {
        "positionX": -0.1,
        "positionY": 0.4,
        "rotation": 9.33,
        "size": -61.9,
    }


def test_documented_available_models_response_decodes() -> None:
    """The example available-models response decodes every listed model."""
    response = AvailableModelsResponse.model_validate(
        {
            "numberOfModels": 2,
            "availableModels": [
                {
                    "modelLoaded": False,
                    "modelName": "My First Model",
                    "modelID": "UniqueIDToIdentifyThisModelBy1",
                    "vtsModelName": "Model_1.vtube.json",
                    "vtsModelIconName": "ModelIconPNGorJPG_1.png",
                },
                {
                    "modelLoaded": True,
                    "modelName": "My Second Model",
                    "modelID": "UniqueIDToIdentifyThisModelBy2",
                    "vtsModelName": "Model_2.vtube.json",
                    "vtsModelIconName": "ModelIconPNGorJPG_1.png",
                },
            ],
        },
    )

    assert response.number_of_models == 2
    assert response.available_models[0].model_id == "UniqueIDToIdentifyThisModelBy1"
    assert response.available_models[0].vts_model_name == "Model_1.vtube.json"
    assert [info.model_loaded for info in response.available_models] == [False, True]


def test_model_load_payloads_use_the_model_id_alias() -> None:
    """Both load payloads carry the documented `modelID` wire key."""
    assert json.loads(ModelLoadRequest(model_id="m1").model_dump_json()) == {
        "modelID": "m1",
    }

    response = ModelLoadResponse.model_validate({"modelID": "UniqueIDOfModelToLoad"})
    assert response.model_id == "UniqueIDOfModelToLoad"
    assert json.loads(response.model_dump_json()) == {
        "modelID": "UniqueIDOfModelToLoad"
    }


def test_move_model_request_dumps_camel_case_and_keeps_nulls() -> None:
    """Omitted move fields serialise as null, which VTS reads as "leave untouched"."""
    request = MoveModelRequest(time_in_seconds=1, values_are_relative_to_model=True)

    assert json.loads(request.model_dump_json()) == {
        "timeInSeconds": 1,
        "valuesAreRelativeToModel": True,
        "positionX": None,
        "positionY": None,
        "rotation": None,
        "size": None,
    }


def test_documented_move_model_request_round_trips() -> None:
    """Every documented move field survives a wire decode and re-encode."""
    request = MoveModelRequest.model_validate(
        {
            "timeInSeconds": 0.2,
            "valuesAreRelativeToModel": False,
            "positionX": 0.1,
            "positionY": -0.7,
            "rotation": 16.3,
            "size": -22.5,
        },
    )

    assert request.time_in_seconds == 0.2
    assert request.values_are_relative_to_model is False
    assert request.size == -22.5
    assert json.loads(request.model_dump_json()) == {
        "timeInSeconds": 0.2,
        "valuesAreRelativeToModel": False,
        "positionX": 0.1,
        "positionY": -0.7,
        "rotation": 16.3,
        "size": -22.5,
    }


def test_payloadless_model_messages_dump_empty_data() -> None:
    """Requests and responses with no fields serialise to an empty object."""
    assert json.loads(CurrentModelRequest().model_dump_json()) == {}
    assert json.loads(AvailableModelsRequest().model_dump_json()) == {}
    assert json.loads(MoveModelResponse().model_dump_json()) == {}
