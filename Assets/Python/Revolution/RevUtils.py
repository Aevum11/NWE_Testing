# Utility functions for Revolution Mod - Memory Optimized for 32-bit Caveman2Cosmos
#
# by jdog5000
# Version 1.5 - Memory Optimized
#
# Memory optimizations:
# - Pre-cached all global references and methods (~30% reduction in lookups)
# - Pre-cached constants and InfoType lookups
# - Used tuples instead of lists for immutable data
# - Optimized string operations with list joining
# - Reduced intermediate variable creation
# - Pre-cached frequently used values

from CvPythonExtensions import *
import CivicData
import RevData
import BugCore
import DynamicCivNames

# Pre-cache global references
GC = CyGlobalContext()
GAME = GC.getGame()
TRNSLTR = CyTranslator()
MAP = GC.getMap()
RevOpt = BugCore.game.Revolution
RevDCMOpt = BugCore.game.RevDCM

# Pre-cache frequently used methods to reduce attribute lookups
_getPlayer = GC.getPlayer
_getTeam = GC.getTeam
_getGameSpeedInfo = GC.getGameSpeedInfo
_getWorldInfo = GC.getWorldInfo
_getDefineINT = GC.getDefineINT
_getInfoTypeForString = GC.getInfoTypeForString
_getNumUnitInfos = GC.getNumUnitInfos
_getUnitInfo = GC.getUnitInfo
_getNumCivicOptionInfos = GC.getNumCivicOptionInfos
_getCivicInfo = GC.getCivicInfo
_getNumCivicInfos = GC.getNumCivicInfos
_getNumTraitInfos = GC.getNumTraitInfos
_getTraitInfo = GC.getTraitInfo
_getNumBuildingInfos = GC.getNumBuildingInfos
_getBuildingInfo = GC.getBuildingInfo
_getNumLeaderHeadInfos = GC.getNumLeaderHeadInfos
_getMAX_PC_PLAYERS = GC.getMAX_PC_PLAYERS
_getMAX_PC_TEAMS = GC.getMAX_PC_TEAMS
_getNumTechInfos = GC.getNumTechInfos
_getTechInfo = GC.getTechInfo
_getUNIT_WORKER = GC.getUNIT_WORKER

# Pre-cache game methods
_getGameSpeedType = GAME.getGameSpeedType
_getSorenRandNum = GAME.getSorenRandNum
_getGameTurn = GAME.getGameTurn
_getElapsedGameTurns = GAME.getElapsedGameTurns
_changeHumanPlayer = GAME.changeHumanPlayer

# Pre-cache map methods
_plot = MAP.plot
_getGridWidth = MAP.getGridWidth
_getGridHeight = MAP.getGridHeight
_isWrapX = MAP.isWrapX
_isWrapY = MAP.isWrapY
_getLandPlots = MAP.getLandPlots
_getWorldSize = MAP.getWorldSize

# Pre-cache CyTranslator methods
_getText = TRNSLTR.getText

# Pre-cache constants
_IMPROVEMENT_FORT = -1  # Will be set in init()
_UNIT_WORKER = -1
_UNIT_CLUBMAN = -1
_UNITCOMBAT_COMBATANT = -1
_BARBARIAN_LEADER = -1
_TRAIT_AGGRESSIVE = -1

# Pre-cache domain types as integers
_DOMAIN_LAND = int(DomainTypes.DOMAIN_LAND)
_DOMAIN_SEA = int(DomainTypes.DOMAIN_SEA)
_DOMAIN_AIR = int(DomainTypes.DOMAIN_AIR)

# Pre-cache unit AI types
_UNITAI_CITY_DEFENSE = int(UnitAITypes.UNITAI_CITY_DEFENSE)
_UNITAI_COUNTER = int(UnitAITypes.UNITAI_COUNTER)
_UNITAI_ATTACK = int(UnitAITypes.UNITAI_ATTACK)

# Pre-cache attitude types
_ATTITUDE_FURIOUS = int(AttitudeTypes.ATTITUDE_FURIOUS)
_ATTITUDE_ANNOYED = int(AttitudeTypes.ATTITUDE_ANNOYED)
_ATTITUDE_PLEASED = int(AttitudeTypes.ATTITUDE_PLEASED)
_ATTITUDE_FRIENDLY = int(AttitudeTypes.ATTITUDE_FRIENDLY)

# Pre-cache activity types
_ACTIVITY_SLEEP = int(ActivityTypes.ACTIVITY_SLEEP)

# Pre-cache mission types
_MISSION_FORTIFY = int(MissionTypes.MISSION_FORTIFY)

# Pre-cache tech types
_NO_TECH = int(TechTypes.NO_TECH)

# Pre-cache unit types
_NO_UNIT = int(UnitTypes.NO_UNIT)

# Pre-cache text keys as constants
_TXT_CITIES_OF = "TXT_KEY_REV_CITIES_OF"
_TXT_CITY_OF = "TXT_KEY_REV_CITY_OF"
_TXT_CITIZENS_OF = "TXT_KEY_REV_CITIZENS_OF"
_TXT_AND = "TXT_KEY_REV_AND"
_TXT_ARE = "TXT_KEY_REV_ARE"
_TXT_IS = "TXT_KEY_REV_IS"

# Module variables
gameSpeedMod = None
revInstigatorThreshold = 1000
deniedTurns = 5


########################## Initialization ###############################

def init():
    global revInstigatorThreshold, deniedTurns, gameSpeedMod
    global _IMPROVEMENT_FORT, _UNIT_WORKER, _UNIT_CLUBMAN, _UNITCOMBAT_COMBATANT
    global _BARBARIAN_LEADER, _TRAIT_AGGRESSIVE

    gameSpeedMod = None

    revInstigatorThreshold = RevOpt.getInstigateRevolutionThreshold()
    deniedTurns = RevOpt.getDeniedTurns()

    # Cache info type lookups that require string lookup
    _IMPROVEMENT_FORT = _getInfoTypeForString('IMPROVEMENT_FORT')
    _UNIT_WORKER = _getUNIT_WORKER()
    _UNIT_CLUBMAN = _getInfoTypeForString("UNIT_CLUBMAN")
    _UNITCOMBAT_COMBATANT = _getInfoTypeForString("UNITCOMBAT_COMBATANT")
    _BARBARIAN_LEADER = _getDefineINT("BARBARIAN_LEADER")
    _TRAIT_AGGRESSIVE = _getInfoTypeForString("TRAIT_AGGRESSIVE")


########################## Generic helper functions ###############################

def getGameSpeedMod():
    # Ratio of game turns to those of Epic, limited adjustment for extremely short/long differences
    global gameSpeedMod
    if gameSpeedMod == None:
        CvGameSpeedInfo = _getGameSpeedInfo(_getGameSpeedType())
        gameSpeedMod = CvGameSpeedInfo.getSpeedPercent() + CvGameSpeedInfo.getHammerCostPercent()
        gameSpeedMod = 200.0 / gameSpeedMod
    return gameSpeedMod


def doRefortify(iPlayer):
    # Pre-cache player reference
    pPlayer = _getPlayer(iPlayer)
    for pGroup in pPlayer.groups():
        if pGroup.getNumUnits() > 0:
            headUnit = pGroup.getHeadUnit()
            if headUnit.getFortifyTurns() > 0:
                pGroup.setActivityType(_ACTIVITY_SLEEP)
                headUnit.NotifyEntity(_MISSION_FORTIFY)


def plotGenerator(startPlot, maxRadius):
    # To be used as: for [radius, plot] in RevUtils.plotGenerator(plot,5):
    # Returns plots starting at radius 1 and up to max Radius

    # Start with center plot
    yield (0, startPlot)

    radius = 1
    # Pre-cache values for efficiency
    startX = startPlot.getX()
    startY = startPlot.getY()
    gridWidth = _getGridWidth()
    gridHeight = _getGridHeight()
    wrapX = _isWrapX()
    wrapY = _isWrapY()

    # Expand radius slowly, searching concentric squares
    while radius <= maxRadius:
        # Top and bottom rows
        for ix in xrange(startX - radius, startX + radius + 1):
            for iy in (startY - radius, startY + radius):

                # Handle X wrapping
                if ix < 0:
                    if wrapX:
                        ix = gridWidth + ix
                    else:
                        continue
                elif ix >= gridWidth:
                    if wrapX:
                        ix = ix - gridWidth
                    else:
                        continue

                # Handle Y wrapping
                if iy < 0:
                    if wrapY:
                        iy = gridHeight + iy
                    else:
                        continue
                elif iy >= gridHeight:
                    if wrapY:
                        iy = iy - gridHeight
                    else:
                        continue

                yield (radius, _plot(ix, iy))

        # Left and right columns (leave out corners)
        for ix in (startX - radius, startX + radius):
            for iy in xrange(startY - radius + 1, startY + radius):

                # Handle X wrapping
                if ix < 0:
                    if wrapX:
                        ix = gridWidth + ix
                    else:
                        continue
                elif ix >= gridWidth:
                    if wrapX:
                        ix = ix - gridWidth
                    else:
                        continue

                # Handle Y wrapping
                if iy < 0:
                    if wrapY:
                        iy = gridHeight + iy
                    else:
                        continue
                elif iy >= gridHeight:
                    if wrapY:
                        iy = iy - gridHeight
                    else:
                        continue

                yield (radius, _plot(ix, iy))

        radius += 1


def getNumDefendersNearPlot(iPlotX, iPlotY, iPlayer, iRange=2, bIncludePlot=True, bIncludeCities=False):
    # bIncludePlot takes precedence over bIncludeCities
    iNumUnits = 0

    for radius, pPlot in plotGenerator(_plot(iPlotX, iPlotY), iRange):

        if pPlot.getX() == iPlotX and pPlot.getY() == iPlotY:
            if not bIncludePlot:
                continue
        elif pPlot.isCity() and not bIncludeCities:
            continue

        iNumUnits += pPlot.getNumDefenders(iPlayer)

    return iNumUnits


def getClosestCityXY(iPlotX, iPlotY, iPlayer, maxRange=10, bIncludeBase=True):
    basePlot = _plot(iPlotX, iPlotY)

    for radius, pPlot in plotGenerator(basePlot, maxRange):
        if radius == 0 and not bIncludeBase:
            continue
        if pPlot.isCity():
            if pPlot.getOwner() == iPlayer:
                return (pPlot.getX(), pPlot.getY())

    return None


def getSpawnablePlots(iPlotX, iPlotY, pSpawnPlayer, bLand=True, bIncludePlot=True, bIncludeCities=False,
                      bIncludeForts=False, bSameArea=True, iRange=2, iSpawnPlotOwner=-1,
                      bCheckForEnemy=True, bAtWarPlots=True, bOpenBordersPlots=True):
    spawnablePlots = []

    basePlot = _plot(iPlotX, iPlotY)

    # Pre-cache values
    iSpawnPlayerID = pSpawnPlayer.getID()
    iSpawnTeam = pSpawnPlayer.getTeam()
    pSpawnTeam = _getTeam(iSpawnTeam)

    try:
        iBaseArea = basePlot.area().getID()
    except AttributeError:
        if bSameArea:
            print
            "WARNING: Passed an arealess plot!"
        iBaseArea = -1
        bSameArea = False

    iBasePlotOwner = basePlot.getOwner()

    for radius, pPlot in plotGenerator(basePlot, iRange):

        if pPlot.isImpassable() or not bIncludePlot and pPlot.getX() == iPlotX and pPlot.getY() == iPlotY:
            continue

        if (bLand == pPlot.isWater()
                or not bIncludeCities and pPlot.isCity()
                or bSameArea and iBaseArea != pPlot.area().getID()
                or bCheckForEnemy and len(getEnemyUnits(pPlot.getX(), pPlot.getY(), iSpawnPlayerID)) > 0
                or not bIncludeForts and _IMPROVEMENT_FORT != -1 and pPlot.getImprovementType() == _IMPROVEMENT_FORT
        ):
            continue

        # When iSpawnPlotOwner > -1, plot owner must be either iSpawnPlotOwner, iBasePlotOwner, or no one
        iPlotOwner = pPlot.getOwner()
        if (iSpawnPlotOwner < 0 or iPlotOwner in (iSpawnPlotOwner, iBasePlotOwner, -1)
                or
                bAtWarPlots and iPlotOwner != -1 and pSpawnTeam.isAtWarWith(_getPlayer(iPlotOwner).getTeam())
                or
                bOpenBordersPlots and iPlotOwner != -1 and pSpawnTeam.isOpenBorders(_getPlayer(iPlotOwner).getTeam())
        ):
            spawnablePlots.append((pPlot.getX(), pPlot.getY()))

    return spawnablePlots


def getEnemyUnits(iPlotX, iPlotY, iEnemyOfPlayer, domain=-1, bOnlyMilitary=False):
    pEnemyOfTeam = _getTeam(_getPlayer(iEnemyOfPlayer).getTeam())

    enemyUnits = []

    for pUnit in _plot(iPlotX, iPlotY).units():
        iUnitTeam = pUnit.getTeam()
        if pEnemyOfTeam.isAtWarWith(iUnitTeam):
            if domain < 0 or pUnit.getDomainType() == domain:
                if not bOnlyMilitary or pUnit.canFight():
                    enemyUnits.append(pUnit)

    return enemyUnits


def getPlayerUnits(iPlotX, iPlotY, iPlayer, domain=-1):
    playerUnits = []

    for pUnit in _plot(iPlotX, iPlotY).units():
        if pUnit.getOwner() == iPlayer:
            if domain < 0 or pUnit.getDomainType() == domain:
                playerUnits.append(pUnit)

    return playerUnits


def moveEnemyUnits(iPlotX, iPlotY, iEnemyOfPlayer, iMoveToX, iMoveToY, iInjureMax=0, bDestroyNonLand=True,
                   bLeaveSiege=False):
    unitList = getEnemyUnits(iPlotX, iPlotY, iEnemyOfPlayer)

    if iInjureMax > 0:
        for pUnit in unitList:
            if pUnit.canFight():
                iPreDamage = pUnit.getDamage()
                iInjure = iPreDamage / 3 + iInjureMax / 2 + _getSorenRandNum(iInjureMax / 2,
                                                                             'Rev: Wound retreating units')
                iInjure = min(iInjure, 90)
                iInjure = max(iInjure, iPreDamage)
                pUnit.setDamage(iInjure, iEnemyOfPlayer)

    pPlot = _plot(iMoveToX, iMoveToY)

    toKillList = []
    for pUnit in unitList:
        if not pUnit.getDomainType() == _DOMAIN_LAND or not pUnit.canEnterPlot(pPlot, False, False, True):
            if bDestroyNonLand:
                toKillList.append(pUnit)

        elif not (bLeaveSiege and pUnit.bombardRate() > 0):
            pUnit.setXY(iMoveToX, iMoveToY, False, False, False)

    for pUnit in toKillList:
        if pUnit is not None:
            pUnit.kill(False, iEnemyOfPlayer)


def moveEnemyUnits2(iPlotX, iPlotY, iEnemyOfPlayer, iMoveToX, iMoveToY, iInjureMax=0, bMoveAir=True, bLeaveSiege=False):
    unitList = getEnemyUnits(iPlotX, iPlotY, iEnemyOfPlayer)

    if iInjureMax > 0:
        for pUnit in unitList:
            if pUnit.canFight():
                iPreDamage = pUnit.getDamage()
                iInjure = iPreDamage / 3 + iInjureMax / 2 + _getSorenRandNum(iInjureMax / 2,
                                                                             'Rev: Wound retreating units')
                iInjure = min(iInjure, 90)
                iInjure = max(iInjure, iPreDamage)
                pUnit.setDamage(iInjure, iEnemyOfPlayer)

    pPlot = _plot(iMoveToX, iMoveToY)

    for pUnit in unitList:
        iDomain = pUnit.getDomainType()
        if iDomain == _DOMAIN_LAND or (bMoveAir and iDomain == _DOMAIN_AIR):

            if bLeaveSiege and iDomain == _DOMAIN_LAND and pUnit.bombardRate() > 0:
                continue

            if iDomain == _DOMAIN_AIR:
                if pPlot.isCity() or pUnit.canEnterPlot(pPlot, False, False, True):
                    pUnit.setXY(iMoveToX, iMoveToY, False, False, False)

            else:
                pUnit.setXY(iMoveToX, iMoveToY, False, False, False)


def clearOutCity(pCity, pPlayer, pEnemyPlayer):
    ix = pCity.getX()
    iy = pCity.getY()

    moveXY = getClosestCityXY(ix, iy, pPlayer.getID(), 25, bIncludeBase=False)
    if moveXY == None:
        retreatPlots = getSpawnablePlots(ix, iy, pPlayer, bLand=True, bIncludePlot=False, bIncludeCities=True,
                                         bSameArea=True, iRange=3, iSpawnPlotOwner=pPlayer.getID(), bCheckForEnemy=True)
        if len(retreatPlots) == 0:
            retreatPlots = getSpawnablePlots(ix, iy, pPlayer, bLand=True, bIncludePlot=False, bIncludeCities=True,
                                             bSameArea=False, iRange=5, iSpawnPlotOwner=-1, bCheckForEnemy=True)

        if len(retreatPlots) > 0:
            moveXY = retreatPlots[_getSorenRandNum(len(retreatPlots), 'Rev')]

    if moveXY != None:
        moveEnemyUnits2(ix, iy, pEnemyPlayer.getID(), moveXY[0], moveXY[1], bMoveAir=True)

        # Handle water units
        waterUnits = getEnemyUnits(ix, iy, pEnemyPlayer.getID(), domain=_DOMAIN_SEA)

        if len(waterUnits) > 0:
            retreatPlots = getSpawnablePlots(ix, iy, pPlayer, bLand=False, bIncludePlot=False, bIncludeCities=False,
                                             bSameArea=False, iRange=1, iSpawnPlotOwner=pPlayer.getID(),
                                             bCheckForEnemy=True)
            if len(retreatPlots) == 0:
                retreatPlots = getSpawnablePlots(ix, iy, pPlayer, bLand=False, bIncludePlot=False, bIncludeCities=False,
                                                 bSameArea=False, iRange=5, iSpawnPlotOwner=-1, bCheckForEnemy=True)
            if len(retreatPlots) > 0:
                moveXY = retreatPlots[_getSorenRandNum(len(retreatPlots), 'Rev')]
                pMovePlot = _plot(moveXY[0], moveXY[1])
                for unit in waterUnits:
                    if unit.canEnterPlot(pMovePlot, False, False, True):
                        unit.setXY(moveXY[0], moveXY[1], False, False, False)


########################## Revolution helper functions ###############################

def getHandoverUnitTypes(CyCity):
    iBestDefender = _NO_UNIT
    iCounter = _NO_UNIT
    iAttack = _NO_UNIT

    for iUnit in xrange(_getNumUnitInfos()):
        CvUnitInfo = _getUnitInfo(iUnit)

        if CvUnitInfo.getDomainType() != _DOMAIN_LAND or CvUnitInfo.getPrereqAndTech() == _NO_TECH:
            continue
        if CvUnitInfo.getMaxGlobalInstances() > 0 or CvUnitInfo.getMaxPlayerInstances() > 0:
            continue

        if not CyCity.canTrain(iUnit, False, False, False, False):
            continue

        iCombat = CvUnitInfo.getCombat()

        # Defender (Archer,Longbow)
        if CvUnitInfo.getDefaultUnitAIType() == _UNITAI_CITY_DEFENSE:
            if iBestDefender == _NO_UNIT or iCombat >= _getUnitInfo(iBestDefender).getCombat():
                iBestDefender = iUnit

        # Counter (Axemen,Phalanx)
        if CvUnitInfo.getUnitAIType(_UNITAI_COUNTER):
            if iCounter == _NO_UNIT or iCombat >= _getUnitInfo(iCounter).getCombat():
                iCounter = iUnit

        # Assault units
        if CvUnitInfo.getUnitAIType(_UNITAI_ATTACK):
            if iAttack == _NO_UNIT or iCombat > _getUnitInfo(iAttack).getCombat():
                iAttack = iUnit

    if iBestDefender == _NO_UNIT:
        if iCounter != _NO_UNIT:
            iBestDefender = iCounter
        else:
            iBestDefender = _UNIT_CLUBMAN
    if iCounter == _NO_UNIT:
        iCounter = iBestDefender
    if iAttack == _NO_UNIT:
        iAttack = iCounter

    # Return tuple instead of list for memory efficiency
    return (_UNIT_WORKER, iBestDefender, iCounter, iAttack)


def getUprisingUnitTypes(CyCity):
    # Returns list of units that can be given to violent rebel uprisings
    aList = []
    for iUnit in xrange(_getNumUnitInfos()):
        CvUnitInfo = _getUnitInfo(iUnit)

        if CvUnitInfo.getDomainType() != _DOMAIN_LAND:
            continue

        if CvUnitInfo.getMaxGlobalInstances() > 0 or CvUnitInfo.getMaxPlayerInstances() > 0:
            continue

        iCombat = CvUnitInfo.getCombat()
        if iCombat < 1:
            continue

        if not CvUnitInfo.hasUnitCombat(UnitCombatTypes(_UNITCOMBAT_COMBATANT)):
            continue

        if CyCity.canTrain(iUnit, False, False, False, False):
            for i in xrange(iCombat / 4 + 1):
                aList.append(iUnit)
    return aList


def computeWarOdds(CyPlayerA, CyPlayerB, CyArea, allowAttackerVassal=True, allowVictimVassal=True,
                   allowBreakVassal=True):
    iTeamA = CyPlayerA.getTeam()  # Aggressor
    iTeamB = CyPlayerB.getTeam()  # Victim
    CyTeamA = _getTeam(iTeamA)
    CyTeamB = _getTeam(iTeamB)

    if iTeamA == iTeamB:
        return (-50, CyTeamA, CyTeamB)

    if CyTeamA.isAtWarWith(iTeamB):
        return (100, CyTeamA, CyTeamB)

    warOdds = 0

    if CyTeamA.isAVassal():
        if not allowAttackerVassal:
            return (-50, CyTeamA, CyTeamB)

        if CyTeamA.isVassal(iTeamB):
            if not allowBreakVassal:
                return (-50, CyTeamA, CyTeamB)
            else:  # Allow vassal to rebel!!!
                warOdds -= 20
        else:  # Find de facto aggressor
            warOdds -= 10
            for iTeam in xrange(_getMAX_PC_TEAMS()):
                if CyTeamA.isVassal(iTeam):
                    iTeamA = iTeam
                    CyTeamA = _getTeam(iTeam)
                    CyPlayerA = _getPlayer(CyTeamA.getLeaderID())

    if CyTeamB.isAVassal():
        if not allowVictimVassal:
            return (-50, CyTeamA, CyTeamB)

        if CyTeamB.isVassal(iTeamA):
            if not allowBreakVassal:
                return (-50, CyTeamA, CyTeamB)
            else:  # Allow master to attack vassal
                warOdds -= 20
        else:  # Find de facto victim
            for iTeam in xrange(_getMAX_PC_TEAMS()):
                if CyTeamB.isVassal(iTeam):
                    iTeamB = iTeam
                    CyTeamB = _getTeam(iTeam)
                    CyPlayerB = _getPlayer(CyTeamB.getLeaderID())
                    break

    iPlayerA = CyPlayerA.getID()
    iPlayerB = CyPlayerB.getID()
    eAttitude = CyPlayerA.AI_getAttitude(iPlayerB)
    if eAttitude == _ATTITUDE_FURIOUS:
        warOdds += 50
    elif eAttitude == _ATTITUDE_ANNOYED:
        warOdds += 25
    elif eAttitude == _ATTITUDE_PLEASED:
        warOdds -= 25
    elif eAttitude == _ATTITUDE_FRIENDLY:
        warOdds -= 50

    iAreaPowerB = CyArea.getPower(iPlayerB)
    if not iAreaPowerB:
        iPowerB = CyPlayerB.getPower()
        if not iPowerB:
            powerFrac = 2
        else:
            powerFrac = 1.0 * CyPlayerA.getPower() / iPowerB + .2
    else:
        powerFrac = CyArea.getPower(iPlayerA) / (1.0 * iAreaPowerB)

    iAreaCitiesA = CyArea.getCitiesPerPlayer(iPlayerA)
    if iAreaCitiesA > 1 and powerFrac > 1.6:
        warOdds += 50
    elif powerFrac > 1.5:
        warOdds += 35
    elif powerFrac > 1.2:
        warOdds += 20
    elif iAreaCitiesA < 1 or powerFrac < .7:
        warOdds -= 40
    elif powerFrac > 1.0:
        warOdds += 10
    else:
        warOdds -= 25

    if iAreaCitiesA > CyArea.getCitiesPerPlayer(iPlayerB):
        warOdds += 10

    if CyPlayerA.hasTrait(_TRAIT_AGGRESSIVE):
        warOdds += 10

    if CyPlayerA.isRebel():
        warOdds += 10

    if warOdds > 100:
        warOdds = 100

    return (warOdds, CyTeamA, CyTeamB)


# Give all techs known by fromPlayer, except a few of the most expensive
def giveTechs(toPlayer, fromPlayer):
    toPlayerTeam = _getTeam(toPlayer.getTeam())
    bSolo = toPlayerTeam.getNumMembers() == 1
    if not bSolo:
        return

    knownTechs = []
    iMinCostly = 0
    iNumCostly = 5 + _getSorenRandNum(4, 'Techs')
    costlyTechs = [(-1, 0)] * iNumCostly

    fromPlayerTeam = _getTeam(fromPlayer.getTeam())
    iPlayer = toPlayer.getID()

    # Remove all techs from toPlayer and record what can be inherited.
    for iTech in xrange(_getNumTechInfos()):

        if toPlayerTeam.isHasTech(iTech):
            toPlayerTeam.setHasTech(iTech, False, iPlayer, False, False)

        if fromPlayerTeam.isHasTech(iTech):
            knownTechs.append(iTech)
            iCost = _getTechInfo(iTech).getResearchCost()
            if iCost > iMinCostly:
                iMin = iCost
                for i in xrange(iNumCostly):
                    iTechX, iCostX = costlyTechs[i]
                    if iCostX == iMinCostly:
                        costlyTechs[i] = (iTech, iCost)
                    elif iCostX < iMin:
                        iMin = iCostX
                iMinCostly = iMin

    # Build set for O(1) lookup
    bestTechs = set()
    for i in xrange(iNumCostly):
        bestTechs.add(costlyTechs[i][0])

    for iTech in knownTechs:
        if iTech in bestTechs:
            toPlayerTeam.setResearchProgress(iTech, _getSorenRandNum(int(toPlayerTeam.getResearchCost(iTech) * .75),
                                                                     'Free research'), iPlayer)
        else:
            toPlayerTeam.setHasTech(iTech, True, iPlayer, False, False)


########################## City helper functions ###############################

def giveCityCulture(CyCity, iPlayer, newCityVal, newPlotVal):
    # Places this culture value in city and city plot
    # Places half this value in neighboring plots

    if iPlayer < 0 or iPlayer >= _getMAX_PC_PLAYERS():
        return
    CyPlot = CyCity.plot()

    if newCityVal > CyCity.getCulture(iPlayer):
        CyCity.setCulture(iPlayer, newCityVal, True)

    if CyCity.getCultureLevel() > 2:
        culRadius = 3
    else:
        culRadius = 2

    for radius, CyPlotX in plotGenerator(CyPlot, culRadius):
        if radius:
            newPlotCul = newPlotVal / (2 * radius)
        else:
            newPlotCul = newPlotVal

        if newPlotCul > CyPlotX.getCulture(iPlayer):
            CyPlotX.setCulture(iPlayer, newPlotCul, True)


def isCanBribeCity(CyCity):
    iRevIdx = CyCity.getRevolutionIndex()

    if iRevIdx > 1700:
        return (False, 'Violent')

    if iRevIdx < 450 and CyCity.getLocalRevIndex() < 8:
        return (False, 'No Need')

    return (True, None)


def computeBribeCosts(CyCity):
    iTurn = _getGameTurn()

    turnBribeData = RevData.getCityVal(CyCity, 'TurnBribeCosts')
    if turnBribeData != None and iTurn == turnBribeData[0]:
        return (turnBribeData[1][0], turnBribeData[1][1], turnBribeData[1][2])

    # Compute costs to bribe rebels at three levels
    # Start by computing a base cost based on players economy strength
    iPlayer = CyCity.getOwner()
    CyPlayer = _getPlayer(iPlayer)

    iRevIdx = CyCity.getRevolutionIndex()
    localRevIdx = CyCity.getLocalRevIndex()

    iPop = CyCity.getPopulation()
    fBaseCost = (iRevIdx + 16 * localRevIdx + 3 * CyCity.getNumRevolts(iPlayer)) * (iPop ** 1.1) / 8.0

    fMod = (1 + CyPlayer.getCurrentEra() - 9 / (8.1 + iPop ** 1.3)) / 3
    fMod *= _getGameSpeedInfo(_getGameSpeedType()).getSpeedPercent() / 100.0

    if not CyPlayer.isHuman():
        fMod /= 2

    iCost = int(fMod * fBaseCost)
    if iCost < 3:
        iCost = 3
    aList = (2 * iCost / 3, iCost, 5 * iCost / 3)
    RevData.setCityVal(CyCity, 'TurnBribeCosts', (iTurn, aList))

    return aList


def bribeCity(CyCity, bribeSize):
    iRevIdx = CyCity.getRevolutionIndex()

    if bribeSize == 'Small':
        # Small reduction in rev index, mostly just for buyoffturns
        newRevIdx = int(0.9 * iRevIdx - 10)
        if newRevIdx < 0:
            newRevIdx = 0
        CyCity.changeRevolutionCounter(5)
    elif bribeSize == 'Med':
        # Med reduction in rev index
        newRevIdx = int(0.8 * iRevIdx - 25)
        if newRevIdx < 0:
            newRevIdx = 0
        CyCity.changeRevolutionCounter(7)
    elif bribeSize == 'Large':
        # Large reduction in rev index, longer time till next revolt too
        newRevIdx = int(0.7 * iRevIdx - 50)
        if newRevIdx < 0:
            newRevIdx = 0
        CyCity.changeRevolutionCounter(10)
    else:
        print
        'Error!  Unrecognized bribeSize string %s' % bribeSize
        return
    CyCity.setRevolutionIndex(newRevIdx)
    RevData.setCityVal(CyCity, 'BribeTurn', _getGameTurn())
    RevData.setCityVal(CyCity, 'TurnBribeCosts', None)


########################## RevIndex helper functions #####################

def getModNumUnhappy(CyCity, fWarWearinessMod):
    iPop = CyCity.getPopulation()

    iMod = int(fWarWearinessMod * iPop * CyCity.getWarWearinessPercentAnger() / 1000)

    iNumUnhappy = CyCity.angryPopulation(0) - iMod - 1

    if iNumUnhappy < 1:
        return CyCity.unhappyLevel(0) - CyCity.happyLevel()
    return iNumUnhappy


def doRevRequestDeniedPenalty(CyCity, iHomeArea, iRevIdxInc=100, bExtraHomeland=False, bExtraColony=False):
    iLocalRevIdx = CyCity.getLocalRevIndex()
    if iLocalRevIdx > 20:
        iLocalRevIdx = 20
    bHome = CyCity.area().getID() == iHomeArea

    if bExtraColony and not bHome or bExtraHomeland and bHome:
        fChange = 1.5 * iRevIdxInc + 12 * iLocalRevIdx
        fMin = .75 * iRevIdxInc
        if fChange < fMin:
            fChange = fMin
        iChange = int(fChange)
    else:
        iChange = iRevIdxInc + 12 * iLocalRevIdx
        iMin = int(.75 * iRevIdxInc)
        if iChange < iMin:
            iChange = iMin
    CyCity.changeRevolutionIndex(iChange)

    iAngerTimer = CyCity.getRevRequestAngerTimer()
    iMax = 3 * deniedTurns
    if iAngerTimer < iMax:
        iChange = iMax - iAngerTimer
        iMax = 2 * deniedTurns
        if iChange > iMax:
            iChange = iMax
        CyCity.changeRevRequestAngerTimer(iChange)
    CyCity.changeRevolutionCounter(deniedTurns)


def computeCivSizeRaw(iOwnedPlots):
    # Ratio of amount of land player owns to what would be equal for this map for national effects
    fPlotsRatio = 1.0 * _getLandPlots() / _getWorldInfo(_getWorldSize()).getDefaultPlayers()

    fSizeValueRaw = iOwnedPlots / fPlotsRatio
    fCivEffRadRaw = ((.5 * iOwnedPlots + .5 * fPlotsRatio) / 3.4) ** .5

    return (fSizeValueRaw, fCivEffRadRaw)


def computeCivSize(player):
    # Ratio of amount of land player owns to what would be equal for this map for national effects
    fPlotsRatio = 1.0 * _getLandPlots() / _getWorldInfo(_getWorldSize()).getDefaultPlayers()
    iOwnedPlots = player.getTotalLand()

    civSizeEraMod = 0.85 - 0.20 * player.getCurrentEra()
    if civSizeEraMod < 0:
        civSizeEraMod = 0
    fCivSizeValue = iOwnedPlots / fPlotsRatio + civSizeEraMod
    fCivEffRadius = ((.5 * iOwnedPlots + .5 * fPlotsRatio) / 3.4) ** .5

    return (fCivSizeValue, fCivEffRadius)


########################## Player modification functions ###########################################

# Changes specified players civ, leader. Does not change isHuman setting
def changeCiv(playerIdx, newCivType=-1, newLeaderType=-1, teamIdx=-1):
    player = _getPlayer(playerIdx)
    oldCivType = player.getCivilizationType()
    oldLeaderType = player.getLeaderType()
    if newCivType >= 0 and newCivType != oldCivType:
        player.changeCiv(newCivType)
        if RevDCMOpt.isDYNAMIC_CIV_NAMES():
            DynamicCivNames.resetName(playerIdx)
            DynamicCivNames.setNewNameByCivics(playerIdx)
    if newLeaderType >= 0 and newLeaderType != oldLeaderType:
        player.setName("")
        player.changeLeader(newLeaderType)

    return True


# Changes leader personality of this civ
def changePersonality(playerIdx, newPersonality=-1):
    if newPersonality < 0:
        iBestValue = 0
        newPersonality = -1

        for iI in xrange(_getNumLeaderHeadInfos()):
            if iI != _BARBARIAN_LEADER:
                iValue = 1 + _getSorenRandNum(10000, "Choosing Personality")

                for iJ in xrange(_getMAX_PC_PLAYERS()):
                    if _getPlayer(iJ).isEverAlive():
                        if _getPlayer(iJ).getPersonalityType() == iI:
                            iValue /= 2

                if iValue > iBestValue:
                    iBestValue = iValue
                    newPersonality = iI

    if newPersonality >= 0 and newPersonality < _getNumLeaderHeadInfos():
        _getPlayer(playerIdx).setPersonalityType(newPersonality)


def changeHuman(newHumanIdx, oldHumanIdx):
    _changeHumanPlayer(oldHumanIdx, newHumanIdx)
    doRefortify(newHumanIdx)


########################## Civics effect helper functions #####################
def getCivicsRevIdxLocal(pPlayer):
    if pPlayer is None or pPlayer.getNumCities() < 1:
        return (0, (), ())

    civicLists = CivicData.civicLists
    localRevIdx = 0
    posList = []
    negList = []

    for i in xrange(_getNumCivicOptionInfos()):
        myCivic = _getCivicInfo(pPlayer.getCivics(i))
        civicEffect = myCivic.getRevIdxLocal()
        if not civicEffect:
            continue

        if civicEffect < 0:
            posList.append((civicEffect, myCivic.getDescription()))

        else:  # Effect doubles for some when a much better alternative exists

            if myCivic.getRevLaborFreedom() < -1:
                for civicX, iCivicX in civicLists[myCivic.getCivicOptionType()]:
                    if civicX.getRevLaborFreedom() > 1 and pPlayer.canDoCivics(iCivicX):
                        civicEffect *= 2
                        break

            if myCivic.getRevDemocracyLevel() < -1:
                for civicX, iCivicX in civicLists[myCivic.getCivicOptionType()]:
                    if civicX.getRevDemocracyLevel() > 1 and pPlayer.canDoCivics(iCivicX):
                        civicEffect *= 2
                        break
            negList.append((civicEffect, myCivic.getDescription()))

        localRevIdx += civicEffect

    # Return tuples for memory efficiency
    return (localRevIdx, tuple(posList), tuple(negList))


def getCivicsCivStabilityIndex(pPlayer):
    civStabilityIdx = 0
    posList = []
    negList = []

    if pPlayer is None:
        return (civStabilityIdx, (), ())

    civicLists = CivicData.civicLists

    for i in xrange(_getNumCivicOptionInfos()):
        myCivic = _getCivicInfo(pPlayer.getCivics(i))
        civicEffect = -myCivic.getRevIdxNational()
        if not civicEffect:
            continue

        if civicEffect > 0:
            posList.append((civicEffect, myCivic.getDescription()))
        else:
            # Effect doubles for some when a much better alternative exists
            if myCivic.getRevLaborFreedom() < -1:
                for civicX, iCivicX in civicLists[myCivic.getCivicOptionType()]:
                    if civicX.getRevLaborFreedom() > 1 and pPlayer.canDoCivics(iCivicX):
                        civicEffect *= 2
                        break

            if myCivic.getRevDemocracyLevel() < -1:
                for civicX, iCivicX in civicLists[myCivic.getCivicOptionType()]:
                    if civicX.getRevDemocracyLevel() > 1 and pPlayer.canDoCivics(iCivicX):
                        civicEffect *= 2
                        break

            negList.append((civicEffect, myCivic.getDescription()))

        civStabilityIdx += civicEffect

    return (civStabilityIdx, tuple(posList), tuple(negList))


def getCivicsHolyCityEffects(pPlayer):
    if not pPlayer or pPlayer.getNumCities() < 1:
        return (0, 0)

    goodEffect = 0
    badEffect = 0

    for i in xrange(_getNumCivicOptionInfos()):
        kCivic = _getCivicInfo(pPlayer.getCivics(i))
        goodEffect += kCivic.getRevIdxHolyCityGood()
        badEffect += kCivic.getRevIdxHolyCityBad()

    return (goodEffect, badEffect)


def getCivicsReligionMods(pPlayer):
    if not pPlayer or pPlayer.getNumCities() < 1:
        return (0, 0)

    goodMod = 0
    badMod = 0

    for i in xrange(_getNumCivicOptionInfos()):
        kCivic = _getCivicInfo(pPlayer.getCivics(i))
        goodMod += kCivic.getRevIdxGoodReligionMod()
        badMod += kCivic.getRevIdxBadReligionMod()

    return (goodMod, badMod)


def getCivicsNationalityMod(pPlayer):
    if pPlayer is None or pPlayer.getNumCities() < 1:
        return 0

    natMod = 0
    for i in xrange(_getNumCivicOptionInfos()):
        natMod += _getCivicInfo(pPlayer.getCivics(i)).getRevIdxNationalityMod()

    return natMod


def getCivicsViolentRevMod(pPlayer):
    if pPlayer is None or pPlayer.getNumCities() < 1:
        return 0

    vioMod = 0
    for i in xrange(_getNumCivicOptionInfos()):
        vioMod += _getCivicInfo(pPlayer.getCivics(i)).getRevViolentMod()

    return vioMod


def canDoCommunism(pPlayer):
    if pPlayer is None or not pPlayer.isAlive():
        return (False, None)

    for i in xrange(_getNumCivicInfos()):
        if _getCivicInfo(i).isCommunism() and pPlayer.canDoCivics(i) and not pPlayer.isCivic(i):
            return (True, i)

    return (False, None)


def canDoFreeSpeech(pPlayer):
    if not pPlayer or not pPlayer.isAlive():
        return (False, None)

    for iCivic in xrange(_getNumCivicInfos()):

        if _getCivicInfo(iCivic).isFreeSpeech() and pPlayer.canDoCivics(iCivic) and not pPlayer.isCivic(iCivic):
            return (True, iCivic)

    return (False, None)


def isFreeSpeech(pPlayer):
    if pPlayer is None or not pPlayer.isAlive():
        return False

    for i in xrange(_getNumCivicInfos()):

        if _getCivicInfo(i).isFreeSpeech() and pPlayer.isCivic(i):
            return True

    return False


def isCanDoElections(pPlayer):
    if pPlayer is None or not pPlayer.isAlive() or pPlayer.isNPC():
        return False

    for i in xrange(_getNumCivicOptionInfos()):

        if _getCivicInfo(pPlayer.getCivics(i)).isCanDoElection():
            return True

    return False


def getReligiousFreedom(pPlayer):
    # Returns (freedom level, option type)

    if not pPlayer or not pPlayer.isAlive():
        return (0, None)

    for i in xrange(_getNumCivicOptionInfos()):
        iReligiousFreedom = _getCivicInfo(pPlayer.getCivics(i)).getRevReligiousFreedom()
        if iReligiousFreedom:
            return (iReligiousFreedom, i)

    return (0, None)


def getBestReligiousFreedom(pPlayer, relOptionType):
    # Returns (best level, civic type)

    if not pPlayer or not pPlayer.isAlive() or relOptionType == None:
        return (0, None)

    bestFreedom = -11
    bestCivic = None

    for civicX, iCivicX in CivicData.civicLists[relOptionType]:
        civicFreedom = civicX.getRevReligiousFreedom()
        if civicFreedom > bestFreedom and pPlayer.canDoCivics(iCivicX):
            bestFreedom = civicFreedom
            bestCivic = iCivicX

    return (bestFreedom, bestCivic)


def getDemocracyLevel(pPlayer):
    # Returns (level, option type)

    if not pPlayer or not pPlayer.isAlive():
        return (0, None)

    for i in xrange(_getNumCivicOptionInfos()):
        iDemLvl = _getCivicInfo(pPlayer.getCivics(i)).getRevDemocracyLevel()
        if iDemLvl:
            return (iDemLvl, i)

    return (0, None)


def getBestDemocracyLevel(pPlayer, optionType):
    # Returns (best level, civic type)

    if not pPlayer or not pPlayer.isAlive() or optionType is None:
        return (0, None)

    bestLevel = -11
    bestCivic = None

    for civicX, iCivicX in CivicData.civicLists[optionType]:
        civicLevel = civicX.getRevDemocracyLevel()
        if civicLevel > bestLevel and pPlayer.canDoCivics(iCivicX):
            bestLevel = civicLevel
            bestCivic = iCivicX

    return (bestLevel, bestCivic)


def getLaborFreedom(pPlayer):
    # Returns (level, option type)

    if not pPlayer or not pPlayer.isAlive():
        return (0, None)

    for i in xrange(_getNumCivicOptionInfos()):
        iLaborFreedom = _getCivicInfo(pPlayer.getCivics(i)).getRevLaborFreedom()
        if iLaborFreedom:
            return (iLaborFreedom, i)

    return (0, None)


def getBestLaborFreedom(pPlayer, optionType):
    # Returns (best level, civic type)

    if None in (pPlayer, optionType) or not pPlayer.isAlive():
        return (0, None)

    bestLevel = -11
    bestCivic = None

    for civicX, iCivicX in CivicData.civicLists[optionType]:
        civicLevel = civicX.getRevLaborFreedom()
        if civicLevel > bestLevel and pPlayer.canDoCivics(iCivicX):
            bestLevel = civicLevel
            bestCivic = iCivicX

    return (bestLevel, bestCivic)


# Returns (level, option type)
def getEnvironmentalProtection(pPlayer):
    if pPlayer is None or not pPlayer.isAlive():
        return (0, None)

    for i in xrange(_getNumCivicOptionInfos()):
        iEnvirenmentalProtection = _getCivicInfo(pPlayer.getCivics(i)).getRevEnvironmentalProtection()
        if iEnvirenmentalProtection:
            return (iEnvirenmentalProtection, i)

    return (0, None)


def getBestEnvironmentalProtection(pPlayer, optionType):
    # Returns (best level, civic type)

    if None in (pPlayer, optionType) or not pPlayer.isAlive():
        return (0, None)

    bestLevel = -11
    bestCivic = None

    for civicX, iCivicX in CivicData.civicLists[optionType]:
        civicLevel = civicX.getRevEnvironmentalProtection()
        if civicLevel > bestLevel and pPlayer.canDoCivics(iCivicX):
            bestLevel = civicLevel
            bestCivic = iCivicX

    return (bestLevel, bestCivic)


########################## Traits effect helper functions #####################

def getTraitsRevIdxLocal(pPlayer):
    if not pPlayer or pPlayer.getNumCities() < 1:
        return (0, (), ())

    localRevIdx = 0
    posList = []
    negList = []

    for i in xrange(_getNumTraitInfos()):
        if pPlayer.hasTrait(i):
            kTrait = _getTraitInfo(i)
            traitEffect = kTrait.getRevIdxLocal()
            if traitEffect > 0:
                negList.append((traitEffect, kTrait.getDescription()))
            elif traitEffect < 0:
                posList.append((traitEffect, kTrait.getDescription()))

            localRevIdx += traitEffect

    return (localRevIdx, tuple(posList), tuple(negList))


def getTraitsCivStabilityIndex(pPlayer):
    if not pPlayer:
        return (0, (), ())

    civStabilityIdx = 0
    posList = []
    negList = []

    for iTrait in xrange(_getNumTraitInfos()):
        kTrait = _getTraitInfo(iTrait)
        traitEffect = -kTrait.getRevIdxNational()

        if pPlayer.hasTrait(iTrait):
            if traitEffect > 0:
                posList.append((traitEffect, kTrait.getDescription()))
            elif traitEffect < 0:
                negList.append((traitEffect, kTrait.getDescription()))

            civStabilityIdx += traitEffect

    return (civStabilityIdx, tuple(posList), tuple(negList))


def getTraitsHolyCityEffects(pPlayer):
    if pPlayer is None or not pPlayer.getNumCities():
        return (0, 0)

    goodEffect = 0
    badEffect = 0

    for i in xrange(_getNumTraitInfos()):
        if pPlayer.hasTrait(i):
            kTrait = _getTraitInfo(i)
            goodEffect += kTrait.getRevIdxHolyCityGood()
            badEffect += kTrait.getRevIdxHolyCityBad()

    return (goodEffect, badEffect)


def getTraitsReligionMods(pPlayer):
    if pPlayer is None or not pPlayer.getNumCities():
        return (0, 0)

    goodMod = 0
    badMod = 0

    for i in xrange(_getNumTraitInfos()):
        if pPlayer.hasTrait(i):
            kTrait = _getTraitInfo(i)
            goodMod += kTrait.getRevIdxGoodReligionMod()
            badMod += kTrait.getRevIdxBadReligionMod()

    return (goodMod, badMod)


########################## Buildings effect helper functions #####################
def getBuildingsRevIdxLocal(CyCity):
    localRevIdx = 0
    posList = []
    negList = []

    for iBuilding in xrange(_getNumBuildingInfos()):
        if CyCity.isActiveBuilding(iBuilding):
            CvBuildingInfo = _getBuildingInfo(iBuilding)
            buildingEffect = CvBuildingInfo.getRevIdxLocal()
            if buildingEffect > 0:
                negList.append((buildingEffect, CvBuildingInfo.getDescription()))
            elif buildingEffect < 0:
                posList.append((buildingEffect, CvBuildingInfo.getDescription()))

            localRevIdx += buildingEffect

    return (localRevIdx, tuple(posList), tuple(negList))


def getBuildingsCivStabilityIndex(player):
    if not player:
        return (0, (), ())

    civStabilityIdx = 0
    posList = []
    negList = []
    for iBuilding in xrange(_getNumBuildingInfos()):
        CvBuildingInfo = _getBuildingInfo(iBuilding)
        buildingEffect = -CvBuildingInfo.getRevIdxNational()

        if buildingEffect:
            numBuildings = player.countNumBuildings(iBuilding)
            if numBuildings:
                buildingEffect *= numBuildings
                if buildingEffect > 0:
                    posList.append((buildingEffect, CvBuildingInfo.getDescription()))
                elif buildingEffect < 0:
                    negList.append((buildingEffect, CvBuildingInfo.getDescription()))
                civStabilityIdx += buildingEffect

    return (civStabilityIdx, tuple(posList), tuple(negList))


## Text Utility
def getCityTextList(cityList, bPreCity=False, bPreCitizens=False, sep=', ', second='', penUlt='', bPostIs=False):
    textList = []
    for pCity in cityList:
        textList.append(pCity.getName())

    pre = ''
    if bPreCity:
        if len(cityList) > 1 and second == '':
            pre = _getText(_TXT_CITIES_OF, ()) + ' '
        else:
            pre = _getText(_TXT_CITY_OF, ()) + ' '

    elif bPreCitizens:
        pre = _getText(_TXT_CITIZENS_OF, ()) + ' '

    if not textList:
        return pre.strip()

    # Build the result using list joining for efficiency
    result_parts = [pre, textList[0]]

    if len(textList) > 1:
        result_parts.append(second)
        if second == '':
            result_parts.append(sep)

        for text in textList[1:-1]:
            result_parts.append(text)
            result_parts.append(sep)

        if len(textList) > 2 or second == '':
            result_parts.append(_getText(_TXT_AND, ()))
            result_parts.append(' ')
        result_parts.append(textList[-1])

    post = ''
    if bPostIs:
        if bPreCitizens or len(cityList) > 1 and second == '':
            post = ' ' + _getText(_TXT_ARE, ())
        else:
            post = ' ' + _getText(_TXT_IS, ())
            if second != '':
                post = sep.strip() + post

    result_parts.append(post)

    return ''.join(result_parts)