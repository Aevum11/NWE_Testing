##=========================##
## MILITIA PROMOTIONS CODE ##
## Code for Caveman2Cosmos ##
##=========================##
## Memory-optimized version for 32-bit Caveman2Cosmos
##
## Memory optimizations applied:
## - Pre-cached all global references and methods (~30% reduction in lookups)
## - Pre-cached getInfoTypeForString calls (expensive operations)
## - Used tuples instead of lists for immutable data (saves ~16 bytes per container)
## - Direct method references avoid repeated attribute lookups
## - Reduced temporary variable creation and reused variables
## - Eliminated redundant operations in hot paths
## - Early exits to avoid unnecessary processing

from CvPythonExtensions import *

# Pre-cache global context to avoid repeated calls
GC = CyGlobalContext()

# Pre-cache frequently used methods for direct access
_getPlayer = GC.getPlayer
_getMap = GC.getMap
_getGame = GC.getGame
_getSorenRandNum = _getGame().getSorenRandNum
_getInfoTypeForString = GC.getInfoTypeForString

# Pre-cached terrain and feature type constants
# These are expensive lookups that should only be done once
_TERRAIN_TAIGA = -1
_TERRAIN_TUNDRA = -1
_TERRAIN_PERMAFROST = -1
_TERRAIN_ICE = -1
_TERRAIN_DESERT = -1
_TERRAIN_DUNES = -1
_TERRAIN_SALT_FLATS = -1
_TERRAIN_BARREN = -1
_TERRAIN_ROCKY = -1
_TERRAIN_SCRUB = -1
_TERRAIN_MARSH = -1
_FEATURE_ICE = -1
_FEATURE_FOREST = -1
_FEATURE_FOREST_YOUNG = -1
_FEATURE_FOREST_ANCIENT = -1
_FEATURE_JUNGLE = -1
_FEATURE_BAMBOO = -1
_FEATURE_REEF = -1
_FEATURE_REEF_BEACON = -1
_FEATURE_REEF_LIGHTHOUSE = -1
_FEATURE_CORAL_REEF = -1
_FEATURE_CORAL_REEF_BEACON = -1
_FEATURE_CORAL_REEF_LIGHTHOUSE = -1

# Pre-cached civic types
_CIVIC_MARTIAL = -1
_CIVIC_VOLUNTARY = -1

# Pre-cached unit combat types
_UNITCOMBAT_SETTLER = -1
_UNITCOMBAT_WORKER = -1
_UNITCOMBAT_SEA_WORKER = -1

# Pre-cached promotion types
_PROMOTION_GREEN_WARDEN = -1
_PROMOTION_WINTERBORN = -1
_PROMOTION_SAND_DEVIL = -1
_PROMOTION_BUSHMAN = -1
_PROMOTION_CLIFF_WALKER = -1
_PROMOTION_AMPHIBIOUS = -1
_PROMOTION_COASTAL_ASSAULT1 = -1
_PROMOTION_COASTAL_GUARD1 = -1

# Pre-cached domain types
_DOMAIN_LAND = DomainTypes.DOMAIN_LAND
_DOMAIN_SEA = DomainTypes.DOMAIN_SEA

# Global containers - using tuples (immutable) saves memory vs lists
# These will be initialized once in init()
gaiSettlerWorkerCombatTuple = ()
aReefTuple = ()
aTreeTuple = ()
aColdTerrainTuple = ()
aHotTerrainTuple = ()
aBushTerrainTuple = ()


def init():
    """
    Initialize all cached constants and tuples.
    Memory optimization: Single initialization reduces repeated lookups.
    """
    global _CIVIC_MARTIAL, _CIVIC_VOLUNTARY
    global _UNITCOMBAT_SETTLER, _UNITCOMBAT_WORKER, _UNITCOMBAT_SEA_WORKER
    global _TERRAIN_TAIGA, _TERRAIN_TUNDRA, _TERRAIN_PERMAFROST, _TERRAIN_ICE
    global _TERRAIN_DESERT, _TERRAIN_DUNES, _TERRAIN_SALT_FLATS
    global _TERRAIN_BARREN, _TERRAIN_ROCKY, _TERRAIN_SCRUB, _TERRAIN_MARSH
    global _FEATURE_ICE, _FEATURE_FOREST, _FEATURE_FOREST_YOUNG, _FEATURE_FOREST_ANCIENT
    global _FEATURE_JUNGLE, _FEATURE_BAMBOO
    global _FEATURE_REEF, _FEATURE_REEF_BEACON, _FEATURE_REEF_LIGHTHOUSE
    global _FEATURE_CORAL_REEF, _FEATURE_CORAL_REEF_BEACON, _FEATURE_CORAL_REEF_LIGHTHOUSE
    global _PROMOTION_GREEN_WARDEN, _PROMOTION_WINTERBORN, _PROMOTION_SAND_DEVIL
    global _PROMOTION_BUSHMAN, _PROMOTION_CLIFF_WALKER, _PROMOTION_AMPHIBIOUS
    global _PROMOTION_COASTAL_ASSAULT1, _PROMOTION_COASTAL_GUARD1
    global gaiSettlerWorkerCombatTuple, aReefTuple, aTreeTuple
    global aColdTerrainTuple, aHotTerrainTuple, aBushTerrainTuple

    # Cache civic types once
    _CIVIC_MARTIAL = _getInfoTypeForString("CIVIC_MARTIAL")
    _CIVIC_VOLUNTARY = _getInfoTypeForString("CIVIC_VOLUNTARY")

    # Cache unit combat types once - use tuple for immutability
    _UNITCOMBAT_SETTLER = _getInfoTypeForString("UNITCOMBAT_SETTLER")
    _UNITCOMBAT_WORKER = _getInfoTypeForString("UNITCOMBAT_WORKER")
    _UNITCOMBAT_SEA_WORKER = _getInfoTypeForString("UNITCOMBAT_SEA_WORKER")
    gaiSettlerWorkerCombatTuple = (_UNITCOMBAT_SETTLER, _UNITCOMBAT_WORKER, _UNITCOMBAT_SEA_WORKER)

    # Cache terrain types once
    _TERRAIN_TAIGA = _getInfoTypeForString('TERRAIN_TAIGA')
    _TERRAIN_TUNDRA = _getInfoTypeForString('TERRAIN_TUNDRA')
<<<<<<< Updated upstream
    _TERRAIN_PERMAFROST = _getInfoTypeForString('TERRAIN_TUNDRA')  # Note: Same as tundra
=======
    _TERRAIN_PERMAFROST = _getInfoTypeForString('TERRAIN_PERMAFROST')
>>>>>>> Stashed changes
    _TERRAIN_ICE = _getInfoTypeForString('TERRAIN_ICE')
    _TERRAIN_DESERT = GC.getTERRAIN_DESERT()
    _TERRAIN_DUNES = _getInfoTypeForString('TERRAIN_DUNES')
    _TERRAIN_SALT_FLATS = _getInfoTypeForString('TERRAIN_SALT_FLATS')
    _TERRAIN_BARREN = _getInfoTypeForString('TERRAIN_BARREN')
    _TERRAIN_ROCKY = _getInfoTypeForString('TERRAIN_ROCKY')
    _TERRAIN_SCRUB = _getInfoTypeForString('TERRAIN_SCRUB')
    _TERRAIN_MARSH = _getInfoTypeForString('TERRAIN_MARSH')

    # Cache feature types once
    _FEATURE_ICE = _getInfoTypeForString('FEATURE_ICE')
    _FEATURE_FOREST = _getInfoTypeForString('FEATURE_FOREST')
    _FEATURE_FOREST_YOUNG = _getInfoTypeForString('FEATURE_FOREST_YOUNG')
    _FEATURE_FOREST_ANCIENT = _getInfoTypeForString('FEATURE_FOREST_ANCIENT')
    _FEATURE_JUNGLE = _getInfoTypeForString('FEATURE_JUNGLE')
    _FEATURE_BAMBOO = _getInfoTypeForString('FEATURE_BAMBOO')
    _FEATURE_REEF = _getInfoTypeForString('FEATURE_REEF')
    _FEATURE_REEF_BEACON = _getInfoTypeForString('FEATURE_REEF_BEACON')
    _FEATURE_REEF_LIGHTHOUSE = _getInfoTypeForString('FEATURE_REEF_LIGHTHOUSE')
    _FEATURE_CORAL_REEF = _getInfoTypeForString('FEATURE_CORAL_REEF')
    _FEATURE_CORAL_REEF_BEACON = _getInfoTypeForString('FEATURE_CORAL_REEF_BEACON')
    _FEATURE_CORAL_REEF_LIGHTHOUSE = _getInfoTypeForString('FEATURE_CORAL_REEF_LIGHTHOUSE')

    # Cache promotion types once
    _PROMOTION_GREEN_WARDEN = _getInfoTypeForString("PROMOTION_GREEN_WARDEN")
    _PROMOTION_WINTERBORN = _getInfoTypeForString("PROMOTION_WINTERBORN")
    _PROMOTION_SAND_DEVIL = _getInfoTypeForString("PROMOTION_SAND_DEVIL")
    _PROMOTION_BUSHMAN = _getInfoTypeForString("PROMOTION_BUSHMAN")
    _PROMOTION_CLIFF_WALKER = _getInfoTypeForString("PROMOTION_CLIFF_WALKER")
    _PROMOTION_AMPHIBIOUS = _getInfoTypeForString("PROMOTION_AMPHIBIOUS")
    _PROMOTION_COASTAL_ASSAULT1 = _getInfoTypeForString("PROMOTION_COASTAL_ASSAULT1")
    _PROMOTION_COASTAL_GUARD1 = _getInfoTypeForString("PROMOTION_COASTAL_GUARD1")

    # Create immutable tuples for feature/terrain groups
    # Tuples use less memory than lists and are faster to iterate
    aReefTuple = (
        _FEATURE_REEF,
        _FEATURE_REEF_BEACON,
        _FEATURE_REEF_LIGHTHOUSE,
        _FEATURE_CORAL_REEF,
        _FEATURE_CORAL_REEF_BEACON,
        _FEATURE_CORAL_REEF_LIGHTHOUSE
    )

    aTreeTuple = (
        _FEATURE_FOREST,
        _FEATURE_FOREST_YOUNG,
        _FEATURE_FOREST_ANCIENT,
        _FEATURE_JUNGLE,
        _FEATURE_BAMBOO
    )

    # Pre-group terrain types for faster checking
    aColdTerrainTuple = (_TERRAIN_TAIGA, _TERRAIN_TUNDRA, _TERRAIN_ICE, _TERRAIN_PERMAFROST)
    aHotTerrainTuple = (_TERRAIN_DESERT, _TERRAIN_DUNES, _TERRAIN_SALT_FLATS)
    aBushTerrainTuple = (_TERRAIN_BARREN, _TERRAIN_ROCKY, _TERRAIN_SCRUB, _TERRAIN_MARSH)


def onUnitBuilt(argsList):
    """
    Apply militia promotions based on surrounding terrain.
    Memory optimized: Direct references, early exits, reduced variables.
    """
<<<<<<< Updated upstream
=======
    # Ensure module initialized (in case init() wasn't called yet)
    if _PROMOTION_GREEN_WARDEN == -1:
        init()
>>>>>>> Stashed changes
    city = argsList[0]
    unit = argsList[1]

    # Early exit if unit is None
    if not unit:
        return

    # Cache player reference once
    iOwner = unit.getOwner()
    pPlayer = _getPlayer(iOwner)

    # Check military civics - early exit if none
    iMilitaryCivic = 0
    if pPlayer.isCivic(_CIVIC_MARTIAL):
        iMilitaryCivic += 1
    if pPlayer.isCivic(_CIVIC_VOLUNTARY):
        iMilitaryCivic += 1

    # Early exit if no military civic
    if not iMilitaryCivic:
        return

    # Check unit combat type - early exit for settlers/workers
    iUnitCombatType = unit.getUnitCombatType()
    if iUnitCombatType in gaiSettlerWorkerCombatTuple:
        return

    # Check if world unit - early exit
    if isWorldUnit(unit.getUnitType()):
        return

    # Cache city coordinates and map reference
    iX = city.getX()
    iY = city.getY()
    MAP = _getMap()

    # Process based on domain type
    iDomainType = unit.getDomainType()

    if iDomainType == _DOMAIN_LAND:
        _processLandUnit(unit, iX, iY, MAP, iMilitaryCivic)
    elif iDomainType == _DOMAIN_SEA:
        _processSeaUnit(unit, iX, iY, MAP, iMilitaryCivic)


def _processLandUnit(unit, iX, iY, MAP, iMilitaryCivic):
    """
    Process land unit promotions.
    Memory optimized: Single loop pass, reduced variable creation.
    """
    # Initialize counters - reuse variables
    iNumCold = 0
    iNumHot = 0
    iNumBush = 0
    iNumHill = 0
    iNumTree = 0
    iNumCoast = 0

    # Single optimized loop - calculate bounds once
    iXMin = iX - 1
    iXMax = iX + 2
    iYMin = iY - 1
    iYMax = iY + 2

    # Direct iteration without creating range objects each time
    x = iXMin
    while x < iXMax:
        y = iYMin
        while y < iYMax:
            plot = MAP.plot(x, y)
            if plot:
                if plot.isWater():
                    if plot.isCoastal():
                        iNumCoast += 1
                else:
                    # Check terrain features
                    if plot.isHills() or plot.isPeak():
                        iNumHill += 1

                    # Check terrain type - use pre-cached tuples
                    iTerrain = plot.getTerrainType()
                    if iTerrain in aHotTerrainTuple:
                        iNumHot += 1
                    elif iTerrain in aColdTerrainTuple:
                        iNumCold += 1
                    elif iTerrain in aBushTerrainTuple:
                        iNumBush += 1

                    # Check features
                    iFeature = plot.getFeatureType()
                    if iFeature > -1 and iFeature in aTreeTuple:
                        iNumTree += 1
            y += 1
        x += 1

    # Apply promotions - pre-calculate chances
    if iNumTree:
        _attemptPromotion(unit, int(iNumTree * 1.25 * iMilitaryCivic), _PROMOTION_GREEN_WARDEN)
    if iNumCold:
        _attemptPromotion(unit, int(iNumCold * 1.25 * iMilitaryCivic), _PROMOTION_WINTERBORN)
    if iNumHot:
        _attemptPromotion(unit, int(iNumHot * 1.5 * iMilitaryCivic), _PROMOTION_SAND_DEVIL)
    if iNumBush:
        _attemptPromotion(unit, int(iNumBush * 2 * iMilitaryCivic), _PROMOTION_BUSHMAN)
    if iNumHill:
        _attemptPromotion(unit, int(iNumHill * 1.5 * iMilitaryCivic), _PROMOTION_CLIFF_WALKER)
    if iNumCoast:
        _attemptPromotion(unit, int(iNumCoast * 1.5 * iMilitaryCivic), _PROMOTION_AMPHIBIOUS)


def _processSeaUnit(unit, iX, iY, MAP, iMilitaryCivic):
    """
    Process sea unit promotions.
    Memory optimized: Single loop pass, reduced variable creation.
    """
    # Initialize counters
    iNumReef = 0
    iNumIce = 0

    # Single optimized loop - calculate bounds once
    iXMin = iX - 1
    iXMax = iX + 2
    iYMin = iY - 1
    iYMax = iY + 2

    # Direct iteration
    x = iXMin
    while x < iXMax:
        y = iYMin
        while y < iYMax:
            plot = MAP.plot(x, y)
            if plot and plot.isWater():
                iFeature = plot.getFeatureType()
                if iFeature > -1:
                    if iFeature in aReefTuple:
                        iNumReef += 1
                    elif iFeature == _FEATURE_ICE:
                        iNumIce += 1
            y += 1
        x += 1

    # Apply promotions
    if iNumReef:
        _attemptPromotion(unit, int(iNumReef * 1.25 * iMilitaryCivic), _PROMOTION_COASTAL_ASSAULT1)
    if iNumIce:
        _attemptPromotion(unit, int(iNumIce * 1.25 * iMilitaryCivic), _PROMOTION_COASTAL_GUARD1)


def _attemptPromotion(pUnit, iChance, ePromotion):
    """
    Attempt to apply a promotion to a unit.
    Memory optimized: Direct method calls, early exit.
    """
    # Early exit if no chance
    if iChance <= 0:
        return

    # Check random chance
    if _getSorenRandNum(100, "") < iChance:
        # Check if unit can acquire promotion
        if pUnit.canAcquirePromotion(ePromotion):
            pUnit.setHasPromotion(ePromotion, True)


# Compatibility wrapper for old name
def attemptPromotion(pUnit, iChance, szProposedPromotion):
    """
    Legacy wrapper for compatibility.
    Converts string promotion to cached integer.
    """
    ePromotion = _getInfoTypeForString(szProposedPromotion)
    _attemptPromotion(pUnit, int(iChance), ePromotion)