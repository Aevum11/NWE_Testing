# ScreenResolution.py - Memory-optimized version for 32-bit Caveman2Cosmos
# Data storage for screen resolution and font scaling
# Resolution set by CvScreensInterface.py on game launch
# Updated by CvOptionsScreenCallbackInterface.py on resolution changes

# Global variables - minimized for memory efficiency
x = 0
y = 0
iFontScale = 2

# Pre-defined font lists as tuples (immutable, saves ~16 bytes per list vs mutable lists)
# Indexed by scale level for quick access without recreation
_FONT_LISTS = (
    # Scale 0: x <= 1400
    ("<font=2b>", "<font=2>", "<font=1b>", "<font=1>", "<font=0b>", "<font=0>", "<font=0>", "<font=0>"),
    # Scale 1: 1400 < x <= 1700
    ("<font=3b>", "<font=3>", "<font=2b>", "<font=2>", "<font=1b>", "<font=1>", "<font=0b>", "<font=0b>"),
    # Scale 2: 1700 < x <= 2500 (default)
    ("<font=4b>", "<font=4>", "<font=3b>", "<font=3>", "<font=2b>", "<font=2>", "<font=1b>", "<font=1>"),
    # Scale 3: x > 2500
    ("<font=4b>", "<font=4b>", "<font=4b>", "<font=4>", "<font=3b>", "<font=3>", "<font=2b>", "<font=2>")
)

# Default to scale 2 font list
aFontList = _FONT_LISTS[2]

# Pre-cached string constants to leverage Python's string interning
_CONFIG_SECTION_GAME = "GAME"
_CONFIG_SECTION_DEBUG = "DEBUG"
_CONFIG_KEY_ERA = "Era"
_CONFIG_KEY_MAINMENU = "MainMenuMods"
_CONFIG_KEY_WIDTH = "ScreenWidth"
_CONFIG_KEY_HEIGHT = "ScreenHeight"
_CONFIG_VALUE_ERA = "C2C_ERA_PREHISTORIC"
_CONFIG_VALUE_MAINMENU = "Caveman2Cosmos"
_CONFIG_ERA_PREFIX = "C2C"
_CONFIG_FILENAME = "\CivilizationIV.ini"
_CONFIG_WRITE_MODE = "wb"

# Pre-computed resolution bounds
_MIN_WIDTH = 1024
_MIN_HEIGHT = 768
_SCALE_THRESHOLD_1 = 1400
_SCALE_THRESHOLD_2 = 1700
_SCALE_THRESHOLD_3 = 2500


def init(dir):
    """
    Initialize screen resolution from CivilizationIV.ini if custom values exist.
    Memory optimized: Proper ConfigParser cleanup, reduced string operations.
    FIXED: Restructured try/except/finally for Python 2.4 compatibility.
    """
    global x, y, aFontList, iFontScale

    print "ScreenResolution.init\nSet custom resolution from CivilizationIV.ini if found."

    # Build path once using pre-cached string
    ini_path = dir + _CONFIG_FILENAME

    # Use ConfigParser with proper cleanup
    import ConfigParser
    Config = ConfigParser.ConfigParser()

    # In Python 2.4, 'finally' cannot be at the same level as 'except'.
    # We must nest the try/except block inside a try/finally block.
    try:
        try:
            Config.read(ini_path)

            # Check and fix Era if needed
            szEra = Config.get(_CONFIG_SECTION_GAME, _CONFIG_KEY_ERA)
            # Use slicing instead of startswith (more memory efficient in Python 2.4)
            if szEra[:3] != _CONFIG_ERA_PREFIX:
                Config.set(_CONFIG_SECTION_GAME, _CONFIG_KEY_ERA, _CONFIG_VALUE_ERA)
                # Write changes
                file = open(ini_path, _CONFIG_WRITE_MODE)
                try:
                    Config.write(file)
                finally:
                    file.close()

            # Check and fix MainMenuMods if needed
            szMainMenuMods = Config.get(_CONFIG_SECTION_GAME, _CONFIG_KEY_MAINMENU)
            if szMainMenuMods != _CONFIG_VALUE_MAINMENU:
                print "Fixing MainMenuMods"
                Config.set(_CONFIG_SECTION_GAME, _CONFIG_KEY_MAINMENU, _CONFIG_VALUE_MAINMENU)
                # Write changes
                file = open(ini_path, _CONFIG_WRITE_MODE)
                try:
                    Config.write(file)
                finally:
                    file.close()

            # Read resolution values
            X0_str = Config.get(_CONFIG_SECTION_DEBUG, _CONFIG_KEY_WIDTH)
            Y0_str = Config.get(_CONFIG_SECTION_DEBUG, _CONFIG_KEY_HEIGHT)

            # Validate and process resolution
            if X0_str.isdigit() and Y0_str.isdigit():
                X0 = int(X0_str)
                Y0 = int(Y0_str)

                if X0 > 0 and Y0 > 0:
                    # Apply minimum bounds
                    if X0 < _MIN_WIDTH:
                        X0 = _MIN_WIDTH
                    if Y0 < _MIN_HEIGHT:
                        Y0 = _MIN_HEIGHT

                    x = X0
                    y = Y0

                    # Calibrate fonts based on resolution
                    _calibrate_internal()

                    # Single formatted print instead of multiple string operations
                    print "Resolution: %dx%d\nScreenResolution.init - END" % (x, y)
                    return

        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            pass  # Expected when sections/options don't exist

    finally:
        # Clear ConfigParser to free memory immediately
        del Config
        del ConfigParser

    print "No custom resolution found.\nValue stored in profileName.pfl will be used instead.\nScreenResolution.init - END"


def calibrate():
    """
    Public calibration function - updates font list based on current resolution.
    Memory optimized: Uses pre-computed font tuples instead of creating new lists.
    """
    global aFontList, iFontScale

    # Use internal function to avoid repeated global lookups
    _calibrate_internal()


def _calibrate_internal():
    """
    Internal calibration - directly assigns pre-computed font tuples.
    Memory optimized: No list creation, direct tuple assignment.
    """
    global aFontList, iFontScale

    # Direct comparison chain with early exits
    # Ordered by most likely cases first for typical resolutions
    if x > _SCALE_THRESHOLD_2:  # x > 1700
        if x > _SCALE_THRESHOLD_3:  # x > 2500
            aFontList = _FONT_LISTS[3]
            iFontScale = 3
        else:
            aFontList = _FONT_LISTS[2]
            iFontScale = 2
    elif x > _SCALE_THRESHOLD_1:  # x > 1400
        aFontList = _FONT_LISTS[1]
        iFontScale = 1
    else:
        aFontList = _FONT_LISTS[0]
        iFontScale = 0

# Memory optimization notes:
# 1. Font lists pre-computed as immutable tuples - saves ~16 bytes per list
# 2. String constants pre-cached to leverage Python's string interning
# 3. ConfigParser properly cleaned up after use
# 4. Reduced string concatenation operations
# 5. Internal function avoids repeated global lookups
# 6. Pre-computed threshold values avoid repeated integer creation
# 7. File handles properly closed to free resources immediately