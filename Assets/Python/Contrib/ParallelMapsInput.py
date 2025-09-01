# Memory-optimized version for Python 2.4 (32-bit Civilization IV)
# Optimizations applied:
# 1. Lazy imports to reduce initial memory footprint
# 2. Local variable caching to reduce attribute access overhead
# 3. Early returns to minimize unnecessary processing
# 4. String formatting optimization using % operator (most efficient in Python 2.4)
# 5. Single-evaluation of conditions with cached results
# 6. Reduced object creation and reference chains
# 7. __slots__ usage where applicable (if creating classes)

# Delayed import pattern - only import when needed
_gc = None
_game = None
_interface = None
_debug_utils = None
_event_manager = None


def _get_gc():
    """Lazy load CyGlobalContext to save memory on startup"""
    global _gc
    if _gc is None:
        from CvPythonExtensions import CyGlobalContext
        _gc = CyGlobalContext()
    return _gc


def _get_interface():
    """Lazy load CyInterface when needed"""
    global _interface
    if _interface is None:
        from CvPythonExtensions import CyInterface
        _interface = CyInterface()
    return _interface


def _get_event_manager():
    """Lazy load event manager when needed"""
    global _event_manager
    if _event_manager is None:
        from BugEventManager import g_eventManager
        _event_manager = g_eventManager
    return _event_manager


def _get_debug_utils():
    """Lazy load debug utils when needed"""
    global _debug_utils
    if _debug_utils is None:
        import DebugUtils
        _debug_utils = DebugUtils
    return _debug_utils


def handleInput(argsList):
    """
    Memory-optimized input handler for map switching

    Optimizations:
    - Early return if in WorldBuilder mode
    - Cached local variables to minimize attribute lookups
    - Single pass condition evaluation
    - Optimized string formatting
    - Lazy module loading
    """
    # Cache global context (lazy loaded)
    gc = _get_gc()

    # Get game reference and cache it
    game = gc.getGame()

    # Early return - most important optimization for reducing unnecessary processing
    if game.GetWorldBuilderMode():
        return 0

    # Extract key from args once
    iKey = argsList[1]

    # Cache debug mode check - single evaluation
    # Use local variable to avoid repeated attribute access
    debug_utils = _get_debug_utils()
    bDebug = gc.isDebugBuild() or debug_utils.bDebugMode

    # Cache current map to avoid repeated calls
    current_map = game.getCurrentMap()

    # Get event manager reference once (lazy loaded)
    event_mgr = _get_event_manager()

    # Cache frequently accessed attributes as locals
    # This reduces attribute lookup overhead in the loop
    evt_alt = event_mgr.bAlt
    evt_shift = event_mgr.bShift
    evt_ctrl = event_mgr.bCtrl

    # Import MapTypes only when needed (lazy import)
    from CvPythonExtensions import MapTypes
    num_maps = MapTypes.NUM_MAPS

    # Pre-allocate variables outside loop when possible
    mapInfo = None
    target_map = None
    map_obj = None

    # Main loop with optimized condition checking
    for i in xrange(num_maps):  # xrange is more memory efficient than range in Python 2.x
        # Early continue pattern to reduce nesting and processing
        if i == current_map:
            continue

        # Get map info
        mapInfo = gc.getMapInfo(i)

        # Cache hotkey value
        hotkey = mapInfo.getHotKeyVal()

        # Skip if key doesn't match - early continue
        if iKey != hotkey:
            continue

        # Check modifier keys - optimized with cached values
        # Early continue pattern for each condition
        if mapInfo.isAltDown() and not evt_alt:
            continue
        if mapInfo.isShiftDown() and not evt_shift:
            continue
        if mapInfo.isCtrlDown() and not evt_ctrl:
            continue

        # Get map object once
        map_obj = gc.getMapByIndex(i)

        # Check if map is accessible
        if not bDebug and not map_obj.plotsInitialized():
            continue

        # At this point, all conditions are met - switch map
        # Optimize message creation with single string format
        interface = _get_interface()

        # Check initialization status once
        if not map_obj.plotsInitialized():
            # Use % formatting (most efficient in Python 2.4)
            msg = "Initialized Map %d: %s" % (i, mapInfo.getDescription())
        else:
            msg = "Map %d: %s" % (i, mapInfo.getDescription())

        # Send message
        interface.addImmediateMessage(msg, "")

        # Switch map
        gc.switchMap(i)

        # Return success immediately
        return 1

    # No valid map found
    return 0


# Optional: Memory pool for frequently created objects
# This can be useful if the module creates temporary objects frequently
class _ObjectPool:
    """Simple object pool for memory efficiency"""
    __slots__ = ('_pool', '_max_size')

    def __init__(self, max_size=10):
        self._pool = []
        self._max_size = max_size

    def acquire(self, cls, *args, **kwargs):
        """Get object from pool or create new"""
        if self._pool:
            obj = self._pool.pop()
            if hasattr(obj, 'reset'):
                obj.reset(*args, **kwargs)
            return obj
        return cls(*args, **kwargs)

    def release(self, obj):
        """Return object to pool"""
        if len(self._pool) < self._max_size:
            self._pool.append(obj)
        # Otherwise let it be garbage collected


# Module-level optimization: pre-compile frequently used format strings
# This avoids repeated string parsing in Python 2.4
_MSG_FORMAT_INIT = "Initialized Map %d: %s"
_MSG_FORMAT_NORMAL = "Map %d: %s"


def handleInput_ultra_optimized(argsList):
    """
    Ultra-optimized version with pre-compiled formats and minimal overhead
    Use this if maximum performance is critical
    """
    gc = _get_gc()
    game = gc.getGame()

    if game.GetWorldBuilderMode():
        return 0

    iKey = argsList[1]

    # Single-line debug check
    debug_utils = _get_debug_utils()
    bDebug = gc.isDebugBuild() or debug_utils.bDebugMode

    current_map = game.getCurrentMap()
    event_mgr = _get_event_manager()

    # Import only when needed
    from CvPythonExtensions import MapTypes

    # Ultra-compact loop with minimal variables
    for i in xrange(MapTypes.NUM_MAPS):
        if i != current_map:
            mapInfo = gc.getMapInfo(i)
            if (iKey == mapInfo.getHotKeyVal() and
                    (not mapInfo.isAltDown() or event_mgr.bAlt) and
                    (not mapInfo.isShiftDown() or event_mgr.bShift) and
                    (not mapInfo.isCtrlDown() or event_mgr.bCtrl)):

                map_obj = gc.getMapByIndex(i)
                if bDebug or map_obj.plotsInitialized():
                    interface = _get_interface()

                    # Use pre-compiled format strings
                    if not map_obj.plotsInitialized():
                        msg = _MSG_FORMAT_INIT % (i, mapInfo.getDescription())
                    else:
                        msg = _MSG_FORMAT_NORMAL % (i, mapInfo.getDescription())

                    interface.addImmediateMessage(msg, "")
                    gc.switchMap(i)
                    return 1

    return 0


# Module cleanup function to free resources if needed
def cleanup():
    """Call this to free cached references if memory is critical"""
    global _gc, _game, _interface, _debug_utils, _event_manager
    _gc = None
    _game = None
    _interface = None
    _debug_utils = None
    _event_manager = None


# Export the optimized handler as the default
# You can switch between handleInput and handleInput_ultra_optimized
# based on your needs
__all__ = ['handleInput', 'handleInput_ultra_optimized', 'cleanup']