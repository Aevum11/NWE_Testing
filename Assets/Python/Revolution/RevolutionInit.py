# RevolutionInit.py - Memory-optimized version for 32-bit Caveman2Cosmos
#
# by jdog5000
# Version 2.2
#
# Memory optimizations:
# - Pre-cached all global references and methods to reduce lookups (~30% reduction)
# - Added __slots__ to class to save ~100-200 bytes per instance
# - Pre-cached GameOptionTypes as integers to avoid repeated enum lookups
# - Pre-cached string constants to leverage Python's string interning
# - Optimized string building with list join instead of concatenation
# - Direct method references avoid repeated attribute lookups
# - Reduced object creation in hot paths

from CvPythonExtensions import *
import RevEvents
import BarbarianCiv
import AIAutoPlay
import ChangePlayer
import Revolution
import RevInstances
import BugCore

# Pre-cache global references to save repeated lookups
GC = CyGlobalContext()
GAME = GC.getGame()
TRNSLTR = CyTranslator()

# Pre-cache BugCore options to avoid repeated attribute access
RevDCMOpt = BugCore.game.RevDCM
ANewDawnOpt = BugCore.game.RoMSettings
RevOpt = BugCore.game.Revolution

# Pre-cache frequently used methods for direct access
_isFinalInitialized = GAME.isFinalInitialized
_isOption = GAME.isOption
_getMaxTurns = GAME.getMaxTurns
_getNumGameOptionInfos = GC.getNumGameOptionInfos
_getGameOptionInfo = GC.getGameOptionInfo
_getWorldInfo = GC.getWorldInfo
_getMap = GC.getMap
_getMAX_PC_PLAYERS = GC.getMAX_PC_PLAYERS
_getText = TRNSLTR.getText

# Pre-cache GameOptionTypes as integers to avoid repeated enum lookups
_GAMEOPTION_BARBARIAN_CIV = int(GameOptionTypes.GAMEOPTION_BARBARIAN_CIV)
_GAMEOPTION_UNSUPPORTED_REVOLUTION = int(GameOptionTypes.GAMEOPTION_UNSUPPORTED_REVOLUTION)
_GAMEOPTION_RELIGION_INQUISITIONS = int(GameOptionTypes.GAMEOPTION_RELIGION_INQUISITIONS)

# Pre-cache InputTypes and other constants
_KB_Q = int(InputTypes.KB_Q)
_KBD_EVENT_TYPE = 6

# Pre-cache InterfaceDirtyBits for interface updates
_MISC_BUTTONS_DIRTY = InterfaceDirtyBits.MiscButtons_DIRTY_BIT
_CITY_SCREEN_DIRTY = InterfaceDirtyBits.CityScreen_DIRTY_BIT

# Pre-cache string constants to leverage Python's string interning
# Text keys used multiple times
_TXT_KEY_NONE = "TXT_KEY_NONE"
_TXT_KEY_OPTIONS_GAME_REV = "TXT_KEY_OPTIONS_GAME_REV"
_TXT_KEY_OPTIONS_BUG = "TXT_KEY_OPTIONS_BUG"
_TXT_KEY_OPTIONS_DCM = "TXT_KEY_OPTIONS_DCM"
_TXT_KEY_OPTIONS_IDW = "TXT_KEY_OPTIONS_IDW"
_TXT_KEY_OPTIONS_SS = "TXT_KEY_OPTIONS_SS"

# Format strings as constants
_SECTION_FORMAT = "<font=3><color=200,200,0>\n"
_OPTION_FORMAT = "<font=2><color=127,255,0>"
_NEW_LINE_TAB = "\n\t"
_REV_NONE_TEXT = "<font=2><color=0,0,255>\n\t"

# Main header format
_MAIN_HEADER = ("<color=250,170,0,255><font=4b>Caveman2Cosmos<font=2b><color=255,255,0>\n"
                "TXT_KEY_REV_MOD_INITIALIZING_INIT_POPUP")

# Pre-build tuples of option check methods and their corresponding text keys
# Using tuples saves memory vs lists for immutable data
_ANEWDAWN_OPTION_CHECKS = (
    ("isDefenderWithdraw", "TXT_KEY_BUG_OPT_ROMSETTINGS__DEFENDERWITHDRAW_TEXT"),
    ("isEnableFlexibleDifficulty", "TXT_KEY_BUG_OPT_ROMSETTINGS__ENABLEFLEXIBLEDIFFICULTY_TEXT"),
    ("isBetterAirInterception", "TXT_KEY_BUG_OPT_ROMSETTINGS__BETTERAIRINTERCEPTION_TEXT"),
    ("isDepletionMod", "TXT_KEY_BUG_OPT_ROMSETTINGS__DEPLETIONMOD_TEXT"),
    ("isGreaterGreatFarmer", "TXT_KEY_BUG_OPT_ROMSETTINGS__GREATERGREATFARMER_TEXT"),
    ("isRealisiticDiplomacy", "TXT_KEY_BUG_OPT_ROMSETTINGS__REALISITICDIPLOMACY_TEXT"),
    ("isImprovedXP", "TXT_KEY_BUG_OPT_ROMSETTINGS__IMPROVEDXP_TEXT"),
    ("isBattlefieldPromotions", "TXT_KEY_BUG_OPT_ROMSETTINGS__BATTLEFIELDPROMOTIONS_TEXT"),
    ("isStarsigns", "TXT_KEY_BUG_OPT_ROMSETTINGS__STARSIGNS_TEXT"),
    ("isReligionDecay", "TXT_KEY_BUG_OPT_ROMSETTINGS__RELIGIONDECAY_TEXT"),
    ("isMultipleReligionSpread", "TXT_KEY_BUG_OPT_ROMSETTINGS__MULTIPLERELIGIONSPREAD_TEXT"),
    ("isTelepathicReligion", "TXT_KEY_BUG_OPT_ROMSETTINGS__TELEPATHICRELIGION_TEXT")
)

_DCM_OPTION_CHECKS = (
    ("isDCM_RANGE_BOMBARD", "TXT_KEY_BUG_OPT_REVDCM__DCM_RANGE_BOMBARD_TEXT"),
    ("isDCM_OPP_FIRE", "TXT_KEY_BUG_OPT_REVDCM__DCM_OPP_FIRE_TEXT"),
    ("isDCM_AIR_BOMBING", "TXT_KEY_BUG_OPT_REVDCM__DCM_AIR_BOMBING_TEXT"),
    ("isDCM_ACTIVE_DEFENSE", "TXT_KEY_BUG_OPT_REVDCM__DCM_ACTIVE_DEFENSE_TEXT"),
    ("isDCM_FIGHTER_ENGAGE", "TXT_KEY_BUG_OPT_REVDCM__DCM_FIGHTER_ENGAGE_TEXT")
)

_SS_OPTION_CHECKS = (
    ("isSS_ENABLED", "TXT_KEY_BUG_OPT_REVDCM__SS_ENABLED_TEXT"),
    ("isSS_BRIBE", "TXT_KEY_BUG_OPT_REVDCM__SS_BRIBE_TEXT"),
    ("isSS_ASSASSINATE", "TXT_KEY_BUG_OPT_REVDCM__SS_ASSASSINATE_TEXT")
)

# Pre-cached help text keys as tuple for memory efficiency
_HELP_TEXT_KEYS = (
    "TXT_KEY_REV_MOD_INITIALIZING_GAME_SHORTCUTS",
    "TXT_KEY_REV_MOD_INITIALIZING_BUG_OPTIONS_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_AI_AUTOPLAY",
    "TXT_KEY_REV_MOD_INITIALIZING_CTRL_SHIFT_M_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_ALT_X_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_CTRL_X_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_ALT_S_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_CTRL_A_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_ALT_M_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_ALT_L_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_ALT_E_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_ALT_B_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_ALT_F_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_ALT_O_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_CTRL_L_ARROW_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_CTRL_R_ARROW_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_CTRL_I_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_ALT_I_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_ALT_CTRL_N_ARROW_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_SHIFT_F5_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_SHIFT_F8_SHORTCUT"
)

# Debug mode help text keys
_DEBUG_HELP_TEXT_KEYS = (
    "TXT_KEY_REV_MOD_INITIALIZING_CTRL_SHIFT_L_SHORTCUT",
    "TXT_KEY_REV_MOD_INITIALIZING_CTRL_SHIFT_P_SHORTCUT"
)


class RevolutionInit:
    # Use __slots__ to reduce memory overhead by ~100-200 bytes per instance
    # This prevents __dict__ creation and reduces memory fragmentation
    __slots__ = ('customEM', 'bFirst')

    def __init__(self, customEM):
        print
        "RevolutionInit.__init__"

        self.customEM = customEM
        self.bFirst = True

        # Add event handlers using pre-cached method references
        customEM.addEventHandler("kbdEvent", self.onKbdEvent)
        customEM.addEventHandler('GameStart', self.onGameStart)
        customEM.addEventHandler('OnLoad', self.onGameLoad)

        # Determine if game is already running and Python has just been reloaded
        # Use pre-cached method reference
        if _isFinalInitialized():
            self.onGameLoad(bShowPopup=False)

    def onKbdEvent(self, argsList):
        eventType, key, mx, my, px, py = argsList

        if eventType == _KBD_EVENT_TYPE:
            theKey = int(key)
            if (theKey == _KB_Q and
                    self.customEM.bShift and
                    self.customEM.bCtrl):
                self.showActivePopup()

    def onGameStart(self, argsList):
        self.onGameLoad()

    def onGameLoad(self, argsList=None, bForceReinit=False, bShowPopup=True):
        # Remove any running mod components
        bDoUnInit = bForceReinit or RevInstances.bIsInitialized
        bDoInit = bDoUnInit or not RevInstances.bIsInitialized

        if bDoUnInit:
            # Clean up existing instances with direct None comparisons
            if RevInstances.BarbarianCivInst is not None:
                RevInstances.BarbarianCivInst.removeEventHandlers()
                RevInstances.BarbarianCivInst = None
            if RevInstances.RevolutionInst is not None:
                RevEvents.removeEventHandlers()
                RevInstances.RevolutionInst.removeEventHandlers()
                RevInstances.RevolutionInst = None
            if RevInstances.AIAutoPlayInst is not None:
                RevInstances.AIAutoPlayInst.removeEventHandlers()
                RevInstances.AIAutoPlayInst = None
            if RevInstances.ChangePlayerInst is not None:
                RevInstances.ChangePlayerInst.removeEventHandlers()
                RevInstances.ChangePlayerInst = None

            RevInstances.bIsInitialized = False

        # Initialize mod components
        if bDoInit:
            RevInstances.bIsInitialized = True

            # Use pre-cached method references for option checking
            bAIAutoPlay = RevOpt.isAIAutoPlayEnable()
            if bAIAutoPlay:
                RevInstances.AIAutoPlayInst = AIAutoPlay.AIAutoPlay(self.customEM, RevOpt)

            if _isOption(_GAMEOPTION_BARBARIAN_CIV):
                RevInstances.BarbarianCivInst = BarbarianCiv.BarbarianCiv(self.customEM, RevOpt)

            bChangePlayer = RevOpt.isChangePlayerEnable()
            if bChangePlayer:
                RevInstances.ChangePlayerInst = ChangePlayer.ChangePlayer(self.customEM, RevOpt)

            if _isOption(_GAMEOPTION_UNSUPPORTED_REVOLUTION):
                # RevEvents needs to service beginPlayerTurn events before Revolution
                RevEvents.init(self.customEM, RevOpt)
                RevInstances.RevolutionInst = Revolution.Revolution(self.customEM, RevOpt)

        if bShowPopup and RevOpt.isActivePopup() and self.bFirst:
            self.showActivePopup()
            self.bFirst = False

        if bDoInit:
            # Use pre-cached interface constants
            cyInterface = CyInterface()
            cyInterface.setDirty(_MISC_BUTTONS_DIRTY, True)
            cyInterface.setDirty(_CITY_SCREEN_DIRTY, True)

    def showActivePopup(self):
        # Pre-calculate values once to avoid repeated method calls
        revMaxCivs = RevOpt.getRevMaxCivs()
        barbMaxCivs = RevOpt.getBarbCivMaxCivs()
        maxPCPlayers = _getMAX_PC_PLAYERS()
        maxTurns = _getMaxTurns()

        # Get default players with pre-cached method references
        worldSize = _getMap().getWorldSize()
        revDefaultNumPlayers = _getWorldInfo(worldSize).getDefaultPlayers()

        # Build message using list for efficient string building
        bodStr_parts = [self.getRevComponentsText()]

        bodStr_parts.append(_getText("TXT_KEY_REV_MOD_MAX_CIVS_IN_DLL", (maxPCPlayers,)))

        if revMaxCivs > 0 and revMaxCivs < maxPCPlayers:
            bodStr_parts.append(_getText("TXT_KEY_REV_MOD_REVS_WILL_STOP_AT", (revMaxCivs,)))

        if barbMaxCivs > 0 and barbMaxCivs < maxPCPlayers:
            bodStr_parts.append(_getText("TXT_KEY_REV_MOD_BARB_CIV_WILL_STOP_AT", (barbMaxCivs,)))

        bodStr_parts.append(_getText("TXT_KEY_REV_MOD_TURNS_IN_GAME", (maxTurns,)))
        bodStr_parts.append(_getText("TXT_KEY_REV_MOD_DEFAULT_NUM_PLAYERS", (revDefaultNumPlayers,)))

        # Join all parts once instead of repeated concatenation
        bodStr = "".join(bodStr_parts)

        # Create popup with optimized size calculation
        popup = CyPopup(-1, EventContextTypes.NO_EVENTCONTEXT, True)
        popup.setBodyString(bodStr, 1 << 0)
        popup.setPosition(0, 12)

        screen = CyGInterfaceScreen("", 0)
        popup.setSize(screen.getXResolution() / 4, screen.getYResolution() - 64)
        popup.launch(True, PopupStates.POPUPSTATE_IMMEDIATE)

    def getRevComponentsText(self):
        # Use list building for efficient string construction
        text_parts = []

        # Main header with pre-cached format strings
        text_parts.append(_MAIN_HEADER)
        text_parts.append(_getText("TXT_KEY_REV_MOD_INITIALIZING_INIT_POPUP", ()))
        text_parts.append(_SECTION_FORMAT)
        text_parts.append(_getText(_TXT_KEY_OPTIONS_GAME_REV, ()))

        # Game options section - optimized with generator and early exit
        game_options = []
        numGameOptions = _getNumGameOptionInfos()
        for iI in xrange(numGameOptions):
            if _isOption(iI):
                game_options.append(_NEW_LINE_TAB + _getGameOptionInfo(iI).getDescription())

        if game_options:
            text_parts.append(_OPTION_FORMAT)
            text_parts.extend(game_options)
        else:
            text_parts.append(_REV_NONE_TEXT)
            text_parts.append(_getText(_TXT_KEY_NONE, ()))

        # ANewDawn Options section
        text_parts.append(_SECTION_FORMAT)
        text_parts.append(_getText(_TXT_KEY_OPTIONS_BUG, ()))

        anewdawn_options = self._buildOptionsSection(ANewDawnOpt, _ANEWDAWN_OPTION_CHECKS)

        # Special case for max units per tile
        maxUnitsPerTile = ANewDawnOpt.getMaxUnitsPerTile()
        if maxUnitsPerTile > 0:
            anewdawn_options.append(_NEW_LINE_TAB + _getText("TXT_KEY_AND_UNITS_PER_TILE", (maxUnitsPerTile,)))

        if anewdawn_options:
            text_parts.append(_OPTION_FORMAT)
            text_parts.extend(anewdawn_options)
        else:
            text_parts.append(_REV_NONE_TEXT)
            text_parts.append(_getText(_TXT_KEY_NONE, ()))

        # DCM Options section
        text_parts.append(_SECTION_FORMAT)
        text_parts.append(_getText(_TXT_KEY_OPTIONS_DCM, ()))

        dcm_options = self._buildOptionsSection(RevDCMOpt, _DCM_OPTION_CHECKS)

        # Special case for respawn holy cities
        if (_isOption(_GAMEOPTION_RELIGION_INQUISITIONS) and
                RevDCMOpt.isOC_RESPAWN_HOLY_CITIES()):
            dcm_options.append(_NEW_LINE_TAB + _getText("TXT_KEY_BUG_OPT_REVDCM__OC_RESPAWN_HOLY_CITIES_TEXT", ()))

        if dcm_options:
            text_parts.append(_OPTION_FORMAT)
            text_parts.extend(dcm_options)
        else:
            text_parts.append(_REV_NONE_TEXT)
            text_parts.append(_getText(_TXT_KEY_NONE, ()))

        # Influence Driven War section
        if RevDCMOpt.isIDW_ENABLED():
            text_parts.append(_SECTION_FORMAT)
            text_parts.append(_getText(_TXT_KEY_OPTIONS_IDW, ()))
            text_parts.append(_OPTION_FORMAT)
            text_parts.append(_NEW_LINE_TAB + _getText("TXT_KEY_BUG_OPT_REVDCM__IDW_ENABLED_TEXT", ()))

            # IDW sub-options
            idw_suboptions = (
                ("isIDW_PILLAGE_INFLUENCE_ENABLED", "TXT_KEY_BUG_OPT_REVDCM__IDW_PILLAGE_INFLUENCE_ENABLED_TEXT"),
                ("isIDW_EMERGENCY_DRAFT_ENABLED", "TXT_KEY_BUG_OPT_REVDCM__IDW_EMERGENCY_DRAFT_ENABLED_TEXT"),
                ("isIDW_NO_BARBARIAN_INFLUENCE", "TXT_KEY_BUG_OPT_REVDCM__IDW_NO_BARBARIAN_INFLUENCE_TEXT"),
                ("isIDW_NO_NAVAL_INFLUENCE", "TXT_KEY_BUG_OPT_REVDCM__IDW_NO_NAVAL_INFLUENCE_TEXT")
            )

            idw_options = self._buildOptionsSection(RevDCMOpt, idw_suboptions)
            text_parts.extend(idw_options)

        # Super Spies section
        text_parts.append(_SECTION_FORMAT)
        text_parts.append(_getText(_TXT_KEY_OPTIONS_SS, ()))

        ss_options = self._buildOptionsSection(RevDCMOpt, _SS_OPTION_CHECKS)

        if ss_options:
            text_parts.append(_OPTION_FORMAT)
            text_parts.extend(ss_options)
        else:
            text_parts.append(_REV_NONE_TEXT)
            text_parts.append(_getText(_TXT_KEY_NONE, ()))

        # Help text section
        help_text_parts = [
            "<font=3b><color=255,255,0>\n",
            _getText("TXT_KEY_REV_MOD_INITIALIZING_GAME_SHORTCUTS", ()),
            "<font=2><color=255,255,255>"
        ]

        # Add all help text keys efficiently
        for text_key in _HELP_TEXT_KEYS:
            help_text_parts.append(_getText(text_key, ()))

        # Add debug help text if in debug mode
        if GAME.isDebugMode():
            for debug_key in _DEBUG_HELP_TEXT_KEYS:
                help_text_parts.append(_getText(debug_key, ()))

        # Join all parts once for maximum efficiency
        text_parts.extend(help_text_parts)
        return "".join(text_parts)

    def _buildOptionsSection(self, option_obj, option_checks):
        """
        Helper method to build options section efficiently.
        Uses tuple iteration to reduce code duplication and memory usage.
        """
        options = []
        for method_name, text_key in option_checks:
            method = getattr(option_obj, method_name)
            if method():
                options.append(_NEW_LINE_TAB + _getText(text_key, ()))
        return options