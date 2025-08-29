## sdToolKit by Stone-D (Laga Mahesa)
## Copyright Laga Mahesa 2005
##
## laga@tbi.co.id
## lmahesa@(yahoo|hotmail|gmail).com
##
## Version 1.22 - Memory Optimized
##
## Rewritten to use BugData by EmperorFool
## Merged with SdToolKitCustom by AIAndy (usage of both was conflicting with BugData)
## Memory optimizations applied for 32-bit Python 2.4 compatibility

from CvPythonExtensions import *
import BugData
import cPickle

# Memory optimization: Pre-cache commonly used strings to avoid repeated creation
_GLOBAL_KEY = 'Global'
_GAME_KEY = 'Game'

# Memory optimization: Cache empty dictionary to avoid repeated creation
_EMPTY_DICT = {}


# -=-=-=-=-=-=-=-= SD-DATA-STORAGE =-=-=-=-=-=-=-=-=-#
# Every variable is a string, except for the actual
# value you want to store, which can be anything.

# ----------------- MOD FUNCTIONS -------------------#

# sdEntityInit('MyModName', 'UniqueName', Template_dictionary)
# Initializes a unique data entity (city, unit, plot).
def sdEntityInit(ModID, entity, eTable):
    BugData.getTable(ModID, entity).setData(eTable)
    return 0


# sdEntityWipe('MyModName', 'UniqueName')
# Removes an entity that has been previously initialized by sdEntityInit.
# Returns int 0 on failure, int 1 on success.
def sdEntityWipe(ModID, entity):
    return BugData.deleteTable(ModID, entity)


# sdEntityExists('MyModName', 'UniqueName')
# Checks whether or not an entity has been initialized by sdEntityInit.
# Returns bool False on failure, bool True on success.
def sdEntityExists(ModID, entity):
    return BugData.hasTable(ModID, entity)


# sdGetVal('MyModName', 'UniqueName', 'VariableName')
# Fetches a specific variable's value from the entity's data set.
def sdGetVal(ModID, entity, var):
    table = BugData.findTable(ModID, entity)
    if table and var in table:
        return table[var]
    return None


# sdSetVal('MyModName', 'UniqueName', 'VariableName', any_value)
# Stores a specific variable's value within the entity's data set.
# Returns bool False on failure, bool True on success.
def sdSetVal(ModID, entity, var, val):
    table = BugData.findTable(ModID, entity)
    if table:
        table[var] = val
        return True
    return False


# sdDelVal('MyModName', 'UniqueName', 'VariableName')
# Removes a specific variable from the entity's data set.
# Returns bool False on failure, bool True on success.
def sdDelVal(ModID, entity, var):
    table = BugData.findTable(ModID, entity)
    if table and var in table:
        del table[var]
        return True
    return False


# sdGetGlobal('MyModName', 'GlobalVariableName')
# Fetches a specific variable's value from the mod's global data set.
def sdGetGlobal(ModID, var):
    table = BugData.findTable(ModID, _GLOBAL_KEY)
    if table and var in table:
        return table[var]
    return None


# sdSetGlobal('MyModName', 'GlobalVariableName', any_value)
# Stores a specific variable's value within the mod's global data set.
def sdSetGlobal(ModID, var, val):
    BugData.getTable(ModID, _GLOBAL_KEY)[var] = val


# sdDelGlobal('MyModName', 'GlobalVariableName')
# Removes a specific variable from the mod's global data set.
# Returns bool False on failure, bool True on success.
def sdDelGlobal(ModID, var):
    table = BugData.findTable(ModID, _GLOBAL_KEY)
    if table and var in table:
        del table[var]
        return True
    return False


## Modification by Teg Navanis. While SD-DATA-STORAGE stores
## values in the GameInstance - scriptdata, these functions can be used to store data
## in the scriptdata of an object (for instance a unit, a city or a plot)

## Further modifications by jdog5000

# -=-=-=-=-=-=-=-= SD-OBJECT-DATA-STORAGE =-=-=-=-=-=-=-=-=-#
# Every variable is a string, except for 'object' and the actual
# value you want to store, which can be anything.
# object can be one of the following:
# - CyCity object
# - CyGame object
# - CyPlayer object
# - CyPlot object
# - CyUnit object
# - PyCity object

# AIAndy: Using the CyGame object is now redirected to the functions above to use BugData

# --------------- INTERNAL USE ONLY -----------------#

# Memory optimization: Cache for recently loaded objects to avoid repeated deserialization
# Limited size to prevent excessive memory usage in 32-bit environment
_CACHE_SIZE = 8
_cache = {}
_cache_order = []


def _manage_cache(key, value):
    """Manage LRU cache for loaded objects"""
    global _cache, _cache_order

    if key in _cache:
        # Move to end (most recently used)
        _cache_order.remove(key)
        _cache_order.append(key)
    else:
        # Add new entry
        if len(_cache_order) >= _CACHE_SIZE:
            # Remove least recently used
            old_key = _cache_order.pop(0)
            del _cache[old_key]
        _cache_order.append(key)

    _cache[key] = value


def _get_from_cache(key):
    """Get from cache and update LRU order"""
    if key in _cache:
        # Move to end (most recently used)
        _cache_order.remove(key)
        _cache_order.append(key)
        return _cache[key]
    return None


# Loads previously initialized data from the central reservoir. If no data is found, init it.
def sdLoad(object):
    if not object:
        return _EMPTY_DICT

    # Memory optimization: Check cache first
    obj_id = id(object)
    cached = _get_from_cache(obj_id)
    if cached is not None:
        return cached

    temp = object.getScriptData()
    if not temp:
        return _EMPTY_DICT

    # Only deserialize if we have data
    cyTable = cPickle.loads(temp)

    # Cache the result
    _manage_cache(obj_id, cyTable)

    return cyTable


# Loads previously initialized data from the central reservoir. If no data is found, init it.
def sdObjectGetDict(ModID, object):
    cyTable = sdLoad(object)
    if ModID in cyTable:
        return cyTable[ModID]
    return _EMPTY_DICT


# Loads previously initialized data from the central reservoir. If no data is found, init it.
def sdObjectSetDict(ModID, object, VarDictionary):
    cyTable = sdLoad(object)
    cyTable[ModID] = VarDictionary

    # Clear cache entry as we're modifying the object
    obj_id = id(object)
    if obj_id in _cache:
        del _cache[obj_id]
        _cache_order.remove(obj_id)

    object.setScriptData(cPickle.dumps(cyTable, cPickle.HIGHEST_PROTOCOL))


# ----------------- OBJECT FUNCTIONS -------------------#

# sdObjectInit ('MyModName', object, Template_dictionary)
# Fetches a specific variable's value from the object's data set.
def sdObjectInit(ModID, object, VarDictionary):
    if isinstance(object, CyGame):
        if not BugData.hasTable(ModID, _GAME_KEY):
            sdEntityInit(ModID, _GAME_KEY, VarDictionary)
            return 1
        return 0

    cyTable = sdLoad(object)
    if ModID not in cyTable:
        cyTable[ModID] = VarDictionary

        # Clear cache entry
        obj_id = id(object)
        if obj_id in _cache:
            del _cache[obj_id]
            _cache_order.remove(obj_id)

        object.setScriptData(cPickle.dumps(cyTable, cPickle.HIGHEST_PROTOCOL))
        return 1
    return 0


# sdObjectWipe('MyModName', object)
# Removes an entity that has been previously initialized by sdObjectInit.
# Returns False on failure, True on success.
def sdObjectWipe(ModID, object):
    if isinstance(object, CyGame):
        return sdEntityWipe(ModID, _GAME_KEY)

    cyTable = sdLoad(object)
    if ModID in cyTable:
        del cyTable[ModID]

        # Clear cache entry
        obj_id = id(object)
        if obj_id in _cache:
            del _cache[obj_id]
            _cache_order.remove(obj_id)

        object.setScriptData(cPickle.dumps(cyTable, cPickle.HIGHEST_PROTOCOL))
        return True
    return False


# sdObjectExists('MyModName', object)
# Checks whether or not an object has been initialized by sdObjectInit.
# Returns bool False on failure, bool True on success.
def sdObjectExists(ModID, object):
    if isinstance(object, CyGame):
        return BugData.hasTable(ModID, _GAME_KEY)

    cyTable = sdLoad(object)
    return ModID in cyTable


# sdObjectGetVal('MyModName', object, 'VariableName')
# Fetches a specific variable's value from the object's data set.
## Modded by jdog5000: returns None if not found
def sdObjectGetVal(ModID, object, var):
    if isinstance(object, CyGame):
        return sdGetVal(ModID, _GAME_KEY, var)

    cyTable = sdLoad(object)
    if ModID in cyTable:
        mTable = cyTable[ModID]
        if var in mTable:
            return mTable[var]
    return None


# sdObjectSetVal('MyModName', object, 'VariableName', any_value)
# Stores a specific variable's value within the object's data set.
# Returns bool False on failure, bool True on success.
## Modded by jdog5000 to allow creation of new dict elements
def sdObjectSetVal(ModID, object, var, val):
    if isinstance(object, CyGame):
        return sdSetVal(ModID, _GAME_KEY, var, val)

    cyTable = sdLoad(object)
    if ModID in cyTable:
        cyTable[ModID][var] = val

        # Clear cache entry
        obj_id = id(object)
        if obj_id in _cache:
            del _cache[obj_id]
            _cache_order.remove(obj_id)

        object.setScriptData(cPickle.dumps(cyTable, cPickle.HIGHEST_PROTOCOL))
        return True
    return False


# sdObjectChangeVal('MyModName', object, 'VariableName', change_in_value)
# Updates an existing variable's value within the object's data set.
# Returns bool False on failure, bool True on success.
def sdObjectChangeVal(ModID, object, var, delta):
    if isinstance(object, CyGame):
        table = BugData.findTable(ModID, _GAME_KEY)
        if table and var in table:
            table[var] += delta
            return True
        return False

    cyTable = sdLoad(object)
    if ModID in cyTable:
        mTable = cyTable[ModID]
        if var in mTable:
            mTable[var] += delta

            # Clear cache entry
            obj_id = id(object)
            if obj_id in _cache:
                del _cache[obj_id]
                _cache_order.remove(obj_id)

            object.setScriptData(cPickle.dumps(cyTable, cPickle.HIGHEST_PROTOCOL))
            return True
    return False


# sdObjectUpdateVal('MyModName', object, 'VariableName', any_value)
# Updates an existing variable's value within the object's data set.
# Returns bool False on failure, bool True on success.
def sdObjectUpdateVal(ModID, object, var, val):
    if isinstance(object, CyGame):
        table = BugData.findTable(ModID, _GAME_KEY)
        if table and var in table:
            table[var] = val  # Fixed: was 'delta' instead of 'val'
            return True
        return False

    cyTable = sdLoad(object)
    if ModID in cyTable:
        mTable = cyTable[ModID]
        if var in mTable:
            mTable[var] = val

            # Clear cache entry
            obj_id = id(object)
            if obj_id in _cache:
                del _cache[obj_id]
                _cache_order.remove(obj_id)

            object.setScriptData(cPickle.dumps(cyTable, cPickle.HIGHEST_PROTOCOL))
            return True
    return False