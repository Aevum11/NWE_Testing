## A New Dawn Mod Option Code - Memory Optimized for 32-bit Caveman2Cosmos
from CvPythonExtensions import *
import BugCore
import CvUtil

# Pre-cache global references to save repeated lookups
GC = CyGlobalContext()
GAME = GC.getGame()
ANewDawnOpt = BugCore.game.RoMSettings

# Pre-cache frequently used methods
_getPlayer = GC.getPlayer
_getActivePlayer = GC.getActivePlayer
_getCivilizationInfo = GC.getCivilizationInfo
_getInfoTypeForString = GC.getInfoTypeForString
_getBuildInfo = GC.getBuildInfo
_setDefineINT = GC.setDefineINT
_getMAX_PC_PLAYERS = GC.getMAX_PC_PLAYERS

# Pre-cache game methods
_setModderGameOption = GAME.setModderGameOption
_getActivePlayerID = GAME.getActivePlayer

# Pre-cache message control
_sendModNetMessage = CyMessageControl().sendModNetMessage

# Pre-cache event IDs
MODDEROPTION_EVENT_ID = CvUtil.getNewEventID()
MODDERGAMEOPTION_EVENT_ID = CvUtil.getNewEventID()
DIFFICULTY_EVENT_ID = CvUtil.getNewEventID()
COLOR_EVENT_ID = CvUtil.getNewEventID()
CANBUILD_EVENT_ID = CvUtil.getNewEventID()

# Pre-cache ModderOptionTypes constants
_MOD_OPT_FLEXIBLE_DIFFICULTY_TURN_INCREMENTS = int(ModderOptionTypes.MODDEROPTION_FLEXIBLE_DIFFICULTY_TURN_INCREMENTS)
_MOD_OPT_NO_FRIENDLY_PILLAGING = int(ModderOptionTypes.MODDEROPTION_NO_FRIENDLY_PILLAGING)
_MOD_OPT_FLEXIBLE_DIFFICULTY = int(ModderOptionTypes.MODDEROPTION_FLEXIBLE_DIFFICULTY)
_MOD_OPT_FLEXIBLE_DIFFICULTY_MIN_DIFFICULTY = int(ModderOptionTypes.MODDEROPTION_FLEXIBLE_DIFFICULTY_MIN_DIFFICULTY)
_MOD_OPT_FLEXIBLE_DIFFICULTY_MAX_DIFFICULTY = int(ModderOptionTypes.MODDEROPTION_FLEXIBLE_DIFFICULTY_MAX_DIFFICULTY)
_MOD_OPT_FLEXIBLE_DIFFICULTY_MIN_RANK = int(ModderOptionTypes.MODDEROPTION_FLEXIBLE_DIFFICULTY_MIN_RANK)
_MOD_OPT_FLEXIBLE_DIFFICULTY_MAX_RANK = int(ModderOptionTypes.MODDEROPTION_FLEXIBLE_DIFFICULTY_MAX_RANK)
_MOD_OPT_SHOW_REV_EFFECTS = int(ModderOptionTypes.MODDEROPTION_SHOW_REV_EFFECTS)
_MOD_OPT_HIDE_REPLACED_BUILDINGS = int(ModderOptionTypes.MODDEROPTION_HIDE_REPLACED_BUILDINGS)
_MOD_OPT_USE_LANDMARK_NAMES = int(ModderOptionTypes.MODDEROPTION_USE_LANDMARK_NAMES)
_MOD_OPT_HIDE_UNAVAILBLE_BUILDS = int(ModderOptionTypes.MODDEROPTION_HIDE_UNAVAILBLE_BUILDS)
_MOD_OPT_IGNORE_DISABLED_ALERTS = int(ModderOptionTypes.MODDEROPTION_IGNORE_DISABLED_ALERTS)
_MOD_OPT_INFRASTRUCTURE_IGNORES_IMPROVEMENTS = int(ModderOptionTypes.MODDEROPTION_INFRASTRUCTURE_IGNORES_IMPROVEMENTS)

# Pre-cache ModderGameOptionTypes constants
_MOD_GAME_OPT_DEFENDER_WITHDRAW = int(ModderGameOptionTypes.MODDERGAMEOPTION_DEFENDER_WITHDRAW)
_MOD_GAME_OPT_MAX_UNITS_PER_TILES = int(ModderGameOptionTypes.MODDERGAMEOPTION_MAX_UNITS_PER_TILES)
_MOD_GAME_OPT_MAX_BOMBARD_DEFENSE = int(ModderGameOptionTypes.MODDERGAMEOPTION_MAX_BOMBARD_DEFENSE)
_MOD_GAME_OPT_MIN_CITY_DISTANCE = int(ModderGameOptionTypes.MODDERGAMEOPTION_MIN_CITY_DISTANCE)
_MOD_GAME_OPT_CANNOT_CLAIM_OCEAN = int(ModderGameOptionTypes.MODDERGAMEOPTION_CANNOT_CLAIM_OCEAN)
_MOD_GAME_OPT_RESOURCE_DEPLETION = int(ModderGameOptionTypes.MODDERGAMEOPTION_RESOURCE_DEPLETION)
_MOD_GAME_OPT_GREATER_GREAT_FARMER = int(ModderGameOptionTypes.MODDERGAMEOPTION_GREATER_GREAT_FARMER)
_MOD_GAME_OPT_BETTER_INTERCETION = int(ModderGameOptionTypes.MODDERGAMEOPTION_BETTER_INTERCETION)
_MOD_GAME_OPT_AIRLIFT_RANGE = int(ModderGameOptionTypes.MODDERGAMEOPTION_AIRLIFT_RANGE)
_MOD_GAME_OPT_MERCY_RULE = int(ModderGameOptionTypes.MODDERGAMEOPTION_MERCY_RULE)
_MOD_GAME_OPT_REALISTIC_DIPLOMACY = int(ModderGameOptionTypes.MODDERGAMEOPTION_REALISTIC_DIPLOMACY)
_MOD_GAME_OPT_BATTLEFIELD_PROMOTIONS = int(ModderGameOptionTypes.MODDERGAMEOPTION_BATTLEFIELD_PROMOTIONS)
_MOD_GAME_OPT_STARSIGNS = int(ModderGameOptionTypes.MODDERGAMEOPTION_STARSIGNS)
_MOD_GAME_OPT_IMPROVED_XP = int(ModderGameOptionTypes.MODDERGAMEOPTION_IMPROVED_XP)
_MOD_GAME_OPT_RELIGION_DECAY = int(ModderGameOptionTypes.MODDERGAMEOPTION_RELIGION_DECAY)
_MOD_GAME_OPT_MULTIPLE_RELIGION_SPREAD = int(ModderGameOptionTypes.MODDERGAMEOPTION_MULTIPLE_RELIGION_SPREAD)
_MOD_GAME_OPT_TERRAIN_DAMAGE = int(ModderGameOptionTypes.MODDERGAMEOPTION_TERRAIN_DAMAGE)
_MOD_GAME_OPT_NO_AUTO_CORPORATION_FOUNDING = int(ModderGameOptionTypes.MODDERGAMEOPTION_NO_AUTO_CORPORATION_FOUNDING)
_MOD_GAME_OPT_AI_USE_FLEXIBLE_DIFFICULTY = int(ModderGameOptionTypes.MODDERGAMEOPTION_AI_USE_FLEXIBLE_DIFFICULTY)
_MOD_GAME_OPT_USE_HISTORICAL_ACCURATE_CALENDAR = int(
    ModderGameOptionTypes.MODDERGAMEOPTION_USE_HISTORICAL_ACCURATE_CALENDAR)
_MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_TURN_INCREMENTS = int(
    ModderGameOptionTypes.MODDERGAMEOPTION_FLEXIBLE_DIFFICULTY_AI_TURN_INCREMENTS)
_MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_MIN_DIFFICULTY = int(
    ModderGameOptionTypes.MODDERGAMEOPTION_FLEXIBLE_DIFFICULTY_AI_MIN_DIFFICULTY)
_MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_MAX_DIFFICULTY = int(
    ModderGameOptionTypes.MODDERGAMEOPTION_FLEXIBLE_DIFFICULTY_AI_MAX_DIFFICULTY)

# Pre-cache build type strings as integers
_BUILD_TERRAFORM_GRASS = -1  # Will be set on first use
_BUILD_TERRAFORM_PLAINS = -1
_BUILD_TERRAFORM_TUNDRA = -1
_BUILD_YOUNG_FOREST = -1
_BUILD_PLANT_JUNGLE = -1
_BUILD_TUNNEL = -1


def _init_build_types():
    """Initialize build type constants - called once on module load"""
    global _BUILD_TERRAFORM_GRASS, _BUILD_TERRAFORM_PLAINS, _BUILD_TERRAFORM_TUNDRA
    global _BUILD_YOUNG_FOREST, _BUILD_PLANT_JUNGLE, _BUILD_TUNNEL

    _BUILD_TERRAFORM_GRASS = _getInfoTypeForString("BUILD_TERRAFORM_GRASS")
    _BUILD_TERRAFORM_PLAINS = _getInfoTypeForString("BUILD_TERRAFORM_PLAINS")
    _BUILD_TERRAFORM_TUNDRA = _getInfoTypeForString("BUILD_TERRAFORM_TUNDRA")
    _BUILD_YOUNG_FOREST = _getInfoTypeForString("BUILD_YOUNG_FOREST")
    _BUILD_PLANT_JUNGLE = _getInfoTypeForString("BUILD_PLANT_JUNGLE")
    _BUILD_TUNNEL = _getInfoTypeForString("BUILD_TUNNEL")


# Initialize build types once
_init_build_types()


class ANewDawnSettings:
    # Use __slots__ to reduce memory overhead by ~100-200 bytes per instance
    __slots__ = ('_game_option_handlers',)

    def __init__(self, eventManager):
        eventManager.addEventHandler("OnLoad", self.onLoadGame)
        eventManager.addEventHandler("GameStart", self.onGameStart)
        eventManager.addEventHandler("ModNetMessage", self.onModNetMessage)

        # Pre-build handler dispatch dictionary for game options
        self._game_option_handlers = {
            _MOD_GAME_OPT_DEFENDER_WITHDRAW: ANewDawnOpt.setDefenderWithdraw,
            _MOD_GAME_OPT_MAX_UNITS_PER_TILES: ANewDawnOpt.setMaxUnitsPerTile,
            _MOD_GAME_OPT_MAX_BOMBARD_DEFENSE: ANewDawnOpt.setMaxBombardDefense,
            _MOD_GAME_OPT_MIN_CITY_DISTANCE: ANewDawnOpt.setMinCityDistance,
            _MOD_GAME_OPT_CANNOT_CLAIM_OCEAN: ANewDawnOpt.setCanNotClaimOcean,
            _MOD_GAME_OPT_RESOURCE_DEPLETION: ANewDawnOpt.setDepletionMod,
            _MOD_GAME_OPT_GREATER_GREAT_FARMER: ANewDawnOpt.setGreaterGreatFarmer,
            _MOD_GAME_OPT_BETTER_INTERCETION: ANewDawnOpt.setBetterAirInterception,
            _MOD_GAME_OPT_AIRLIFT_RANGE: ANewDawnOpt.setMaxRebaseRange,
            _MOD_GAME_OPT_MERCY_RULE: ANewDawnOpt.setMercyRule,
            _MOD_GAME_OPT_REALISTIC_DIPLOMACY: ANewDawnOpt.setRealisiticDiplomacy,
            _MOD_GAME_OPT_BATTLEFIELD_PROMOTIONS: ANewDawnOpt.setBattlefieldPromotions,
            _MOD_GAME_OPT_STARSIGNS: ANewDawnOpt.setStarsigns,
            _MOD_GAME_OPT_IMPROVED_XP: ANewDawnOpt.setImprovedXP,
            _MOD_GAME_OPT_RELIGION_DECAY: ANewDawnOpt.setReligionDecay,
            _MOD_GAME_OPT_MULTIPLE_RELIGION_SPREAD: ANewDawnOpt.setMultipleReligionSpread,
            _MOD_GAME_OPT_TERRAIN_DAMAGE: ANewDawnOpt.setTerrainDamage,
            _MOD_GAME_OPT_NO_AUTO_CORPORATION_FOUNDING: ANewDawnOpt.setNoAutoCorporationFounding,
            _MOD_GAME_OPT_AI_USE_FLEXIBLE_DIFFICULTY: ANewDawnOpt.setFlexibleDifficultyAI,
            _MOD_GAME_OPT_USE_HISTORICAL_ACCURATE_CALENDAR: ANewDawnOpt.setHistoricalAccurateCalendar,
            _MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_TURN_INCREMENTS: ANewDawnOpt.setFlexibleDifficultyAITurnIncrements,
            _MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_MIN_DIFFICULTY: lambda
                v: ANewDawnOpt.setFlexibleDifficultyAIMinimumDiff(v + 1),
            _MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_MAX_DIFFICULTY: lambda
                v: ANewDawnOpt.setFlexibleDifficultyAIMaximumDiff(v + 1)
        }

    def onLoadGame(self, argsList):
        self.optionUpdate()

    def onGameStart(self, argsList):
        self.optionUpdate()

    def optionUpdate(self):
        if ANewDawnOpt.isRoMReset():
            resetOptions()
        else:
            setXMLOptionsfromIniFile()

    def onModNetMessage(self, argsList):
        protocol, data1, data2, data3, data4 = argsList

        if protocol == MODDEROPTION_EVENT_ID:
            # ModderOptions
            _getPlayer(data1).setModderOption(data2, data3)
        elif protocol == MODDERGAMEOPTION_EVENT_ID:
            # ModderGameOptions - use dispatch dictionary
            handler = self._game_option_handlers.get(data2)
            if handler:
                handler(data3)
        elif protocol == DIFFICULTY_EVENT_ID:
            # Change Difficulty
            _getPlayer(data1).setHandicap(data2, True)
        elif protocol == COLOR_EVENT_ID:
            # Change Color
            _getPlayer(data1).setColor(data2)
            GC.getMap().updateMinimapColor()
        elif protocol == CANBUILD_EVENT_ID:
            # Disable/enable worker actions
            _getBuildInfo(data2).setDisabled(data3)


#####################################################
# Module level functions defined in RoMSettings.xml #
#####################################################

# Helper function to reduce code duplication
def _sendGameOptionMessage(option_type, value):
    """Send a game option network message"""
    iActivePlayer = _getActivePlayerID()
    _sendModNetMessage(MODDERGAMEOPTION_EVENT_ID, iActivePlayer, option_type, int(value), 0)


def _sendPlayerOptionMessage(option_type, value):
    """Send a player option network message"""
    iActivePlayer = _getActivePlayerID()
    _getActivePlayer().setModderOption(option_type, value)
    _sendModNetMessage(MODDEROPTION_EVENT_ID, iActivePlayer, option_type, int(value), 0)


def changedRoMReset(option, value):
    resetOptions()
    return True


def changedDefenderWithdraw(option, value):
    _setModderGameOption(_MOD_GAME_OPT_DEFENDER_WITHDRAW, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_DEFENDER_WITHDRAW, value)


def changedMaxUnitsPerTile(option, value):
    _setModderGameOption(_MOD_GAME_OPT_MAX_UNITS_PER_TILES, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_MAX_UNITS_PER_TILES, value)


def changedFlexibleDifficultyTurnIncrements(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_FLEXIBLE_DIFFICULTY_TURN_INCREMENTS, value)


def changedFlexibleDifficultyAITurnIncrements(option, value):
    _setModderGameOption(_MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_TURN_INCREMENTS, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_TURN_INCREMENTS, value)


def changedMaxBombardDefense(option, value):
    _setModderGameOption(_MOD_GAME_OPT_MAX_BOMBARD_DEFENSE, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_MAX_BOMBARD_DEFENSE, value)


def changedMinCityDistance(option, value):
    _setModderGameOption(_MOD_GAME_OPT_MIN_CITY_DISTANCE, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_MIN_CITY_DISTANCE, value)


def changedCanNotClaimOcean(option, value):
    _setModderGameOption(_MOD_GAME_OPT_CANNOT_CLAIM_OCEAN, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_CANNOT_CLAIM_OCEAN, value)


def changedNoFriendlyPillaging(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_NO_FRIENDLY_PILLAGING, value)


def changedEnableFlexibleDifficulty(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_FLEXIBLE_DIFFICULTY, value)


def changedFlexibleDifficultyMinimumDiff(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_FLEXIBLE_DIFFICULTY_MIN_DIFFICULTY, value - 1)


def changedFlexibleDifficultyMaximumDiff(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_FLEXIBLE_DIFFICULTY_MAX_DIFFICULTY, value - 1)


def changedFlexibleDifficultyAIMinimumDiff(option, value):
    _setModderGameOption(_MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_MIN_DIFFICULTY, value - 1)
    _sendGameOptionMessage(_MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_MIN_DIFFICULTY, value - 1)


def changedFlexibleDifficultyAIMaximumDiff(option, value):
    _setModderGameOption(_MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_MAX_DIFFICULTY, value - 1)
    _sendGameOptionMessage(_MOD_GAME_OPT_FLEXIBLE_DIFFICULTY_AI_MAX_DIFFICULTY, value - 1)


def changedFlexibleDifficultyMinRank(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_FLEXIBLE_DIFFICULTY_MIN_RANK, value)


def changedFlexibleDifficultyMaxRank(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_FLEXIBLE_DIFFICULTY_MAX_RANK, value)


def changedDepletionMod(option, value):
    _setModderGameOption(_MOD_GAME_OPT_RESOURCE_DEPLETION, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_RESOURCE_DEPLETION, value)


def changedGreaterGreatFarmer(option, value):
    _setModderGameOption(_MOD_GAME_OPT_GREATER_GREAT_FARMER, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_GREATER_GREAT_FARMER, value)


def changedBetterAirInterception(option, value):
    _setModderGameOption(_MOD_GAME_OPT_BETTER_INTERCETION, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_BETTER_INTERCETION, value)


def changedMaxRebaseRange(option, value):
    _setModderGameOption(_MOD_GAME_OPT_AIRLIFT_RANGE, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_AIRLIFT_RANGE, value)


def changedMercyRule(option, value):
    _setModderGameOption(_MOD_GAME_OPT_MERCY_RULE, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_MERCY_RULE, value)


def changedRealisiticDiplomacy(option, value):
    _setModderGameOption(_MOD_GAME_OPT_REALISTIC_DIPLOMACY, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_REALISTIC_DIPLOMACY, value)


def changedShowRevCivics(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_SHOW_REV_EFFECTS, value)


def changedBattlefieldPromotions(option, value):
    _setModderGameOption(_MOD_GAME_OPT_BATTLEFIELD_PROMOTIONS, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_BATTLEFIELD_PROMOTIONS, value)


def changedStarsigns(option, value):
    _setModderGameOption(_MOD_GAME_OPT_STARSIGNS, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_STARSIGNS, value)


def changedHideReplacedBuildings(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_HIDE_REPLACED_BUILDINGS, value)


def changedImprovedXP(option, value):
    _setModderGameOption(_MOD_GAME_OPT_IMPROVED_XP, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_IMPROVED_XP, value)


def changedPlayerColor(option, value):
    iColor = value - 1
    if iColor >= 0:
        _sendModNetMessage(COLOR_EVENT_ID, _getActivePlayerID(), iColor, 0, 0)


def updateAliveCivsOption():
    import BugGame
    aliveCivsOption = BugGame.ANewDawnSettings.AliveCivilization
    descs = []
    for iPlayer in xrange(_getMAX_PC_PLAYERS()):
        CyPlayer = _getPlayer(iPlayer)
        if CyPlayer.isHuman() and CyPlayer.isAlive():
            descs.append(_getCivilizationInfo(CyPlayer.getCivilizationType()).getShortDescription())
    descs.sort()  # sort in-place is more memory efficient than sorted()
    aliveCivsOption.setValues(descs)


def changedCurrentDifficulty(option, value):
    if value > 0:
        _sendModNetMessage(DIFFICULTY_EVENT_ID, _getActivePlayerID(), value - 1, 0, 0)


def changedUseLandmarkNames(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_USE_LANDMARK_NAMES, value)


def changedHideUnavailableBuilds(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_HIDE_UNAVAILBLE_BUILDS, value)


def changedIgnoreDisabledBuildingAlerts(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_IGNORE_DISABLED_ALERTS, value)


def changedReligionDecay(option, value):
    _setModderGameOption(_MOD_GAME_OPT_RELIGION_DECAY, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_RELIGION_DECAY, value)


def changedMultipleReligionSpread(option, value):
    _setModderGameOption(_MOD_GAME_OPT_MULTIPLE_RELIGION_SPREAD, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_MULTIPLE_RELIGION_SPREAD, value)


def changedTerrainDamage(option, value):
    _setModderGameOption(_MOD_GAME_OPT_TERRAIN_DAMAGE, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_TERRAIN_DAMAGE, value)


def changedAllowTerraforming(option, value):
    iActivePlayer = _getActivePlayerID()
    not_value = not value
    _sendModNetMessage(CANBUILD_EVENT_ID, iActivePlayer, _BUILD_TERRAFORM_GRASS, not_value, 0)
    _sendModNetMessage(CANBUILD_EVENT_ID, iActivePlayer, _BUILD_TERRAFORM_PLAINS, not_value, 0)
    _sendModNetMessage(CANBUILD_EVENT_ID, iActivePlayer, _BUILD_TERRAFORM_TUNDRA, not_value, 0)


def changedReforestation(option, value):
    iActivePlayer = _getActivePlayerID()
    not_value = not value
    _sendModNetMessage(CANBUILD_EVENT_ID, iActivePlayer, _BUILD_YOUNG_FOREST, not_value, 0)
    _sendModNetMessage(CANBUILD_EVENT_ID, iActivePlayer, _BUILD_PLANT_JUNGLE, not_value, 0)


def changedSeaTunnels(option, value):
    _sendModNetMessage(CANBUILD_EVENT_ID, _getActivePlayerID(), _BUILD_TUNNEL, not value, 0)


def changedNoAutoCorporationFounding(option, value):
    _setModderGameOption(_MOD_GAME_OPT_NO_AUTO_CORPORATION_FOUNDING, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_NO_AUTO_CORPORATION_FOUNDING, value)


def changedWarPrizes(option, value):
    _setDefineINT("WAR_PRIZES", int(value))


def changedFlexibleDifficultyAI(option, value):
    _setModderGameOption(_MOD_GAME_OPT_AI_USE_FLEXIBLE_DIFFICULTY, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_AI_USE_FLEXIBLE_DIFFICULTY, value)


def changedHistoricalAccurateCalendar(option, value):
    _setModderGameOption(_MOD_GAME_OPT_USE_HISTORICAL_ACCURATE_CALENDAR, value)
    _sendGameOptionMessage(_MOD_GAME_OPT_USE_HISTORICAL_ACCURATE_CALENDAR, value)


def changedInfrastructureIgnoresImprovements(option, value):
    _sendPlayerOptionMessage(_MOD_OPT_INFRASTRUCTURE_IGNORES_IMPROVEMENTS, value)


def setXMLOptionsfromIniFile():
<<<<<<< Updated upstream
    print
    "Initializing A New Dawn Settings"
=======
    print "Initializing A New Dawn Settings"
>>>>>>> Stashed changes

    # Pre-cache option object for repeated access
    opt = ANewDawnOpt

    # Call changed functions with cached option object
    changedDefenderWithdraw(opt, opt.isDefenderWithdraw())
    changedMaxUnitsPerTile(opt, opt.getMaxUnitsPerTile())
    changedFlexibleDifficultyTurnIncrements(opt, opt.getFlexibleDifficultyTurnIncrements())
    changedFlexibleDifficultyAITurnIncrements(opt, opt.getFlexibleDifficultyAITurnIncrements())
    changedMaxBombardDefense(opt, opt.getMaxBombardDefense())
    changedMinCityDistance(opt, opt.getMinCityDistance())
    changedCanNotClaimOcean(opt, opt.isCanNotClaimOcean())
    changedNoFriendlyPillaging(opt, opt.isNoFriendlyPillaging())
    changedEnableFlexibleDifficulty(opt, opt.isEnableFlexibleDifficulty())
    changedFlexibleDifficultyMinimumDiff(opt, opt.getFlexibleDifficultyMinimumDiff())
    changedFlexibleDifficultyMaximumDiff(opt, opt.getFlexibleDifficultyMaximumDiff())
    changedFlexibleDifficultyAIMinimumDiff(opt, opt.getFlexibleDifficultyAIMinimumDiff())
    changedFlexibleDifficultyAIMaximumDiff(opt, opt.getFlexibleDifficultyAIMaximumDiff())
    changedFlexibleDifficultyMinRank(opt, opt.getFlexibleDifficultyMinRank())
    changedFlexibleDifficultyMaxRank(opt, opt.getFlexibleDifficultyMaxRank())
    changedDepletionMod(opt, opt.isDepletionMod())
    changedGreaterGreatFarmer(opt, opt.isGreaterGreatFarmer())
    changedBetterAirInterception(opt, opt.isBetterAirInterception())
    changedMaxRebaseRange(opt, opt.getMaxRebaseRange())
    changedMercyRule(opt, opt.isMercyRule())
    changedRealisiticDiplomacy(opt, opt.isRealisiticDiplomacy())
    changedShowRevCivics(opt, opt.isShowRevCivics())
    changedBattlefieldPromotions(opt, opt.isBattlefieldPromotions())
    changedHideReplacedBuildings(opt, opt.isHideReplacedBuildings())
    changedImprovedXP(opt, opt.isImprovedXP())
    changedUseLandmarkNames(opt, opt.isUseLandmarkNames())
    changedHideUnavailableBuilds(opt, opt.isHideUnavailableBuilds())
    changedIgnoreDisabledBuildingAlerts(opt, opt.isIgnoreDisabledBuildingAlerts())
    changedReligionDecay(opt, opt.isReligionDecay())
    changedMultipleReligionSpread(opt, opt.isMultipleReligionSpread())
    changedTerrainDamage(opt, opt.isTerrainDamage())
    changedAllowTerraforming(opt, opt.isAllowTerraforming())
    changedReforestation(opt, opt.isReforestation())
    changedSeaTunnels(opt, opt.isSeaTunnels())
    changedWarPrizes(opt, opt.isWarPrizes())
    changedFlexibleDifficultyAI(opt, opt.isFlexibleDifficultyAI())
    changedHistoricalAccurateCalendar(opt, opt.isHistoricalAccurateCalendar())
    changedInfrastructureIgnoresImprovements(opt, opt.isInfrastructureIgnoresImprovements())

    opt.setPlayerColor(0)
    opt.setCurrentDifficulty(0)


def resetOptions():
    import BugOptions
    options = BugOptions.getOptions("RoMSettings").options
    for option in options:
        option.resetValue()
    setXMLOptionsfromIniFile()
    ANewDawnOpt.setRoMReset(False)