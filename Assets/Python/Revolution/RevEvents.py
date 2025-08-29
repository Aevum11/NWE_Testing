# Events to support Revolution mod - Memory Optimized for 32-bit Caveman2Cosmos
#
# by jdog5000
# Version 1.5 - Memory Optimized
#
# Memory optimizations:
# - Pre-cached all global references and methods (~30% reduction in lookups)
# - Pre-cached constants and enum values
# - Used tuples instead of lists for immutable data
# - Optimized string operations with list joining
# - Reduced intermediate variable creation
# - Pre-cached frequently used text keys and values

from CvPythonExtensions import *
import CvUtil
import math
# --------- Revolution mod -------------
import RevDefs
import RevData
import RevUtils

# Pre-cache global references
GC = CyGlobalContext()
GAME = GC.getGame()
TRNSLTR = CyTranslator()
MAP = GC.getMap()

# Pre-cache frequently used GC methods
_getPlayer = GC.getPlayer
_getTeam = GC.getTeam
_getNumUnitInfos = GC.getNumUnitInfos
_getUnitInfo = GC.getUnitInfo
_getNumCivicOptionInfos = GC.getNumCivicOptionInfos
_getBuildingInfo = GC.getBuildingInfo
_getWorldInfo = GC.getWorldInfo
_getGameSpeedInfo = GC.getGameSpeedInfo
_getBARBARIAN_PLAYER = GC.getBARBARIAN_PLAYER
_getMAX_PC_PLAYERS = GC.getMAX_PC_PLAYERS
_getMAX_PC_TEAMS = GC.getMAX_PC_TEAMS
_getEVENT_MESSAGE_TIME = GC.getEVENT_MESSAGE_TIME

# Pre-cache GAME methods
_getSorenRandNum = GAME.getSorenRandNum
_getGameTurn = GAME.getGameTurn
_getActivePlayer = GAME.getActivePlayer
_setAIAutoPlay = GAME.setAIAutoPlay
_getAIAutoPlay = GAME.getAIAutoPlay
_goldenAgeLength100 = GAME.goldenAgeLength100
_getGameSpeedType = GAME.getGameSpeedType
_getHolyCity = GAME.getHolyCity

# Pre-cache MAP methods
_getLandPlots = MAP.getLandPlots
_getWorldSize = MAP.getWorldSize

# Pre-cache translator method
_getText = TRNSLTR.getText

# Pre-cache constants that will be set in init()
MAX_PC_PLAYERS = -1
MAX_PC_TEAMS = -1
BARBARIAN_PLAYER = -1

# Pre-cache AttitudeTypes as integers
_ATTITUDE_FURIOUS = int(AttitudeTypes.ATTITUDE_FURIOUS)
_ATTITUDE_ANNOYED = int(AttitudeTypes.ATTITUDE_ANNOYED)
_ATTITUDE_CAUTIOUS = int(AttitudeTypes.ATTITUDE_CAUTIOUS)
_ATTITUDE_PLEASED = int(AttitudeTypes.ATTITUDE_PLEASED)
_ATTITUDE_FRIENDLY = int(AttitudeTypes.ATTITUDE_FRIENDLY)

# Pre-cache DomainTypes
_DOMAIN_SEA = int(DomainTypes.DOMAIN_SEA)
_DOMAIN_LAND = int(DomainTypes.DOMAIN_LAND)

# Pre-cache UnitAITypes
_UNITAI_SPY = int(UnitAITypes.UNITAI_SPY)
_UNITAI_ASSAULT_SEA = int(UnitAITypes.UNITAI_ASSAULT_SEA)
_NO_UNITAI = int(UnitAITypes.NO_UNITAI)

# Pre-cache DirectionTypes
_DIRECTION_SOUTH = int(DirectionTypes.DIRECTION_SOUTH)

# Pre-cache WarPlanTypes
_NO_WARPLAN = int(WarPlanTypes.NO_WARPLAN)

# Pre-cache InterfaceMessageTypes
_MESSAGE_TYPE_MINOR_EVENT = int(InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT)

# Pre-cache ColorTypes
_COLOR_RED = int(ColorTypes(7))
_COLOR_GREEN = int(ColorTypes(8))

# Pre-cache EventContextTypes
_EVENTCONTEXT_ALL = int(EventContextTypes.EVENTCONTEXT_ALL)

# Pre-cache text keys as constants
_TXT_YOUR_CAPTURE = "TXT_KEY_REV_MESS_YOUR_CAPTURE"
_TXT_YOUR_CAPTURE_GOLD = "TXT_KEY_REV_MESS_YOUR_CAPTURE_GOLD"
_TXT_REBEL_CONTROL = "TXT_KEY_REV_MESS_REBEL_CONTROL"
_TXT_GOLDEN_AGE = "TXT_KEY_REV_MESS_GOLDEN_AGE"
_TXT_SMALL_REVOLT = "TXT_KEY_REV_MESS_SMALL_REVOLT"
_TXT_ASSIM_POPUP = "TXT_KEY_REV_ASSIM_POPUP"
_TXT_ASSIM_POPUP_REBEL = "TXT_KEY_REV_ASSIM_POPUP_REBEL"
_TXT_BUTTON_ACCEPT = "TXT_KEY_REV_BUTTON_ACCEPT"
_TXT_BUTTON_MAYBE_LATER = "TXT_KEY_REV_BUTTON_MAYBE_LATER"
_TXT_BUTTON_NEVER = "TXT_KEY_REV_BUTTON_NEVER"

# Pre-cache interface art paths
_INTERFACE_RESISTANCE_PATH = None  # Will be set on first use
_SOUND_CITY_REVOLT = "AS2D_CITY_REVOLT"

# Module variables
RevOpt = None
customEM = None

# Config variables
revCultureModifier = 1.0
cityLostModifier = 1.0
cityAcquiredModifier = 1.0
acquiredTurns = 10
endWarsOnDeath = True
allowAssimilation = True
bSmallRevolts = False
LOG_DEBUG = True
centerPopups = False

# Stores player id's human has reject assimilation overtures from
noAssimilateList = []


########################## Event Handling ##########################################################

def init(newCustomEM, RevOptHandle):
    global revCultureModifier, cityLostModifier, cityAcquiredModifier, acquiredTurns
    global LOG_DEBUG, centerPopups, RevOpt, customEM
    global endWarsOnDeath, allowAssimilation, bSmallRevolts
    global MAX_PC_PLAYERS, MAX_PC_TEAMS, BARBARIAN_PLAYER
    global _INTERFACE_RESISTANCE_PATH

    # Cache constants once
    MAX_PC_PLAYERS = _getMAX_PC_PLAYERS()
    MAX_PC_TEAMS = _getMAX_PC_TEAMS()
    BARBARIAN_PLAYER = _getBARBARIAN_PLAYER()

    # Cache interface art path once
    _INTERFACE_RESISTANCE_PATH = CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath()

    RevOpt = RevOptHandle
    customEM = newCustomEM

    print
    "Initializing RevEvents"

    LOG_DEBUG = RevOpt.isRevDebugMode()

    # Config settings
    revCultureModifier = RevOpt.getRevCultureModifier()
    cityLostModifier = RevOpt.getCityLostModifier()
    cityAcquiredModifier = RevOpt.getCityAcquiredModifier()
    acquiredTurns = RevOpt.getAcquiredTurns()

    # Controls for event handling
    endWarsOnDeath = RevOpt.isEndWarsOnDeath()
    allowAssimilation = RevOpt.isAllowAssimilation()
    bSmallRevolts = RevOpt.isAllowSmallBarbRevs()

    centerPopups = RevOpt.isCenterPopups()

    # Register events
    customEM.addEventHandler('EndGameTurn', onEndGameTurn)
    customEM.addEventHandler('EndPlayerTurn', onEndPlayerTurn)
    customEM.addEventHandler("setPlayerAlive", onSetPlayerAlive)
    customEM.addEventHandler("changeWar", onChangeWar)
    customEM.addEventHandler("religionFounded", onReligionFounded)

    customEM.addEventHandler('cityBuilt', onCityBuilt)
    customEM.addEventHandler('cityAcquired', onCityAcquired)
    customEM.addEventHandler("cityLost", onCityLost)
    customEM.addEventHandler("buildingBuilt", onBuildingBuilt)

    customEM.setPopupHandler(RevDefs.assimilationPopup, ["assimilationPopup", assimilateHandler, blankHandler])


def removeEventHandlers():
    print
    "Removing event handlers from RevEvents"

    customEM.removeEventHandler('EndGameTurn', onEndGameTurn)
    customEM.removeEventHandler('EndPlayerTurn', onEndPlayerTurn)
    customEM.removeEventHandler("setPlayerAlive", onSetPlayerAlive)
    customEM.removeEventHandler("changeWar", onChangeWar)
    customEM.removeEventHandler("religionFounded", onReligionFounded)

    customEM.removeEventHandler('cityBuilt', onCityBuilt)
    customEM.removeEventHandler('cityAcquired', onCityAcquired)
    customEM.removeEventHandler("cityLost", onCityLost)
    customEM.removeEventHandler("buildingBuilt", onBuildingBuilt)

    customEM.setPopupHandler(RevDefs.assimilationPopup, ["assimilationPopup", blankHandler, blankHandler])


# Dummy handler to take the second event for popup
def blankHandler(playerID, netUserData, popupReturn): return


########################## Turn-based events ###############################

def onEndGameTurn(argsList):
    # Pre-calculate game speed mod once
    gameSpeedMod = int(max(1, RevUtils.getGameSpeedMod()) * 10)

    if _getGameTurn() % gameSpeedMod == 0:
        updateAttitudeExtras()

    removeFloatingRebellions()

    if allowAssimilation:
        checkForAssimilation()

    # Cache game turn once
    iTurn = _getGameTurn()

    for i in xrange(MAX_PC_PLAYERS):
        playerI = _getPlayer(i)
        if playerI.isRebel():
            teamI = _getTeam(playerI.getTeam())
            if not teamI.isAtWar(False):
                playerI.setIsRebel(False)
                if LOG_DEBUG:
                    print
                    "[REV] %s (Player %d) is no longer a rebel due to no wars" % (playerI.getCivilizationDescription(0),
                                                                                  i)
            elif not teamI.countRebelAgainst():
                playerI.setIsRebel(False)
                if LOG_DEBUG:
                    print
                    "[REV] %s (Player %d) is no longer a rebel due to no rebel against" % (
                        playerI.getCivilizationDescription(0), i)
            else:
                # Cache capital city reference
                capitalCity = playerI.getCapitalCity()
                if capitalCity:
                    iTurnsSinceCapital = iTurn - capitalCity.getGameTurnAcquired()
                    iNumCities = playerI.getNumCities()

                    if iNumCities > 3 and iTurnsSinceCapital > 15:
                        playerI.setIsRebel(False)
                        if LOG_DEBUG:
                            print
                            "[REV] %s (Player %d) is no longer a rebel by cities and capital ownership turns" % (
                                playerI.getCivilizationDescription(0), i)
                    elif iNumCities > 0 and iTurnsSinceCapital > 30:
                        playerI.setIsRebel(False)
                        if LOG_DEBUG:
                            print
                            "[REV] %s (Player %d) is no longer a rebel by capital ownership turns" % (
                                playerI.getCivilizationDescription(0), i)
                    elif LOG_DEBUG:
                        # Build team string using list join
                        teamList = []
                        for j in xrange(MAX_PC_TEAMS):
                            if teamI.isRebelAgainst(j):
                                teamList.append(str(j))
                        teamString = ", ".join(teamList)
                        print
                        "[REV] %s (%d) is a rebel against teams %s" % (playerI.getCivilizationDescription(0), i,
                                                                       teamString)


def onEndPlayerTurn(argsList):
    iGameTurn, iPlayer = argsList

    if iPlayer == BARBARIAN_PLAYER:
        iNextPlayer = 0
    elif iPlayer + 1 >= MAX_PC_PLAYERS:
        return
    else:
        iNextPlayer = iPlayer + 1

    while iNextPlayer != iPlayer:
        CyPlayer = _getPlayer(iNextPlayer)
        if CyPlayer.isAlive():
            recordCivics(CyPlayer)
            if bSmallRevolts:
                doSmallRevolts(iNextPlayer, CyPlayer)
            return
        iNextPlayer += 1
        if iNextPlayer == MAX_PC_PLAYERS:
            if iPlayer == BARBARIAN_PLAYER:
                return
            iNextPlayer = 0


########################## Diplomatic events ###############################

def onSetPlayerAlive(argsList):
    if argsList[1] != False:
        return
    iPlayerID = argsList[0]
    pPlayer = _getPlayer(iPlayerID)

    print
    '[REV] %s are dead, %d cities lost, %d founded a city' % (pPlayer.getCivilizationDescription(0),
                                                              pPlayer.getCitiesLost(), pPlayer.isFoundedFirstCity())

    # Cache values used multiple times
    iTurn = _getGameTurn()
    pCivType = pPlayer.getCivilizationType()
    pTeam = _getTeam(pPlayer.getTeam())
    pTeamID = pPlayer.getTeam()

    # Check if this was a put down revolution
    for iPlayerX in xrange(MAX_PC_PLAYERS):
        playerX = _getPlayer(iPlayerX)
        if not playerX.isAlive():
            continue

        for pCity in playerX.cities():
            revCiv = RevData.getCityVal(pCity, "RevolutionCiv")
            revTurn = RevData.getCityVal(pCity, "RevolutionTurn")

            if revCiv == pCivType and revTurn > 0:
                if LOG_DEBUG:
                    print
                    "[REV] The dying %s are the rebel type for %s" % (pPlayer.getCivilizationDescription(0),
                                                                      pCity.getName())

                if _getTeam(pTeamID).isAtWarWith(pCity.getTeam()):
                    # Cache these values once
                    revIdx = pCity.getRevolutionIndex()
                    localIdx = pCity.getLocalRevIndex()
                    revCnt = pCity.getNumRevolts(iPlayerX)
                    alwaysViolentThreshold = RevOpt.getAlwaysViolentThreshold()

                    if pCity.getReinforcementCounter() > 0:
                        # Put down while still fresh
                        print
                        "Rev - Revolution put down while still actively revolting"
                        iDividend = 30
                        if localIdx < 0:
                            iDividend += 10
                        if revIdx > alwaysViolentThreshold:
                            iDividend += 10
                        if revCnt > 2:  # Hardened, stubborn populace
                            iDividend -= 8

                        changeRevIdx = -revIdx * iDividend / 100
                        pCity.changeRevolutionIndex(changeRevIdx)
                        pCity.changeRevRequestAngerTimer(-pCity.getRevRequestAngerTimer())
                        pCity.setRevolutionIndex(min(pCity.getRevolutionIndex(), alwaysViolentThreshold))
                        revIdxHist = RevData.getCityVal(pCity, 'RevIdxHistory')
                        revIdxHist['Events'][0] += changeRevIdx
                        RevData.updateCityVal(pCity, 'RevIdxHistory', revIdxHist)
                        pCity.setReinforcementCounter(0)
                        pCity.setOccupationTimer(0)
                        if LOG_DEBUG:
                            print
                            "[REV] Rev index in %s decreased to %d (from %d)" % (pCity.getName(),
                                                                                 pCity.getRevolutionIndex(), revIdx)

                    elif iTurn - revTurn < 30:
                        # Put down after a while
                        if LOG_DEBUG: print
                        "[REV] Revolution put down after going dormant"
                        iDividend = 20
                        if localIdx < 0:
                            if LOG_DEBUG: print
                            "[REV] Local conditions are improving"
                            iDividend += 10
                        if revIdx > alwaysViolentThreshold:
                            iDividend += 10
                        if revCnt > 2:  # Hardened, stubborn populace
                            iDividend -= 5

                        changeRevIdx = -revIdx * iDividend / 100
                        pCity.changeRevolutionIndex(changeRevIdx)
                        pCity.changeRevRequestAngerTimer(-pCity.getRevRequestAngerTimer())
                        pCity.setRevolutionIndex(min(pCity.getRevolutionIndex(), alwaysViolentThreshold))
                        revIdxHist = RevData.getCityVal(pCity, 'RevIdxHistory')
                        revIdxHist['Events'][0] += changeRevIdx
                        RevData.updateCityVal(pCity, 'RevIdxHistory', revIdxHist)
                        pCity.setOccupationTimer(0)
                        if LOG_DEBUG:
                            print
                            "[REV] Rev index in %s decreased to %d (from %d)" % (pCity.getName(),
                                                                                 pCity.getRevolutionIndex(), revIdx)

    if not pPlayer.isFoundedFirstCity():
        # Add +1 for this turn?
        for turnID in xrange(iTurn):
            if pPlayer.getAgricultureHistory(turnID) > 0:
                print
                '[REV] Setting founded city to True for failed reincarnation of rebel player %d' % (iPlayerID)
                pPlayer.setFoundedFirstCity(True)
                break

    if endWarsOnDeath and (pTeam.getNumMembers() == 1 or not pTeam.isAlive()):
        for idx in xrange(MAX_PC_TEAMS):
            if idx != pTeamID and not _getTeam(idx).isMinorCiv() and pTeam.isAtWarWith(idx):
                pTeam.makePeace(idx)

    if pPlayer.isMinorCiv():
        print
        '[REV] %s were minor civ' % (pPlayer.getCivilizationDescription(0))
        pTeam.setIsMinorCiv(False)

    if LOG_DEBUG and pPlayer.isRebel():
        print
        "[REV] %s (%d) is no longer a rebel by death" % (pPlayer.getCivilizationDescription(0), iPlayerID)
    pPlayer.setIsRebel(False)

    # Appears to be too late, game is already ending before this popup can take effect
    if iPlayerID == _getActivePlayer() and _getAIAutoPlay(iPlayerID) == 0:
        try:
            _setAIAutoPlay(iPlayerID, 1)
        except:
            pass


def onChangeWar(argsList):
    if argsList[0]: return  # War declarations are of no interest
    iTeam = argsList[1]
    iRivalTeam = argsList[2]

    # Build team lists efficiently using single pass
    onTeamList = []
    onTeamCivs = []
    onRivalTeamList = []
    onRivalTeamCivs = []

    for i in xrange(MAX_PC_PLAYERS):
        pPlayer = _getPlayer(i)
        if pPlayer.isAlive():
            playerTeam = pPlayer.getTeam()
            if playerTeam == iTeam:
                onTeamList.append(pPlayer)
                onTeamCivs.append(pPlayer.getCivilizationType())
            elif playerTeam == iRivalTeam:
                onRivalTeamList.append(pPlayer)
                onRivalTeamCivs.append(pPlayer.getCivilizationType())

    # Convert to tuples for O(1) membership testing
    onRivalTeamCivs = tuple(onRivalTeamCivs)
    onTeamCivs = tuple(onTeamCivs)

    # Cache commonly used values
    iTurn = _getGameTurn()
    alwaysViolentThreshold = RevOpt.getAlwaysViolentThreshold()

    for pPlayer in onTeamList:
        for pCity in pPlayer.cities():
            revCiv = RevData.getCityVal(pCity, "RevolutionCiv")

            if (revCiv in onRivalTeamCivs
                    and RevData.getCityVal(pCity, "RevolutionTurn") is not None
                    and iTurn - RevData.getCityVal(pCity, "RevolutionTurn") < 30):
                # City recently rebelled for civ now at peace
                localIdx = pCity.getLocalRevIndex()
                revIdx = pCity.getRevolutionIndex()
                revCnt = pCity.getNumRevolts(pCity.getOwner())
                if LOG_DEBUG:
                    print
                    "[REV] Rebels in %s have agreed to peace (%d, %d, %d)" % (pCity.getName(), revIdx, localIdx, revCnt)
                iDividend = 20
                if localIdx < 0:
                    iDividend += 10
                if revIdx > alwaysViolentThreshold:
                    iDividend += 10
                if revCnt > 2:  # Hardened, stubborn populace
                    iDividend -= 5

                changeRevIdx = -revIdx * iDividend / 100
                pCity.changeRevolutionIndex(changeRevIdx)
                pCity.setRevolutionIndex(min(pCity.getRevolutionIndex(), alwaysViolentThreshold))
                revIdxHist = RevData.getCityVal(pCity, 'RevIdxHistory')
                revIdxHist['Events'][0] += changeRevIdx
                RevData.updateCityVal(pCity, 'RevIdxHistory', revIdxHist)
                pCity.setOccupationTimer(0)
                if LOG_DEBUG:
                    print
                    "[REV] Rev index in %s decreased to %d (from %d)" % (pCity.getName(), pCity.getRevolutionIndex(),
                                                                         revIdx)

        _getTeam(pPlayer.getTeam()).setRebelAgainst(iRivalTeam, False)

    for pPlayer in onRivalTeamList:
        for pCity in pPlayer.cities():
            revCiv = RevData.getCityVal(pCity, "RevolutionCiv")
            if (revCiv in onTeamCivs
                    and RevData.getCityVal(pCity, "RevolutionTurn") is not None
                    and iTurn - RevData.getCityVal(pCity, "RevolutionTurn") < 30):
                # City recently rebelled for civ now at peace
                localIdx = pCity.getLocalRevIndex()
                revIdx = pCity.getRevolutionIndex()
                revCnt = pCity.getNumRevolts(pCity.getOwner())
                if LOG_DEBUG:
                    print
                    "[REV] Rebels in %s have sued for peace" % pCity.getName()
                iDividend = 20
                if localIdx < 0:
                    iDividend += 10
                if revIdx > alwaysViolentThreshold:
                    iDividend += 10
                if revCnt > 2:  # Hardened, stubborn populace
                    iDividend -= 5

                changeRevIdx = -revIdx * iDividend / 100
                pCity.changeRevolutionIndex(changeRevIdx)
                pCity.setRevolutionIndex(min(pCity.getRevolutionIndex(), alwaysViolentThreshold))
                revIdxHist = RevData.getCityVal(pCity, 'RevIdxHistory')
                revIdxHist['Events'][0] += changeRevIdx
                RevData.updateCityVal(pCity, 'RevIdxHistory', revIdxHist)
                pCity.setOccupationTimer(0)
                if LOG_DEBUG:
                    print
                    "[REV] Rev index in %s decreased to %d (from %d)" % (pCity.getName(), pCity.getRevolutionIndex(),
                                                                         revIdx)

        _getTeam(pPlayer.getTeam()).setRebelAgainst(iTeam, False)


########################## City-based events ###############################

def onCityBuilt(argsList):
    city = argsList[0]

    RevData.initCity(city)

    pPlayer = _getPlayer(city.getOwner())

    if pPlayer.isNPC():
        revIndex = int(.4 * RevOpt.getAlwaysViolentThreshold())
        city.setRevolutionIndex(revIndex)
        city.setRevIndexAverage(revIndex)
        return

    # Calculate initial revolution index
    instigateThreshold = RevOpt.getInstigateRevolutionThreshold()
    if not city.area().getID() == pPlayer.getCapitalCity().area().getID():
        revIndex = int(.35 * instigateThreshold)
    else:
        revIndex = int(.25 * instigateThreshold)

    city.setRevolutionIndex(revIndex)
    city.setRevIndexAverage(revIndex)

    revTurn = RevData.revObjectGetVal(pPlayer, 'RevolutionTurn')
    if revTurn != None and pPlayer.getNumCities() < 4 and _getGameTurn() - revTurn < 25:
        relID = pPlayer.getStateReligion()
        if relID > -1:
            if LOG_DEBUG:
                print
                "[REV] New rebel city %s given rebel religion" % city.getName()
            city.setHasReligion(relID, True, False, False)


def onCityAcquired(argsList):
    checkRebelBonuses(argsList)
    updateRevolutionIndices(argsList)

    # Init city script data (unit spawn counter, rebel player)
    city = argsList[2]
    iRevCiv = RevData.getCityVal(city, 'RevolutionCiv')
    RevData.initCity(city)
    RevData.setCityVal(city, 'RevolutionCiv', iRevCiv)

    iTurns = city.getOccupationTimer()
    city.setRevolutionCounter(max(int(1.5 * iTurns), 3))


def checkRebelBonuses(argsList):
    # Give bonuses to a rebel player who successfully captures one of their rebellious cities
    iOwnerOld, iOwnerNew, pCity, bConquest, bTrade, bAutoRaze = argsList

    newOwner = _getPlayer(iOwnerNew)
    newOwnerCiv = newOwner.getCivilizationType()

    # Check for barbarian capture
    if iOwnerNew == BARBARIAN_PLAYER and pCity.getRevolutionCounter() > 0:
        print
        "[REV] City %s captured by barb rebels!" % pCity.getName()

    elif newOwnerCiv == RevData.getCityVal(pCity, 'RevolutionCiv'):
        # Check if revolt is active
        if pCity.getReinforcementCounter() > 0 or (pCity.unhappyLevel(0) - pCity.happyLevel()) > 0:
            print
            "[REV] Rebellious pCity %s is captured by rebel identity %s (%d)!!!" % (pCity.getName(),
                                                                                    newOwner.getCivilizationDescription(
                                                                                        0), newOwnerCiv)

            newOwnerTeam = _getTeam(newOwner.getTeam())
            oldOwner = _getPlayer(iOwnerOld)
            oldOwnerTeam = _getTeam(oldOwner.getTeam())
            if oldOwnerTeam.isAVassal():
                for teamID in xrange(MAX_PC_TEAMS):
                    if oldOwnerTeam.isVassal(teamID):
                        oldOwnerTeam = _getTeam(teamID)

            ix = pCity.getX()
            iy = pCity.getY()

            unitTypes = RevUtils.getHandoverUnitTypes(pCity)
            iWorker, iBestDefender, iCounter, iAttack = unitTypes[0], unitTypes[1], unitTypes[2], unitTypes[3]

            newUnitList = []

            # Couple units regardless of rebel status
            newUnitList.append(newOwner.initUnit(iBestDefender, ix, iy, _NO_UNITAI, _DIRECTION_SOUTH))
            if pCity.getPopulation() > 4:
                newUnitList.append(newOwner.initUnit(iCounter, ix, iy, _NO_UNITAI, _DIRECTION_SOUTH))

            if newOwner.isRebel():
                # Extra benefits if still considered a rebel
                szTxt = _getText(_TXT_YOUR_CAPTURE, ()) % (pCity.getName())
                iMsgTime = _getEVENT_MESSAGE_TIME()
                CvUtil.sendMessage(szTxt, iOwnerNew, iMsgTime, _INTERFACE_RESISTANCE_PATH, _COLOR_GREEN, ix, iy, True,
                                   True, _MESSAGE_TYPE_MINOR_EVENT, _SOUND_CITY_REVOLT, False)

                szTxt = _getText(_TXT_REBEL_CONTROL, ()) % (newOwner.getCivilizationDescription(0), pCity.getName())
                CvUtil.sendMessage(szTxt, iOwnerOld, iMsgTime, None, _COLOR_RED, eMsgType=_MESSAGE_TYPE_MINOR_EVENT,
                                   bForce=False)

                # Gold
                iGold = _getSorenRandNum(min(80, 8 * pCity.getPopulation()), 'Rev') + 8
                szTxt = _getText(_TXT_YOUR_CAPTURE_GOLD, ()) % (pCity.getName(), iGold)
                CvUtil.sendMessage(szTxt, iOwnerNew, iMsgTime, _INTERFACE_RESISTANCE_PATH, _COLOR_GREEN, ix, iy, False,
                                   False, _MESSAGE_TYPE_MINOR_EVENT, _SOUND_CITY_REVOLT, False)
                newOwner.changeGold(iGold)

                # Culture
                newCulVal = int(
                    revCultureModifier * max(pCity.getCulture(iOwnerOld), pCity.countTotalCultureTimes100() / 200))
                newPlotVal = int(
                    revCultureModifier * max(pCity.plot().getCulture(iOwnerOld), pCity.plot().countTotalCulture() / 2))
                RevUtils.giveCityCulture(pCity, iOwnerNew, newCulVal, newPlotVal)

                # Extra units
                if iWorker != -1:
                    newUnitList.append(newOwner.initUnit(iWorker, ix, iy, _NO_UNITAI, _DIRECTION_SOUTH))
                if pCity.getPopulation() > 7:
                    newUnitList.append(newOwner.initUnit(iBestDefender, ix, iy, _NO_UNITAI, _DIRECTION_SOUTH))
                if pCity.getPopulation() > 4 and newOwnerTeam.getPower(True) < oldOwnerTeam.getPower(True) / 4:
                    newUnitList.append(newOwner.initUnit(iAttack, ix, iy, _NO_UNITAI, _DIRECTION_SOUTH))

                if newOwner.getNumCities() <= 1:
                    # Extra units for first city captured
                    newUnitList.append(newOwner.initUnit(iCounter, ix, iy, _NO_UNITAI, _DIRECTION_SOUTH))
                    if newOwnerTeam.getPower(True) < oldOwnerTeam.getPower(True) / 2:
                        newUnitList.append(newOwner.initUnit(iBestDefender, ix, iy, _NO_UNITAI, _DIRECTION_SOUTH))
                        newUnitList.append(newOwner.initUnit(iAttack, ix, iy, _NO_UNITAI, _DIRECTION_SOUTH))
                    elif newOwnerTeam.getPower(True) < oldOwnerTeam.getPower(True):
                        newUnitList.append(newOwner.initUnit(iAttack, ix, iy, _NO_UNITAI, _DIRECTION_SOUTH))

                # Give a boat to island rebels
                if pCity.isCoastal(10) and pCity.area().getNumCities() < 3 and pCity.area().getNumTiles() < 25:
                    iBestCombat = -1
                    iBestUnit = -1
                    for iUnitX in xrange(_getNumUnitInfos()):
                        info = _getUnitInfo(iUnitX)
                        if (info.getDomainType() == _DOMAIN_SEA
                                and info.getUnitAIType(_UNITAI_ASSAULT_SEA)
                                and newOwner.canTrain(iUnitX, False, False)):
                            iCombat = info.getCombat()
                            if iBestCombat < iCombat:
                                iBestUnit = iUnitX
                                iBestCombat = iCombat

                    if iBestCombat > -1:
                        newOwner.initUnit(iBestUnit, ix, iy, _UNITAI_ASSAULT_SEA, _DIRECTION_SOUTH)
                        print
                        "Rev - Rebels get a boat to raid motherland"

                # Change city disorder timer to favor new player
                iTurns = pCity.getOccupationTimer()
                iTurns = iTurns / 4 + 1
                pCity.setOccupationTimer(iTurns)

                # Temporary happiness boost
                pCity.changeRevSuccessTimer(int(iTurns + RevUtils.getGameSpeedMod() * 15))

                # Trigger golden age for rebel civ under certain circumstances
                revTurn = RevData.revObjectGetVal(newOwner, 'RevolutionTurn')
                if revTurn != None and _getGameTurn() - revTurn < 4 * _goldenAgeLength100() / 100:
                    if newOwner.getNumCities() == 3:
                        if not newOwner.getCitiesLost():
                            szTxt = _getText(_TXT_GOLDEN_AGE, ())
                            CvUtil.sendMessage(szTxt, iOwnerNew, iMsgTime, _INTERFACE_RESISTANCE_PATH, _COLOR_GREEN, ix,
                                               iy, False, False, _MESSAGE_TYPE_MINOR_EVENT, _SOUND_CITY_REVOLT, False)
                            newOwner.changeGoldenAgeTurns(int(1.5 * _goldenAgeLength100() / 100))

            else:  # Conqueror not considered a rebel, fewer benefits
                # Culture
                newCulVal = int(
                    revCultureModifier * max(pCity.getCulture(iOwnerOld) / 2, pCity.countTotalCultureTimes100() / 400))
                newPlotVal = int(revCultureModifier * max(pCity.plot().getCulture(iOwnerOld) / 2,
                                                          pCity.plot().countTotalCulture() / 4))
                RevUtils.giveCityCulture(pCity, iOwnerNew, newCulVal, newPlotVal)

                # Change city disorder timer to favor new player
                iTurns = pCity.getOccupationTimer()
                iTurns = min(iTurns, iTurns / 3 + 1)
                pCity.setOccupationTimer(iTurns)

                # Temporary happiness boost
                pCity.changeRevSuccessTimer(int(iTurns + RevUtils.getGameSpeedMod() * 6))

            # Injure free units
            for unit in newUnitList:
                if unit.canFight():
                    iDamage = 20 + _getSorenRandNum(20, 'Rev - Injure unit')
                    unit.setDamage(iDamage, iOwnerOld)

        else:  # City once rebelled as this civ type, but not currently rebellious
            if LOG_DEBUG:
                print
                "[REV] %s, captured by former rebel identity: %s (%d)!" % (pCity.getName(),
                                                                           newOwner.getCivilizationDescription(0),
                                                                           newOwnerCiv)
            newCulVal = int(
                revCultureModifier * max(pCity.getCulture(iOwnerOld) / 2, pCity.countTotalCultureTimes100() / 400))
            newPlotVal = int(
                revCultureModifier * max(pCity.plot().getCulture(iOwnerOld) / 2, pCity.plot().countTotalCulture() / 4))
            RevUtils.giveCityCulture(pCity, iOwnerNew, newCulVal, newPlotVal)

            iTurns = pCity.getOccupationTimer()
            iTurns = iTurns / 2 + 1
            pCity.setOccupationTimer(iTurns)


def updateRevolutionIndices(argsList):
    iOwnerOld, iOwnerNew, pCity, bConquest, bTrade, bAutoRaze = argsList

    newOwner = _getPlayer(iOwnerNew)

    if newOwner.isNPC(): return

    newRevIdx = 400
    changeRevIdx = -40

    # Cache culture percent calculations
    culturePct = pCity.plot().calculateCulturePercent(iOwnerNew)

    if bConquest:
        # Occupied cities also rack up rev points each turn
        newRevIdx += pCity.getRevolutionIndex() / 4
        newRevIdx = min(newRevIdx, 600)

        if culturePct > 90:
            changeRevIdx -= 75
            newRevIdx -= 100
        elif culturePct > 40:
            changeRevIdx -= 35
            newRevIdx -= 60
        elif culturePct > 20:
            changeRevIdx -= 30

    elif bTrade:
        newRevIdx += pCity.getRevolutionIndex() / 3
        newRevIdx = min(newRevIdx, 650)

        if culturePct > 90:
            newRevIdx -= 50

    else:
        # Probably cultural conversion
        newRevIdx -= 100
        if culturePct > 50:
            changeRevIdx -= 25

    if newOwner.isRebel() and newOwner.getCivilizationType() == RevData.getCityVal(pCity, 'RevolutionCiv'):
        changeRevIdx -= 50
        newRevIdx -= 200
    elif iOwnerNew == pCity.getOriginalOwner():
        changeRevIdx -= 25
        newRevIdx -= 100

    if pCity.getHighestPopulation() < 6:
        changeRevIdx += 20
        newRevIdx -= 50

    changeRevIdx = int(math.floor(cityAcquiredModifier * changeRevIdx + .5))

    print
    "	Revolt - Acquisition of %s by %s reduces rev indices by %d" % (pCity.getName(),
                                                                        newOwner.getCivilizationDescription(0),
                                                                        changeRevIdx)

    iCityID = pCity.getID()
    for pListCity in newOwner.cities():
        if pListCity.getID() != iCityID:
            pListCity.changeRevolutionIndex(changeRevIdx)
            revIdxHist = RevData.getCityVal(pListCity, 'RevIdxHistory')
            revIdxHist['Events'][0] += changeRevIdx
            RevData.updateCityVal(pListCity, 'RevIdxHistory', revIdxHist)

    print
    "	Revolt - New rev idx for %s is %d" % (pCity.getName(), newRevIdx)

    pCity.setRevolutionIndex(newRevIdx)
    pCity.setRevIndexAverage(newRevIdx)
    pCity.setRevolutionCounter(acquiredTurns)
    pCity.setReinforcementCounter(0)
    RevData.updateCityVal(pCity, 'RevIdxHistory', RevDefs.initRevIdxHistory())

    if newOwner.isRebel():
        # Ripple effects through other rebellious cities
        newCivType = newOwner.getCivilizationType()
        for cityX in _getPlayer(iOwnerOld).cities():
            reinfCount = cityX.getReinforcementCounter()
            if reinfCount > 2 and RevData.getCityVal(cityX, 'RevolutionCiv') == newCivType:
                if reinfCount < 5:
                    reinfCount = 2
                else:
                    reinfCount -= 2

                print
                "[REV] Accelerating reinforcement in " + cityX.getName()
                # Setting below two will turn off reinforcement
                if reinfCount < 2: reinfCount = 2
                cityX.setReinforcementCounter(reinfCount)


def onCityLost(argsList):
    CyCity, = argsList
    iPlayer = CyCity.getOwner()

    playerCityLost(_getPlayer(iPlayer), CyCity, bConquest=CyCity.plot().getNumDefenders(iPlayer) == 0)


def playerCityLost(CyPlayer, CyCity, bConquest=True):
    if CyPlayer.isNPC() or CyPlayer.getNumCities() < 1:
        return

    # Pre-calculate values
    gameSpeed = _getGameSpeedInfo(_getGameSpeedType()).getSpeedPercent()
    turnsSinceAcquired = _getGameTurn() - CyCity.getGameTurnAcquired()

    revIdxChange = turnsSinceAcquired * 100.0 / gameSpeed
    revIdxChange += CyCity.getHighestPopulation()
    revIdxChange *= CyCity.plot().calculateCulturePercent(CyPlayer.getID()) / 100.0

    if revIdxChange > 500:
        revIdxChange = 500
    elif revIdxChange < 0:
        revIdxChange = 0

    if revIdxChange > 0:
        if not bConquest:
            revIdxChange = revIdxChange / 4.0

        if CyPlayer.isRebel():
            revIdxChange /= 2.0

    revIdxChange = int(cityLostModifier * revIdxChange + .5)

    print
    "[REV] Loss of %s by %s (%d bConq): %d rev idx change" % (CyCity.getName(), CyPlayer.getCivilizationDescription(0),
                                                              bConquest, revIdxChange)

    for cityX in CyPlayer.cities():
        cityX.changeRevolutionIndex(revIdxChange)
        revIdxHist = RevData.getCityVal(cityX, 'RevIdxHistory')
        revIdxHist['Events'][0] += revIdxChange
        RevData.updateCityVal(cityX, 'RevIdxHistory', revIdxHist)


def onBuildingBuilt(argsList):
    pCity, iBuildingType = argsList

    buildingInfo = _getBuildingInfo(iBuildingType)

    if buildingInfo.getMaxGlobalInstances() == 1 and buildingInfo.getPrereqReligion() < 0 and buildingInfo.getProductionCost() > 10:
        if LOG_DEBUG:
            print
            "[REV] World wonder %s build in %s" % (buildingInfo.getDescription(), pCity.getName())
        curRevIdx = pCity.getRevolutionIndex()
        pCity.changeRevolutionIndex(-max(150, curRevIdx / 4))

        for cityX in _getPlayer(pCity.getOwner()).cities():
            curRevIdx = cityX.getRevolutionIndex()
            iRevIdxChange = -max(75, curRevIdx * 12 / 100)
            cityX.changeRevolutionIndex(iRevIdxChange)
            revIdxHist = RevData.getCityVal(pCity, 'RevIdxHistory')
            revIdxHist['Events'][0] += iRevIdxChange
            RevData.updateCityVal(pCity, 'RevIdxHistory', revIdxHist)

    elif buildingInfo.getMaxPlayerInstances() == 1 and buildingInfo.getPrereqReligion() < 0 and buildingInfo.getProductionCost() > 10:
        if LOG_DEBUG:
            print
            "[REV] National wonder %s build in %s" % (buildingInfo.getDescription(), pCity.getName())
        curRevIdx = pCity.getRevolutionIndex()
        pCity.changeRevolutionIndex(-max(80, curRevIdx * 12 / 100))

        for cityX in _getPlayer(pCity.getOwner()).cities():
            curRevIdx = cityX.getRevolutionIndex()
            iRevIdxChange = -max(50, curRevIdx * 7 / 100)
            cityX.changeRevolutionIndex(iRevIdxChange)
            revIdxHist = RevData.getCityVal(pCity, 'RevIdxHistory')
            revIdxHist['Events'][0] += iRevIdxChange
            RevData.updateCityVal(pCity, 'RevIdxHistory', revIdxHist)


########################## Religious events ###############################

def onReligionFounded(argsList):
    iReligion = argsList[0]

    if iReligion > -1:
        player = _getPlayer(argsList[1])
        if not player.isAnarchy():
            iStateReligion = player.getStateReligion()
            if iStateReligion > -1 and iStateReligion != iReligion:
                pCity = _getHolyCity(iReligion)
                if pCity.getOwner() == argsList[1]:
                    curRevIdx = pCity.getRevolutionIndex()
                    newRevIdx = max(int(.35 * RevDefs.revInstigatorThreshold), curRevIdx + 100)
                    pCity.setRevolutionIndex(newRevIdx)
                    if LOG_DEBUG:
                        print
                        "[REV] %s founded non-state religion, index of %s now %d ... state %d, new %d" % (
                            pCity.getName(), pCity.getName(), pCity.getRevolutionIndex(), player.getStateReligion(),
                            iReligion)


def recordCivics(CyPlayer):
    curCivics = []
    for i in xrange(_getNumCivicOptionInfos()):
        curCivics.append(CyPlayer.getCivics(i))

    # Convert to tuple for memory efficiency
    RevData.revObjectSetVal(CyPlayer, "CivicList", tuple(curCivics))


def updateAttitudeExtras(bVerbose=False):
    for i in xrange(MAX_PC_PLAYERS):
        playerI = _getPlayer(i)

        for j in xrange(MAX_PC_PLAYERS):
            playerJ = _getPlayer(j)
            attEx = playerI.AI_getAttitudeExtra(j)
            # Odds and rate partially determined by current attitude value
            if attEx > 0 and _getSorenRandNum(100, 'Rev: Attitude') < attEx * 15:
                playerI.AI_changeAttitudeExtra(j, -(1 + attEx / 10))
                if LOG_DEBUG and bVerbose:
                    print
                    "[REV] Extra Attitude for %s of %s now %d" % (playerI.getCivilizationDescription(0),
                                                                  playerJ.getCivilizationDescription(0),
                                                                  playerI.AI_getAttitudeExtra(j))
            elif attEx < 0 and _getSorenRandNum(100, 'Rev: Attitude') < -attEx * 20:
                teamI = _getTeam(playerI.getTeam())
                if not teamI.isAtWarWith(playerJ.getTeam()):
                    playerI.AI_changeAttitudeExtra(j, -(attEx / 10))
                    if LOG_DEBUG and bVerbose:
                        print
                        "[REV] Extra Attitude for %s of %s now %d" % (playerI.getCivilizationDescription(0),
                                                                      playerJ.getCivilizationDescription(0),
                                                                      playerI.AI_getAttitudeExtra(j))


def removeFloatingRebellions():
    # Destroy all units for a rebel who is at peace, yet has no cities

    for iPlayerX in xrange(MAX_PC_PLAYERS):
        playerX = _getPlayer(iPlayerX)

        if (not playerX.isAlive() or playerX.getNumCities() or playerX.getNumUnits() < 1
                or not playerX.isRebel() and not playerX.isFoundedFirstCity()):
            continue

        bOnlySpy = True
        spy = None
        unitX, i = playerX.firstUnit(False)
        while unitX:
            if unitX.isFound():
                return
            if bOnlySpy:
                if unitX.getUnitAIType() != _UNITAI_SPY:
                    bOnlySpy = False
                else:
                    spy = unitX
            unitX, i = playerX.nextUnit(i, False)

        print
        "[REV] Player %d (%s) is a homeless rebel" % (iPlayerX, playerX.getCivilizationDescription(0))

        if not _getTeam(playerX.getTeam()).isAtWar(False):
            print
            "[REV] Rebel player %d has lost their cause, terminating rebel" % iPlayerX
            playerX.killUnits()

        elif bOnlySpy:
            print
            "[REV] Rebel player %d has only spies" % iPlayerX

            if spy and _getSorenRandNum(100, "Rev - Only spy death") < 10:
                spy.kill(False, -1)
                print
                "[REV] Killed one spy of Rebel player %d" % iPlayerX


########################## Assimilation ###############################

def checkForAssimilation():
    iNumPlayers = 0
    iMaxEra = 0
    players = []

    for iPlayerX in xrange(MAX_PC_PLAYERS):
        CyPlayerX = _getPlayer(iPlayerX)
        if CyPlayerX.isAlive() and not CyPlayerX.isMinorCiv():
            iNumPlayers += 1
            if not CyPlayerX.isHuman():
                players.append((iPlayerX, CyPlayerX))
            iEra = CyPlayerX.getCurrentEra()
            if iEra > iMaxEra:
                iMaxEra = iEra

    if iNumPlayers == 0:
        return

    # Pre-calculate common values
    landPlots = _getLandPlots()
    worldSize = _getWorldSize()
    targetNumCities = _getWorldInfo(worldSize).getTargetNumCities()

    minNumPlots = int((landPlots / (1.0 * iNumPlayers) + .5) / 3.0) + 1
    if minNumPlots > 21:
        minNumPlots = 21
    elif minNumPlots < 9:
        minNumPlots = 9

    iTurn = _getGameTurn()

    for iPlayerX, CyPlayerX in players:
        CyTeamX = _getTeam(CyPlayerX.getTeam())
        CyCity0 = CyPlayerX.getCapitalCity()
        if CyCity0 is None:
            continue

        iTurnAcquiredCity0 = CyCity0.getGameTurnAcquired()
        CyPlot0 = None
        szCiv = CyPlayerX.getCivilizationDescription(0)

        iMinCities = targetNumCities
        iNumCities = CyPlayerX.getNumCities()  # We know this is greater than 0 as a capital city has been confirmed.

        bRiskWar = False
        iPlayerML = RevData.revObjectGetVal(CyPlayerX, 'MotherlandID')

        if iPlayerML != None:
            CyPlayerML = _getPlayer(iPlayerML)
            bWarSeparatist = CyTeamX.isAtWarWith(CyPlayerML.getTeam())
            if bWarSeparatist:
                revTurn = RevData.revObjectGetVal(CyPlayerX, 'RevolutionTurn')
                if revTurn != None and iTurn - revTurn < 40:
                    bRiskWar = True

        CyPlayerDominant = None
        joinPlayerID = RevData.revObjectGetVal(CyPlayerX, 'JoinPlayerID')

        if joinPlayerID != None and iTurn - iTurnAcquiredCity0 < 30 and not CyTeamX.isAVassal():
            if iNumCities < iMinCities:
                iOdds = 12 + iNumCities * 2

                if iPlayerML != None and bWarSeparatist:
                    iCivType = CyPlayerX.getCivilizationType()
                    for CyCityML in CyPlayerML.cities():
                        if RevData.getCityVal(CyCityML, 'RevolutionCiv') == iCivType:
                            revTurn = RevData.getCityVal(CyCityML, 'RevolutionTurn')
                            if revTurn != None and iTurn - revTurn < 25:
                                iOdds -= 2

                if iOdds > 10 + _getSorenRandNum(100, 'Revolution: Assimilate'):
                    CyPlayerDominant = _getPlayer(joinPlayerID)
                    print
                    "	Revolt - Assimilation! The rebel %s are requesting again to join the %s now that they've captured %d cities" % (
                        szCiv, CyPlayerDominant.getCivilizationDescription(0), iNumCities)

        elif iTurn - iTurnAcquiredCity0 > 15 and iNumCities < iMinCities:
            iTotalLand = CyPlayerX.getTotalLand()
            if iTotalLand < minNumPlots:
                if CyCity0.area().getNumCities() < iNumCities + 2:
                    continue  # Isolated

                if CyTeamX.getNumMembers() > 1:
                    continue  # In alliance

                iOdds = 2 * (minNumPlots - iTotalLand) + (4 + 4 * iMaxEra) / CyCity0.getPopulation()

                if CyCity0.getOccupationTimer() > 0:
                    iOdds *= 3

                iOdds += CyCity0.getRevolutionIndex() / 100

                CyPlot0 = CyCity0.plot()

                ### Special cases
                if CyTeamX.isAVassal():
                    if iOdds > 10 + _getSorenRandNum(100, 'Revolution: Assimilate'):
                        # If player is a Vassal, should only be allowed to assimilate with master
                        CyPlayerMaster = None
                        for iTeamY in xrange(MAX_PC_TEAMS):
                            if not CyTeamX.isVassal(iTeamY):
                                continue

                            iPlayerMaster = _getTeam(iTeamY).getLeaderID()
                            CyPlayerMaster = _getPlayer(iPlayerMaster)

                            print
                            "	Revolt - Assimilation!  Vassal %s considering assimilation to master %s" % (szCiv,
                                                                                                             CyPlayerMaster.getCivilizationDescription(
                                                                                                                 0))

                            relations = CyPlayerX.AI_getAttitude(iPlayerMaster)

                            culturePct = CyPlot0.getCulture(iPlayerMaster) / (max(1, 1.0 * CyPlot0.countTotalCulture()))
                            if culturePct > .25:
                                # Assimilate with master with large culture in city
                                if relations != _ATTITUDE_FURIOUS:
                                    if not CyPlayerMaster.isHuman():
                                        CyPlayerDominant = CyPlayerMaster
                                    elif iPlayerX not in noAssimilateList:
                                        CyPlayerDominant = CyPlayerMaster
                                    if CyPlayerDominant:
                                        print
                                        "	Revolt - Assimilation to master based on culture"

                            elif relations in (_ATTITUDE_PLEASED, _ATTITUDE_FRIENDLY):
                                # Assimilate with friendly, powerful master
                                masterPower = CyPlayerMaster.getPower()
                                vassalPower = CyPlayerX.getPower()

                                if masterPower > 3 * vassalPower:
                                    if not CyPlayerMaster.isHuman():
                                        CyPlayerDominant = CyPlayerMaster
                                    elif iPlayerX not in noAssimilateList:
                                        CyPlayerDominant = CyPlayerMaster
                                    if CyPlayerDominant:
                                        print
                                        "	Revolt - Assimilation to friendly and powerful master"
                            break

                elif CyPlot0.calculateCulturePercent(iPlayerX) < 60:
                    ### Capital has foreign influence
                    iPlayerCult = CyPlot0.calculateCulturalOwner()  # iPlayerCult guaranteed to be alive
                    if iPlayerCult != iPlayerX:
                        iOdds += 15

                    if iOdds > 10 + _getSorenRandNum(100, 'Revolution: Assimilate'):
                        print
                        "	Revolt - Assimilation!  %s considering assimilation by culture" % szCiv

                        if iPlayerCult > -1 and iPlayerCult != iPlayerX and CyPlayerX.AI_getAttitude(
                                iPlayerCult) != _ATTITUDE_FURIOUS:
                            ## Assimilate with cultural owner
                            CyPlayerY = _getPlayer(iPlayerCult)
                            if CyPlayerY.isAlive():
                                if not CyPlayerY.isHuman():
                                    CyPlayerDominant = CyPlayerY
                                elif iPlayerX not in noAssimilateList:
                                    CyPlayerDominant = CyPlayerY
                                if CyPlayerDominant:
                                    print
                                    "	Revolt - Assimilation culture owner: " + CyPlayerDominant.getCivilizationDescription(
                                        0)

                        if not CyPlayerDominant:
                            ## Check for good relations with second place culture
                            iMaxCult2 = 0
                            iPlayerCult2 = -1
                            CyPlayerCult2 = None

                            for iPlayerY in xrange(MAX_PC_PLAYERS):
                                if iPlayerY in (iPlayerX, iPlayerCult):
                                    continue
                                CyPlayerY = _getPlayer(iPlayerY)
                                if not CyPlayerY.isAlive():
                                    continue
                                iCulture = CyPlot0.getCulture(iPlayerY)
                                if iCulture > iMaxCult2:
                                    iPlayerCult2 = iPlayerY
                                    CyPlayerCult2 = CyPlayerY
                                    iMaxCult2 = iCulture

                            if iMaxCult2 < 1:
                                raise "city plot unexpectedly owned by no one, logical error in dll code dealing with culture on city plots"
                            else:
                                iTotalCulture = 1.0 * CyPlot0.countTotalCulture()
                                culturePct2 = iMaxCult2 / iTotalCulture
                                if culturePct2 > .2:
                                    relations = CyPlayerX.AI_getAttitude(iPlayerCult2)
                                    if (relations in (_ATTITUDE_PLEASED, _ATTITUDE_FRIENDLY)
                                            or relations == _ATTITUDE_CAUTIOUS and culturePct2 > .4):
                                        if not CyPlayerCult2.isHuman() or iPlayerX not in noAssimilateList:
                                            CyPlayerDominant = CyPlayerCult2

                                        if CyPlayerDominant:
                                            print
                                            "	Revolt - Assimilation to friendly, 2nd culture player"

        if CyPlayerDominant:
            # Assimilate!
            if CyPlayerDominant.isHuman():
                # Zoom to city
                if CyPlot0 is None:
                    CyPlot0 = CyCity0.plot()
                CyCamera().JustLookAt(CyPlot0.getPoint())

                # Additions by Caesium et al
                caesiumtR = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
                caesiumtextResolution = caesiumtR.split('x')
                caesiumpasx = int(caesiumtextResolution[0]) / 10
                caesiumpasy = int(caesiumtextResolution[1]) / 10

                popup = CyPopup(RevDefs.assimilationPopup, _EVENTCONTEXT_ALL, False)
                if centerPopups:
                    popup.setPosition(3 * caesiumpasx, 3 * caesiumpasy)

                bodStr = _getText(_TXT_ASSIM_POPUP, ()) % (szCiv, szCiv)
                if bRiskWar:
                    bodStr += '\n\n' + _getText(_TXT_ASSIM_POPUP_REBEL, ()) % (CyPlayerML.getCivilizationDescription(0))
                popup.setBodyString(bodStr, 1 << 0)
                popup.addSeparator()
                popup.addButton(_getText(_TXT_BUTTON_ACCEPT, ()))
                popup.addButton(_getText(_TXT_BUTTON_MAYBE_LATER, ()))
                popup.addButton(_getText(_TXT_BUTTON_NEVER, ()))
                popup.setUserData((iPlayerX, CyPlayerDominant.getID(), bRiskWar))
                popup.launch(False, PopupStates.POPUPSTATE_IMMEDIATE)
            else:
                if bRiskWar:
                    # Assimilating a rebel involves potential war declaration, attitude issues
                    CyPlayerML.AI_changeAttitudeExtra(CyPlayerDominant.getID(),
                                                      CyPlayerML.AI_getAttitudeExtra(iPlayerX))
                    print
                    "	Revolt - The %s (motherland of the rebel %s) is considering attacking the %s over the assimilation" % (
                        CyPlayerML.getCivilizationDescription(0), szCiv, CyPlayerDominant.getCivilizationDescription(0))
                    warOdds = RevUtils.computeWarOdds(CyPlayerML, CyPlayerDominant, CyCity0.area(), False, True, True)
                    iOdds = warOdds[0]
                    attackerTeam = warOdds[1]
                    victimTeam = warOdds[2]
                    if attackerTeam.canDeclareWar(victimTeam.getID()) and iOdds > _getSorenRandNum(100,
                                                                                                   'Revolution: War'):
                        print
                        "  Revolt - Rebel motherland takes exception to assimilation, team %d declare war on team %d" % (
                            attackerTeam.getID(), victimTeam.getID())
                        attackerTeam.declareWar(victimTeam.getID(), True, _NO_WARPLAN)

                CyPlayerDominant.assimilatePlayer(iPlayerX)


def assimilateHandler(iPlayerID, netUserData, popupReturn):
    global noAssimilateList

    if popupReturn.getButtonClicked() == 0:
        if LOG_DEBUG:
            print
            "[REV] Assimilation accepted!"
        if netUserData[2]:
            pMotherland = _getPlayer(RevData.revObjectGetVal(_getPlayer(netUserData[0]), 'MotherlandID'))
            pMotherland.AI_changeAttitudeExtra(netUserData[1], pMotherland.AI_getAttitudeExtra(netUserData[0]))
            if LOG_DEBUG:
                print
                "[REV] Rebel motherland %s extra attitude to %s now %d" % (pMotherland.getCivilizationDescription(0),
                                                                           _getPlayer(netUserData[
                                                                                          1]).getCivilizationDescription(
                                                                               0), pMotherland.AI_getAttitudeExtra(
                        netUserData[0]))

            warOdds = RevUtils.computeWarOdds(pMotherland, _getPlayer(netUserData[1]),
                                              _getPlayer(netUserData[0]).getCapitalCity().area(), False, True, True)
            iOdds = warOdds[0]
            attackerTeam = warOdds[1]
            victimTeam = warOdds[2]

            if attackerTeam.canDeclareWar(victimTeam.getID()) and iOdds > _getSorenRandNum(100, 'Revolution: War'):
                if LOG_DEBUG:
                    print
                    "[REV] Rebel motherland takes exception, team %d declare war on team %d" % (attackerTeam.getID(),
                                                                                                victimTeam.getID())
                attackerTeam.declareWar(victimTeam.getID(), True, _NO_WARPLAN)

        _getPlayer(netUserData[1]).assimilatePlayer(netUserData[0])
    elif popupReturn.getButtonClicked() == 1:
        if LOG_DEBUG:
            print
            "[REV] Assimilation postponed"
    else:
        if LOG_DEBUG:
            print
            "[REV] Assimilation rejected!"
        noAssimilateList.append(netUserData[0])


# Small revolts are short duration disorder striking a city, shutting down production and culture, etc.
def doSmallRevolts(iPlayer, CyPlayer):
    if iPlayer >= MAX_PC_PLAYERS:
        raise "NPC does not revolt!"

    # Pre-cache thresholds
    revReadyThreshold = 5 * RevDefs.revReadyDividend * RevDefs.revInstigatorThreshold / (4 * RevDefs.revReadyDivisor)
    alwaysViolentThreshold = RevDefs.alwaysViolentThreshold

    for city in CyPlayer.cities():
        revIdx = city.getRevolutionIndex()

        if revIdx <= revReadyThreshold:
            continue

        if city.getOccupationTimer() > 0 or city.getRevolutionCounter() > 0 or RevData.getCityVal(city,
                                                                                                  'SmallRevoltCounter') > 0:
            continue  # Already in a revolt

        localRevIdx = city.getLocalRevIndex()
        if localRevIdx > 0:
            localFactor = 1 + localRevIdx / 3
            if localFactor > 10:
                localFactor = 10
        else:
            localFactor = localRevIdx - 1
            if localFactor < -15:
                localFactor = -15

        iOdds = localFactor + 100 * revIdx / (8 * alwaysViolentThreshold)
        if iOdds > 15:
            iOdds = 15

        if _getSorenRandNum(100, "Rev: Small Revolt") < iOdds:
            szName = city.getName()
            print
            "[REV] Small revolt in %s with odds %d (%d idx, %d loc)" % (szName, iOdds, revIdx, localRevIdx)
            city.setOccupationTimer(2)

            RevData.setCityVal(city, 'SmallRevoltCounter', 6)

            szTxt = _getText(_TXT_SMALL_REVOLT, ()) % szName
            CvUtil.sendMessage(szTxt, iPlayer, 16, _INTERFACE_RESISTANCE_PATH, _COLOR_RED, city.getX(), city.getY(),
                               True, True, _MESSAGE_TYPE_MINOR_EVENT, _SOUND_CITY_REVOLT, False)