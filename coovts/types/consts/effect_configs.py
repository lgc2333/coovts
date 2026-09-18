"""`Files/EffectConfigs.cs` of DenchiSoft/VTubeStudio@0f46ef4.

https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef4/Files/EffectConfigs.cs
"""

from enum import auto

from ...utils.enum import RawStrEnum


class EffectConfigs(RawStrEnum):
    """
    IDs of all post processing effect configs that can be set via the VTube Studio API.
    There are currently 258 configs.
    This file was automatically generated on Sunday, 10 March 2024 03:05
    """

    # region Effect: ColorGrading

    ColorGrading_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    ColorGrading_HueShift = auto()
    """
    type: Float, sets_active: False
    min: -180, max: 180
    default: 0
    explanation: Hue shift
    """

    ColorGrading_Saturation = auto()
    """
    type: Float, sets_active: False
    min: -100, max: 100
    default: 0
    explanation: Saturation
    """

    ColorGrading_Brightness = auto()
    """
    type: Float, sets_active: False
    min: -100, max: 100
    default: 0
    explanation: Brightness
    """

    ColorGrading_Contrast = auto()
    """
    type: Float, sets_active: False
    min: -100, max: 100
    default: 0
    explanation: Contrast
    """

    ColorGrading_ColorFilter = auto()
    """
    type: Color, sets_active: False
    default: FFFFFF alpha: False
    explanation: Color filter
    """

    ColorGrading_WhitebalanceTemperature = auto()
    """
    type: Float, sets_active: False
    min: -100, max: 100
    default: 0
    explanation: Whitebalance temperature
    """

    ColorGrading_WhitebalanceTint = auto()
    """
    type: Float, sets_active: False
    min: -100, max: 100
    default: 0
    explanation: Whitebalance tint
    """

    ColorGrading_Invert = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Invert color
    """

    # endregion

    # region Effect: WeatherEffects

    WeatherEffects_RainStrength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Rain strength
    """

    WeatherEffects_SnowStrength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Snow strength
    """

    WeatherEffects_RainInFront = auto()
    """
    type: Bool, sets_active: False
    default: True
    explanation: Rain  -  In front
    """

    WeatherEffects_SnowInFront = auto()
    """
    type: Bool, sets_active: False
    default: True
    explanation: Snow  -  In front
    """

    # endregion

    # region Effect: Bloom

    Bloom_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Bloom_ModelColorDarken = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Model color darken
    """

    Bloom_BackgroundColorDarken = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Background color darken
    """

    Bloom_MainThreshold = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.4
    explanation: Bloom threshold
    """

    Bloom_MainIntensity = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: Bloom intensity
    """

    Bloom_MainColorTint = auto()
    """
    type: Color, sets_active: False
    default: 62159B alpha: False
    explanation: Bloom tint color
    """

    Bloom_StreakThreshold = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.4
    explanation: Light streak threshold
    """

    Bloom_StreakIntensity = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: Light streak intensity
    """

    Bloom_StreakColorTint = auto()
    """
    type: Color, sets_active: False
    default: 870B8F alpha: False
    explanation: Light streak tint color
    """

    Bloom_StreakVertical = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: Light streak vertical
    """

    Bloom_MicIncreasesBloom = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Microphone effect - Microphone volume boosts strength
    """

    Bloom_Quality = auto()
    """
    type: Int, sets_active: False
    min: 0, max: 10
    default: 7
    explanation: Quality - Bloom quality
    """

    # endregion

    # region Effect: Backlight

    Backlight_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Backlight_BgBlurOverModel = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.4
    explanation: Blur BG overlay - For Model
    """

    Backlight_BgBlurOverBg = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Blur BG overlay - For Background
    """

    Backlight_DarkenModel = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.4
    explanation: Model color darken
    """

    Backlight_DarkenBg = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Background color darken
    """

    Backlight_StrengthNormal = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 1
    explanation: Backlight strength - Main
    """

    Backlight_StrengthDirectional = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.7
    explanation: Backlight strength - Directional
    """

    Backlight_BrightnessLimit = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.9
    explanation: Backlight brightness limit
    """

    Backlight_BacklightDirection = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 360
    default: 45
    explanation: Backlight direction
    """

    Backlight_BacklightBothDirections = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Backlight dir. both sides
    """

    Backlight_BacklightSoftness = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.8
    explanation: Backlight softness
    """

    Backlight_BacklightColorTint = auto()
    """
    type: Color, sets_active: False
    default: 5E3E96 alpha: False
    explanation: Backlight color tint
    """

    Backlight_BacklightColorFromBg = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.2
    explanation: Backlight col. from background
    """

    Backlight_OutlineSize = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Outline size
    """

    Backlight_OutlineColorMain = auto()
    """
    type: Color, sets_active: False
    default: DD103C alpha: True
    explanation: Outline color
    """

    Backlight_OutlineColorStripes = auto()
    """
    type: Color, sets_active: False
    default: 070001 alpha: True
    explanation: Outline stripe color
    """

    Backlight_OutlineStripeCount = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Outline stripe count
    """

    Backlight_OutlineStripeSpeed = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0.2
    explanation: Outline stripe speed
    """

    Backlight_OutlineStripeCurve = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Outline stripe curve
    """

    Backlight_ShadowMainColor = auto()
    """
    type: Color, sets_active: False
    default: 08090C alpha: True
    explanation: Shadow color
    """

    Backlight_ShadowOffsetX = auto()
    """
    type: Float, sets_active: False
    min: -10, max: 10
    default: 0
    explanation: Shadow offset X
    """

    Backlight_ShadowOffsetY = auto()
    """
    type: Float, sets_active: False
    min: -10, max: 10
    default: 0
    explanation: Shadow offset Y
    """

    # endregion

    # region Effect: CustomParticles

    CustomParticles_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off - Multiplier for opacity
    """

    CustomParticles_BaseMoveWithHead = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: -0.4
    explanation: [All] Move with head movement
    """

    CustomParticles_SparkleStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 1
    explanation: [Sparkle] Amount
    """

    CustomParticles_SparkleSize = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.4
    explanation: [Sparkle] Size
    """

    CustomParticles_SparkleColorA = auto()
    """
    type: Color, sets_active: False
    default: FF0000 alpha: True
    explanation: [Sparkle] Color A
    """

    CustomParticles_SparkleColorB = auto()
    """
    type: Color, sets_active: False
    default: E13457 alpha: True
    explanation: [Sparkle] Color B
    """

    CustomParticles_FloatyStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.4
    explanation: [Floaty particles] Amount
    """

    CustomParticles_FloatySize = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.2
    explanation: [Floaty particles] Size
    """

    CustomParticles_FloatyColorA = auto()
    """
    type: Color, sets_active: False
    default: 5F3ACE alpha: True
    explanation: [Floaty particles] Color A
    """

    CustomParticles_FloatyColorB = auto()
    """
    type: Color, sets_active: False
    default: F8899F alpha: True
    explanation: [Floaty particles] Color B
    """

    CustomParticles_CloudStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 1
    explanation: [Fog] Amount
    """

    CustomParticles_CloudSize = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: [Fog] Size
    """

    CustomParticles_CloudColorA = auto()
    """
    type: Color, sets_active: False
    default: 832525 alpha: True
    explanation: [Fog] Color A
    """

    CustomParticles_CloudColorB = auto()
    """
    type: Color, sets_active: False
    default: C83ACE alpha: True
    explanation: [Fog] Color B
    """

    CustomParticles_SphereStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.2
    explanation: [Light spheres] Amount
    """

    CustomParticles_SphereSize = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.8
    explanation: [Light spheres] Size
    """

    CustomParticles_SphereColorA = auto()
    """
    type: Color, sets_active: False
    default: 3037E9 alpha: True
    explanation: [Light spheres] Color A
    """

    CustomParticles_SphereColorB = auto()
    """
    type: Color, sets_active: False
    default: E810AC alpha: True
    explanation: [Light spheres] Color B
    """

    CustomParticles_HeartsStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: [Hearts] Amount
    """

    CustomParticles_HeartsSize = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: [Hearts] Size
    """

    CustomParticles_HeartsColorA = auto()
    """
    type: Color, sets_active: False
    default: FF1262 alpha: True
    explanation: [Hearts] Color A
    """

    CustomParticles_HeartsColorB = auto()
    """
    type: Color, sets_active: False
    default: FF0031 alpha: True
    explanation: [Hearts] Color B
    """

    CustomParticles_Custom1TextureFile = auto()
    """
    type: SceneItem, sets_active: False
    default:
    explanation: [Custom 1] Texture file
    """

    CustomParticles_Custom1ColorA = auto()
    """
    type: Color, sets_active: False
    default: FFFFFF alpha: True
    explanation: [Custom 1] Color A
    """

    CustomParticles_Custom1ColorB = auto()
    """
    type: Color, sets_active: False
    default: FFFFFF alpha: True
    explanation: [Custom 1] Color B
    """

    CustomParticles_Custom1MaterialTypeId = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: [Custom 1] Additive Particles - Will make particles shiny
    """

    CustomParticles_Custom1InBack = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: [Custom 1] Show behind model
    """

    CustomParticles_Custom1MoveWithHead = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: -0.5
    explanation: [Custom 1] Move with head movement
    """

    CustomParticles_Custom1Size = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: [Custom 1] Size
    """

    CustomParticles_Custom1Amount = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: [Custom 1] Amount
    """

    CustomParticles_Custom1FillToCenter = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: [Custom 1] Fill to center
    """

    CustomParticles_Custom1BaseRotation = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 180
    default: 15
    explanation: [Custom 1] Base Rotation
    """

    CustomParticles_Custom1RotationSpeed = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: [Custom 1] Rotation Speed
    """

    CustomParticles_Custom1MoveFasterMicVol = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: [Custom 1] Microphone effect - Microphone volume moves particles faster
    """

    CustomParticles_Custom2TextureFile = auto()
    """
    type: SceneItem, sets_active: False
    default:
    explanation: [Custom 2] Texture file
    """

    CustomParticles_Custom2ColorA = auto()
    """
    type: Color, sets_active: False
    default: FFFFFF alpha: True
    explanation: [Custom 2] Color A
    """

    CustomParticles_Custom2ColorB = auto()
    """
    type: Color, sets_active: False
    default: FFFFFF alpha: True
    explanation: [Custom 2] Color B
    """

    CustomParticles_Custom2MaterialTypeId = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: [Custom 2] Additive Particles - Will make particles shiny
    """

    CustomParticles_Custom2InBack = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: [Custom 2] Show behind model
    """

    CustomParticles_Custom2MoveWithHead = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: -0.5
    explanation: [Custom 2] Move with head movement
    """

    CustomParticles_Custom2Size = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: [Custom 2] Size
    """

    CustomParticles_Custom2Amount = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: [Custom 2] Amount
    """

    CustomParticles_Custom2FillToCenter = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: [Custom 2] Fill to center
    """

    CustomParticles_Custom2BaseRotation = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 180
    default: 15
    explanation: [Custom 2] Base Rotation
    """

    CustomParticles_Custom2RotationSpeed = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: [Custom 2] Rotation Speed
    """

    CustomParticles_Custom2MoveFasterMicVol = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: [Custom 2] Microphone effect - Microphone volume moves particles faster
    """

    # endregion

    # region Effect: BackgroundShift

    BackgroundShift_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    BackgroundShift_ZoomIn = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: Zoom in
    """

    BackgroundShift_MicZoomIn = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Microphone effect - Microphone volume zooms in
    """

    BackgroundShift_TrackingX = auto()
    """
    type: Float, sets_active: False
    min: -2, max: 2
    default: 0.5
    explanation: Move from X tracking
    """

    BackgroundShift_TrackingY = auto()
    """
    type: Float, sets_active: False
    min: -2, max: 2
    default: 0.5
    explanation: Move from Y tracking
    """

    BackgroundShift_TrackingSmoothing = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: Tracking movement smoothing
    """

    BackgroundShift_RandomMovementX = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 2
    default: 0.5
    explanation: Move X randomly
    """

    BackgroundShift_RandomMovementY = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 2
    default: 0.5
    explanation: Move Y randomly
    """

    BackgroundShift_RandomMovementRotation = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 2
    default: 0.15
    explanation: Rotate randomly
    """

    BackgroundShift_RandomMovementSpeed = auto()
    """
    type: Float, sets_active: False
    min: 0.01, max: 2
    default: 0.2
    explanation: Random movement speed
    """

    BackgroundShift_BlurMixBack = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Blur back visibility
    """

    BackgroundShift_BlurMainBack = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Blur back strength
    """

    BackgroundShift_BlurBrightnessBack = auto()
    """
    type: Float, sets_active: False
    min: -3, max: 3
    default: 1
    explanation: Blur back brightness
    """

    BackgroundShift_BlurMixFront = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Blur front visibility
    """

    BackgroundShift_BlurMainFront = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Blur front strength
    """

    BackgroundShift_BlurBrightnessFront = auto()
    """
    type: Float, sets_active: False
    min: -3, max: 3
    default: 1
    explanation: Blur front brightness
    """

    # endregion

    # region Effect: SimpleOverlay

    SimpleOverlay_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off - Multiplier for opacity
    """

    SimpleOverlay_TextureFile = auto()
    """
    type: SceneItem, sets_active: False
    default:
    explanation: Overlay image file
    """

    SimpleOverlay_ZoomIn = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.35
    explanation: Zoom in
    """

    SimpleOverlay_TrackingX = auto()
    """
    type: Float, sets_active: False
    min: -2, max: 2
    default: -0.5
    explanation: Move from X tracking
    """

    SimpleOverlay_TrackingY = auto()
    """
    type: Float, sets_active: False
    min: -2, max: 2
    default: -0.5
    explanation: Move from Y tracking
    """

    SimpleOverlay_TrackingSmoothing = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: Tracking movement smoothing
    """

    SimpleOverlay_RandomMovementX = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 2
    default: 0.4
    explanation: Move X randomly
    """

    SimpleOverlay_RandomMovementY = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 2
    default: 0.4
    explanation: Move Y randomly
    """

    SimpleOverlay_RandomMovementRotation = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 2
    default: 0.1
    explanation: Rotate randomly
    """

    SimpleOverlay_RandomMovementSpeed = auto()
    """
    type: Float, sets_active: False
    min: 0.01, max: 2
    default: 0.2
    explanation: Random movement speed
    """

    SimpleOverlay_TintColor = auto()
    """
    type: Color, sets_active: False
    default: FFFFFF alpha: True
    explanation: Tint color
    """

    # endregion

    # region Effect: Vignette

    Vignette_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Vignette_Smoothness = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.9
    explanation: Smoothness
    """

    Vignette_Color = auto()
    """
    type: Color, sets_active: False
    default: 000000 alpha: True
    explanation: Color
    """

    Vignette_CenterX = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0
    explanation: Center X
    """

    Vignette_CenterY = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0
    explanation: Center Y
    """

    Vignette_Roundness = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 1
    explanation: Roundness
    """

    Vignette_Circular = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: Even side length
    """

    # endregion

    # region Effect: ChromaticAberration

    ChromaticAberration_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    ChromaticAberration_BlurEdges = auto()
    """
    type: Bool, sets_active: False
    default: True
    explanation: Blur edges
    """

    # endregion

    # region Effect: OldFilm

    OldFilm_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    OldFilm_FilmFps = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 30
    default: 15
    explanation: FPS limit
    """

    OldFilm_FilmContrast = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 5
    default: 1
    explanation: Contrast
    """

    OldFilm_FilmBurn = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 4
    default: 0.9
    explanation: Film burn
    """

    OldFilm_FilmSceneCut = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 2
    default: 0.9
    explanation: Film dirt size
    """

    # endregion

    # region Effect: Lowfps

    Lowfps_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Lowfps_FpsLimit = auto()
    """
    type: Int, sets_active: False
    min: 1, max: 60
    default: 15
    explanation: FPS limit
    """

    Lowfps_FpsRandom = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: FPS jitter strength
    """

    Lowfps_ScreenTearing = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Screen tearing
    """

    # endregion

    # region Effect: Datamosh

    Datamosh_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Datamosh_Size = auto()
    """
    type: Int, sets_active: False
    min: 1, max: 200
    default: 16
    explanation: Size
    """

    Datamosh_ResetAfterSecs = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 60
    default: 3
    explanation: Reset after seconds
    """

    Datamosh_Entropy = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Entropy
    """

    Datamosh_NoiseContrast = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Noise Contrast
    """

    Datamosh_VelocityScale = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Velocity Scale
    """

    Datamosh_Diffusion = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Diffusion
    """

    # endregion

    # region Effect: LineScanner

    LineScanner_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    LineScanner_Direction = auto()
    """
    type: Int, sets_active: False
    min: 1, max: 4
    default: 1
    explanation: Direction
    """

    LineScanner_ScanStepTotal = auto()
    """
    type: Int, sets_active: False
    min: 16, max: 2048
    default: 1024
    explanation: Total scan steps
    """

    LineScanner_ScanStepSize = auto()
    """
    type: Int, sets_active: False
    min: 1, max: 16
    default: 4
    explanation: Scan step size
    """

    LineScanner_ScanLineColor = auto()
    """
    type: Color, sets_active: False
    default: 0C0001 alpha: True
    explanation: Scan line color
    """

    LineScanner_ScanLineSize = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.15
    explanation: Scan line size
    """

    LineScanner_ScanLineWaitBetweenScansSecs = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 30
    default: 3
    explanation: Wait between scans - Reset after seconds
    """

    # endregion

    # region Effect: ParticleShower

    ParticleShower_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off - Multiplier for opacity
    """

    ParticleShower_TextureFile1 = auto()
    """
    type: SceneItem, sets_active: False
    default:
    explanation: [Custom 1] Texture file
    """

    ParticleShower_TextureFile2 = auto()
    """
    type: SceneItem, sets_active: False
    default:
    explanation: [Custom 2] Texture file
    """

    ParticleShower_TextureFile3 = auto()
    """
    type: SceneItem, sets_active: False
    default:
    explanation: [Custom 3] Texture file
    """

    ParticleShower_Speed1 = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.4
    explanation: [Custom 1] Fall speed
    """

    ParticleShower_Speed2 = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.4
    explanation: [Custom 2] Fall speed
    """

    ParticleShower_Speed3 = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.4
    explanation: [Custom 3] Fall speed
    """

    ParticleShower_InBack1 = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: [Custom 1] Show behind model
    """

    ParticleShower_InBack2 = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: [Custom 2] Show behind model
    """

    ParticleShower_InBack3 = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: [Custom 3] Show behind model
    """

    # endregion

    # region Effect: AnalogGlitch

    AnalogGlitch_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    AnalogGlitch_ScanlineJitter = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Scanline Jitter
    """

    AnalogGlitch_VerticalJump = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Vertical jump
    """

    AnalogGlitch_HorizontalShake = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Horizontal shake
    """

    AnalogGlitch_ColorDrift = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Color Drift
    """

    AnalogGlitch_MicEffect = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Microphone effect - Microphone volume boosts strength
    """

    # endregion

    # region Effect: DigitalGlitch

    DigitalGlitch_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Strength - Strength of the effect
    """

    DigitalGlitch_Colorshift = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Color Shift - How much to shift the color for this effect?
    """

    DigitalGlitch_MicEffect = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Microphone effect - Microphone volume boosts strength
    """

    # endregion

    # region Effect: Letterbox

    Letterbox_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Letterbox_ProgressY = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.3
    explanation: Letterbox Y
    """

    Letterbox_ProgressX = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Letterbox X
    """

    Letterbox_Zoom = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Zoom in
    """

    Letterbox_Color = auto()
    """
    type: Color, sets_active: False
    default: 000000 alpha: True
    explanation: Tint color
    """

    # endregion

    # region Effect: FoggyWindow

    FoggyWindow_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    FoggyWindow_FogStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Fog amount
    """

    FoggyWindow_FogTint = auto()
    """
    type: Color, sets_active: False
    default: 3AABEE alpha: True
    explanation: Fog color tint
    """

    FoggyWindow_FogBoost = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.6
    explanation: Fog brightness boost
    """

    FoggyWindow_RaindropVisibility = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.8
    explanation: Raindrop visibility
    """

    FoggyWindow_RaindropSpeed = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0.2
    explanation: Raindrop speed
    """

    FoggyWindow_RaindropSize = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.8
    explanation: Raindrop size
    """

    FoggyWindow_FogWipeSize = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.2
    explanation: Fog wipe size
    """

    FoggyWindow_FogWipeLifetimeSeconds = auto()
    """
    type: Float, sets_active: False
    min: 2, max: 30
    default: 5
    explanation: Fog wipe seconds
    """

    FoggyWindow_FogLifetimeInfinite = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: Wiped fog stays wiped
    """

    # endregion

    # region Effect: Speedlines

    Speedlines_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Speedlines_XCenter = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0
    explanation: X center
    """

    Speedlines_YCenter = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0
    explanation: Y center
    """

    Speedlines_ColorA = auto()
    """
    type: Color, sets_active: False
    default: EDEBF8 alpha: True
    explanation: Speedlines color A
    """

    Speedlines_ColorB = auto()
    """
    type: Color, sets_active: False
    default: 110101 alpha: True
    explanation: Speedlines color B
    """

    Speedlines_MicEffect = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Microphone effect - Microphone volume boosts strength
    """

    # endregion

    # region Effect: Pixelation

    Pixelation_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Pixelation_Resolution = auto()
    """
    type: Int, sets_active: False
    min: 10, max: 600
    default: 128
    explanation: Resolution
    """

    Pixelation_Colorize = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 1
    explanation: Color filter
    """

    Pixelation_C1 = auto()
    """
    type: Color, sets_active: False
    default: 241A1A alpha: True
    explanation: Color  1
    """

    Pixelation_C2 = auto()
    """
    type: Color, sets_active: False
    default: 3F2C2C alpha: True
    explanation: Color  2
    """

    Pixelation_C3 = auto()
    """
    type: Color, sets_active: False
    default: 7D4C4C alpha: True
    explanation: Color  3
    """

    Pixelation_C4 = auto()
    """
    type: Color, sets_active: False
    default: 9C6161 alpha: True
    explanation: Color  4
    """

    Pixelation_C5 = auto()
    """
    type: Color, sets_active: False
    default: B08282 alpha: True
    explanation: Color  5
    """

    Pixelation_C6 = auto()
    """
    type: Color, sets_active: False
    default: E5BDBD alpha: True
    explanation: Color  6
    """

    Pixelation_C7 = auto()
    """
    type: Color, sets_active: False
    default: E9D5D5 alpha: True
    explanation: Color  7
    """

    Pixelation_C8 = auto()
    """
    type: Color, sets_active: False
    default: FEFEFE alpha: True
    explanation: Color  8
    """

    Pixelation_Fry = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Fry
    """

    # endregion

    # region Effect: LensDistortion

    LensDistortion_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    LensDistortion_LensStrength = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0
    explanation: Lens strength
    """

    LensDistortion_ZoomIn = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0
    explanation: Zoom in
    """

    LensDistortion_Squish = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0
    explanation: Squish
    """

    # endregion

    # region Effect: WaveDistortion

    WaveDistortion_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    WaveDistortion_HeatStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.2
    explanation: Heat wave strength
    """

    WaveDistortion_RaindropStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.4
    explanation: Raindrop strength
    """

    WaveDistortion_RaindropFrequency = auto()
    """
    type: Float, sets_active: False
    min: 1, max: 5
    default: 1.6
    explanation: Raindrop interval (sec)
    """

    WaveDistortion_ZoomIn = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Zoom in
    """

    WaveDistortion_RotationBase = auto()
    """
    type: Float, sets_active: False
    min: -180, max: 180
    default: 0
    explanation: Base Rotation
    """

    WaveDistortion_WaveXStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.1
    explanation: Wave strength X
    """

    WaveDistortion_WaveXScroll = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0.5
    explanation: Wave scroll X
    """

    WaveDistortion_WaveXFrequency = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Wave frequency X
    """

    WaveDistortion_WaveYStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.1
    explanation: Wave strength Y
    """

    WaveDistortion_WaveYScroll = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0.5
    explanation: Wave scroll Y
    """

    WaveDistortion_WaveYFrequency = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Wave frequency Y
    """

    # endregion

    # region Effect: BlurEffects

    BlurEffects_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    BlurEffects_BasicBlurVisibility = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Blur visibility
    """

    BlurEffects_BasicBlurStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Blur strength
    """

    BlurEffects_PixelationBlur = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Pixelation
    """

    BlurEffects_MotionBlur = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Motion blur
    """

    # endregion

    # region Effect: Grain

    Grain_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Grain_Size = auto()
    """
    type: Float, sets_active: False
    min: 0.1, max: 3
    default: 1.7
    explanation: Size
    """

    Grain_Luminosity = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Luminosity
    """

    Grain_Colored = auto()
    """
    type: Bool, sets_active: False
    default: False
    explanation: Colored
    """

    # endregion

    # region Effect: Vhs

    Vhs_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Vhs_Fisheye = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 1
    explanation: Monitor fisheye
    """

    Vhs_Vignette = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.2
    explanation: Vignette
    """

    Vhs_ScreenBleed = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 5
    default: 1
    explanation: Sideways blur
    """

    Vhs_NoiseGrain = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Grain noise
    """

    Vhs_NoiseLines = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.5
    explanation: Line noise
    """

    Vhs_TwitchVertical = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 5
    default: 1
    explanation: Horizontal twitch (up/down)
    """

    Vhs_TwitchHorizontal = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 5
    default: 1
    explanation: Vertical twitch (left/right)
    """

    Vhs_Interlacing = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.1
    explanation: Interlacing
    """

    Vhs_GammaCorrection = auto()
    """
    type: Float, sets_active: False
    min: -1, max: 1
    default: 0
    explanation: Gamma correction
    """

    Vhs_PaleColor = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.2
    explanation: Pale color
    """

    Vhs_AfterImageAmount = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Afterimage strength
    """

    Vhs_AfterImageColor = auto()
    """
    type: Color, sets_active: False
    default: FF6202 alpha: False
    explanation: Afterimage color
    """

    # endregion

    # region Effect: Outline

    Outline_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Outline_Sharpen = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Sharpen image
    """

    Outline_Visibility = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Outline visibility
    """

    Outline_Color = auto()
    """
    type: Color, sets_active: False
    default: 000000 alpha: True
    explanation: Outline color
    """

    Outline_Threshold = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.9
    explanation: Outline threshold
    """

    Outline_Contrast = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0.2
    explanation: Outline contrast
    """

    # endregion

    # region Effect: Posterize

    Posterize_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    # endregion

    # region Effect: Ascii

    Ascii_Strength = auto()
    """
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Effect on/off
    """

    Ascii_Size = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 10
    default: 3
    explanation: Size
    """

    Ascii_CharacterVisibility = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 1
    explanation: Character visibility
    """

    Ascii_CharacterColorStrength = auto()
    """
    type: Float, sets_active: False
    min: 0, max: 1
    default: 0
    explanation: Color overlay strength
    """

    Ascii_CharacterColor = auto()
    """
    type: Color, sets_active: False
    default: 1EB916 alpha: False
    explanation: Color overlay
    """

    # endregion

    # region Effect: ModelGlitch

    ModelGlitch_StrengthExplode = auto()
    """
    RESTRICTED EXPERIMENTAL EFFECT
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Explode model parts
    """

    ModelGlitch_StrengthWiggle = auto()
    """
    RESTRICTED EXPERIMENTAL EFFECT
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Wiggle model parts
    """

    ModelGlitch_StrengthPulse = auto()
    """
    RESTRICTED EXPERIMENTAL EFFECT
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Pulsate model parts
    """

    ModelGlitch_StrengthLiquify = auto()
    """
    RESTRICTED EXPERIMENTAL EFFECT
    type: Float, sets_active: True
    min: 0, max: 1
    default: 0
    explanation: Liquify model parts
    """

    # endregion
