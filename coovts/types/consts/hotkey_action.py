"""`Files/HotkeyAction.cs` of DenchiSoft/VTubeStudio@0f46ef4.

https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef4/Files/HotkeyAction.cs
"""

from enum import auto

from ...utils.enum import RawStrEnum


class HotkeyAction(RawStrEnum):
    """Enum for the actions that can be triggered by hotkeys."""

    Unset = auto()
    """Unset."""

    TriggerAnimation = auto()
    """Play an animation."""

    ChangeIdleAnimation = auto()
    """Change the idle animation."""

    ToggleExpression = auto()
    """Toggle an expression."""

    RemoveAllExpressions = auto()
    """Remove all expressions."""

    MoveModel = auto()
    """Moves the model to the target position."""

    ChangeBackground = auto()
    """Change the current background."""

    ReloadMicrophone = auto()
    """Reload the current microphone."""

    ReloadTextures = auto()
    """Reload the model texture."""

    CalibrateCam = auto()
    """Calibrate Camera."""

    ChangeVTSModel = auto()
    """Change VTS Model."""

    TakeScreenshot = auto()
    """Take a screenshot with the previous settings."""

    ScreenColorOverlay = auto()
    """Activates/Deactivates model screen color overlay."""

    RemoveAllItems = auto()
    """Removes all items from the scene."""

    ToggleItemScene = auto()
    """Loads an item scene."""

    DownloadRandomWorkshopItem = auto()
    """
    Downloads a random item from the Steam Workshop and attempts to load it into the
    scene.
    """

    ExecuteItemAction = auto()
    """Executes a hotkey in the given Live2D item."""

    ArtMeshColorPreset = auto()
    """Loads the recorded ArtMesh multiply/screen color preset."""

    ToggleTracker = auto()
    """Toggles the tracking on/off. Can be webcam or USB/WiFi connected phone."""

    ToggleTwitchFeature = auto()
    """Toggles a Twitch feature (for example Emote Dropper) on/off."""

    LoadEffectPreset = auto()
    """Loads post processing effect preset."""

    ToggleLive2DEditorAPI = auto()
    """Toggles Live2D Editor API parameter sync on/off."""

    WebItemAction = auto()
    """Triggers Web Item action."""

    ToggleModelSound = auto()
    """Toggles model/item SFX volume on/off."""
