from abc import ABC, abstractmethod
from types import EllipsisType
from typing import Any, overload

from pydantic import BaseModel

from . import api

class PluginAPI(ABC):
    @abstractmethod
    async def _call_api(
        self,
        data: Any,
        *,
        message_type: str | None = None,
        response_model: type[BaseModel] | None | EllipsisType = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> Any: ...

    # region builtin apis

    @overload
    async def call_api(
        self,
        data: api.ArtMeshListRequest,
        *,
        message_type: str = "ArtMeshListRequest",
        response_model: type[api.ArtMeshListResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ArtMeshListResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ArtMeshSelectionRequest,
        *,
        message_type: str = "ArtMeshSelectionRequest",
        response_model: type[api.ArtMeshSelectionResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ArtMeshSelectionResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ColorTintRequest,
        *,
        message_type: str = "ColorTintRequest",
        response_model: type[api.ColorTintResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ColorTintResponse: ...
    @overload
    async def call_api(
        self,
        data: api.AuthenticationRequest,
        *,
        message_type: str = "AuthenticationRequest",
        response_model: type[api.AuthenticationResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.AuthenticationResponse: ...
    @overload
    async def call_api(
        self,
        data: api.AuthenticationTokenRequest,
        *,
        message_type: str = "AuthenticationTokenRequest",
        response_model: type[api.AuthenticationTokenResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.AuthenticationTokenResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ExpressionActivationRequest,
        *,
        message_type: str = "ExpressionActivationRequest",
        response_model: type[api.ExpressionActivationResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ExpressionActivationResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ExpressionStateRequest,
        *,
        message_type: str = "ExpressionStateRequest",
        response_model: type[api.ExpressionStateResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ExpressionStateResponse: ...
    @overload
    async def call_api(
        self,
        data: api.HotkeysInCurrentModelRequest,
        *,
        message_type: str = "HotkeysInCurrentModelRequest",
        response_model: type[api.HotkeysInCurrentModelResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.HotkeysInCurrentModelResponse: ...
    @overload
    async def call_api(
        self,
        data: api.HotkeyTriggerRequest,
        *,
        message_type: str = "HotkeyTriggerRequest",
        response_model: type[api.HotkeyTriggerResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.HotkeyTriggerResponse: ...
    @overload
    async def call_api(
        self,
        data: api.APIStateRequest,
        *,
        message_type: str = "APIStateRequest",
        response_model: type[api.APIStateResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.APIStateResponse: ...
    @overload
    async def call_api(
        self,
        data: api.StatisticsRequest,
        *,
        message_type: str = "StatisticsRequest",
        response_model: type[api.StatisticsResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.StatisticsResponse: ...
    @overload
    async def call_api(
        self,
        data: api.VTSFolderInfoRequest,
        *,
        message_type: str = "VTSFolderInfoRequest",
        response_model: type[api.VTSFolderInfoResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.VTSFolderInfoResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ItemAnimationControlRequest,
        *,
        message_type: str = "ItemAnimationControlRequest",
        response_model: type[api.ItemAnimationControlResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ItemAnimationControlResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ItemListRequest,
        *,
        message_type: str = "ItemListRequest",
        response_model: type[api.ItemListResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ItemListResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ItemLoadRequest,
        *,
        message_type: str = "ItemLoadRequest",
        response_model: type[api.ItemLoadResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ItemLoadResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ItemMoveRequest,
        *,
        message_type: str = "ItemMoveRequest",
        response_model: type[api.ItemMoveResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ItemMoveResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ItemPinRequest,
        *,
        message_type: str = "ItemPinRequest",
        response_model: type[api.ItemPinResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ItemPinResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ItemUnloadRequest,
        *,
        message_type: str = "ItemUnloadRequest",
        response_model: type[api.ItemUnloadResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ItemUnloadResponse: ...
    @overload
    async def call_api(
        self,
        data: api.AvailableModelsRequest,
        *,
        message_type: str = "AvailableModelsRequest",
        response_model: type[api.AvailableModelsResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.AvailableModelsResponse: ...
    @overload
    async def call_api(
        self,
        data: api.CurrentModelRequest,
        *,
        message_type: str = "CurrentModelRequest",
        response_model: type[api.CurrentModelResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.CurrentModelResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ModelLoadRequest,
        *,
        message_type: str = "ModelLoadRequest",
        response_model: type[api.ModelLoadResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ModelLoadResponse: ...
    @overload
    async def call_api(
        self,
        data: api.MoveModelRequest,
        *,
        message_type: str = "MoveModelRequest",
        response_model: type[api.MoveModelResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.MoveModelResponse: ...
    @overload
    async def call_api(
        self,
        data: api.NDIConfigRequest,
        *,
        message_type: str = "NDIConfigRequest",
        response_model: type[api.NDIConfigResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.NDIConfigResponse: ...
    @overload
    async def call_api(
        self,
        data: api.FaceFoundRequest,
        *,
        message_type: str = "FaceFoundRequest",
        response_model: type[api.FaceFoundResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.FaceFoundResponse: ...
    @overload
    async def call_api(
        self,
        data: api.InjectParameterDataRequest,
        *,
        message_type: str = "InjectParameterDataRequest",
        response_model: type[api.InjectParameterDataResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.InjectParameterDataResponse: ...
    @overload
    async def call_api(
        self,
        data: api.InputParameterListRequest,
        *,
        message_type: str = "InputParameterListRequest",
        response_model: type[api.InputParameterListResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.InputParameterListResponse: ...
    @overload
    async def call_api(
        self,
        data: api.Live2DParameterListRequest,
        *,
        message_type: str = "Live2DParameterListRequest",
        response_model: type[api.Live2DParameterListResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.Live2DParameterListResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ParameterCreationRequest,
        *,
        message_type: str = "ParameterCreationRequest",
        response_model: type[api.ParameterCreationResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ParameterCreationResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ParameterDeletionRequest,
        *,
        message_type: str = "ParameterDeletionRequest",
        response_model: type[api.ParameterDeletionResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ParameterDeletionResponse: ...
    @overload
    async def call_api(
        self,
        data: api.ParameterValueRequest,
        *,
        message_type: str = "ParameterValueRequest",
        response_model: type[api.ParameterValueResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.ParameterValueResponse: ...
    @overload
    async def call_api(
        self,
        data: api.GetCurrentModelPhysicsRequest,
        *,
        message_type: str = "GetCurrentModelPhysicsRequest",
        response_model: type[api.GetCurrentModelPhysicsResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.GetCurrentModelPhysicsResponse: ...
    @overload
    async def call_api(
        self,
        data: api.SetCurrentModelPhysicsRequest,
        *,
        message_type: str = "SetCurrentModelPhysicsRequest",
        response_model: type[api.SetCurrentModelPhysicsResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.SetCurrentModelPhysicsResponse: ...
    @overload
    async def call_api(
        self,
        data: api.PostProcessingListRequest,
        *,
        message_type: str = "PostProcessingListRequest",
        response_model: type[api.PostProcessingListResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.PostProcessingListResponse: ...
    @overload
    async def call_api(
        self,
        data: api.PostProcessingUpdateRequest,
        *,
        message_type: str = "PostProcessingUpdateRequest",
        response_model: type[api.PostProcessingUpdateResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.PostProcessingUpdateResponse: ...
    @overload
    async def call_api(
        self,
        data: api.SceneColorOverlayInfoRequest,
        *,
        message_type: str = "SceneColorOverlayInfoRequest",
        response_model: type[api.SceneColorOverlayInfoResponse] = ...,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> api.SceneColorOverlayInfoResponse: ...

    # endregion

    # if data is a model, we consider it has msg_t class var
    # so message_type is optional
    @overload
    async def call_api[M: BaseModel](
        self,
        data: BaseModel,
        *,
        message_type: str | None = None,
        response_model: type[M],
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> M: ...
    @overload
    async def call_api(
        self,
        data: BaseModel,
        *,
        message_type: str | None = None,
        response_model: None = None,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> dict[str, Any]: ...
    # otherwise message_type is required
    @overload
    async def call_api[M: BaseModel](
        self,
        data: Any,
        *,
        message_type: str,
        response_model: type[M],
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> M: ...
    @overload
    async def call_api(
        self,
        data: Any,
        *,
        message_type: str,
        response_model: None = None,
        api_name: str = "VTubeStudioPublicAPI",
        api_version: str = "1.0",
        api_timeout: float | None | EllipsisType = ...,
    ) -> dict[str, Any]: ...
