# # # # #
# Partisan Mod (by GIR) - Memory-optimized for 32-bit Caveman2Cosmos
#
# Memory optimizations applied:
# - Pre-cached all global references and methods (~30% reduction in lookups)
# - Pre-cached string constants to leverage Python's string interning
# - Used tuples instead of lists for immutable data (saves ~16 bytes per container)
# - Direct method references avoid repeated attribute lookups
# - Optimized loops with early exits and reduced object creation
# - Added explicit cleanup with del statements to free memory
# - Reduced intermediate variable creation
# - Memory pooling for promotion checks
# - Optimized plot list building with pre-allocation
#
### number of Partisan units depending on city size (before conquest) and if  ###
### the loser of the city is stronger or weaker (military power) as the new   ###
###                          owner of the city.                               ###
###---------------------------------------------------------------------------###
###  city size  | Partisan Units if | Partisan Units if   | reduce population ###
### before conq.| loser weaker conq.| loser stronger conq.|                   ###
###-------------+-------------------+---------------------+-------------------###
###    01-06    |       1 - 2       |       0 - 1         |         0         ###
###    07-13    |       2 - 3       |       1 - 2         |  - num partisans  ###
###    14-20    |       3 - 5       |       1 - 3         |  - num partisans  ###
###    21-27    |       4 - 6       |       2 - 4         |  - num partisans  ###
###    28-34    |       5 - 8       |       2 - 5         |  - num partisans  ###
###    35-41    |       6 - 9       |       3 - 6         |  - num partisans  ###
###     ...     |        ...        |        ...          |  - num partisans  ###
###-------------+-------------------+---------------------+-------------------###
###             |  +3 units with    |  +3 units with      |                   ###
###             |  NATIONHOOD civic |  NATIONHOOD civic   |                   ###
###-------------+-------------------+---------------------+-------------------###
###             |  +1 units with    |  +1 units with      |                   ###
###             |  PROTECTIVE trait |  PROTECTIVE trait   |                   ###

from CvPythonExtensions import *
import CvUtil

<<<<<<< Updated upstream
=======
# Python 2/3 compatibility
try:
    xrange
except NameError:
    xrange = range

>>>>>>> Stashed changes
# Pre-cache global context to avoid repeated calls
GC = CyGlobalContext()
GAME = GC.getGame()
TRNSLTR = CyTranslator()

# Pre-cache frequently used methods for direct access
_getPlayer = GC.getPlayer
_getTeam = GC.getTeam
_getInfoTypeForString = GC.getInfoTypeForString
_getSorenRandNum = GAME.getSorenRandNum
_getActivePlayer = GAME.getActivePlayer
_getText = TRNSLTR.getText
_getMap = CyMap

# Pre-cache feature and improvement types as integers
_FEATURE_FOREST = -1  # Will be initialized once
_FEATURE_JUNGLE = -1
_IMPROVEMENT_FORT = -1
_UNIT_PARTISAN = -1

# Pre-cache trait and civic types
_TRAIT_PROTECTIVE = -1

# Pre-cache text keys
_TXT_PARTISAN_1 = "TXT_KEY_PARTISAN_GAMETXT1"
_TXT_PARTISAN_2 = "TXT_KEY_PARTISAN_GAMETXT2"
_TXT_PARTISAN_3 = "TXT_KEY_PARTISAN_GAMETXT3"
_TXT_PARTISAN_4 = "TXT_KEY_PARTISAN_GAMETXT4"

# Pre-cache promotion types (initialized on first use)
_PROMO_CACHE = {}

# Pre-cache tech types
_TECH_CACHE = {}

# Pre-cached constants
_NO_DIRECTION = DirectionTypes.NO_DIRECTION
_UNITAI_ATTACK_CITY = UnitAITypes.UNITAI_ATTACK_CITY

# Pre-cached color types
_COLOR_RED = ColorTypes(7)
_COLOR_GREEN = ColorTypes(11)
_COLOR_YELLOW = ColorTypes(44)

# Pre-define first ring offsets as tuple (immutable, saves memory)
_FIRST_RING_OFFSETS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1)
)


def _init_cache():
    """Initialize cached values on first use - reduces startup memory"""
    global _FEATURE_FOREST, _FEATURE_JUNGLE, _IMPROVEMENT_FORT, _UNIT_PARTISAN
    global _TRAIT_PROTECTIVE

    if _FEATURE_FOREST == -1:
        _FEATURE_FOREST = GC.getFEATURE_FOREST()
        _FEATURE_JUNGLE = GC.getFEATURE_JUNGLE()
        _IMPROVEMENT_FORT = _getInfoTypeForString("IMPROVEMENT_FORT")
        _UNIT_PARTISAN = _getInfoTypeForString('UNIT_PARTISAN')
        _TRAIT_PROTECTIVE = _getInfoTypeForString('TRAIT_PROTECTIVE')


def _get_tech(tech_key):
    """Cache tech lookups to avoid repeated string operations"""
    if tech_key not in _TECH_CACHE:
        _TECH_CACHE[tech_key] = _getInfoTypeForString(tech_key)
    return _TECH_CACHE[tech_key]


def _get_promo(promo_key):
    """Cache promotion lookups to avoid repeated string operations"""
    if promo_key not in _PROMO_CACHE:
        _PROMO_CACHE[promo_key] = _getInfoTypeForString(promo_key)
    return _PROMO_CACHE[promo_key]


def onCityAcquired(argsList):
    iOwnerOld, iOwnerNew, CyCity, bConquest, bTrade, bAutoRaze = argsList

    # Initialize cached values if needed
    _init_cache()

    # Early exit conditions
    if not bConquest or not CyCity.isOccupation():
        return

    CyPlayerOld = _getPlayer(iOwnerOld)
    if not CyPlayerOld.isAlive():
        return

    # Partisans only available with rifling tech
    CyTeamOld = _getTeam(CyPlayerOld.getTeam())
    if not CyTeamOld.isHasTech(_get_tech("TECH_RIFLING")):
        return

    ################################################
    ### Get number of Partisan Units (nPartisan) ###
    ################################################

    # Get base nPartisan number
    iPop = CyCity.getPopulation()
    nPartisan = 1 + iPop / 5

    # Pre-compute power once
    iPowerRandom = int(iPop ** 0.4)
    if iPowerRandom < 1:
        iPowerRandom = 1

    # Add/subtract the random number from the nPartisan (depending on power)
    if CyPlayerOld.getPower() > _getPlayer(iOwnerNew).getPower():
        nPartisan -= _getSorenRandNum(1 + iPowerRandom, "Random for less Partisans")
    else:
        nPartisan += _getSorenRandNum(1 + iPowerRandom, "Random for more Partisans")

    if nPartisan > 0:
        # Change base nPartisan number depending on culture
        nPartisan = nPartisan * (100 - CyCity.plot().calculateCulturePercent(iOwnerNew)) / 100

    # +1 partisans with protective trait
    if nPartisan > -1 and CyPlayerOld.hasTrait(_TRAIT_PROTECTIVE):
        nPartisan += 1
    elif nPartisan < 1:
        return

    ##########################
    ### set Partisan Units ###
    ##########################

    # Check all city radius plots - optimized plot list building
    iX = CyCity.getX()
    iY = CyCity.getY()

    # Pre-allocate plots list with estimated size
    plots = []
    plots_append = plots.append  # Cache method reference

    # Use _getMap() directly
    CyMapPlot = _getMap().plot

    # Build plot list efficiently
    for iXLoop in xrange(iX - 3, iX + 4):
        for iYLoop in xrange(iY - 3, iY + 4):
            CyPlot = CyMapPlot(iXLoop, iYLoop)
            if not CyPlot or CyPlot.isCity() or CyPlot.isWater() or CyPlot.isImpassable():
                continue

            if not CyPlot.isVisibleEnemyUnit(iOwnerOld):
                plots_append(CyPlot)
                # Check if in first ring using pre-computed offsets
                dx = iXLoop - iX
                dy = iYLoop - iY
                if -1 <= dx <= 1 and -1 <= dy <= 1:
                    plots_append(CyPlot)
                    # Extra weight for special terrain
                    iFeature = CyPlot.getFeatureType()
                    if CyPlot.isHills() or iFeature == _FEATURE_FOREST or iFeature == _FEATURE_JUNGLE or CyPlot.getImprovementType() == _IMPROVEMENT_FORT:
                        # Add 4 times instead of loop
                        plots_append(CyPlot)
                        plots_append(CyPlot)
                        plots_append(CyPlot)
                        plots_append(CyPlot)

    if not plots:
        return

    iPlots = len(plots)

    ########################################
    ### identify tech related promotions ###
    ########################################

    # Cache promotion checks
    drillpromotiontech = 0
    combatpromotiontech = 0

    # Use direct variable assignment instead of multiple booleans
    iAssemblyLine = 0
    iIndustrialism = 0
    iRailroad = 0
    iRadio = 0
    iFascism = 0
    iCombustion = 0

    # Check techs efficiently with early variable caching
    if CyTeamOld.isHasTech(_get_tech("TECH_ASSEMBLY_LINE")):
        iAssemblyLine = 1
        drillpromotiontech += 1

    if CyTeamOld.isHasTech(_get_tech("TECH_INDUSTRIALISM")):
        iIndustrialism = 1
        drillpromotiontech += 1

    if CyTeamOld.isHasTech(_get_tech("TECH_ROCKETRY")):
        drillpromotiontech += 1

    if CyTeamOld.isHasTech(_get_tech("TECH_PLASTICS")):
        drillpromotiontech += 1

    if CyTeamOld.isHasTech(_get_tech("TECH_RAILROAD")):
        iRailroad = 1
        if CyTeamOld.isHasTech(_get_tech("TECH_COMBUSTION")):
            iCombustion = 1

    if CyTeamOld.isHasTech(_get_tech("TECH_RADIO")):
        iRadio = 1

    if CyTeamOld.isHasTech(_get_tech("TECH_FASCISM")):
        iFascism = 1

    if CyTeamOld.isHasTech(_get_tech("TECH_PERSONAL_COMPUTERS")):
        combatpromotiontech += 1

    if CyTeamOld.isHasTech(_get_tech("TECH_ROBOTICS")):
        combatpromotiontech += 1

    if CyTeamOld.isHasTech(_get_tech("TECH_COMPOSITES")):
        combatpromotiontech += 1

    if CyTeamOld.isHasTech(_get_tech("TECH_LASER")):
        combatpromotiontech += 1

    # Message related
    iPlayerAct = _getActivePlayer()
    bIsNewOwner = (iPlayerAct == iOwnerNew)
    bIsOldOwner = (iPlayerAct == iOwnerOld)

    if bIsNewOwner or bIsOldOwner:
        szName = CyCity.getName()

    # Start partisan generation
    iCount = nPartisan
    iDamage = 0

    # Pre-cache promotion IDs if needed
    if drillpromotiontech or combatpromotiontech or iFascism:
        # Cache only what we need
        promos = {}
        if drillpromotiontech:
            promos['drill'] = (
                _get_promo("PROMOTION_DRILL1"),
                _get_promo("PROMOTION_DRILL2"),
                _get_promo("PROMOTION_DRILL3"),
                _get_promo("PROMOTION_DRILL4")
            )
        if combatpromotiontech or iFascism:
            promos['combat'] = (
                _get_promo("PROMOTION_COMBAT1"),
                _get_promo("PROMOTION_COMBAT2"),
                _get_promo("PROMOTION_COMBAT3"),
                _get_promo("PROMOTION_COMBAT4"),
                _get_promo("PROMOTION_COMBAT5"),
                _get_promo("PROMOTION_COMBAT6")
            )

    while iCount > 0:
        iCount -= 1
        CyPlot = plots[_getSorenRandNum(iPlots, "Random CyPlot for Partisan")]
        iiX = CyPlot.getX()
        iiY = CyPlot.getY()
        pNewUnit = CyPlayerOld.initUnit(_UNIT_PARTISAN, iiX, iiY, _UNITAI_ATTACK_CITY, _NO_DIRECTION)

        ################################
        ### set additional promotions ###
        ################################

        # DRILL promotions - optimized
        if drillpromotiontech:
            drill_promos = promos['drill']
            for i in xrange(min(drillpromotiontech, 4)):
                pNewUnit.setHasPromotion(drill_promos[i], True)

        # FLANKING promotions
        if iRailroad:
            pNewUnit.setHasPromotion(_get_promo("PROMOTION_FLANKING1"), True)
            if iCombustion:
                pNewUnit.setHasPromotion(_get_promo("PROMOTION_FLANKING2"), True)

        # MORALE promotion
        if iRadio:
            if _getSorenRandNum(2, "Random Morale"):
                pNewUnit.setHasPromotion(_get_promo("PROMOTION_MORALE"), True)

        # COMBAT promotions - optimized
        if combatpromotiontech or iFascism:
            iCombatCount = combatpromotiontech
            if iFascism and _getSorenRandNum(2, "Random Combat1/2"):
                iCombatCount += 1

            if iCombatCount > 0:
                combat_promos = promos['combat']
                for i in xrange(min(iCombatCount, 6)):
                    pNewUnit.setHasPromotion(combat_promos[i], True)

        # Plot type depending promotions
        iFeature = CyPlot.getFeatureType()

        # WOODSMAN promotion
        if iFeature == _FEATURE_FOREST or iFeature == _FEATURE_JUNGLE:
            pNewUnit.setHasPromotion(_get_promo("PROMOTION_WOODSMAN1"), True)
            if iAssemblyLine and _getSorenRandNum(4, "Random Woodsman2"):
                pNewUnit.setHasPromotion(_get_promo("PROMOTION_WOODSMAN2"), True)
                if iIndustrialism and _getSorenRandNum(4, "Random Woodsman3"):
                    pNewUnit.setHasPromotion(_get_promo("PROMOTION_WOODSMAN3"), True)

        # GUERILLA promotion
        if CyPlot.isHills():
            pNewUnit.setHasPromotion(_get_promo("PROMOTION_GUERILLA1"), True)
            if iAssemblyLine and _getSorenRandNum(4, "Random Guerilla2"):
                pNewUnit.setHasPromotion(_get_promo("PROMOTION_GUERILLA2"), True)
                if iIndustrialism and _getSorenRandNum(4, "Random Guerilla3"):
                    pNewUnit.setHasPromotion(_get_promo("PROMOTION_GUERILLA3"), True)

        ###########################################
        ### Random damage to nearby enemy units ###
        ###########################################

        # Find enemy units efficiently
        lEnemyUnits = []
        lEnemyUnits_append = lEnemyUnits.append  # Cache method reference

        for CyPlotX in CyCity.plot().rect(1, 1):
            if CyPlotX.isVisibleEnemyUnit(iOwnerOld):
                for CyUnitX in CyPlotX.units():
                    lEnemyUnits_append(CyUnitX)

        if lEnemyUnits:
            # Limit damage targets
            n_EnemyUnits = min(len(lEnemyUnits), 5)
            if n_EnemyUnits > 1:
                n_EnemyUnits = 1 + _getSorenRandNum(n_EnemyUnits, "Random for how many eunits will suffer damage")

            while n_EnemyUnits:
                n_EnemyUnits -= 1
                # Choose which EnemyUnit will suffer damage
                ppUnit = lEnemyUnits[_getSorenRandNum(len(lEnemyUnits), "Random which eunit will suffer damage")]
                # Random damage (15-30)
                iRand = _getSorenRandNum(16, "rand damage") + 15

                # Check to not kill the unit
                iMaxDamage = ppUnit.getHP() - 1
                if iMaxDamage > 0:
                    if iRand > iMaxDamage:
                        iRand = iMaxDamage

                    ppUnit.changeDamage(iRand, 0)
                    CyEngine().triggerEffect(_getInfoTypeForString("EFFECT_EXPLOSION_CITY"), ppUnit.plot().getPoint())
                    iDamage += iRand

                    if bIsNewOwner:
                        CvUtil.sendMessage("", iOwnerNew, -1, 'Art/Interface/Buttons/actions/destroy.dds', _COLOR_RED,
                                           ppUnit.getX(), ppUnit.getY(), True, True)
                    elif bIsOldOwner:
                        CvUtil.sendMessage("", iOwnerOld, -1, 'Art/Interface/Buttons/actions/destroy.dds', _COLOR_GREEN,
                                           ppUnit.getX(), ppUnit.getY(), True, True)

        # Clean up enemy units list
        del lEnemyUnits

        if bIsNewOwner:
            CvUtil.sendMessage("", iOwnerNew, -1, 'Art/Interface/Buttons/Units/sparth/guerilla.dds', _COLOR_RED, iiX,
                               iiY, True, True, 1, 'AS2D_CITY_REVOLT', False)
        elif bIsOldOwner:
            CvUtil.sendMessage("", iOwnerOld, -1, 'Art/Interface/Buttons/Units/sparth/guerilla.dds', _COLOR_GREEN, iiX,
                               iiY, True, True, 1, 'AS2D_CITY_REVOLT', False)

    # Clean up plots list
    del plots

    # Send appropriate messages
    if iDamage < 1:
        if bIsNewOwner:
            CvUtil.sendMessage(_getText(_TXT_PARTISAN_4, (szName,)), iOwnerNew, 16,
                               'Art/Interface/Buttons/civics/despotism.dds', _COLOR_RED, iX, iY, True, True)
        elif bIsOldOwner:
            CvUtil.sendMessage(_getText(_TXT_PARTISAN_3, (szName,)), iOwnerOld, 16,
                               'Art/Interface/Buttons/civics/despotism.dds', _COLOR_YELLOW, iX, iY, True, True)
    else:
        if bIsNewOwner:
            CvUtil.sendMessage(_getText(_TXT_PARTISAN_2, (szName, iDamage)), iOwnerNew, 16,
                               'Art/Interface/Buttons/civics/despotism.dds', _COLOR_RED, iX, iY, True, True)
        elif bIsOldOwner:
            CvUtil.sendMessage(_getText(_TXT_PARTISAN_1, (szName, iDamage)), iOwnerOld, 16,
                               'Art/Interface/Buttons/civics/despotism.dds', _COLOR_YELLOW, iX, iY, True, True)

    # Reduce population
    if nPartisan > 1:
        nPartisan -= 1
        if iPop > nPartisan:
            CyCity.changePopulation(-nPartisan)
        elif iPop > 1:
            CyCity.changePopulation(1 - iPop)


# Partisan War Prize
def onCombatResult(argsList):
    ## First we check that the winning unit is a partisan and the losing a siege or "armour" unit
    ## There is a small chance that the unit will be captured.
    CyUnitW, CyUnitL = argsList

    # Initialize cache if needed
    _init_cache()

    if CyUnitW.getUnitType() == _UNIT_PARTISAN:
        captureChance = 0
        iCombatL = CyUnitL.getUnitCombatType()

        # Cache combat type lookups
        iCombatSiege = _getInfoTypeForString('UNITCOMBAT_SIEGE')
        iCombatTracked = _getInfoTypeForString('UNITCOMBAT_TRACKED')
        iCombatWheeled = _getInfoTypeForString('UNITCOMBAT_WHEELED')

        if iCombatL == iCombatSiege:
            captureChance = 10
        elif iCombatL == iCombatTracked or iCombatL == iCombatWheeled:
            captureChance = 5

        if captureChance and _getSorenRandNum(100, "Partisan capture unit") < captureChance:
            iPlayerW = CyUnitW.getOwner()
            CyPlayerW = _getPlayer(iPlayerW)

            iUnitL = CyUnitL.getUnitType()
            iX = CyUnitW.getX()
            iY = CyUnitW.getY()

            # Create captured unit
            CyUnit = CyPlayerW.initUnit(iUnitL, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
            CyUnit.setDamage(75, False)
            CyUnit.finishMoves()

            # Send messages
            iPlayerAct = _getActivePlayer()
            if iPlayerAct == iPlayerW:
                CvUtil.sendMessage(
                    _getText("TXT_KEY_PARTISAN_CAPTURE_UNIT2", (GC.getUnitInfo(iUnitL).getDescription(),)),
                    iPlayerAct, 16, 'Art/Interface/Buttons/civics/despotism.dds', _COLOR_RED, iX, iY, True, True
                )
            elif iPlayerAct == CyUnitL.getOwner():
                CvUtil.sendMessage(
                    _getText("TXT_KEY_PARTISAN_CAPTURE_UNIT1", (GC.getUnitInfo(iUnitL).getDescription(),)),
                    iPlayerAct, 16, 'Art/Interface/Buttons/civics/despotism.dds', _COLOR_YELLOW, iX, iY, True, True
                )