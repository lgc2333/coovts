"""Wire-shape tests for the item models of `coovts.types.api`."""

import json

from coovts.types.api import (
    ItemListRequest,
    ItemListResponse,
    ItemLoadRequest,
    ItemMoveInfo,
    ItemMoveRequest,
    ItemPinInfo,
    ItemPinRequest,
    ItemSortRequest,
    ItemUnloadRequest,
)


def test_documented_list_response_round_trips_through_wire_keys() -> None:
    """The example list response decodes and re-emits the documented wire keys."""
    response = ItemListResponse.model_validate(
        {
            "itemsInSceneCount": 1,
            "totalItemsAllowedCount": 60,
            "canLoadItemsRightNow": True,
            "itemInstancesInScene": [
                {
                    "fileName": "Ribbon (@denchisoft)",
                    "instanceID": "18de53dc47154b00afdd382a6ebd2194",
                    "order": 1,
                    "type": "Live2D",
                    "censored": False,
                    "flipped": False,
                    "locked": False,
                    "smoothing": 0.0,
                    "framerate": 0.0,
                    "frameCount": -1,
                    "currentFrame": -1,
                    "pinnedToModel": True,
                    "pinnedModelID": "47c71722c5304a039b0570b60a189875",
                    "pinnedArtMeshID": "D_FACE_00",
                    "groupName": "",
                    "sceneName": "",
                    "fromWorkshop": False,
                },
            ],
            "availableItemFiles": [
                {
                    "fileName": "Ribbon (@denchisoft)",
                    "type": "Live2D",
                    "loadedCount": 1,
                },
            ],
        },
    )

    assert response.items_in_scene_count == 1
    assert response.total_items_allowed_count == 60
    assert response.can_load_items_right_now is True
    assert response.available_spots == []
    instance = response.item_instances_in_scene[0]
    assert instance.file_name == "Ribbon (@denchisoft)"
    assert instance.instance_id == "18de53dc47154b00afdd382a6ebd2194"
    assert instance.pinned_to_model is True
    assert instance.pinned_model_id == "47c71722c5304a039b0570b60a189875"
    assert instance.pinned_art_mesh_id == "D_FACE_00"
    assert response.available_item_files[0].loaded_count == 1

    assert json.loads(response.model_dump_json()) == {
        "itemsInSceneCount": 1,
        "totalItemsAllowedCount": 60,
        "canLoadItemsRightNow": True,
        "availableSpots": [],
        "itemInstancesInScene": [
            {
                "fileName": "Ribbon (@denchisoft)",
                "instanceID": "18de53dc47154b00afdd382a6ebd2194",
                "order": 1,
                "type": "Live2D",
                "censored": False,
                "flipped": False,
                "locked": False,
                "smoothing": 0.0,
                "framerate": 0.0,
                "frameCount": -1,
                "currentFrame": -1,
                "pinnedToModel": True,
                "pinnedModelID": "47c71722c5304a039b0570b60a189875",
                "pinnedArtMeshID": "D_FACE_00",
                "groupName": "",
                "sceneName": "",
                "fromWorkshop": False,
            },
        ],
        "availableItemFiles": [
            {
                "fileName": "Ribbon (@denchisoft)",
                "type": "Live2D",
                "loadedCount": 1,
            },
        ],
    }


def test_list_request_defaults_emit_the_wire_shape() -> None:
    """A bare list request asks for nothing, with the instance ID filter under its alias."""
    assert json.loads(ItemListRequest().model_dump_json()) == {
        "includeAvailableSpots": False,
        "includeItemInstancesInScene": False,
        "includeAvailableItemFiles": False,
        "onlyItemsWithFileName": None,
        "onlyItemsWithInstanceID": None,
    }


def test_load_request_required_fields_emit_the_wire_shape() -> None:
    """A load request only needs the position and file, everything else keeps its default."""
    assert json.loads(
        ItemLoadRequest(
            file_name="some_item_name.jpg",
            position_x=0,
            position_y=0.5,
            size=0.33,
            rotation=90,
            order=4,
        ).model_dump_json(),
    ) == {
        "fileName": "some_item_name.jpg",
        "positionX": 0.0,
        "positionY": 0.5,
        "size": 0.33,
        "rotation": 90.0,
        "fadeTime": 0.5,
        "order": 4,
        "failIfOrderTaken": False,
        "smoothing": 0.0,
        "censored": False,
        "flipped": False,
        "locked": False,
        "unloadWhenPluginDisconnects": True,
        "customDataBase64": "",
        "customDataAskUserFirst": True,
        "customDataSkipAskingUserIfWhitelisted": True,
        "customDataAskTimer": -1.0,
    }


def test_pin_request_emits_the_wire_shape() -> None:
    """A pin request nests the pin info under its aliased vertex ID fields."""
    request = ItemPinRequest(
        pin=True,
        item_instance_id="4a241269394f463ca16b8b21aa636568",
        angle_relative_to="RelativeToModel",
        size_relative_to="RelativeToWorld",
        vertex_pin_type="Provided",
        pin_info=ItemPinInfo(
            model_id="d87b771d2902473bbaa0226d03ef4754",
            art_mesh_id="hair_right_4",
            angle=23.938,
            size=0.33,
            vertex_id1=17,
            vertex_id2=9,
            vertex_id3=55,
            vertex_weight1=0.25,
            vertex_weight2=0.5,
            vertex_weight3=0.25,
        ),
    )

    assert request.pin_info.vertex_id1 == 17
    assert request.pin_info.vertex_id2 == 9
    assert request.pin_info.vertex_id3 == 55
    assert json.loads(request.model_dump_json()) == {
        "pin": True,
        "itemInstanceID": "4a241269394f463ca16b8b21aa636568",
        "angleRelativeTo": "RelativeToModel",
        "sizeRelativeTo": "RelativeToWorld",
        "vertexPinType": "Provided",
        "pinInfo": {
            "modelID": "d87b771d2902473bbaa0226d03ef4754",
            "artMeshID": "hair_right_4",
            "angle": 23.938,
            "size": 0.33,
            "vertexID1": 17,
            "vertexID2": 9,
            "vertexID3": 55,
            "vertexWeight1": 0.25,
            "vertexWeight2": 0.5,
            "vertexWeight3": 0.25,
        },
    }


def test_unload_and_sort_requests_emit_the_wire_shape() -> None:
    """Unloading targets instance IDs, sorting targets the front-layer insertion point."""
    assert json.loads(
        ItemUnloadRequest(
            instance_ids=["SomeInstanceIdOfItemToUnload"],
            file_names=["UnloadAllItemInstancesWithThisFileName"],
        ).model_dump_json(),
    ) == {
        "unloadAllInScene": False,
        "unloadAllLoadedByThisPlugin": False,
        "allowUnloadingItemsLoadedByUserOrOtherPlugins": True,
        "instanceIDs": ["SomeInstanceIdOfItemToUnload"],
        "fileNames": ["UnloadAllItemInstancesWithThisFileName"],
    }
    assert json.loads(
        ItemSortRequest(
            item_instance_id="b616cf51fe3444729ccbf6ee54a14d1a",
            front_on=True,
            back_on=True,
            set_split_point="UseArtMeshID",
            set_front_order="UseArtMeshID",
            set_back_order="UseSpecialID",
            split_at="MyArtMeshIDInItemModel91",
            within_model_order_front="MyArtMeshIDInMainModel73",
            within_model_order_back="FullyInBack",
        ).model_dump_json(),
    ) == {
        "itemInstanceID": "b616cf51fe3444729ccbf6ee54a14d1a",
        "frontOn": True,
        "backOn": True,
        "setSplitPoint": "UseArtMeshID",
        "setFrontOrder": "UseArtMeshID",
        "setBackOrder": "UseSpecialID",
        "splitAt": "MyArtMeshIDInItemModel91",
        "withinModelOrderFront": "MyArtMeshIDInMainModel73",
        "withinModelOrderBack": "FullyInBack",
    }


def test_move_request_emits_the_wire_shape() -> None:
    """The move request carries one wire entry per item, fade mode included."""
    request = ItemMoveRequest(
        items_to_move=[
            ItemMoveInfo(
                item_instance_id="ItemInstanceId",
                time_in_seconds=1,
                fade_mode="easeOut",
                position_x=0.2,
                position_y=-0.8,
                size=0.6,
                rotation=180,
                order=-1000,
                set_flip=True,
                flip=False,
                user_can_stop=True,
            ),
        ],
    )

    assert request.items_to_move[0].item_instance_id == "ItemInstanceId"
    assert json.loads(request.model_dump_json()) == {
        "itemsToMove": [
            {
                "itemInstanceID": "ItemInstanceId",
                "timeInSeconds": 1.0,
                "fadeMode": "easeOut",
                "positionX": 0.2,
                "positionY": -0.8,
                "size": 0.6,
                "rotation": 180.0,
                "order": -1000,
                "setFlip": True,
                "flip": False,
                "userCanStop": True,
            },
        ],
    }
