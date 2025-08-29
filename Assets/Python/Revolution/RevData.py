# Interface to SdToolKit for Revolution Mod
# Optimized for memory efficiency in 32-bit Python 2.4
# Version 0.3

import CvPythonExtensions
import SdToolKit
import RevDefs

# Cache for type checks to avoid repeated isinstance calls
_TYPE_CACHE = {}

# Pre-compiled error messages to avoid string concatenation
_ERR_NOT_RECOGNIZED = "ERROR: Not recognized: "
_ERR_VAR_NOT_VALID = "Error! Var %s is not a valid cityData variable"
_WARN_UNRECOG_PLAYER = "WARNING: Unrecognized player variable "
_WARN_UNRECOG_CITY = "WARNING: Unrecognized city variable "
_WARN_MISSING_KEY = "Warning! RevIdxHistory missing key "
_MSG_INIT_PLAYER = "RevData: Initializing player object"
_MSG_INIT_CITY = "RevData: Initializing city object"

# Cache CyPlayer and CyCity types for faster lookup
_CyPlayerType = CvPythonExtensions.CyPlayer
_CyCityType = CvPythonExtensions.CyCity

# String constants for frequently used keys
_REVOLUTION = 'Revolution'
_REVIDXHISTORY = 'RevIdxHistory'
_REVOLUTIONINDEX = 'RevolutionIndex'


def revLoad(object):
    """Load previously initialized data for Revolution mod from the central reservoir."""
    cyTable = SdToolKit.sdLoad(object)
    if _REVOLUTION in cyTable:
        return cyTable[_REVOLUTION]
    return {}


# ----------------- OBJECT FUNCTIONS -------------------#

def revObjectInit(object, VarDictionary=None):
    """Initialize objects revolution member to the template dictionary."""
    if VarDictionary is None:
        VarDictionary = {}
    return SdToolKit.sdObjectInit(_REVOLUTION, object, VarDictionary)


def revObjectWipe(object):
    """Remove an entity that has been previously initialized."""
    return SdToolKit.sdObjectWipe(_REVOLUTION, object)


def revObjectExists(object):
    """Check whether an object has been initialized."""
    return SdToolKit.sdObjectExists(_REVOLUTION, object)


def _getObjectType(object):
    """Cache object type checks to avoid repeated isinstance calls."""
    obj_id = id(object)
    if obj_id not in _TYPE_CACHE:
        if isinstance(object, _CyPlayerType):
            _TYPE_CACHE[obj_id] = 1  # Player
        elif isinstance(object, _CyCityType):
            _TYPE_CACHE[obj_id] = 2  # City
        else:
            _TYPE_CACHE[obj_id] = 0  # Unknown
    return _TYPE_CACHE[obj_id]


def _initObjectIfNeeded(object):
    """Initialize object if it doesn't exist, return object type."""
    obj_type = _getObjectType(object)

    if obj_type == 1:  # Player
        print _MSG_INIT_PLAYER
        initPlayer(object)
        return 1
    elif obj_type == 2:  # City
        print _MSG_INIT_CITY
        initCity(object)
        return 2
    else:
        # SDTK will fail
        print _ERR_NOT_RECOGNIZED, object
        return 0


def revObjectGetVal(object, var):
    """Fetch a specific variable's value from the object's data set."""
    if not revObjectExists(object):
        obj_type = _initObjectIfNeeded(object)
        if obj_type == 0:
            return None
    else:
        # Cache type for validation
        obj_type = _getObjectType(object)

    # Validate variable names (only in debug, can be commented out for production)
    if obj_type == 1:  # Player
        if var not in RevDefs._playerDataTemplate:
            print _WARN_UNRECOG_PLAYER, var
    elif obj_type == 2:  # City
        if var not in RevDefs._cityDataTemplate:
            print _WARN_UNRECOG_CITY, var

    return SdToolKit.sdObjectGetVal(_REVOLUTION, object, var)


def revObjectSetVal(object, var, val):
    """Store a specific variable's value within the object's data set."""
    if not revObjectExists(object):
        if _initObjectIfNeeded(object) == 0:
            return False

    return SdToolKit.sdObjectSetVal(_REVOLUTION, object, var, val)


def revObjectChangeVal(object, var, delta):
    """Update an existing variable's value within the object's data set."""
    return SdToolKit.sdObjectChangeVal(_REVOLUTION, object, var, delta)


def revObjectUpdateVal(object, var, val):
    """Update an existing variable's value within the object's data set."""
    return SdToolKit.sdObjectUpdateVal(_REVOLUTION, object, var, val)


# ----------- Initialization functions ------------------

def initCity(pCity):
    """Initialize city data structure efficiently."""
    # Single check instead of double checking
    if revObjectExists(pCity):
        if not revObjectWipe(pCity):
            return False

    if revObjectInit(pCity, RevDefs.getCityDataTemplate()):
        # Direct call to avoid function overhead
        revObjectSetVal(pCity, _REVIDXHISTORY, RevDefs.initRevIdxHistory())
        return True
    return False


def initPlayer(pPlayer):
    """Initialize player data structure efficiently."""
    # Single check instead of double checking
    if revObjectExists(pPlayer):
        if not revObjectWipe(pPlayer):
            return False

    return revObjectInit(pPlayer, RevDefs.getPlayerDataTemplate())


# ----------- Functions for cities ------------------

# Cache for frequently accessed city data keys
_cityDataKeys = None


def _getCityDataKeys():
    """Lazy load and cache city data keys."""
    global _cityDataKeys
    if _cityDataKeys is None:
        _cityDataKeys = RevDefs._cityDataTemplate.keys()
    return _cityDataKeys


def getCityVal(pCity, var):
    """Get city value with optimized validation and initialization."""
    val = revObjectGetVal(pCity, var)

    # Special handling for RevIdxHistory
    if var == _REVIDXHISTORY:
        if val is None:
            # Initialize on demand
            revIdxHist = RevDefs.initRevIdxHistory()
            revObjectSetVal(pCity, _REVIDXHISTORY, revIdxHist)
            return revIdxHist

        # Validate and repair structure if needed
        # Use cached reference to avoid repeated lookups
        keyList = RevDefs.revIdxHistKeyList
        valKeys = val.keys()
        keyListLen = len(keyList)

        if len(valKeys) < keyListLen:
            # Only iterate if we know keys are missing
            for key in keyList:
                if key not in valKeys:
                    print _WARN_MISSING_KEY, key, ", initializing it"
                    val[key] = [0]

    elif val is None and var not in _getCityDataKeys():
        initCity(pCity)
        print _ERR_VAR_NOT_VALID % var
        assert False

    return val


def setCityVal(pCity, var, val):
    """Set city value with single initialization attempt."""
    if revObjectSetVal(pCity, var, val):
        return True

    # Try once after initialization
    initCity(pCity)
    return revObjectSetVal(pCity, var, val)


def updateCityVal(pCity, var, val):
    """Update city value with single initialization attempt."""
    if revObjectUpdateVal(pCity, var, val):
        return True

    # Try once after initialization
    initCity(pCity)
    return revObjectUpdateVal(pCity, var, val)


def changeCityVal(pCity, var, delta):
    """Change city value with validation and single initialization attempt."""
    # Type check only for RevolutionIndex
    if var == _REVOLUTIONINDEX and delta != int(delta):
        assert False

    if revObjectChangeVal(pCity, var, delta):
        return True

    # Try once after initialization
    initCity(pCity)
    return revObjectChangeVal(pCity, var, delta)


# Cleanup function to clear caches when needed (optional, call manually if memory is critical)
def clearCaches():
    """Clear internal caches to free memory if needed."""
    global _TYPE_CACHE, _cityDataKeys
    _TYPE_CACHE.clear()
    _cityDataKeys = None