## A New Dawn Mod Code - Memory-optimized version for 32-bit Caveman2Cosmos
##

from CvPythonExtensions import *
import BugOptions
import BugCore
import CvUtil

# Pre-cache global references to save repeated lookups
GC = CyGlobalContext()
AutomatedOpts = BugCore.game.AutomatedSettings

# Pre-cache frequently used methods
_getPlayer = GC.getPlayer
_getActivePlayer = GC.getActivePlayer
_getGame = GC.getGame
_getActivePlayerID = _getGame().getActivePlayer
_sendModNetMessage = CyMessageControl().sendModNetMessage

# Pre-cache event IDs
MODDEROPTION_EVENT_ID = CvUtil.getNewEventID()
CANAUTOBUILD_EVENT_ID = CvUtil.getNewEventID()
CANPLAYERAUTOBUILD_EVENT_ID = CvUtil.getNewEventID()

# Pre-cache ModderOptionTypes constants as integers to avoid repeated lookups
_MOD_OPT_AUTO_PILLAGE_AVOID_ENEMY_UNITS = int(ModderOptionTypes.MODDEROPTION_AUTO_PILLAGE_AVOID_ENEMY_UNITS)
_MOD_OPT_AUTO_PILLAGE_AVOID_BARBARIAN_CITIES = int(ModderOptionTypes.MODDEROPTION_AUTO_PILLAGE_AVOID_BARBARIAN_CITIES)
_MOD_OPT_HIDE_AUTO_PILLAGE = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_PILLAGE)
_MOD_OPT_AUTO_HUNT_NO_CITY_CAPTURING = int(ModderOptionTypes.MODDEROPTION_AUTO_HUNT_NO_CITY_CAPTURING)
_MOD_OPT_AUTO_HUNT_ALLOW_UNIT_SUICIDING = int(ModderOptionTypes.MODDEROPTION_AUTO_HUNT_ALLOW_UNIT_SUICIDING)
_MOD_OPT_AUTO_HUNT_RETURN_FOR_UPGRADES = int(ModderOptionTypes.MODDEROPTION_AUTO_HUNT_RETURN_FOR_UPGRADES)
_MOD_OPT_HIDE_AUTO_HUNT = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_HUNT)
_MOD_OPT_AUTO_HUNT_MIN_COMBAT_ODDS = int(ModderOptionTypes.MODDEROPTION_AUTO_HUNT_MIN_COMBAT_ODDS)
_MOD_OPT_AUTO_PATROL_CAN_LEAVE_BORDERS = int(ModderOptionTypes.MODDEROPTION_AUTO_PATROL_CAN_LEAVE_BORDERS)
_MOD_OPT_AUTO_PATROL_ALLOW_UNIT_SUICIDING = int(ModderOptionTypes.MODDEROPTION_AUTO_PATROL_ALLOW_UNIT_SUICIDING)
_MOD_OPT_AUTO_PATROL_NO_CITY_CAPTURING = int(ModderOptionTypes.MODDEROPTION_AUTO_PATROL_NO_CITY_CAPTURING)
_MOD_OPT_HIDE_AUTO_PATROL = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_PATROL)
_MOD_OPT_AUTO_PATROL_MIN_COMBAT_ODDS = int(ModderOptionTypes.MODDEROPTION_AUTO_PATROL_MIN_COMBAT_ODDS)
_MOD_OPT_AUTO_DEFENSE_CAN_LEAVE_CITY = int(ModderOptionTypes.MODDEROPTION_AUTO_DEFENSE_CAN_LEAVE_CITY)
_MOD_OPT_HIDE_AUTO_DEFENSE = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_DEFENSE)
_MOD_OPT_AUTO_DEFENSE_MIN_COMBAT_ODDS = int(ModderOptionTypes.MODDEROPTION_AUTO_DEFENSE_MIN_COMBAT_ODDS)
_MOD_OPT_AUTO_AIR_CAN_DEFEND = int(ModderOptionTypes.MODDEROPTION_AUTO_AIR_CAN_DEFEND)
_MOD_OPT_AUTO_AIR_CAN_REBASE = int(ModderOptionTypes.MODDEROPTION_AUTO_AIR_CAN_REBASE)
_MOD_OPT_HIDE_AUTO_AIR = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_AIR)
_MOD_OPT_HIDE_AUTO_EXPLORE = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_EXPLORE)
_MOD_OPT_HIDE_AUTO_SPREAD = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_SPREAD)
_MOD_OPT_HIDE_AUTO_CARAVAN = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_CARAVAN)
_MOD_OPT_HIDE_AUTO_PIRATE = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_PIRATE)
_MOD_OPT_AUTO_PIRATE_MIN_COMBAT_ODDS = int(ModderOptionTypes.MODDEROPTION_AUTO_PIRATE_MIN_COMBAT_ODDS)
_MOD_OPT_HIDE_AUTO_PROTECT = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_PROTECT)
_MOD_OPT_HIDE_AUTO_UPGRADE = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_UPGRADE)
_MOD_OPT_UPGRADE_MOST_EXPENSIVE = int(ModderOptionTypes.MODDEROPTION_UPGRADE_MOST_EXPENSIVE)
_MOD_OPT_UPGRADE_MOST_EXPERIENCED = int(ModderOptionTypes.MODDEROPTION_UPGRADE_MOST_EXPERIENCED)
_MOD_OPT_UPGRADE_MIN_GOLD = int(ModderOptionTypes.MODDEROPTION_UPGRADE_MIN_GOLD)
_MOD_OPT_HIDE_AUTO_PROMOTE = int(ModderOptionTypes.MODDEROPTION_HIDE_AUTO_PROMOTE)

# Pre-cache string constants to leverage Python's string interning
_RESET_KEY = "Reset"
_AUTOMATED_SETTINGS = "AutomatedSettings"


def _setPlayerOption(option_type, value):
    """Helper function to set player option and send network message - reduces code duplication"""
    iActivePlayer = _getActivePlayerID()
    _getActivePlayer().setModderOption(option_type, value)
    _sendModNetMessage(MODDEROPTION_EVENT_ID, iActivePlayer, option_type, int(value), 0)


class AutomatedSettings:
    # Use __slots__ to reduce memory overhead by ~100-200 bytes per instance
    __slots__ = ()

    def __init__(self, eventManager):
        eventManager.addEventHandler("OnLoad", self.onLoadGame)
        eventManager.addEventHandler("GameStart", self.onGameStart)
        eventManager.addEventHandler("ModNetMessage", self.onModNetMessage)

    def onLoadGame(self, argsList):
        self.optionUpdate()

    def onGameStart(self, argsList):
        self.optionUpdate()

    def optionUpdate(self):
        if AutomatedOpts.isReset():
            resetOptions()
        else:
            setXMLOptionsfromIniFile()

    def onModNetMessage(self, argsList):
        protocol, data1, data2, data3, data4 = argsList

        if protocol == MODDEROPTION_EVENT_ID:
            # ModderOptions - use pre-cached method
            _getPlayer(data1).setModderOption(data2, data3)
        elif protocol == CANAUTOBUILD_EVENT_ID:
            # Use pre-cached method and method chaining to reduce intermediate variables
            pPlayer = _getPlayer(data1)
            pPlayer.getCity(data2).setAutomatedCanBuild(data3, data4)
        elif protocol == CANPLAYERAUTOBUILD_EVENT_ID:
            # Use pre-cached method
            _getPlayer(data1).setAutomatedCanBuild(data3, data4)


#####################################################
# Module level functions defined in RoMSettings.xml #
#####################################################

def getCanAutoBuildEventID():
    return CANAUTOBUILD_EVENT_ID


def getCanPlayerAutoBuildEventID():
    return CANPLAYERAUTOBUILD_EVENT_ID


def changedReset(option, value):
    resetOptions()
    return True


# Optimized option change functions using helper function to eliminate code duplication
def changedAvoidEnemyUnits(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_PILLAGE_AVOID_ENEMY_UNITS, value)


def changedAvoidBarbarianCities(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_PILLAGE_AVOID_BARBARIAN_CITIES, value)


def changedHideAutomatePillage(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_PILLAGE, value)


def changedNoCapturingCities(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_HUNT_NO_CITY_CAPTURING, value)


def changedAllowUnitSuiciding(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_HUNT_ALLOW_UNIT_SUICIDING, value)


def changedAutoHuntReturnForUpgrades(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_HUNT_RETURN_FOR_UPGRADES, value)


def changedHideAutomateHunt(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_HUNT, value)


def changedAutoHuntMinimumAttackOdds(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_HUNT_MIN_COMBAT_ODDS, value)


def changedCanLeaveBorders(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_PATROL_CAN_LEAVE_BORDERS, value)


def changedPatrolAllowUnitSuiciding(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_PATROL_ALLOW_UNIT_SUICIDING, value)


def changedNoPatrolCapturingCities(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_PATROL_NO_CITY_CAPTURING, value)


def changedHideAutomatePatrol(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_PATROL, value)


def changedAutoPatrolMinimumAttackOdds(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_PATROL_MIN_COMBAT_ODDS, value)


def changedCanLeaveCity(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_DEFENSE_CAN_LEAVE_CITY, value)


def changedHideAutomateDefense(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_DEFENSE, value)


def changedAutoDefenseMinimumAttackOdds(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_DEFENSE_MIN_COMBAT_ODDS, value)


def changedAirUnitCanDefend(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_AIR_CAN_DEFEND, value)


def changedAirUnitCanRebase(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_AIR_CAN_REBASE, value)


def changedHideAirAutomations(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_AIR, value)


def changedHideAutoExplore(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_EXPLORE, value)


def changedHideAutoSpread(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_SPREAD, value)


def changedHideAutoCaravan(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_CARAVAN, value)


def changedHideAutoPirate(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_PIRATE, value)


def changedAutoPirateMinimumAttackOdds(option, value):
    _setPlayerOption(_MOD_OPT_AUTO_PIRATE_MIN_COMBAT_ODDS, value)


def changedHideAutoProtect(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_PROTECT, value)


def changedHideAutoUpgrade(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_UPGRADE, value)


def changedMostExpensive(option, value):
    _setPlayerOption(_MOD_OPT_UPGRADE_MOST_EXPENSIVE, value)


def changedMostExpierenced(option, value):
    _setPlayerOption(_MOD_OPT_UPGRADE_MOST_EXPERIENCED, value)


def changedMinimumUpgradeGold(option, value):
    _setPlayerOption(_MOD_OPT_UPGRADE_MIN_GOLD, value)


def changedHideAutoPromote(option, value):
    _setPlayerOption(_MOD_OPT_HIDE_AUTO_PROMOTE, value)


def setXMLOptionsfromIniFile():
    """Optimized initialization of automated settings"""
    print
    "Initializing Automated Settings"

    # Pre-cache BugOptions access to avoid repeated method calls
    automatedOptions = BugOptions.getOptions(_AUTOMATED_SETTINGS).options

    # Use direct iteration instead of range/len for Python 2.4 compatibility and efficiency
    for option in automatedOptions:
        if option.getKey() != _RESET_KEY:
            option.doDirties()


def resetOptions():
    """Optimized reset of all automated options"""
    # Pre-cache BugOptions access to avoid repeated method calls
    automatedOptions = BugOptions.getOptions(_AUTOMATED_SETTINGS).options

    # Reset all options efficiently using direct iteration
    for option in automatedOptions:
        option.resetValue()

    # Call initialization
    setXMLOptionsfromIniFile()
    AutomatedOpts.setReset(False)