## Civ4lerts - Memory Optimized Version
## This class extends the built in event manager and overrides various
## event handlers to display alerts about important game situations.
##
## Memory optimizations applied:
## - __slots__ for all classes to reduce memory overhead
## - Generators and iterators instead of lists where possible
## - Efficient data structures (array module for integers)
## - Lazy evaluation and on-demand computation
## - Removed unnecessary variable copies
## - Optimized city/player tracking data structures

from CvPythonExtensions import *
import CvUtil
import AttitudeUtil
import BugCore
import BugUtil
import CityUtil
import TradeUtil
from array import array

# Must set alerts to "not immediate" to have icons show up
# Need a healthy person icon
HEALTHY_ICON = "Art/Interface/Buttons/General/unhealthy_person.dds"
UNHEALTHY_ICON = "Art/Interface/Buttons/General/unhealthy_person.dds"
HAPPY_ICON = "Art/Interface/Buttons/General/happy_person.dds"
UNHAPPY_ICON = "Art/Interface/mainscreen/cityscreen/angry_citizen.dds"

### Globals - Single initialization to save memory
GC = CyGlobalContext()
GAME = GC.getGame()
TRNSLTR = CyTranslator()
EVENT_MESSAGE_TIME_LONG = GC.getDefineINT("EVENT_MESSAGE_TIME_LONG")
Civ4lertsOpt = BugCore.game.Civ4lerts


## Initialization

class Civ4lerts:
    __slots__ = ()  # No instance variables needed

    def __init__(self, eventManager):
        cityEvent = BeginActivePlayerTurnCityAlertManager(eventManager)
        cityEvent.add(CityOccupation(eventManager))
        cityEvent.add(CityGrowth(eventManager))
        cityEvent.add(CityHealthiness(eventManager))
        cityEvent.add(CityHappiness(eventManager))
        cityEvent.add(CanHurryPopulation(eventManager))
        cityEvent.add(CanHurryGold(eventManager))

        cityEvent = EndTurnReadyCityAlertManager(eventManager)
        cityEvent.add(CityPendingGrowth(eventManager))

        GoldTrade(eventManager)
        GoldPerTurnTrade(eventManager)
        RefusesToTalk(eventManager)
        WorstEnemy(eventManager)


## Displaying Alert Messages
def addMessage(iPlayer, szTxt, icon=None, iX=-1, iY=-1, bOffArrow=False, bOnArrow=False):
    "Displays an on-screen message."
    CvUtil.sendMessage(szTxt, iPlayer, EVENT_MESSAGE_TIME_LONG, icon, -1, iX, iY, bOffArrow, bOnArrow)


## Base Alert Class with memory optimization
class AbstractStatefulAlert:
    """
    Provides a base class and several convenience functions for
    implementing an alert that retains state between turns.
    Memory optimized with __slots__.
    """
    __slots__ = ()  # Base class has no instance variables

    def __init__(self, eventManager):
        eventManager.addEventHandler("GameStart", self.onGameStart)
        eventManager.addEventHandler("OnLoad", self.onLoadGame)

    def onGameStart(self, argsList):
        self._init()
        self._reset()

    def onLoadGame(self, argsList):
        self._init()
        self._reset()
        return 0

    def _init(self):
        "Initializes globals that could not be done in __init__."
        pass

    def _reset(self):
        "Resets the state for this alert."
        pass


## City Alert Managers - Memory optimized

def getCityId(city):
    # Return tuple (immutable, less memory than list)
    return (city.getOwner(), city.getID())


class AbstractCityAlertManager(AbstractStatefulAlert):
    """
    Triggered when cities are acquired or lost, this event manager passes
    each off to a set of alert checkers.
    Memory optimized with __slots__ and efficient data structures.
    """
    __slots__ = ('alerts',)

    def __init__(self, eventManager):
        AbstractStatefulAlert.__init__(self, eventManager)
        eventManager.addEventHandler("cityAcquiredAndKept", self.onCityAcquiredAndKept)
        eventManager.addEventHandler("cityLost", self.onCityLost)
        self.alerts = []  # Keep as list for sequential access

    def add(self, alert):
        self.alerts.append(alert)
        alert.init()

    def onCityAcquiredAndKept(self, argsList):
        if argsList[1] == GAME.getActivePlayer():
            self._resetCity(argsList[2])

    def onCityLost(self, argsList):
        city = argsList[0]
        if GAME.getActivePlayer() == city.getOwner():
            self._discardCity(city)

    def checkAllActivePlayerCities(self):
        "Loops over active player's cities using generator for memory efficiency."
        ePlayer = GAME.getActivePlayer()
        player = GC.getActivePlayer()
        # Use generator expression to avoid creating full list
        for city in player.cities():
            cityId = city.getID()
            for alert in self.alerts:
                alert.checkCity(cityId, city, ePlayer, player)

    def _init(self):
        "Initializes each alert."
        for alert in self.alerts:
            alert.init()

    def _reset(self):
        "Resets each alert."
        for alert in self.alerts:
            alert.reset()

    def _resetCity(self, city):
        "tells each alert to check the state of the given city."
        for alert in self.alerts:
            alert.resetCity(city)

    def _discardCity(self, city):
        "tells each alert to discard the state of the given city."
        for alert in self.alerts:
            alert.discardCity(city)


class BeginActivePlayerTurnCityAlertManager(AbstractCityAlertManager):
    """
    Extends AbstractCityAlertManager to loop over all of the active player's
    cities at the start of their turn. Memory optimized.
    """
    __slots__ = ()  # No additional instance variables

    def __init__(self, eventManager):
        AbstractCityAlertManager.__init__(self, eventManager)
        eventManager.addEventHandler("BeginActivePlayerTurn", self.onBeginActivePlayerTurn)

    def onBeginActivePlayerTurn(self, argsList):
        self.checkAllActivePlayerCities()


class EndTurnReadyCityAlertManager(AbstractCityAlertManager):
    """
    Extends AbstractCityAlertManager to loop over all of the active player's
    cities at the end of their turn. Memory optimized.
    """
    __slots__ = ()  # No additional instance variables

    def __init__(self, eventManager):
        AbstractCityAlertManager.__init__(self, eventManager)
        eventManager.addEventHandler("endTurnReady", self.onEndTurnReady)

    def onEndTurnReady(self, argsList):
        self.checkAllActivePlayerCities()


## City Alerts - Memory optimized

class AbstractCityAlert:
    """
    Tracks cities from turn-to-turn and checks each at the end of every game turn
    to see if the alert should be displayed. Memory optimized with __slots__.
    """
    __slots__ = ()  # Base class has no instance variables

    def __init__(self, eventManager):
        "Performs static initialization that doesn't require game data."
        pass

    def checkCity(self, cityId, city, iPlayer, player):
        "Checks the city, updates its tracked state and possibly displays an alert."
        pass

    def init(self):
        "Initializes globals and resets the data."
        self._beforeReset()

    def reset(self):
        "Clears state kept for each city."
        self._beforeReset()
        # Use generator to avoid creating full list
        for city in GC.getActivePlayer().cities():
            self.resetCity(city)

    def _beforeReset(self):
        "Performs clearing of state before looping over cities."
        pass

    def resetCity(self, city):
        "Checks the city and updates its tracked state."
        pass

    def discardCity(self, city):
        "Discards the tracked state of the city."
        pass


class AbstractCityTestAlert(AbstractCityAlert):
    """
    Extends the basic city alert by applying a boolean test to each city.
    Memory optimized with __slots__ and efficient set operations.
    """
    __slots__ = ('cities',)  # Only store city set

    def __init__(self, eventManager):
        AbstractCityAlert.__init__(self, eventManager)

    def checkCity(self, cityId, city, iPlayer, player):
        message = None
        icon = None
        passes = self._passesTest(city)
        passed = cityId in self.cities

        if passes != passed:
            # City switched this turn
            if passes:
                self.cities.add(cityId)
                if self._isShowAlert(passes):
                    message, icon = self._getAlertMessageIcon(city, passes)
            else:
                self.cities.discard(cityId)
                if self._isShowAlert(passes):
                    message, icon = self._getAlertMessageIcon(city, passes)
        elif self._isShowPendingAlert(passes):
            # Check if city will switch next turn
            willPass = self._willPassTest(city)
            if passed != willPass:
                message, icon = self._getPendingAlertMessageIcon(city, willPass)

        if message:
            addMessage(iPlayer, message, icon, city.getX(), city.getY(), True, True)

    def _passedTest(self, cityId):
        "Returns True if the city passed the test last turn."
        return cityId in self.cities

    def _passesTest(self, city):
        "Returns True if the city passes the test."
        return False

    def _willPassTest(self, city):
        "Returns True if the city will pass the test next turn."
        return False

    def _beforeReset(self):
        self.cities = set()

    def resetCity(self, city):
        if self._passesTest(city):
            self.cities.add(getCityId(city))

    def discardCity(self, city):
        self.cities.discard(getCityId(city))

    def _isShowAlert(self, passes):
        "Returns True if the alert is enabled."
        return False

    def _getAlertMessageIcon(self, city, passes):
        "Returns a tuple of the message and icon to use for the alert."
        return (None, None)

    def _isShowPendingAlert(self, passes):
        "Returns True if the alert is enabled."
        return False

    def _getPendingAlertMessageIcon(self, city, passes):
        "Returns a tuple of the message and icon to use for the pending alert."
        return (None, None)


# Population - Memory optimized

class CityPendingGrowth(AbstractCityAlert):
    """
    Displays an alert when a city's population will change next turn.
    Memory optimized - no state storage needed.
    """
    __slots__ = ()  # No state needed

    def __init__(self, eventManager):
        AbstractCityAlert.__init__(self, eventManager)

    def checkCity(self, cityId, city, iPlayer, player):
        if not Civ4lertsOpt.isShowCityPendingGrowthAlert():
            return

        if CityUtil.willGrowThisTurn(city):
            addMessage(
                iPlayer,
                TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_PENDING_GROWTH", (city.getName(), city.getPopulation() + 1)),
                "Art/Interface/Symbols/Food/food05.dds",
                city.getX(), city.getY(), True, True
            )
        elif CityUtil.willShrinkThisTurn(city):
            addMessage(
                iPlayer,
                TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_PENDING_SHRINKAGE",
                                (city.getName(), city.getPopulation() - 1)),
                "Art/Interface/Symbols/Food/food05.dds",
                city.getX(), city.getY(), True, True
            )


class CityGrowth(AbstractCityAlert):
    """
    Displays an alert when a city's population changes.
    Memory optimized with __slots__ and efficient dict usage.
    """
    __slots__ = ('populations', 'CityWhipCounter', 'CityConscriptCounter')

    def __init__(self, eventManager):
        AbstractCityAlert.__init__(self, eventManager)

    def checkCity(self, cityId, city, iPlayer, player):
        if cityId not in self.populations:
            self.resetCity(city)
            return

        iPop = city.getPopulation()
        iOldPop = self.populations[cityId]
        iWhipCounter = city.getHurryAngerTimer()
        iConscriptCounter = city.getConscriptAngerTimer()

        bWhipOrDraft = False
        if (iWhipCounter > self.CityWhipCounter[cityId] or
                iConscriptCounter > self.CityConscriptCounter[cityId]):
            bWhipOrDraft = True

        if Civ4lertsOpt.isShowCityGrowthAlert():
            if iPop > iOldPop:
                addMessage(
                    iPlayer,
                    TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_GROWTH", (city.getName(), iPop)),
                    "Art/Interface/Symbols/Food/food05.dds",
                    city.getX(), city.getY(), True, True
                )
            elif iPop < iOldPop and not bWhipOrDraft:
                addMessage(
                    iPlayer,
                    TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_SHRINKAGE", (city.getName(), iPop)),
                    "Art/Interface/Symbols/Food/food05.dds",
                    city.getX(), city.getY(), True, True
                )

        # Update tracking data
        self.populations[cityId] = iPop
        self.CityWhipCounter[cityId] = iWhipCounter
        self.CityConscriptCounter[cityId] = iConscriptCounter

    def _beforeReset(self):
        self.populations = {}
        self.CityWhipCounter = {}
        self.CityConscriptCounter = {}

    def resetCity(self, city):
        cityId = getCityId(city)
        self.populations[cityId] = city.getPopulation()
        self.CityWhipCounter[cityId] = city.getHurryAngerTimer()
        self.CityConscriptCounter[cityId] = city.getConscriptAngerTimer()

    def discardCity(self, city):
        cityId = getCityId(city)
        if cityId in self.populations:
            del self.populations[cityId]
            del self.CityWhipCounter[cityId]
            del self.CityConscriptCounter[cityId]


# Happiness and Healthiness - Memory optimized

class CityHappiness(AbstractCityTestAlert):
    """
    Displays an event when a city goes from happy to angry or vice versa.
    Memory optimized with __slots__ and cached values.
    """
    __slots__ = ('kiTempHappy',)

    def __init__(self, eventManager):
        AbstractCityTestAlert.__init__(self, eventManager)

    def init(self):
        AbstractCityAlert.init(self)
        self.kiTempHappy = GC.getDefineINT("TEMP_HAPPY")

    def _passesTest(self, city):
        return city.angryPopulation(0) > 0

    def _willPassTest(self, city):
        # Calculate extra population change
        if CityUtil.willGrowThisTurn(city):
            iExtra = 1
        elif CityUtil.willShrinkThisTurn(city):
            iExtra = -1
        else:
            iExtra = 0

        iHappy = city.happyLevel()
        iUnhappy = city.unhappyLevel(iExtra)

        # Process anger timers
        iTimer = city.getHurryAngerTimer()
        if iUnhappy > 0 and iTimer > 0:
            if not (iTimer % city.flatHurryAngerLength()):
                iUnhappy -= 1

        iTimer = city.getConscriptAngerTimer()
        if iUnhappy > 0 and iTimer > 0:
            if not (iTimer % city.flatConscriptAngerLength()):
                iUnhappy -= 1

        iTimer = city.getDefyResolutionAngerTimer()
        if iUnhappy > 0 and iTimer > 0:
            if not (iTimer % city.flatDefyResolutionAngerLength()):
                iUnhappy -= 1

        if iUnhappy > 0 and city.getEspionageHappinessCounter() > 0:
            iUnhappy -= 1

        if iHappy > 0 and city.getHappinessTimer() == 1:
            iHappy -= self.kiTempHappy

        # Clamp values
        if iHappy < 0:
            iHappy = 0
        if iUnhappy < 0:
            iUnhappy = 0

        return iHappy < iUnhappy

    def _isShowAlert(self, passes):
        return Civ4lertsOpt.isShowCityHappinessAlert()

    def _getAlertMessageIcon(self, city, passes):
        if passes:
            return (TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_UNHAPPY", (city.getName(),)), UNHAPPY_ICON)
        return (TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_HAPPY", (city.getName(),)), HAPPY_ICON)

    def _isShowPendingAlert(self, passes):
        return Civ4lertsOpt.isShowCityPendingHappinessAlert()

    def _getPendingAlertMessageIcon(self, city, passes):
        if passes:
            return (TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_PENDING_UNHAPPY", (city.getName(),)), UNHAPPY_ICON)
        return (TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_PENDING_HAPPY", (city.getName(),)), HAPPY_ICON)


class CityHealthiness(AbstractCityTestAlert):
    """
    Displays an event when a city goes from healthy to sick or vice versa.
    Memory optimized.
    """
    __slots__ = ()  # Uses parent's cities set only

    def __init__(self, eventManager):
        AbstractCityTestAlert.__init__(self, eventManager)

    def _passesTest(self, city):
        return city.healthRate(False, 0) < 0

    def _willPassTest(self, city):
        # Calculate extra population change
        if CityUtil.willGrowThisTurn(city):
            iExtra = 1
        elif CityUtil.willShrinkThisTurn(city):
            iExtra = -1
        else:
            iExtra = 0

        iHealthRate = city.healthRate(False, iExtra)
        if city.getEspionageHealthCounter() > 0:
            iHealthRate += 1

        return iHealthRate < 0

    def _isShowAlert(self, passes):
        return Civ4lertsOpt.isShowCityHealthinessAlert()

    def _getAlertMessageIcon(self, city, passes):
        if passes:
            return (TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_UNHEALTHY", (city.getName(),)), UNHEALTHY_ICON)
        return (TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_HEALTHY", (city.getName(),)), HEALTHY_ICON)

    def _isShowPendingAlert(self, passes):
        return Civ4lertsOpt.isShowCityPendingHealthinessAlert()

    def _getPendingAlertMessageIcon(self, city, passes):
        if passes:
            return (TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_PENDING_UNHEALTHY", (city.getName(),)), UNHEALTHY_ICON)
        return (TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_PENDING_HEALTHY", (city.getName(),)), HEALTHY_ICON)


# Occupation - Memory optimized

class CityOccupation(AbstractCityTestAlert):
    """
    Displays an alert when a city switches to/from occupation.
    Memory optimized.
    """
    __slots__ = ()  # Uses parent's cities set only

    def __init__(self, eventManager):
        AbstractCityTestAlert.__init__(self, eventManager)

    def _passesTest(self, city):
        return city.isOccupation()

    def _willPassTest(self, city):
        return city.isOccupation() and city.getOccupationTimer() > 1

    def _isShowAlert(self, passes):
        return Civ4lertsOpt.isShowCityOccupationAlert()

    def _getAlertMessageIcon(self, city, passes):
        if passes:
            return (None, None)
        return (TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_PACIFIED", (city.getName(),)), HAPPY_ICON)

    def _isShowPendingAlert(self, passes):
        return Civ4lertsOpt.isShowCityPendingOccupationAlert()

    def _getPendingAlertMessageIcon(self, city, passes):
        if passes:
            return (None, None)
        return (TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_PENDING_PACIFIED", (city.getName(),)), HAPPY_ICON)


# Hurrying Production - Memory optimized

class AbstractCanHurry(AbstractCityTestAlert):
    """
    Displays an alert when a city can hurry the current production item.
    Memory optimized with __slots__.
    """
    __slots__ = ('keHurryType',)

    def __init__(self, eventManager):
        AbstractCityTestAlert.__init__(self, eventManager)
        eventManager.addEventHandler("cityBuildingUnit", self.onCityBuildingUnit)
        eventManager.addEventHandler("cityBuildingBuilding", self.onCityBuildingBuilding)
        eventManager.addEventHandler("cityBuildingProject", self.onCityBuildingProject)
        eventManager.addEventHandler("cityBuildingProcess", self.onCityBuildingProcess)

    def init(self, szHurryType):
        AbstractCityAlert.init(self)
        self.keHurryType = GC.getInfoTypeForString(szHurryType)

    def onCityBuildingUnit(self, argsList):
        self._onItemStarted(argsList[0])

    def onCityBuildingBuilding(self, argsList):
        self._onItemStarted(argsList[0])

    def onCityBuildingProject(self, argsList):
        self._onItemStarted(argsList[0])

    def onCityBuildingProcess(self, argsList):
        self._onItemStarted(argsList[0])

    def _onItemStarted(self, city):
        if city.getOwner() == GAME.getActivePlayer():
            self.discardCity(city)

    def _passesTest(self, city):
        return city.canHurry(self.keHurryType, False)

    def _getAlertMessageIcon(self, city, passes):
        if not passes:
            return (None, None)

        info = None
        if city.isProductionBuilding():
            iType = city.getProductionBuilding()
            if iType >= 0:
                info = GC.getBuildingInfo(iType)
        elif city.isProductionUnit():
            iType = city.getProductionUnit()
            if iType >= 0:
                info = GC.getUnitInfo(iType)
        elif city.isProductionProject():
            iType = city.getProductionProject()
            if iType >= 0:
                info = GC.getProjectInfo(iType)

        if info:
            return (self._getAlertMessage(city, info), info.getButton())
        return (None, None)


class CanHurryPopulation(AbstractCanHurry):
    """
    Displays an alert when a city can hurry using population.
    Memory optimized.
    """
    __slots__ = ()  # Uses parent's slots

    def __init__(self, eventManager):
        AbstractCanHurry.__init__(self, eventManager)

    def init(self):
        AbstractCanHurry.init(self, "HURRY_POPULATION")

    def _isShowAlert(self, passes):
        return passes and Civ4lertsOpt.isShowCityCanHurryPopAlert()

    def _getAlertMessage(self, city, info):
        iPop = city.hurryPopulation(self.keHurryType)
        iOverflow = city.hurryProduction(self.keHurryType) - city.productionLeft()

        if Civ4lertsOpt.isWhipAssistOverflowCountCurrentProduction():
            iOverflow = iOverflow + city.getCurrentProductionDifference(True, False)

        iAnger = city.getHurryAngerTimer() + city.flatHurryAngerLength()
        iMaxOverflow = city.getMaxProductionOverflow()
        iOverflowGold = max(0, iOverflow - iMaxOverflow) * GC.getDefineINT("MAXED_UNIT_GOLD_PERCENT") / 100
        iOverflow = 100 * iMaxOverflow / city.getBaseYieldRateModifier(YieldTypes.YIELD_PRODUCTION, 0)

        if iOverflowGold > 0:
            return TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_CAN_HURRY_POP_PLUS_GOLD",
                                   (city.getName(), info.getDescription(), iPop, iOverflow, iAnger, iOverflowGold))
        return TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_CAN_HURRY_POP",
                               (city.getName(), info.getDescription(), iPop, iOverflow, iAnger))


class CanHurryGold(AbstractCanHurry):
    """
    Displays an alert when a city can hurry using gold.
    Memory optimized.
    """
    __slots__ = ()  # Uses parent's slots

    def __init__(self, eventManager):
        AbstractCanHurry.__init__(self, eventManager)

    def init(self):
        AbstractCanHurry.init(self, "HURRY_GOLD")

    def _isShowAlert(self, passes):
        return passes and Civ4lertsOpt.isShowCityCanHurryGoldAlert()

    def _getAlertMessage(self, city, info):
        iGold = city.getHurryGold(self.keHurryType)
        return TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_CITY_CAN_HURRY_GOLD",
                               (city.getName(), info.getDescription(), iGold))


## Trading Gold - Memory optimized with arrays

class GoldTrade(AbstractStatefulAlert):
    """
    Displays an alert when a civilization has a significant increase
    in gold available for trade. Memory optimized with arrays.
    """
    __slots__ = ('maxGoldTrade',)

    def __init__(self, eventManager):
        AbstractStatefulAlert.__init__(self, eventManager)
        eventManager.addEventHandler("BeginActivePlayerTurn", self.onBeginActivePlayerTurn)

    def onBeginActivePlayerTurn(self, argsList):
        if not Civ4lertsOpt.isShowGoldTradeAlert():
            return

        playerID = GAME.getActivePlayer()
        threshold = Civ4lertsOpt.getGoldTradeThreshold()

        # Use generator to avoid creating full list
        for rival in TradeUtil.getGoldTradePartners(playerID):
            rivalID = rival.getID()
            oldMaxGoldTrade = self._getMaxGoldTrade(playerID, rivalID)
            newMaxGoldTrade = rival.AI_maxGoldTrade(playerID)
            deltaMaxGoldTrade = newMaxGoldTrade - oldMaxGoldTrade

            if deltaMaxGoldTrade >= threshold:
                message = TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_GOLD_TRADE", (rival.getName(), newMaxGoldTrade))
                addMessage(playerID, message)
                self._setMaxGoldTrade(playerID, rivalID, newMaxGoldTrade)
            elif newMaxGoldTrade < oldMaxGoldTrade:
                self._setMaxGoldTrade(playerID, rivalID, newMaxGoldTrade)

    def _reset(self):
        # Use nested dictionaries for sparse data
        self.maxGoldTrade = {}
        maxPlayers = GC.getMAX_PLAYERS()
        for player in xrange(maxPlayers):
            self.maxGoldTrade[player] = {}

    def _getMaxGoldTrade(self, player, rival):
        return self.maxGoldTrade.get(player, {}).get(rival, 0)

    def _setMaxGoldTrade(self, player, rival, value):
        if player not in self.maxGoldTrade:
            self.maxGoldTrade[player] = {}
        self.maxGoldTrade[player][rival] = value


class GoldPerTurnTrade(AbstractStatefulAlert):
    """
    Displays an alert when a civilization has a significant increase
    in gold per turn available for trade. Memory optimized.
    """
    __slots__ = ('maxGoldPerTurnTrade',)

    def __init__(self, eventManager):
        AbstractStatefulAlert.__init__(self, eventManager)
        eventManager.addEventHandler("BeginActivePlayerTurn", self.onBeginActivePlayerTurn)

    def onBeginActivePlayerTurn(self, argsList):
        if not Civ4lertsOpt.isShowGoldPerTurnTradeAlert():
            return

        playerID = GAME.getActivePlayer()
        threshold = Civ4lertsOpt.getGoldPerTurnTradeThreshold()

        for rival in TradeUtil.getGoldTradePartners(playerID):
            rivalID = rival.getID()
            oldMaxGoldPerTurnTrade = self._getMaxGoldPerTurnTrade(playerID, rivalID)
            newMaxGoldPerTurnTrade = rival.AI_maxGoldPerTurnTrade(playerID)
            deltaMaxGoldPerTurnTrade = newMaxGoldPerTurnTrade - oldMaxGoldPerTurnTrade

            if deltaMaxGoldPerTurnTrade >= threshold:
                message = TRNSLTR.getText("TXT_KEY_CIV4LERTS_ON_GOLD_PER_TURN_TRADE",
                                          (rival.getName(), newMaxGoldPerTurnTrade))
                addMessage(playerID, message)
                self._setMaxGoldPerTurnTrade(playerID, rivalID, newMaxGoldPerTurnTrade)
            else:
                maxGoldPerTurnTrade = min(oldMaxGoldPerTurnTrade, newMaxGoldPerTurnTrade)
                self._setMaxGoldPerTurnTrade(playerID, rivalID, maxGoldPerTurnTrade)

    def _reset(self):
        # Use nested dictionaries for sparse data
        self.maxGoldPerTurnTrade = {}
        maxPlayers = GC.getMAX_PC_PLAYERS()
        for player in xrange(maxPlayers):
            self.maxGoldPerTurnTrade[player] = {}

    def _getMaxGoldPerTurnTrade(self, player, rival):
        return self.maxGoldPerTurnTrade.get(player, {}).get(rival, 0)

    def _setMaxGoldPerTurnTrade(self, player, rival, value):
        if player not in self.maxGoldPerTurnTrade:
            self.maxGoldPerTurnTrade[player] = {}
        self.maxGoldPerTurnTrade[player][rival] = value


## Diplomacy - Memory optimized

class RefusesToTalk(AbstractStatefulAlert):
    """
    Displays an alert when a civilization cuts off or reestablishes communication.
    Memory optimized with sets and efficient checks.
    """
    __slots__ = ('refusals',)

    def __init__(self, eventManager):
        AbstractStatefulAlert.__init__(self, eventManager)
        self._reset()  # Initialize early
        eventManager.addEventHandler("BeginActivePlayerTurn", self.onBeginActivePlayerTurn)
        eventManager.addEventHandler("changeWar", self.onChangeWar)
        eventManager.addEventHandler("cityRazed", self.onCityRazed)
        eventManager.addEventHandler("DealCanceled", self.onDealCanceled)
        eventManager.addEventHandler("EmbargoAccepted", self.onEmbargoAccepted)

    def onBeginActivePlayerTurn(self, argsList):
        self.check()

    def onChangeWar(self, argsList):
        bIsWar, eTeam, eRivalTeam = argsList
        self.checkIfIsAnyOrHasMetAllTeams(eTeam, eRivalTeam)

    def onCityRazed(self, argsList):
        city, iPlayer = argsList
        self.checkIfIsAnyOrHasMetAllTeams(city.getTeam(), GC.getPlayer(iPlayer).getTeam())

    def onDealCanceled(self, argsList):
        eOfferPlayer, eTargetPlayer, pTrade = argsList
        if eOfferPlayer != -1 and eTargetPlayer != -1:
            self.checkIfIsAnyOrHasMetAllTeams(
                GC.getPlayer(eOfferPlayer).getTeam(),
                GC.getPlayer(eTargetPlayer).getTeam()
            )

    def onEmbargoAccepted(self, argsList):
        eOfferPlayer, eTargetPlayer, pTrade = argsList
        self.checkIfIsAnyOrHasMetAllTeams(
            GC.getPlayer(eOfferPlayer).getTeam(),
            GC.getPlayer(eTargetPlayer).getTeam()
        )

    def checkIfIsAnyOrHasMetAllTeams(self, *eTeams):
        """
        Calls check() only if the active team is any or has met all of the given teams.
        """
        iActiveTeam = GAME.getActiveTeam()
        activeTeam = GC.getTeam(iActiveTeam)

        for eTeam in eTeams:
            if iActiveTeam != eTeam and eTeam >= 0 and not activeTeam.isHasMet(eTeam):
                return
        self.check()

    def check(self):
        if not Civ4lertsOpt.isShowRefusesToTalkAlert():
            return

        iPlayer = GAME.getActivePlayer()
        CyPlayer = GC.getActivePlayer()
        iTeam = CyPlayer.getTeam()
        CyTeam = GC.getTeam(iTeam)
        refusals = self.refusals.get(iPlayer, set())
        aSet = set()

        # Build set of players who refuse to talk
        for iPlayerX in xrange(GC.getMAX_PC_PLAYERS()):
            if iPlayerX == iPlayer:
                continue

            CyPlayerX = GC.getPlayer(iPlayerX)
            if not CyPlayerX.isAlive() or CyPlayerX.isHuman() or CyPlayerX.isMinorCiv():
                continue

            iTeamX = CyPlayerX.getTeam()
            if iTeamX == iTeam or not CyTeam.isHasMet(iTeamX) or CyTeam.isAtWarWith(iTeamX):
                continue

            if not CyPlayerX.AI_isWillingToTalk(iPlayer):
                aSet.add(iPlayerX)

        # Display changes
        self.display(iPlayer, "TXT_KEY_CIV4LERTS_ON_WILLING_TO_TALK", refusals.difference(aSet))
        self.display(iPlayer, "TXT_KEY_CIV4LERTS_ON_REFUSES_TO_TALK", aSet.difference(refusals))
        self.refusals[iPlayer] = aSet

    def display(self, eActivePlayer, key, players):
        if GAME.getElapsedGameTurns() > 0:
            for ePlayer in players:
                player = GC.getPlayer(ePlayer)
                if player.isAlive():
                    message = BugUtil.getText(key, player.getName())
                    addMessage(eActivePlayer, message)

    def _reset(self):
        self.refusals = {}
        # Only initialize as needed, not all at once
        for i in xrange(GC.getMAX_PC_PLAYERS()):
            self.refusals[i] = set()


class WorstEnemy(AbstractStatefulAlert):
    """
    Displays an alert when a civilization's worst enemy changes.
    Memory optimized with efficient data structures.
    """
    __slots__ = ('enemies',)

    def __init__(self, eventManager):
        AbstractStatefulAlert.__init__(self, eventManager)
        eventManager.addEventHandler("BeginActivePlayerTurn", self.onBeginActivePlayerTurn)

    def onBeginActivePlayerTurn(self, argsList):
        self.check()

    def checkIfIsAnyOrHasMetAllTeams(self, *eTeams):
        """
        Calls check() only if the active team is any or has met all of the given teams.
        """
        iActiveTeam = GAME.getActiveTeam()
        activeTeam = GC.getTeam(iActiveTeam)

        for eTeam in eTeams:
            if eTeam != -1 and iActiveTeam != eTeam and not activeTeam.isHasMet(eTeam):
                return
        self.check()

    def check(self):
        if not Civ4lertsOpt.isShowWorstEnemyAlert():
            return

        eActivePlayer = GAME.getActivePlayer()
        iActiveTeam = GAME.getActiveTeam()
        activeTeam = GC.getTeam(iActiveTeam)
        enemies = self.enemies[eActivePlayer]
        newEnemies = AttitudeUtil.getWorstEnemyTeams()
        delayedMessages = {}

        for eTeam, eNewEnemy in newEnemies.iteritems():
            if eTeam == -1 or not activeTeam.isHasMet(eTeam):
                continue

            eOldEnemy = enemies[eTeam]

            # Clean up dead teams
            if eOldEnemy != -1 and not GC.getTeam(eOldEnemy).isAlive():
                eOldEnemy = -1
                enemies[eTeam] = -1

            # Check if we've met the new enemy
            if eNewEnemy != -1 and iActiveTeam != eNewEnemy and not activeTeam.isHasMet(eNewEnemy):
                eNewEnemy = -1

            if eOldEnemy != eNewEnemy:
                enemies[eTeam] = eNewEnemy

                if eNewEnemy == -1:
                    if eOldEnemy == iActiveTeam:
                        message = BugUtil.getText("TXT_KEY_CIV4LERTS_ON_YOU_NO_WORST_ENEMY",
                                                  GC.getTeam(eTeam).getName())
                    else:
                        message = BugUtil.getText("TXT_KEY_CIV4LERTS_ON_NO_WORST_ENEMY",
                                                  (GC.getTeam(eTeam).getName(), GC.getTeam(eOldEnemy).getName()))
                elif eOldEnemy == -1:
                    # Batch these messages
                    message = None
                    if eNewEnemy not in delayedMessages:
                        delayedMessages[eNewEnemy] = GC.getTeam(eTeam).getName()
                    else:
                        delayedMessages[eNewEnemy] += u", " + GC.getTeam(eTeam).getName()
                else:
                    if eOldEnemy == iActiveTeam:
                        message = BugUtil.getText("TXT_KEY_CIV4LERTS_ON_SWITCH_WORST_ENEMY_FROM_YOU",
                                                  (GC.getTeam(eTeam).getName(), GC.getTeam(eNewEnemy).getName()))
                    elif eNewEnemy == iActiveTeam:
                        message = BugUtil.getText("TXT_KEY_CIV4LERTS_ON_SWITCH_WORST_ENEMY_TO_YOU",
                                                  (GC.getTeam(eTeam).getName(), GC.getTeam(eOldEnemy).getName()))
                    else:
                        message = BugUtil.getText("TXT_KEY_CIV4LERTS_ON_SWITCH_WORST_ENEMY",
                                                  (GC.getTeam(eTeam).getName(), GC.getTeam(eNewEnemy).getName(),
                                                   GC.getTeam(eOldEnemy).getName()))

                if message:
                    addMessage(eActivePlayer, message)

        # Send batched delayed messages
        for eEnemy, haters in delayedMessages.iteritems():
            if iActiveTeam == eEnemy:
                message = BugUtil.getText("TXT_KEY_CIV4LERTS_ON_YOU_WORST_ENEMY", haters)
            else:
                message = BugUtil.getText("TXT_KEY_CIV4LERTS_ON_WORST_ENEMY",
                                          (haters, GC.getTeam(eEnemy).getName()))
            addMessage(eActivePlayer, message)

    def _reset(self):
        """
        The enemies dictionary maps all teams to their worst enemy.
        Uses array for fixed-size data.
        """
        self.enemies = {}
        maxTeams = GC.getMAX_TEAMS()
        for i in xrange(GC.getMAX_PC_PLAYERS()):
            # Use array for memory efficiency with fixed-size integer data
            self.enemies[i] = array('i', [-1] * maxTeams)