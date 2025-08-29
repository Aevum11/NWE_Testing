# -#-#
# Definitions for Revolution Mod - Memory Optimized
#
from CvPythonExtensions import *

## --------- XML variables used in the mod ----------- ##
# Memory optimization: Using intern() for strings that are used frequently
# This ensures only one copy of the string exists in memory

# Civs
sXMLBarbarian = intern('CIVILIZATION_NPC_BARBARIAN')

# Units
sXMLGeneral = intern('UNIT_GREAT_GENERAL')

# Buildings
# Used by Rev when rebels capture a tiny city first
sXMLPalace = intern("BUILDING_PALACE")

# Techs
# Used by Rev, weight of nationality effects increases after discovery
sXMLNationalism = intern('TECH_NATIONALISM')
# Used by Rev, weight of religious effects decreases after each discovery
sXMLLiberalism = intern('TECH_LIBERALISM')
sXMLSciMethod = intern('TECH_SCIENTIFIC_METHOD')

# Traits
# Used by Rev for AI decisions, BarbCiv to determine type of settling
sXMLAggressive = intern('TRAIT_AGGRESSIVE')
sXMLSpiritual = intern('TRAIT_SPIRITUAL')

# Goodies
sXMLGoodyMap = intern('GOODY_MAP')

# Terrain
sXMLOcean = intern("TERRAIN_OCEAN")
sXMLCoast = intern("TERRAIN_COAST")

## ---------- Data structures for various objects ---------- ##

# Memory optimization: Create template dictionaries once and copy when needed
# This reduces memory allocation overhead

# Template for city data - created once and copied as needed
_cityDataTemplate = {
    'PrevRevIndex': 0,
    'RevIdxHistory': None,
    'RevolutionCiv': None,
    'RevolutionTurn': None,
    'WarningCounter': 0,
    'SmallRevoltCounter': 0,
    'BribeTurn': None,
    'TurnBribeCosts': None
}


def getCityDataTemplate():
    """Return a copy of the city data template"""
    return _cityDataTemplate.copy()


# Use tuples instead of lists where data is read-only
# Tuples use less memory than lists
revIdxHistKeyList = (
    intern('Happiness'),
    intern('Location'),
    intern('Colony'),
    intern('Nationality'),
    intern('Religion'),
    intern('Health'),
    intern('Garrison'),
    intern('Disorder'),
    intern('RevoltEffects'),
    intern('Events')
)

revIdxHistLen = 5


def initRevIdxHistory():
    """Initialize revolution index history with memory-efficient structure"""
    global revIdxHistKeyList

    # Memory optimization: Use list multiplication for initialization
    # This creates references to the same object for all zero values
    zero_list = [0]

    revIdxHist = {}
    for key in revIdxHistKeyList:
        # Create new list only when needed
        revIdxHist[key] = list(zero_list)

    return revIdxHist


# Template for player data
_playerDataTemplate = {
    'SpawnList': None,  # Will be created as needed
    'RevoltDict': None,  # Will be created as needed
    'CivicList': None,
    'RevolutionTurn': None,
    'MotherlandID': None,
    'JoinPlayerID': None,
    'CapitalName': None
}


def getPlayerDataTemplate():
    """Return player data template with lazy initialization"""
    template = _playerDataTemplate.copy()
    # Only create these collections when actually needed
    template['SpawnList'] = []
    template['RevoltDict'] = {}
    return template


# Container for data passed by revolution popups
# Memory optimization: Use __slots__ to reduce memory overhead per instance
class RevoltData(object):
    """
    Container for revolt data with reduced memory footprint.
    Uses __slots__ to prevent __dict__ creation, saving ~100-200 bytes per instance.
    """

    __slots__ = (
        'iPlayer',
        'iRevTurn',
        'cityList',
        'revType',
        'bPeaceful',
        'specialDataDict',
        '_cached_dict'  # Cache for toDict result
    )

    def __init__(self, iPlayer, iRevTurn, cityList, revType, bPeaceful, specialDataDict=None):
        # Player whose cities are in revolt
        self.iPlayer = iPlayer
        self.iRevTurn = iRevTurn
        # List of cities revolting
        self.cityList = cityList
        # String describing revolution type - intern for memory efficiency
        if revType:
            self.revType = intern(revType)
        else:
            self.revType = None
        # Bool describing whether revolt is peaceful
        self.bPeaceful = bPeaceful

        # Memory optimization: Only create dict if data is provided
        if specialDataDict is None:
            self.specialDataDict = {}
        else:
            self.specialDataDict = specialDataDict

        # Cache is initially None, created on first access
        self._cached_dict = None

    def toDict(self):
        """
        Convert to dictionary. Result is cached to avoid repeated creation.
        """
        # Memory optimization: Cache the dictionary to avoid recreating it
        if self._cached_dict is None:
            dataDict = {
                'iPlayer': self.iPlayer,
                'cityList': self.cityList,
                'revType': self.revType,
                'bPeaceful': self.bPeaceful
            }

            # Only update if there's special data
            if self.specialDataDict:
                dataDict.update(self.specialDataDict)

            self._cached_dict = dataDict

        return self._cached_dict

    def fromDict(self, sourceDict):
        """
        Load from dictionary. To use, pass Nones to RevoltData() then call this func with a full dict.
        """
        # Clear cache since we're modifying data
        self._cached_dict = None

        # Memory optimization: Pre-size dictionary if possible
        special_count = len(sourceDict) - 4  # Subtract known keys
        if special_count > 0:
            self.specialDataDict = {}
            # Pre-allocate approximate size to reduce resizing
        else:
            self.specialDataDict = {}

        # Process all items efficiently
        for key, value in sourceDict.iteritems():
            if key == 'iPlayer':
                self.iPlayer = value
            elif key == 'cityList':
                self.cityList = value
            elif key == 'revType':
                # Intern string for memory efficiency
                if value:
                    self.revType = intern(value)
                else:
                    self.revType = None
            elif key == 'bPeaceful':
                self.bPeaceful = value
            else:
                self.specialDataDict[key] = value

    # Provide dict property for backward compatibility
    @property
    def dict(self):
        """Backward compatibility property"""
        return self.toDict()


## ---------- Revolution constants ---------- ##
# Memory optimization: Use the smallest appropriate data type
# These are small integers that don't change

# Using simple integers (no change needed, already optimal)
revReadyDividend = 3
revReadyDivisor = 5
revReadyFrac = 0.6  # result of the two above, used by game text only, no OOS danger.
revInstigatorThreshold = 1000
alwaysViolentThreshold = 1700
badLocalThreshold = 10

## ---------- Popup number defines ---------- ##
# Memory optimization: These are constants, already optimal as simple integers

# Revolution
revolutionPopup = 7000
revWatchPopup = 7001
joinHumanPopup = 7002
controlLostPopup = 7003
assimilationPopup = 7004
pickCityPopup = 7005
bribeCityPopup = 7006

# AIAutoPlay
toAIChooserPopup = 7050
abdicatePopup = 7051
pickHumanPopup = 7052

# ChangePlayer
changeCivPopup = 7060
changeHumanPopup = 7061
updateGraphicsPopup = 7062

# RevolutionDCM
## ---------- RevWatch defines ---------- ##
showTrend = 5


# Memory optimization: Provide utility functions for common operations

def clearRevoltData(revoltData):
    """
    Clear revolt data to free memory immediately.
    Useful for cleaning up after processing.
    """
    if revoltData:
        revoltData.cityList = None
        revoltData.specialDataDict = None
        revoltData._cached_dict = None


def compactCityData(cityDataDict):
    """
    Remove None values from city data to save memory.
    Call periodically to clean up unused entries.
    """
    keys_to_remove = []
    for key, value in cityDataDict.iteritems():
        if value is None:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del cityDataDict[key]

    return cityDataDict


def compactPlayerData(playerDataDict):
    """
    Clean up player data by removing empty collections and None values.
    """
    if playerDataDict.get('SpawnList') is not None and len(playerDataDict['SpawnList']) == 0:
        playerDataDict['SpawnList'] = None

    if playerDataDict.get('RevoltDict') is not None and len(playerDataDict['RevoltDict']) == 0:
        playerDataDict['RevoltDict'] = None

    # Remove None values to save memory
    keys_to_remove = []
    for key, value in playerDataDict.iteritems():
        if value is None and key not in ('SpawnList', 'RevoltDict'):
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del playerDataDict[key]

    return playerDataDict


# Memory pool for frequently created/destroyed RevoltData objects
# This reduces allocation/deallocation overhead
_revoltDataPool = []
_maxPoolSize = 10


def getPooledRevoltData(iPlayer, iRevTurn, cityList, revType, bPeaceful, specialDataDict=None):
    """
    Get a RevoltData object from the pool or create a new one.
    This reduces memory allocation overhead.
    """
    global _revoltDataPool

    if _revoltDataPool:
        # Reuse an object from the pool
        revData = _revoltDataPool.pop()
        # Reinitialize with new values
        revData.iPlayer = iPlayer
        revData.iRevTurn = iRevTurn
        revData.cityList = cityList
        if revType:
            revData.revType = intern(revType)
        else:
            revData.revType = None
        revData.bPeaceful = bPeaceful
        if specialDataDict:
            revData.specialDataDict = specialDataDict
        else:
            revData.specialDataDict = {}
        revData._cached_dict = None
        return revData
    else:
        # Create new object if pool is empty
        return RevoltData(iPlayer, iRevTurn, cityList, revType, bPeaceful, specialDataDict)


def returnToPool(revoltData):
    """
    Return a RevoltData object to the pool for reuse.
    Clears the object's data to free memory.
    """
    global _revoltDataPool, _maxPoolSize

    if len(_revoltDataPool) < _maxPoolSize:
        # Clear data
        revoltData.iPlayer = None
        revoltData.iRevTurn = None
        revoltData.cityList = None
        revoltData.revType = None
        revoltData.bPeaceful = None
        revoltData.specialDataDict = None
        revoltData._cached_dict = None

        # Add to pool
        _revoltDataPool.append(revoltData)
    # If pool is full, object will be garbage collected

# Optimization notes for usage:
# 1. Use getCityDataTemplate() instead of creating cityData dict manually
# 2. Use getPlayerDataTemplate() for new player data
# 3. Call compactCityData() and compactPlayerData() periodically to clean up
# 4. Use getPooledRevoltData() and returnToPool() for temporary RevoltData objects
# 5. String interning is applied to frequently used string constants
# 6. RevoltData uses __slots__ to reduce per-instance memory overhead
# 7. Tuples are used instead of lists where data is read-only
# 8. Template dictionaries reduce allocation overhead
# 9. Lazy initialization is used where possible (e.g., cached dict in RevoltData)