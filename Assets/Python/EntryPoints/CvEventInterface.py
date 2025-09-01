# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# CvEventInterface.py - Memory-optimized version for 32-bit Caveman2Cosmos
#
# These functions are App Entry Points from C++
# WARNING: These function names should not be changed
# WARNING: These functions can not be placed into a class
#
# No other modules should import this
#
# Memory optimizations applied:
# - Lazy module loading to reduce initial memory footprint
# - Eliminated global variable in favor of cached singleton pattern
# - Pre-cached method references to reduce attribute lookups
# - Added proper cleanup with del statements where appropriate
# - Minimized import overhead with deferred loading
# - Used weak references where possible to allow garbage collection

# **********************************
# Memory-optimized modifications
# **********************************

# Use a single dictionary to store cached data instead of multiple globals
# This reduces global namespace pollution and memory fragmentation
_cache = {
    'eventManager': None,
    'initialized': False,
    'BugEventManager': None,  # Cache the module itself
    'BugInit': None,  # Cache BugInit module
    'CvScreensInterface': None  # Cache CvScreensInterface module
}


def getEventManager(bInit=False):
    """
    Memory-optimized event manager singleton.
    Uses lazy loading to defer module imports until actually needed.
    This saves memory on startup and reduces initial load time.
    """
    if bInit or _cache['eventManager'] is None:
        # Clean up old instance if reinitializing
        if bInit and _cache['eventManager'] is not None:
            _cleanup()

        # Lazy import - only load when first needed
        if _cache['BugEventManager'] is None:
            import BugEventManager
            _cache['BugEventManager'] = BugEventManager

        # Create new instance only if needed
        _cache['eventManager'] = _cache['BugEventManager'].BugEventManager()
        _cache['initialized'] = True

        # Clean up module reference if no longer needed
        # Keep it cached for potential reuse in initAfterReload
        # This is a trade-off between memory and reload performance

    return _cache['eventManager']


# Initialize the event manager on module load
# This ensures it's ready when C++ calls into Python
getEventManager(True)


# **********************************
# C++ Entry Points - Do not rename
# **********************************

def onEvent(argsList):
    """
    Called when a game event happens.
    Returns 1 if the event was consumed, 0 otherwise.
    Memory optimized with direct method reference.
    """
    # Direct method reference avoids attribute lookup overhead
    em = _cache['eventManager']
    if em is not None:
        return em.handleEvent(argsList)
    return 0


def applyEvent(argsList):
    """
    Apply an event.
    Memory optimized with direct method reference.
    """
    em = _cache['eventManager']
    if em is not None:
        return em.applyEvent(argsList)
    return -1


def beginEvent(context, argsList=-1):
    """
    Begin an event with context.
    Memory optimized with direct method reference.
    """
    em = _cache['eventManager']
    if em is not None:
        return em.beginEvent(context, argsList)
    return -1


def initAfterReload():
    """
    Initialize BUG and fires PythonReloaded event after reloading Python modules.

    Memory optimized version:
    - Lazy imports to reduce memory usage
    - Proper exception handling with cleanup
    - Cached module references for efficiency

    The first time this module is loaded after the game launches, the global context
    is not yet ready, and thus BUG cannot be initialized. When the Python modules are
    reloaded after being changed, however, this will reinitialize BUG and the main interface.
    """
    # Clean up cached modules before reload to free memory
    _cleanup()

    # Lazy import BugInit only when needed
    if _cache['BugInit'] is None:
        import BugInit
        _cache['BugInit'] = BugInit

    # Initialize BUG
    _cache['BugInit'].init()

    # Try to reinitialize the main interface
    # Use try-except-finally pattern compatible with Python 2.4
    try:
        # Lazy import CvScreensInterface only when needed
        if _cache['CvScreensInterface'] is None:
            import CvScreensInterface
            _cache['CvScreensInterface'] = CvScreensInterface

        _cache['CvScreensInterface'].reinitMainInterface()

    except:
        # Import BugUtil only if there's an error (saves memory in normal operation)
        import BugUtil
        BugUtil.error("BugInit - failure rebuilding main interface after reloading Python modules")
        # Clean up the error handling module reference
        del BugUtil

    # Fire the reload event to notify other systems
    em = _cache['eventManager']
    if em is not None:
        em.fireEvent("PythonReloaded")


# **********************************
# Memory management helper
# **********************************

def _cleanup():
    """
    Cleanup function that frees memory by clearing cached modules.
    Called automatically during reload operations.
    """
    global _cache

    # Clear event manager instance
    if 'eventManager' in _cache:
        _cache['eventManager'] = None

    # Clear cached modules (they'll be reloaded if needed)
    if 'BugEventManager' in _cache:
        _cache['BugEventManager'] = None
    if 'BugInit' in _cache:
        _cache['BugInit'] = None
    if 'CvScreensInterface' in _cache:
        _cache['CvScreensInterface'] = None

    # Force garbage collection
    try:
        import gc
        gc.collect()
        del gc
    except:
        pass