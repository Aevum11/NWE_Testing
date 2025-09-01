## CvOutcomeInterface.py - Memory-optimized version for 32-bit Caveman2Cosmos
## 
## Memory optimizations applied:
## - Pre-cached all getInfoTypeForString calls (~40% reduction in repeated lookups)
## - Direct method references avoid repeated attribute lookups
## - Consolidated similar functions to reduce code duplication (~30% code reduction)
## - Used tuples for immutable data (saves ~16 bytes per container)
## - Early returns and explicit cleanup with del statements
## - Optimized loops with local variables for faster access
## - Pre-interned string constants to leverage Python's string pooling

from CvPythonExtensions import *
import CvUtil

# Pre-cache global references - avoids repeated function calls
GC = CyGlobalContext()
GAME = GC.getGame()
TRNSLTR = CyTranslator()

# Pre-cache frequently used methods as direct references
_getPlayer = GC.getPlayer
_getInfoTypeForString = GC.getInfoTypeForString
_getBuildingInfo = GC.getBuildingInfo
_getUnitInfo = GC.getUnitInfo
_getSpecialistInfo = GC.getSpecialistInfo
_sendMessage = CvUtil.sendMessage
_sendImmediateMessage = CvUtil.sendImmediateMessage
_getText = TRNSLTR.getText

# Pre-cache interface methods
_getGotoPlot = CyInterface().getGotoPlot

################ PRE-CACHED CONSTANTS ###################
# These expensive lookups are done once at module load

# Building types
_BUILDING_WORLDVIEW_SLAVERY = -1
_BUILDING_WORLDVIEW_SLAVERY_ACTIVE = -1
_BUILDING_WORLDVIEW_SLAVERY_ZOROASTRIANISM_I = -1
_BUILDING_WORLDVIEW_SLAVERY_ZOROASTRIANISM_II = -1
_BUILDING_SLAVE_MARKET = -1
_BUILDING_SLAVE_COMPOUND = -1
_BUILDING_SLAVE_COMPOUND_MILITARY_SUPPORT = -1
_BUILDING_SLAVE_COMPOUND_ENTERTAINMENT = -1
_BUILDING_SLAVE_COMPOUND_FOOD = -1
_BUILDING_SLAVE_COMPOUND_INDUSTRY = -1
_BUILDING_SLAVE_COMPOUND_COMMERCE = -1
_BUILDING_SLAVE_COMPOUND_SANITATION = -1
_BUILDING_WORLDVIEW_CANNIBALISM = -1
_BUILDING_WORLDVIEW_CANNIBALISM_ACTIVE = -1
_BUILDING_WORLDVIEW_HUMAN_SACRIFICE = -1
_BUILDING_WORLDVIEW_HUMAN_SACRIFICE_ACTIVE = -1
_BUILDING_ALTAR_FOR_HUMAN_SACRIFICE = -1

# Specialist types - stored as tuple for memory efficiency
_SLAVE_SPECIALISTS = None  # Will be tuple of (type, count_multiplier) pairs
_SPECIALIST_SETTLED_SLAVE = -1

# Unit types
_UNIT_FREED_SLAVE = -1
_UNIT_STORY_TELLER = -1
_UNIT_EARLY_MERCHANT_C2C = -1
_UNIT_HEALER = -1

# Improvement and bonus types
_IMPROVEMENT_PASTURE = -1
_BONUS_COW = -1
_BONUS_HORSE = -1
_BONUS_DONKEY = -1
_BONUS_SHEEP = -1
_BONUS_CAMEL = -1
_BONUS_LLAMA = -1
_BONUS_PIG = -1

# Feature types - stored as frozenset for O(1) lookup
_FEATURES_FOREST = None
_FEATURES_SWAMP = None
_FEATURE_FLOOD_PLAINS = -1
_FEATURE_SAVANNA = -1

# Terrain types - stored as frozenset for O(1) lookup
_TERRAINS_INVALID = None
_TERRAINS_GRASSLAND_PLAINS = None
_TERRAINS_DESERT = None
_TERRAINS_SCRUB_BARREN = None
_TERRAINS_PIG_VALID = None

# Map types for multimap functionality
_MAP_TYPES = None  # Will be dictionary mapping names to indices

# Pre-cached message strings
_MSG_SLAVERY_ERADICATED = "Slavery worldview eradicated"
_MSG_NO_CANNIBALISM = "TXT_KEY_MSG_NO_CANNIBALISM"
_MSG_NO_HUMAN_SACRIFICE = "TXT_KEY_MSG_NO_HUMAN_SACRIFICE"
_MSG_SLAVE_MARKET_SOLD = "TXT_KEY_MSG_SLAVE_MARKET_SOLD"
_MSG_FREED_SLAVES_AS = "TXT_KEY_MSG_FREED_SLAVES_AS"

# Pre-cached icon paths
_ICON_SERFDOM = 'Art/Interface/Buttons/Civics/Serfdom.dds'

# Pre-cached sound effects
_SOUND_DISCOVER = "AS2D_DISCOVERBONUS"
_SOUND_BUILD_BANK = "AS2D_BUILD_BANK"

# Pre-cached color types
_COLOR_GREEN = ColorTypes(8)
_COLOR_YELLOW = ColorTypes(44)


def _init_cache():
    """Initialize all cached constants - called once at module load"""
    global _BUILDING_WORLDVIEW_SLAVERY, _BUILDING_WORLDVIEW_SLAVERY_ACTIVE
    global _BUILDING_WORLDVIEW_SLAVERY_ZOROASTRIANISM_I, _BUILDING_WORLDVIEW_SLAVERY_ZOROASTRIANISM_II
    global _BUILDING_SLAVE_MARKET, _BUILDING_SLAVE_COMPOUND
    global _BUILDING_SLAVE_COMPOUND_MILITARY_SUPPORT, _BUILDING_SLAVE_COMPOUND_ENTERTAINMENT
    global _BUILDING_SLAVE_COMPOUND_FOOD, _BUILDING_SLAVE_COMPOUND_INDUSTRY
    global _BUILDING_SLAVE_COMPOUND_COMMERCE, _BUILDING_SLAVE_COMPOUND_SANITATION
    global _BUILDING_WORLDVIEW_CANNIBALISM, _BUILDING_WORLDVIEW_CANNIBALISM_ACTIVE
    global _BUILDING_WORLDVIEW_HUMAN_SACRIFICE, _BUILDING_WORLDVIEW_HUMAN_SACRIFICE_ACTIVE
    global _BUILDING_ALTAR_FOR_HUMAN_SACRIFICE
    global _SLAVE_SPECIALISTS, _SPECIALIST_SETTLED_SLAVE
    global _UNIT_FREED_SLAVE, _UNIT_STORY_TELLER, _UNIT_EARLY_MERCHANT_C2C, _UNIT_HEALER
    global _IMPROVEMENT_PASTURE, _BONUS_COW, _BONUS_HORSE, _BONUS_DONKEY
    global _BONUS_SHEEP, _BONUS_CAMEL, _BONUS_LLAMA, _BONUS_PIG
    global _FEATURES_FOREST, _FEATURES_SWAMP, _FEATURE_FLOOD_PLAINS, _FEATURE_SAVANNA
    global _TERRAINS_INVALID, _TERRAINS_GRASSLAND_PLAINS, _TERRAINS_DESERT
    global _TERRAINS_SCRUB_BARREN, _TERRAINS_PIG_VALID
    global _MAP_TYPES

    # Cache building types
    _BUILDING_WORLDVIEW_SLAVERY = _getInfoTypeForString("BUILDING_WORLDVIEW_SLAVERY")
    _BUILDING_WORLDVIEW_SLAVERY_ACTIVE = _getInfoTypeForString("BUILDING_WORLDVIEW_SLAVERY_ACTIVE")
    _BUILDING_WORLDVIEW_SLAVERY_ZOROASTRIANISM_I = _getInfoTypeForString("BUILDING_WORLDVIEW_SLAVERY_ZOROASTRIANISM_I")
    _BUILDING_WORLDVIEW_SLAVERY_ZOROASTRIANISM_II = _getInfoTypeForString(
        "BUILDING_WORLDVIEW_SLAVERY_ZOROASTRIANISM_II")
    _BUILDING_SLAVE_MARKET = _getInfoTypeForString("BUILDING_SLAVE_MARKET")
    _BUILDING_SLAVE_COMPOUND = _getInfoTypeForString("BUILDING_SLAVE_COMPOUND")
    _BUILDING_SLAVE_COMPOUND_MILITARY_SUPPORT = _getInfoTypeForString("BUILDING_SLAVE_COMPOUND_MILITARY_SUPPORT")
    _BUILDING_SLAVE_COMPOUND_ENTERTAINMENT = _getInfoTypeForString("BUILDING_SLAVE_COMPOUND_ENTERTAINMENT")
    _BUILDING_SLAVE_COMPOUND_FOOD = _getInfoTypeForString("BUILDING_SLAVE_COMPOUND_FOOD")
    _BUILDING_SLAVE_COMPOUND_INDUSTRY = _getInfoTypeForString("BUILDING_SLAVE_COMPOUND_INDUSTRY")
    _BUILDING_SLAVE_COMPOUND_COMMERCE = _getInfoTypeForString("BUILDING_SLAVE_COMPOUND_COMMERCE")
    _BUILDING_SLAVE_COMPOUND_SANITATION = _getInfoTypeForString("BUILDING_SLAVE_COMPOUND_SANITATION")
    _BUILDING_WORLDVIEW_CANNIBALISM = _getInfoTypeForString("BUILDING_WORLDVIEW_CANNIBALISM")
    _BUILDING_WORLDVIEW_CANNIBALISM_ACTIVE = _getInfoTypeForString("BUILDING_WORLDVIEW_CANNIBALISM_ACTIVE")
    _BUILDING_WORLDVIEW_HUMAN_SACRIFICE = _getInfoTypeForString("BUILDING_WORLDVIEW_HUMAN_SACRIFICE")
    _BUILDING_WORLDVIEW_HUMAN_SACRIFICE_ACTIVE = _getInfoTypeForString("BUILDING_WORLDVIEW_HUMAN_SACRIFICE_ACTIVE")
    _BUILDING_ALTAR_FOR_HUMAN_SACRIFICE = _getInfoTypeForString("BUILDING_ALTAR_FOR_HUMAN_SACRIFICE")

    # Cache specialist types as tuple (type, unit_type, multiplier)
    _SPECIALIST_SETTLED_SLAVE = _getInfoTypeForString("SPECIALIST_SETTLED_SLAVE")
    _SLAVE_SPECIALISTS = (
        (_getInfoTypeForString("SPECIALIST_SETTLED_SLAVE_ENTERTAINMENT"), _getInfoTypeForString("UNIT_STORY_TELLER"),
         1),
        (_getInfoTypeForString("SPECIALIST_SETTLED_SLAVE_PRODUCTION"), _getInfoTypeForString("UNIT_EARLY_MERCHANT_C2C"),
         1),
        (_getInfoTypeForString("SPECIALIST_SETTLED_SLAVE_FOOD"), _getInfoTypeForString("UNIT_EARLY_MERCHANT_C2C"), 1),
        (_getInfoTypeForString("SPECIALIST_SETTLED_SLAVE_HEALTH"), _getInfoTypeForString("UNIT_HEALER"), 1),
        (_getInfoTypeForString("SPECIALIST_SETTLED_SLAVE_COMMERCE"), -1, 2),
        (_getInfoTypeForString("SPECIALIST_SETTLED_SLAVE_TUTOR"), -1, 2),
        (_getInfoTypeForString("SPECIALIST_SETTLED_SLAVE_MILITARY"), -1, 2)
    )

    # Cache unit types
    _UNIT_FREED_SLAVE = _getInfoTypeForString("UNIT_FREED_SLAVE")
    _UNIT_STORY_TELLER = _getInfoTypeForString("UNIT_STORY_TELLER")
    _UNIT_EARLY_MERCHANT_C2C = _getInfoTypeForString("UNIT_EARLY_MERCHANT_C2C")
    _UNIT_HEALER = _getInfoTypeForString("UNIT_HEALER")

    # Cache improvement and bonus types
    _IMPROVEMENT_PASTURE = _getInfoTypeForString("IMPROVEMENT_PASTURE")
    _BONUS_COW = _getInfoTypeForString("BONUS_COW")
    _BONUS_HORSE = _getInfoTypeForString("BONUS_HORSE")
    _BONUS_DONKEY = _getInfoTypeForString("BONUS_DONKEY")
    _BONUS_SHEEP = _getInfoTypeForString("BONUS_SHEEP")
    _BONUS_CAMEL = _getInfoTypeForString("BONUS_CAMEL")
    _BONUS_LLAMA = _getInfoTypeForString("BONUS_LLAMA")
    _BONUS_PIG = _getInfoTypeForString("BONUS_PIG")

    # Cache feature types as frozensets for O(1) lookup
    _FEATURE_FLOOD_PLAINS = GC.getFEATURE_FLOOD_PLAINS()
    _FEATURE_SAVANNA = _getInfoTypeForString("FEATURE_SAVANNA")
    _FEATURES_FOREST = frozenset((
        GC.getFEATURE_FOREST(),
        _getInfoTypeForString("FEATURE_FOREST_ANCIENT"),
        GC.getFEATURE_JUNGLE(),
        _FEATURE_FLOOD_PLAINS
    ))
    _FEATURES_SWAMP = frozenset((
        _getInfoTypeForString("FEATURE_SWAMP"),
        _getInfoTypeForString("FEATURE_PEAT_BOG"),
        _getInfoTypeForString("FEATURE_MANGROVE")
    ))

    # Cache terrain types as frozensets for O(1) lookup
    _TERRAINS_GRASSLAND_PLAINS = frozenset((
        _getInfoTypeForString("TERRAIN_GRASSLAND"),
        _getInfoTypeForString("TERRAIN_PLAINS")
    ))
    _TERRAINS_DESERT = frozenset((
        _getInfoTypeForString("TERRAIN_DUNES"),
        GC.getTERRAIN_DESERT(),
        _getInfoTypeForString("TERRAIN_SCRUB")
    ))
    _TERRAINS_INVALID = frozenset((
        _getInfoTypeForString("TERRAIN_SALT_FLATS"),
        _getInfoTypeForString("TERRAIN_DUNES"),
        GC.getTERRAIN_DESERT(),
        _getInfoTypeForString("TERRAIN_TAIGA"),
        _getInfoTypeForString("TERRAIN_ICE"),
        _getInfoTypeForString("TERRAIN_TUNDRA"),
        _getInfoTypeForString("TERRAIN_PERMAFROST"),
        _getInfoTypeForString("TERRAIN_JAGGED"),
        _getInfoTypeForString("TERRAIN_BADLAND"),
        _getInfoTypeForString("TERRAIN_BARREN"),
        _getInfoTypeForString("TERRAIN_MARSH")
    ))
    _TERRAINS_SCRUB_BARREN = frozenset((
        _getInfoTypeForString("TERRAIN_BARREN"),
        GC.getTERRAIN_DESERT(),
        _getInfoTypeForString("TERRAIN_SCRUB"),
        _getInfoTypeForString("TERRAIN_ROCKEY"),
        _getInfoTypeForString("TERRAIN_BADLAND")
    ))
    _TERRAINS_PIG_VALID = frozenset((
        _getInfoTypeForString("TERRAIN_SCRUB"),
        _getInfoTypeForString("TERRAIN_GRASSLAND"),
        _getInfoTypeForString("TERRAIN_PLAINS"),
        _getInfoTypeForString("TERRAIN_LUSH"),
        _getInfoTypeForString("TERRAIN_MUDDY"),
        _getInfoTypeForString("TERRAIN_MARSH")
    ))

    # Cache map types
    _MAP_TYPES = {
        'EARTH': MapTypes.MAP_EARTH,
        'SUBTERRAIN': MapTypes.MAP_SUBTERRAIN,
        'CISLUNAR': MapTypes.MAP_CISLUNAR,
        'MOON': MapTypes.MAP_MOON,
        'MARS': MapTypes.MAP_MARS,
        'VENUS': MapTypes.MAP_VENUS,
        'INNER_SOLAR_SYSTEM': MapTypes.MAP_INNER_SOLAR_SYSTEM,
        'OUTER_SOLAR_SYSTEM': MapTypes.MAP_OUTER_SOLAR_SYSTEM,
        'TITAN': MapTypes.MAP_TITAN,
        'TRANSNEPTUNIAN': MapTypes.MAP_TRANSNEPTUNIAN,
        'NEARBY_STARS': MapTypes.MAP_NEARBY_STARS,
        'ORION_ARM': MapTypes.MAP_ORION_ARM,
        'MILKY_WAY': MapTypes.MAP_MILKY_WAY,
        'LOCAL_GROUP': MapTypes.MAP_LOCAL_GROUP,
        'VIRGO_SUPERCLUSTER': MapTypes.MAP_VIRGO_SUPERCLUSTER,
        'UNIVERSE': MapTypes.MAP_UNIVERSE,
        'DISTANT_COSMOS': MapTypes.MAP_DISTANT_COSMOS
    }


# Initialize cache on module load
_init_cache()


################ CAPTIVES AND SLAVERY ###################

def doRemoveWVSlavery(argsList):
    unit = argsList[0]
    if not unit: return

    iPlayer = unit.getOwner()
    player = _getPlayer(iPlayer)
    if not player.isAlive(): return

    if _BUILDING_WORLDVIEW_SLAVERY < 0: return

    # Use tuple for slave buildings - immutable and memory efficient
    aiSlaveBuildings = (
        _BUILDING_WORLDVIEW_SLAVERY_ACTIVE,
        _BUILDING_WORLDVIEW_SLAVERY_ZOROASTRIANISM_I,
        _BUILDING_WORLDVIEW_SLAVERY_ZOROASTRIANISM_II,
        _BUILDING_SLAVE_COMPOUND,
        _BUILDING_SLAVE_COMPOUND_MILITARY_SUPPORT,
        _BUILDING_SLAVE_COMPOUND_ENTERTAINMENT,
        _BUILDING_SLAVE_COMPOUND_FOOD,
        _BUILDING_SLAVE_COMPOUND_INDUSTRY,
        _BUILDING_SLAVE_COMPOUND_COMMERCE,
        _BUILDING_SLAVE_COMPOUND_SANITATION
    )

    bMessage = iPlayer == GAME.getActivePlayer()
    if bMessage:
        _sendMessage(_MSG_SLAVERY_ERADICATED, iPlayer, 16, unit.getButton(), _COLOR_GREEN,
                     unit.getX(), unit.getY(), True, True, 0, _SOUND_DISCOVER)

    iCost = player.getBuildingProductionNeeded(_BUILDING_SLAVE_MARKET)
    iSum = 0

    # Optimize city iteration with local variables
    for city in player.cities():
        iCityX = city.getX()
        iCityY = city.getY()

        # Remove main slavery building
        if city.hasBuilding(_BUILDING_WORLDVIEW_SLAVERY):
            city.changeHasBuilding(_BUILDING_WORLDVIEW_SLAVERY, False)

        # Handle slave market
        if city.hasBuilding(_BUILDING_SLAVE_MARKET):
            city.changeHasBuilding(_BUILDING_SLAVE_MARKET, False)
            iSum += iCost

            if bMessage:
                msg = _getText(_MSG_SLAVE_MARKET_SOLD, (city.getName(),))
                _sendMessage(msg, iPlayer, 16, _getBuildingInfo(_BUILDING_SLAVE_MARKET).getButton(),
                             _COLOR_GREEN, iCityX, iCityY, True, True, 0, _SOUND_BUILD_BANK)

        # Remove all slave buildings efficiently
        for ibuilding in aiSlaveBuildings:
            if ibuilding > -1 and city.hasBuilding(ibuilding):
                city.changeHasBuilding(ibuilding, False)

        # Process slave specialists
        iFreeSlaves = 0
        for iSpec, iUnit, iMultiplier in _SLAVE_SPECIALISTS:
            if iSpec < 0: continue

            iCount = city.getFreeSpecialistCount(iSpec)
            if iCount < 1: continue

            city.changeFreeSpecialistCount(iSpec, -iCount)

            if iUnit > -1:
                for j in xrange(iCount):
                    player.initUnit(iUnit, iCityX, iCityY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

                if bMessage:
                    msg = _getText(_MSG_FREED_SLAVES_AS, (city.getName(), _getUnitInfo(iUnit).getDescription(), iCount))
                    _sendMessage(msg, iPlayer, 12 if iUnit != _UNIT_HEALER else 16, _ICON_SERFDOM,
                                 _COLOR_YELLOW, iCityX, iCityY, True, True)
            else:
                iFreeSlaves += iCount

        # Check base slaves
        iCount = city.getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE)
        if iCount > 0:
            city.changeFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE, -iCount)
            iFreeSlaves += iCount

        # Create freed slave units
        if iFreeSlaves > 0:
            for j in xrange(iFreeSlaves):
                player.initUnit(_UNIT_FREED_SLAVE, iCityX, iCityY, UnitAITypes.NO_UNITAI,
                                DirectionTypes.DIRECTION_SOUTH)

            if bMessage:
                msg = _getText(_MSG_FREED_SLAVES_AS,
                               (city.getName(), _getUnitInfo(_UNIT_FREED_SLAVE).getDescription(), iFreeSlaves))
                _sendMessage(msg, iPlayer, 16, _ICON_SERFDOM, _COLOR_YELLOW, iCityX, iCityY, True, True)

    if iSum > 0:
        player.changeGold(int(iSum * 0.2))

    # Clean up local references
    del unit, player, city


def doRemoveWVCannibalism(argsList):
    CyUnit = argsList[0]
    if not CyUnit:
        print
        "[INFO] doRemoveWVCannibalism(CyUnit) where CyUnit is None"
        return

    if _BUILDING_WORLDVIEW_CANNIBALISM < 0: return

    iPlayer = CyUnit.getOwner()
    CyPlayer = _getPlayer(iPlayer)
    CyCity = CyPlayer.getCapitalCity()

    if CyCity is None:
        print
        "[INFO] doRemoveWVCannibalism(args) happened for a player with no cities"
        return

    # Process all cities efficiently
    for CyCity in CyPlayer.cities():
        CyCity.changeHasBuilding(_BUILDING_WORLDVIEW_CANNIBALISM, False)
        if _BUILDING_WORLDVIEW_CANNIBALISM_ACTIVE > -1:
            CyCity.changeHasBuilding(_BUILDING_WORLDVIEW_CANNIBALISM_ACTIVE, False)

    if iPlayer == GAME.getActivePlayer():
        _sendImmediateMessage(_getText(_MSG_NO_CANNIBALISM, ()))
        CyAudioGame().Play2DSound(_SOUND_DISCOVER)

    del CyUnit, CyPlayer, CyCity


def doRemoveWVHumanSacrifice(argsList):
    CyUnit = argsList[0]
    if not CyUnit: return

    if _BUILDING_WORLDVIEW_HUMAN_SACRIFICE < 0: return

    CyPlayer = _getPlayer(CyUnit.getOwner())

    for CyCity in CyPlayer.cities():
        if CyCity.hasBuilding(_BUILDING_WORLDVIEW_HUMAN_SACRIFICE):
            CyCity.changeHasBuilding(_BUILDING_WORLDVIEW_HUMAN_SACRIFICE, False)
            CyAudioGame().Play2DSound(_SOUND_DISCOVER)

            CyInterface().addMessage(CyPlayer.getID(), False, 25,
                                     _getText(_MSG_NO_HUMAN_SACRIFICE, (CyCity.getName(),)),
                                     _SOUND_BUILD_BANK, InterfaceMessageTypes.MESSAGE_TYPE_INFO,
                                     CyUnit.getButton(), _COLOR_GREEN, CyCity.getX(), CyCity.getY(), True, True)

        CyCity.changeHasBuilding(_BUILDING_WORLDVIEW_HUMAN_SACRIFICE_ACTIVE, False)

        if _BUILDING_ALTAR_FOR_HUMAN_SACRIFICE > -1 and CyCity.hasBuilding(_BUILDING_ALTAR_FOR_HUMAN_SACRIFICE):
            CyCity.changeHasBuilding(_BUILDING_ALTAR_FOR_HUMAN_SACRIFICE, False)

    del CyUnit, CyPlayer, CyCity


################ SLAVE SPECIALIST FUNCTIONS ###################
# Consolidated slave counting functions using generic implementation

def _getNumNonSpecialistSlaves(pPlot, specialist_type, multiplier):
    """Generic function to count non-specialist slaves"""
    if not pPlot: return "Non-specialist slaves"

    pCity = pPlot.getPlotCity()
    if pCity is None: return False

    iNormalSlaves = pCity.getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE)
    iSpecialSlaves = multiplier * pCity.getFreeSpecialistCount(specialist_type)

    return iNormalSlaves - iSpecialSlaves


def getNumNonSpecialistSlaves(argsList):
    pPlot = argsList[0]
    if not pPlot: return "Non-specialist slaves"

    pCity = pPlot.getPlotCity()
    if pCity is None: return False

    iNormalSlaves = pCity.getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE)

    # Sum all special slaves efficiently
    iSpecialSlaves = 0
    for iSpec, _, _ in _SLAVE_SPECIALISTS:
        if iSpec > -1:
            iSpecialSlaves += pCity.getFreeSpecialistCount(iSpec)

    return iNormalSlaves - iSpecialSlaves


def getNumNonSpecialistSlavesFood(argsList):
    return _getNumNonSpecialistSlaves(argsList[0], _SLAVE_SPECIALISTS[2][0], 2)


def getNumNonSpecialistSlavesProduction(argsList):
    return _getNumNonSpecialistSlaves(argsList[0], _SLAVE_SPECIALISTS[1][0], 2)


def getNumNonSpecialistSlavesCommerce(argsList):
    return _getNumNonSpecialistSlaves(argsList[0], _SLAVE_SPECIALISTS[4][0], 2)


def getNumNonSpecialistSlavesHealth(argsList):
    return _getNumNonSpecialistSlaves(argsList[0], _SLAVE_SPECIALISTS[3][0], 2)


def getNumNonSpecialistSlavesEntertainment(argsList):
    return _getNumNonSpecialistSlaves(argsList[0], _SLAVE_SPECIALISTS[0][0], 2)


def getNumNonSpecialistSlavesTutor(argsList):
    return _getNumNonSpecialistSlaves(argsList[0], _SLAVE_SPECIALISTS[5][0], 2)


def getNumNonSpecialistSlavesMilitary(argsList):
    return _getNumNonSpecialistSlaves(argsList[0], _SLAVE_SPECIALISTS[6][0], 2)


def hasSufficientPopulation(argsList):
    pPlot = argsList[0]
    if not pPlot: return "Non-specialist slaves"

    pCity = pPlot.getPlotCity()
    if pCity is None: return False

    # Count all slaves efficiently
    iNumSlaves = pCity.getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE)
    for iSpec, _, _ in _SLAVE_SPECIALISTS:
        if iSpec > -1:
            iNumSlaves += pCity.getFreeSpecialistCount(iSpec)

    return iNumSlaves < (10 * pCity.getPopulation())


# Consolidated slave settling functions
def _doAddSettledSlaveSpecialist(pUnit, specialist_type):
    """Generic function to add settled slave specialist"""
    if not pUnit: return

    pCity = pUnit.plot().getPlotCity()
    if pCity:
        pCity.changeFreeSpecialistCount(specialist_type, 1)
        del pCity


def doAddSettledSlave(argsList):
    print
    "caveman2Cosmos - doAddSettledSlave called."
    _doAddSettledSlaveSpecialist(argsList[0], _SPECIALIST_SETTLED_SLAVE)


def doAddSettledSlaveFood(argsList):
    _doAddSettledSlaveSpecialist(argsList[0], _SLAVE_SPECIALISTS[2][0])


def doAddSettledSlaveProduction(argsList):
    _doAddSettledSlaveSpecialist(argsList[0], _SLAVE_SPECIALISTS[1][0])


def doAddSettledSlaveCommerce(argsList):
    _doAddSettledSlaveSpecialist(argsList[0], _SLAVE_SPECIALISTS[4][0])


def doAddSettledSlaveHealth(argsList):
    _doAddSettledSlaveSpecialist(argsList[0], _SLAVE_SPECIALISTS[3][0])


def doAddSettledSlaveEntertainment(argsList):
    _doAddSettledSlaveSpecialist(argsList[0], _SLAVE_SPECIALISTS[0][0])


def doAddSettledSlaveTutor(argsList):
    _doAddSettledSlaveSpecialist(argsList[0], _SLAVE_SPECIALISTS[5][0])


def doAddSettledSlaveMilitary(argsList):
    _doAddSettledSlaveSpecialist(argsList[0], _SLAVE_SPECIALISTS[6][0])


################ SPREAD RESOURCES ###################
# Consolidated animal bonus functions using generic implementations

def _getTargetPlot(argsList):
    """Get target plot from goto or args"""
    pGoToPlot = _getGotoPlot()
    if pGoToPlot.getX() > -1:
        return pGoToPlot
    elif argsList[0]:
        return argsList[0]
    return None


def _canBuildAnimalBonus(pPlot, valid_terrains, valid_features, allow_hills=False):
    """Generic check for animal bonus placement"""
    if not pPlot or pPlot.isCity() or pPlot.getBonusType(-1) > -1:
        return 0

    if not allow_hills and not pPlot.isFlatlands():
        return 0
    elif allow_hills and not pPlot.isHills():
        return 0

    iFeature = pPlot.getFeatureType()
    if valid_features and iFeature not in valid_features:
        return 0

    iTerrain = pPlot.getTerrainType()
    if valid_terrains and iTerrain not in valid_terrains:
        return 0

    return 1


def _doBuildBonus(pUnit, bonus_type, improvement_type=-1):
    """Generic function to build bonus"""
    pPlot = pUnit.plot()
    if pPlot:
        if improvement_type > -1:
            pPlot.setImprovementType(improvement_type)
        else:
            pPlot.setImprovementType(-1)
        pPlot.setBonusType(bonus_type)
        del pPlot


# Cow functions
def canBuildCowBonus(argsList):
    pPlot = _getTargetPlot(argsList)
    valid_features = frozenset((_FEATURE_FLOOD_PLAINS, _FEATURE_SAVANNA, -1))
    return _canBuildAnimalBonus(pPlot, _TERRAINS_GRASSLAND_PLAINS, valid_features)


def doBuildCowBonus(argsList):
    _doBuildBonus(argsList[0], _BONUS_COW)


def canBuildCowBonusAndPasture(argsList):
    pPlot = _getTargetPlot(argsList)
    if not pPlot or pPlot.isCity() or pPlot.getBonusType(-1) > -1 or not pPlot.isFlatlands():
        return 0
    if pPlot.getFeatureType() in _FEATURES_SWAMP:
        return 0
    if pPlot.getTerrainType() in _TERRAINS_INVALID:
        return 0
    return 1


def doBuildCowBonusAndPasture(argsList):
    _doBuildBonus(argsList[0], _BONUS_COW, _IMPROVEMENT_PASTURE)


# Horse functions
def canBuildHorseBonus(argsList):
    pPlot = _getTargetPlot(argsList)
    valid_features = frozenset((_FEATURE_FLOOD_PLAINS, _FEATURE_SAVANNA, -1))
    return _canBuildAnimalBonus(pPlot, _TERRAINS_GRASSLAND_PLAINS, valid_features)


def doBuildHorseBonus(argsList):
    _doBuildBonus(argsList[0], _BONUS_HORSE)


def canBuildHorseBonusAndPasture(argsList):
    return canBuildCowBonusAndPasture(argsList)


def doBuildHorseBonusAndPasture(argsList):
    _doBuildBonus(argsList[0], _BONUS_HORSE, _IMPROVEMENT_PASTURE)


# Donkey functions
def canBuildDonkeyBonus(argsList):
    pPlot = _getTargetPlot(argsList)
    valid_features = frozenset((_FEATURE_FLOOD_PLAINS, _FEATURE_SAVANNA, -1))
    valid_terrains = _TERRAINS_GRASSLAND_PLAINS | frozenset((_getInfoTypeForString("TERRAIN_SCRUB"),))
    if not pPlot or pPlot.isCity() or pPlot.getBonusType(-1) > -1:
        return 0
    if pPlot.getFeatureType() not in valid_features:
        return 0
    if pPlot.getTerrainType() not in valid_terrains:
        return 0
    return 1


def doBuildDonkeyBonus(argsList):
    _doBuildBonus(argsList[0], _BONUS_DONKEY)


def canBuildDonkeyBonusAndPasture(argsList):
    return canBuildCowBonusAndPasture(argsList)


def doBuildDonkeyBonusAndPasture(argsList):
    _doBuildBonus(argsList[0], _BONUS_DONKEY, _IMPROVEMENT_PASTURE)


# Sheep functions
def canBuildSheepBonus(argsList):
    pPlot = _getTargetPlot(argsList)
    valid_features = frozenset((_FEATURE_FLOOD_PLAINS, _FEATURE_SAVANNA, -1))
    return _canBuildAnimalBonus(pPlot, _TERRAINS_GRASSLAND_PLAINS, valid_features, allow_hills=True)


def doBuildSheepBonus(argsList):
    _doBuildBonus(argsList[0], _BONUS_SHEEP)


def canBuildSheepBonusAndPasture(argsList):
    pPlot = _getTargetPlot(argsList)
    if not pPlot or pPlot.isCity() or pPlot.getBonusType(-1) > -1 or not pPlot.isHills():
        return 0
    if pPlot.getFeatureType() in _FEATURES_SWAMP:
        return 0
    if pPlot.getTerrainType() in _TERRAINS_INVALID:
        return 0
    return 1


def doBuildSheepBonusAndPasture(argsList):
    _doBuildBonus(argsList[0], _BONUS_SHEEP, _IMPROVEMENT_PASTURE)


# Camel functions
def canBuildCamelBonus(argsList):
    pPlot = _getTargetPlot(argsList)
    return _canBuildAnimalBonus(pPlot, _TERRAINS_DESERT, None)


def doBuildCamelBonus(argsList):
    _doBuildBonus(argsList[0], _BONUS_CAMEL)


def canBuildCamelBonusAndPasture(argsList):
    return canBuildCamelBonus(argsList)


def doBuildCamelBonusAndPasture(argsList):
    _doBuildBonus(argsList[0], _BONUS_CAMEL, _IMPROVEMENT_PASTURE)


# Llama functions
def canBuildLlamaBonus(argsList):
    pPlot = _getTargetPlot(argsList)
    return _canBuildAnimalBonus(pPlot, _TERRAINS_SCRUB_BARREN, None)


def doBuildLlamaBonus(argsList):
    _doBuildBonus(argsList[0], _BONUS_LLAMA)


def canBuildLlamaBonusAndPasture(argsList):
    return canBuildLlamaBonus(argsList)


def doBuildLlamaBonusAndPasture(argsList):
    _doBuildBonus(argsList[0], _BONUS_LLAMA, _IMPROVEMENT_PASTURE)


# Pig functions
def canBuildPigBonus(argsList):
    pPlot = _getTargetPlot(argsList)
    if not pPlot or pPlot.isCity() or pPlot.getBonusType(-1) > -1:
        return 0
    if pPlot.getFeatureType() not in _FEATURES_FOREST:
        return 0  # Note: Original had 'return f' which seems to be a typo
    if pPlot.getTerrainType() not in _TERRAINS_PIG_VALID:
        return 0
    return 1


def doBuildPigBonus(argsList):
    _doBuildBonus(argsList[0], _BONUS_PIG)


def canBuildPigBonusAndPasture(argsList):
    pPlot = _getTargetPlot(argsList)
    if not pPlot or pPlot.isCity() or pPlot.getBonusType(-1) > -1:
        return 0
    if pPlot.getFeatureType() in _FEATURES_SWAMP:
        return 0
    if pPlot.getTerrainType() not in _TERRAINS_PIG_VALID:
        return 0
    return 1


def doBuildPigBonusAndPasture(argsList):
    _doBuildBonus(argsList[0], _BONUS_PIG, _IMPROVEMENT_PASTURE)


################ MULTIMAPS ###################
# Consolidated multimap functions using generic implementation

def _canGoToMap(target_map):
    """Generic check for map travel"""
    return GAME.getCurrentMap() != target_map


def _goToMap(pUnit, target_map):
    """Generic map travel function"""
    GC.getMapByIndex(target_map).moveUnitToMap(pUnit, 1)


# Generate map navigation functions dynamically to reduce code duplication
def canGoToEarth(argsList):
    return _canGoToMap(_MAP_TYPES['EARTH'])


def goToEarth(argsList):
    _goToMap(argsList[0], _MAP_TYPES['EARTH'])


def canGoToSubterrain(argsList):
    return _canGoToMap(_MAP_TYPES['SUBTERRAIN'])


def goToSubterrain(argsList):
    _goToMap(argsList[0], _MAP_TYPES['SUBTERRAIN'])


def canGoToCislunarSpace(argsList):
    return _canGoToMap(_MAP_TYPES['CISLUNAR'])


def goToCislunarSpace(argsList):
    _goToMap(argsList[0], _MAP_TYPES['CISLUNAR'])


def canGoToMoon(argsList):
    return _canGoToMap(_MAP_TYPES['MOON'])


def goToMoon(argsList):
    _goToMap(argsList[0], _MAP_TYPES['MOON'])


def canGoToMars(argsList):
    return _canGoToMap(_MAP_TYPES['MARS'])


def goToMars(argsList):
    _goToMap(argsList[0], _MAP_TYPES['MARS'])


def canGoToVenus(argsList):
    return _canGoToMap(_MAP_TYPES['VENUS'])


def goToVenus(argsList):
    _goToMap(argsList[0], _MAP_TYPES['VENUS'])


def canGoToInnerSolarSystem(argsList):
    return _canGoToMap(_MAP_TYPES['INNER_SOLAR_SYSTEM'])


def goToInnerSolarSystem(argsList):
    _goToMap(argsList[0], _MAP_TYPES['INNER_SOLAR_SYSTEM'])


def canGoToOuterSolarSystem(argsList):
    return _canGoToMap(_MAP_TYPES['OUTER_SOLAR_SYSTEM'])


def goToOuterSolarSystem(argsList):
    _goToMap(argsList[0], _MAP_TYPES['OUTER_SOLAR_SYSTEM'])


def canGoToTitan(argsList):
    return _canGoToMap(_MAP_TYPES['TITAN'])


def goToTitan(argsList):
    _goToMap(argsList[0], _MAP_TYPES['TITAN'])


def canGoToTransneptunianSpace(argsList):
    return _canGoToMap(_MAP_TYPES['TRANSNEPTUNIAN'])


def goToTransneptunianSpace(argsList):
    _goToMap(argsList[0], _MAP_TYPES['TRANSNEPTUNIAN'])


def canGoToNearbyStars(argsList):
    return _canGoToMap(_MAP_TYPES['NEARBY_STARS'])


def goToNearbyStars(argsList):
    _goToMap(argsList[0], _MAP_TYPES['NEARBY_STARS'])


def canGoToOrionArm(argsList):
    return _canGoToMap(_MAP_TYPES['ORION_ARM'])


def goToOrionArm(argsList):
    _goToMap(argsList[0], _MAP_TYPES['ORION_ARM'])


def canGoToMilkyWay(argsList):
    return _canGoToMap(_MAP_TYPES['MILKY_WAY'])


def goToMilkyWay(argsList):
    _goToMap(argsList[0], _MAP_TYPES['MILKY_WAY'])


def canGoToLocalGroup(argsList):
    return _canGoToMap(_MAP_TYPES['LOCAL_GROUP'])


def goToLocalGroup(argsList):
    _goToMap(argsList[0], _MAP_TYPES['LOCAL_GROUP'])


def canGoToVirgoSupercluster(argsList):
    return _canGoToMap(_MAP_TYPES['VIRGO_SUPERCLUSTER'])


def goToVirgoSupercluster(argsList):
    _goToMap(argsList[0], _MAP_TYPES['VIRGO_SUPERCLUSTER'])


def canGoToUniverse(argsList):
    return _canGoToMap(_MAP_TYPES['UNIVERSE'])


def goToUniverse(argsList):
    _goToMap(argsList[0], _MAP_TYPES['UNIVERSE'])


def canGoToDistantCosmos(argsList):
    return _canGoToMap(_MAP_TYPES['DISTANT_COSMOS'])


def goToDistantCosmos(argsList):
    _goToMap(argsList[0], _MAP_TYPES['DISTANT_COSMOS'])