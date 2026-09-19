"""Wire-shape tests for the param models of `coovts.types.api`."""

import json

from coovts.types.api import (
    FaceFoundRequest,
    FaceFoundResponse,
    InjectParameterDataRequest,
    InjectParameterDataResponse,
    InputParameterListRequest,
    InputParameterListResponse,
    Live2DParameterListRequest,
    Live2DParameterListResponse,
    ParameterCreationRequest,
    ParameterCreationResponse,
    ParameterDeletionRequest,
    ParameterDeletionResponse,
    ParameterValue,
    ParameterValueRequest,
    ParameterValueResponse,
)


def test_documented_face_found_response_decodes() -> None:
    """The example face-found response decodes its single boolean."""
    response = FaceFoundResponse.model_validate({"found": True})

    assert response.found is True
    assert json.loads(FaceFoundResponse(found=False).model_dump_json()) == {
        "found": False
    }


def test_documented_input_parameter_list_response_decodes() -> None:
    """The example tracking-parameter list decodes custom and default parameters."""
    response = InputParameterListResponse.model_validate(
        {
            "modelLoaded": True,
            "modelName": "My Currently Loaded Model",
            "modelID": "UniqueIDOfModel",
            "customParameters": [
                {
                    "name": "MyCustomParamName1",
                    "addedBy": "My Plugin Name",
                    "value": 12.4,
                    "min": -30,
                    "max": 30,
                    "defaultValue": 0,
                },
                {
                    "name": "MyCustomParamName2",
                    "addedBy": "My Plugin Name",
                    "value": 0.833,
                    "min": -10,
                    "max": 10,
                    "defaultValue": 0,
                },
                {
                    "name": "MyCustomParamName3",
                    "addedBy": "My Other Plugin Name",
                    "value": 0,
                    "min": 0,
                    "max": 1,
                    "defaultValue": 0,
                },
            ],
            "defaultParameters": [
                {
                    "name": "FaceAngleX",
                    "addedBy": "VTube Studio",
                    "value": 45.78,
                    "min": -30,
                    "max": 30,
                    "defaultValue": 0,
                },
                {
                    "name": "FacePositionX",
                    "addedBy": "VTube Studio",
                    "value": 8.33,
                    "min": -10,
                    "max": 10,
                    "defaultValue": 0,
                },
            ],
        },
    )

    assert response.model_id == "UniqueIDOfModel"
    assert [param.name for param in response.custom_parameters] == [
        "MyCustomParamName1",
        "MyCustomParamName2",
        "MyCustomParamName3",
    ]
    assert response.custom_parameters[0].added_by == "My Plugin Name"
    assert response.custom_parameters[0].default_value == 0
    assert response.default_parameters[0].name == "FaceAngleX"
    assert response.default_parameters[0].value == 45.78


def test_documented_parameter_value_response_decodes() -> None:
    """The example one-parameter response decodes into the shared parameter shape."""
    response = ParameterValueResponse.model_validate(
        {
            "name": "MyCustomParamName1",
            "addedBy": "My Plugin Name",
            "value": 12.4,
            "min": -30,
            "max": 30,
            "defaultValue": 0,
        },
    )

    assert response.name == "MyCustomParamName1"
    assert response.added_by == "My Plugin Name"
    assert response.min == -30
    assert json.loads(response.model_dump_json()) == {
        "name": "MyCustomParamName1",
        "addedBy": "My Plugin Name",
        "value": 12.4,
        "min": -30,
        "max": 30,
        "defaultValue": 0,
    }


def test_documented_live2d_parameter_list_response_decodes() -> None:
    """The example Live2D parameter list decodes its parameter array."""
    response = Live2DParameterListResponse.model_validate(
        {
            "modelLoaded": True,
            "modelName": "My Currently Loaded Model",
            "modelID": "UniqueIDOfModel",
            "parameters": [
                {
                    "name": "MyLive2DParameterID1",
                    "value": 12.4,
                    "min": -30,
                    "max": 30,
                    "defaultValue": 0,
                },
                {
                    "name": "MyLive2DParameterID2",
                    "value": 0,
                    "min": 0,
                    "max": 1,
                    "defaultValue": 0,
                },
            ],
        },
    )

    assert response.model_loaded is True
    assert response.model_id == "UniqueIDOfModel"
    assert [(param.name, param.value) for param in response.parameters] == [
        ("MyLive2DParameterID1", 12.4),
        ("MyLive2DParameterID2", 0),
    ]


def test_documented_inject_parameter_data_request_dumps_the_wire_shape() -> None:
    """The example parameter-injection request emits `faceFound`, `mode` and `weight`."""
    request = InjectParameterDataRequest(
        parameter_values=[
            ParameterValue(id="FaceAngleX", value=12.31),
            ParameterValue(id="MyNewParamName", weight=0.8, value=0.7),
        ],
    )

    assert json.loads(request.model_dump_json()) == {
        "faceFound": False,
        "mode": "set",
        "parameterValues": [
            {"id": "FaceAngleX", "value": 12.31, "weight": 1},
            {"id": "MyNewParamName", "value": 0.7, "weight": 0.8},
        ],
    }

    additive = InjectParameterDataRequest.model_validate(
        {
            "faceFound": True,
            "mode": "add",
            "parameterValues": [{"id": "FaceAngleX", "value": 1.0}],
        },
    )

    assert additive.face_found is True
    assert additive.mode == "add"
    assert json.loads(additive.model_dump_json()) == {
        "faceFound": True,
        "mode": "add",
        "parameterValues": [{"id": "FaceAngleX", "value": 1.0, "weight": 1.0}],
    }


def test_parameter_name_payloads_dump_the_wire_keys() -> None:
    """Creation/value/deletion payloads emit their aliases and default explanation."""
    assert json.loads(
        ParameterCreationRequest(
            parameter_name="x",
            min=0,
            max=1,
            default_value=0.5,
        ).model_dump_json(),
    ) == {
        "parameterName": "x",
        "explanation": "",
        "min": 0,
        "max": 1,
        "defaultValue": 0.5,
    }
    assert json.loads(
        ParameterValueRequest(name="MyCustomParamName1").model_dump_json()
    ) == {
        "name": "MyCustomParamName1",
    }
    assert json.loads(
        ParameterCreationResponse(parameter_name="MyNewParamName").model_dump_json(),
    ) == {"parameterName": "MyNewParamName"}
    assert json.loads(
        ParameterDeletionRequest(parameter_name="MyNewParamName").model_dump_json(),
    ) == {"parameterName": "MyNewParamName"}
    assert json.loads(
        ParameterDeletionResponse(parameter_name="MyNewParamName").model_dump_json(),
    ) == {"parameterName": "MyNewParamName"}

    assert json.loads(FaceFoundRequest().model_dump_json()) == {}
    assert json.loads(InputParameterListRequest().model_dump_json()) == {}
    assert json.loads(Live2DParameterListRequest().model_dump_json()) == {}
    assert json.loads(InjectParameterDataResponse().model_dump_json()) == {}
