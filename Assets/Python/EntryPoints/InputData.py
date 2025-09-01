import _core
import _misc


class InputData:
    """Memory-optimized InputData class using __slots__ to reduce instance overhead."""

    # Use __slots__ to eliminate __dict__ and reduce memory per instance
    # This can save 100-200 bytes per instance in 32-bit Python
    __slots__ = ('App',)

    # Static key mapping at class level - created once, not per method call
    # This saves memory by avoiding dictionary recreation on each isKeyDown call
    _KEY_MAP = {
        13: 65,  # A
        16: 68,  # D
        31: 83,  # S
        35: 87,  # W
        100: 317,  # Up
        102: 316,  # Left
        103: 318,  # Right
        105: 319,  # Down
    }

    def __init__(self):
        # Direct assignment without intermediate variable
        # Saves a reference and reduces peak memory during initialization
        self.App = _core.App()
        self.App.MainLoop()

    def getModifierKeys(self):
        # Direct return of list comprehension
        # Avoids creating intermediate variables for each key state
        # More memory efficient than storing then returning
        return [
            _misc.GetKeyState(307),  # Alt
            _misc.GetKeyState(308),  # Ctrl
            _misc.GetKeyState(306)  # Shift
        ]

    def isKeyDown(self, iKey):
        # Use class-level mapping to avoid recreation
        # Direct dictionary lookup without intermediate variable
        if iKey in self._KEY_MAP:
            # Direct return without storing in variable
            return _misc.GetKeyState(self._KEY_MAP[iKey])

        # Use % formatting instead of concatenation
        # More memory efficient in Python 2.4
        print
        "InputData.isKeyDown() - Warning\n\tUnknown key: %d" % iKey
        return "Unknown"


# Module-level singleton instance
# No change needed here as this is already efficient
instance = InputData()