#
# CvUtil - Fixed Version
#
import sys  # for file ops
import traceback  # for error reporting

# For Civ game code access
from CvPythonExtensions import *
import ScreenResolution as SR

# Unicode compatibility for cross-runtime resilience
try:
    unicode
except NameError:
    # Python 3 compatibility (for linting/tools)
    unicode = str

# Constants
INITIAL_EVENT_ID = 9999
BUG_FIRST_SCREEN = 1000

# Font justification constants
FONT_LEFT_JUSTIFY = 1 << 0
FONT_RIGHT_JUSTIFY = 1 << 1
FONT_CENTER_JUSTIFY = 1 << 2

# Message defaults
DEFAULT_MESSAGE_TIME = 16
DEFAULT_MESSAGE_COLOR = -1
DEFAULT_MAP_COORDS = -1

# globals
GC = CyGlobalContext()
CyIF = CyInterface()
TRNSLTR = CyTranslator()

# Simple thread safety for Python 2.4 compatibility
try:
    import threading

    _id_lock = threading.RLock()
except ImportError:
    # Fallback for environments without threading support
    class DummyLock:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def acquire(self):
            pass

        def release(self):
            pass


    _id_lock = DummyLock()

# Event IDs
_g_nextEventID = INITIAL_EVENT_ID


def getNewEventID():
    """
    Defines a new event and returns its unique ID
    to be passed to BugEventManager.beginEvent(id).
    Thread-safe implementation.
    """
    global _g_nextEventID
    # Python 2.4 compatible context manager usage
    try:
        _id_lock.acquire()
        _g_nextEventID += 1
        return _g_nextEventID
    finally:
        _id_lock.release()


# Screen IDs
_g_nextScreenID = BUG_FIRST_SCREEN


def getNewScreenID():
    """
    Returns a new unique screen ID.
    Thread-safe implementation.
    """
    global _g_nextScreenID
    # Python 2.4 compatible context manager usage
    try:
        _id_lock.acquire()
        screen_id = _g_nextScreenID
        _g_nextScreenID += 1
        return screen_id
    finally:
        _id_lock.release()


def _write_unicode_safe(mgr_method_unicode, mgr_method_normal, content):
    """
    Helper function to handle unicode writing safely.
    Reduces code duplication between RedirectDebug and RedirectError.
    """
    if isinstance(content, unicode):
        mgr_method_unicode(content)
    else:
        mgr_method_normal(content)


class RedirectDebug:
    """Send Debug Messages to Civ Engine - file-like interface"""

    def __init__(self):
        self.m_PythonMgr = CyPythonMgr()
        self.encoding = 'utf-8'  # Standard encoding attribute

    def write(self, stuff):
        """Write debug message, handling unicode appropriately"""
        _write_unicode_safe(
            self.m_PythonMgr.debugMsgWide,
            self.m_PythonMgr.debugMsg,
            stuff
        )

    def flush(self):
        """No-op flush for file-like interface compatibility"""
        pass

    def isatty(self):
        """Return False as this is not a terminal"""
        return False


class RedirectError:
    """Send Error Messages to Civ Engine - file-like interface"""

    def __init__(self):
        self.m_PythonMgr = CyPythonMgr()
        self.encoding = 'utf-8'  # Standard encoding attribute

    def write(self, stuff):
        """Write error message, handling unicode appropriately"""
        _write_unicode_safe(
            self.m_PythonMgr.errorMsgWide,
            self.m_PythonMgr.errorMsg,
            stuff
        )

    def flush(self):
        """No-op flush for file-like interface compatibility"""
        pass

    def isatty(self):
        """Return False as this is not a terminal"""
        return False


def myExceptHook(exc_type, exc_value, exc_tb):
    """
    Custom exception hook with proper error handling.
    Safely formats and reports exceptions even if traceback formatting fails.
    Also routes errors to in-game error log.
    """
    try:
        lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        error_msg = "".join(lines)
    except Exception:
        # Fallback if traceback formatting fails
        try:
            error_msg = "Exception occurred: %s: %s" % (exc_type.__name__, str(exc_value))
        except Exception:
            error_msg = "Critical exception occurred but could not be formatted"

    # Route to stderr
    try:
        sys.stderr.write(error_msg)
    except Exception:
        pass

    # Also route to in-game error log
    try:
        python_mgr = CyPythonMgr()
        if isinstance(error_msg, unicode):
            python_mgr.errorMsgWide(error_msg)
        else:
            python_mgr.errorMsg(error_msg)
    except Exception:
        pass


# Register the exception hook
sys.excepthook = myExceptHook


def _add_combat_message_if_nonzero(player, text_key, value, change):
    """
    Helper function to add combat message only if value is non-zero.
    Optimizes performance by reducing function calls and string operations.
    """
    if value:
        adjusted_value = value * change
        msg = TRNSLTR.getText(text_key, (adjusted_value,))
        CyIF.addCombatMessage(player, msg)


def combatDetailMessageBuilder(cdUnit, ePlayer, iChange):
    """
    Builds detailed combat messages for a unit.
    Optimized version using helper function to reduce boilerplate.
    """
    if not cdUnit:
        return  # Input validation

    # Use helper function to reduce boilerplate and improve maintainability
    add_msg_if_nonzero = _add_combat_message_if_nonzero

    # Process modifiers using helper function
    if hasattr(cdUnit, 'iExtraCombatPercent'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_EXTRA_COMBAT_PERCENT", cdUnit.iExtraCombatPercent, iChange)

    if hasattr(cdUnit, 'iAnimalCombatModifierTA'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_ANIMAL_COMBAT", cdUnit.iAnimalCombatModifierTA, iChange)

    if hasattr(cdUnit, 'iAIAnimalCombatModifierTA'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_AI_ANIMAL_COMBAT", cdUnit.iAIAnimalCombatModifierTA,
                           iChange)

    if hasattr(cdUnit, 'iAnimalCombatModifierAA'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_ANIMAL_COMBAT", cdUnit.iAnimalCombatModifierAA, iChange)

    if hasattr(cdUnit, 'iAIAnimalCombatModifierAA'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_AI_ANIMAL_COMBAT", cdUnit.iAIAnimalCombatModifierAA,
                           iChange)

    if hasattr(cdUnit, 'iBarbarianCombatModifierTB'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_BARBARIAN_COMBAT", cdUnit.iBarbarianCombatModifierTB,
                           iChange)

    if hasattr(cdUnit, 'iAIBarbarianCombatModifierTB'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_BARBARIAN_AI_COMBAT", cdUnit.iAIBarbarianCombatModifierTB,
                           iChange)

    if hasattr(cdUnit, 'iBarbarianCombatModifierAB'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_BARBARIAN_COMBAT", cdUnit.iBarbarianCombatModifierAB,
                           iChange)

    if hasattr(cdUnit, 'iAIBarbarianCombatModifierAB'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_BARBARIAN_AI_COMBAT", cdUnit.iAIBarbarianCombatModifierAB,
                           iChange)

    if hasattr(cdUnit, 'iPlotDefenseModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_PLOT_DEFENSE", cdUnit.iPlotDefenseModifier, iChange)

    if hasattr(cdUnit, 'iFortifyModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_FORTIFY", cdUnit.iFortifyModifier, iChange)

    if hasattr(cdUnit, 'iCityDefenseModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CITY_DEFENSE", cdUnit.iCityDefenseModifier, iChange)

    if hasattr(cdUnit, 'iHillsAttackModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_HILLS_ATTACK", cdUnit.iHillsAttackModifier, iChange)

    if hasattr(cdUnit, 'iHillsDefenseModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_HILLS", cdUnit.iHillsDefenseModifier, iChange)

    if hasattr(cdUnit, 'iFeatureAttackModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_FEATURE_ATTACK", cdUnit.iFeatureAttackModifier, iChange)

    if hasattr(cdUnit, 'iFeatureDefenseModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_FEATURE", cdUnit.iFeatureDefenseModifier, iChange)

    if hasattr(cdUnit, 'iTerrainAttackModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_TERRAIN_ATTACK", cdUnit.iTerrainAttackModifier, iChange)

    if hasattr(cdUnit, 'iTerrainDefenseModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_TERRAIN", cdUnit.iTerrainDefenseModifier, iChange)

    if hasattr(cdUnit, 'iCityAttackModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CITY_ATTACK", cdUnit.iCityAttackModifier, iChange)

    if hasattr(cdUnit, 'iDomainDefenseModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_DOMAIN_DEFENSE", cdUnit.iDomainDefenseModifier, iChange)

    if hasattr(cdUnit, 'iCityBarbarianDefenseModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CITY_BARBARIAN_DEFENSE",
                           cdUnit.iCityBarbarianDefenseModifier, iChange)

    if hasattr(cdUnit, 'iDefenseModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CLASS_DEFENSE", cdUnit.iDefenseModifier, iChange)

    if hasattr(cdUnit, 'iAttackModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CLASS_ATTACK", cdUnit.iAttackModifier, iChange)

    if hasattr(cdUnit, 'iCombatModifierT'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CLASS_COMBAT", cdUnit.iCombatModifierT, iChange)

    if hasattr(cdUnit, 'iCombatModifierA'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CLASS_COMBAT", cdUnit.iCombatModifierA, iChange)

    if hasattr(cdUnit, 'iDomainModifierA'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CLASS_DOMAIN", cdUnit.iDomainModifierA, iChange)

    if hasattr(cdUnit, 'iDomainModifierT'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CLASS_DOMAIN", cdUnit.iDomainModifierT, iChange)

    if hasattr(cdUnit, 'iAnimalCombatModifierA'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CLASS_ANIMAL_COMBAT", cdUnit.iAnimalCombatModifierA,
                           iChange)

    if hasattr(cdUnit, 'iAnimalCombatModifierT'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CLASS_ANIMAL_COMBAT", cdUnit.iAnimalCombatModifierT,
                           iChange)

    if hasattr(cdUnit, 'iRiverAttackModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CLASS_RIVER_ATTACK", cdUnit.iRiverAttackModifier, iChange)

    if hasattr(cdUnit, 'iAmphibAttackModifier'):
        add_msg_if_nonzero(ePlayer, "TXT_KEY_COMBAT_MESSAGE_CLASS_AMPHIB_ATTACK", cdUnit.iAmphibAttackModifier, iChange)


def combatMessageBuilder(cdAttacker, cdDefender, iCombatOdds):
    """
    Builds combat messages between attacker and defender.
    Optimized for memory efficiency and encoding safety.
    Avoids duplicate messages to same player.
    """
    if not cdAttacker or not cdDefender:
        return  # Input validation

    # Safer strength access with fallbacks
    attacker_str = max(1, getattr(cdAttacker, 'iCurrCombatStr', 0))
    defender_str = max(1, getattr(cdDefender, 'iCurrCombatStr', 0))

    # Build combat message efficiently using Unicode-safe list joining
    message_parts = []

    # Attacker info
    if cdAttacker.eOwner == cdAttacker.eVisualOwner:
        attacker_owner = GC.getPlayer(cdAttacker.eOwner).getName()
        message_parts.append(u"%s's " % unicode(attacker_owner))

    message_parts.append(u"%s (%.2f)" % (unicode(cdAttacker.sUnitName), attacker_str / 100.0))
    message_parts.append(u" " + unicode(TRNSLTR.getText("TXT_KEY_COMBAT_MESSAGE_VS", ())) + u" ")

    # Defender info
    if cdDefender.eOwner == cdDefender.eVisualOwner:
        defender_owner = GC.getPlayer(cdDefender.eOwner).getName()
        message_parts.append(u"%s's " % unicode(defender_owner))

    message_parts.append(u"%s (%.2f)" % (unicode(cdDefender.sUnitName), defender_str / 100.0))

    # Join all parts efficiently with Unicode
    combat_message = u"".join(message_parts)

    # Collect unique players to avoid duplicate messages
    players_to_notify = set([cdAttacker.eOwner, cdDefender.eOwner])

    # Send main combat message to all unique players
    for player in players_to_notify:
        CyIF.addCombatMessage(player, combat_message)

    # Send odds message to all unique players
    odds_message = u"%s %.1f%%" % (
        unicode(TRNSLTR.getText("TXT_KEY_COMBAT_MESSAGE_ODDS", ())),
        iCombatOdds / 10.0
    )
    for player in players_to_notify:
        CyIF.addCombatMessage(player, odds_message)

    # Send detailed combat messages
    combatDetailMessageBuilder(cdAttacker, cdAttacker.eOwner, -1)
    combatDetailMessageBuilder(cdDefender, cdAttacker.eOwner, 1)
    combatDetailMessageBuilder(cdAttacker, cdDefender.eOwner, -1)
    combatDetailMessageBuilder(cdDefender, cdDefender.eOwner, 1)


def _get_safe_font_prefix():
    """
    Safely get font prefix with fallback to avoid crashes.
    """
    try:
        if hasattr(SR, 'aFontList') and len(SR.aFontList) > 5:
            return SR.aFontList[5]
        else:
            return u""  # Safe fallback
    except (IndexError, AttributeError):
        return u""


def sendMessage(szTxt, iPlayer=None, iTime=DEFAULT_MESSAGE_TIME, szIcon=None,
                eColor=DEFAULT_MESSAGE_COLOR, iMapX=DEFAULT_MAP_COORDS,
                iMapY=DEFAULT_MAP_COORDS, bOffArrow=False, bOnArrow=False,
                eMsgType=0, szSound=None, bForce=True):
    """
    Centralized function for displaying messages in the message box.
    Enhanced with input validation, encoding safety, and font fallback.
    """
    if not szTxt:
        return  # No message to send

    # Determine player
    if iPlayer is None:
        iPlayer = GC.getGame().getActivePlayer()

    if iPlayer == -1:
        return  # Invalid player

    # Validate player bounds
    max_players = GC.getMAX_PLAYERS()
    if iPlayer < 0 or iPlayer >= max_players:
        return  # Player index out of bounds

    # Handle AI auto-play mode
    if GC.getGame().getAIAutoPlay(iPlayer):
        szIcon = None
        iMapX = iMapY = iTime = -1
        bForce = bOffArrow = bOnArrow = False

    # Safe font prefix and Unicode normalization
    font_prefix = _get_safe_font_prefix()
    formatted_text = unicode(font_prefix) + unicode(szTxt)

    # Send the message
    CyIF.addMessage(iPlayer, bForce, iTime, formatted_text, szSound, eMsgType,
                    szIcon, eColor, iMapX, iMapY, bOffArrow, bOnArrow)


def sendImmediateMessage(szTxt, szSound=None):
    """
    Sends an immediate message to the interface.
    Enhanced with input validation and encoding safety.
    """
    if not szTxt:
        return  # No message to send

    # Safe font prefix and Unicode normalization
    font_prefix = _get_safe_font_prefix()
    formatted_text = unicode(font_prefix) + unicode(szTxt)

    CyIF.addImmediateMessage(formatted_text, szSound)