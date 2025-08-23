#
# CvUtil - Fixed Version
#
import sys  # for file ops
import traceback  # for error reporting

# For Civ game code access
from CvPythonExtensions import *
import ScreenResolution as SR

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

# Thread-safe ID generation with simple locking mechanism
# Simple thread safety for Python 2.4 compatibility
try:
    import threading

    _id_lock = threading.RLock()
except ImportError:
    # Fallback for environments without threading support
    class DummyLock:
        def __enter__(self): pass

        def __exit__(self, *args): pass


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
    """Send Debug Messages to Civ Engine"""

    def __init__(self):
        self.m_PythonMgr = CyPythonMgr()

    def write(self, stuff):
        """Write debug message, handling unicode appropriately"""
        _write_unicode_safe(
            self.m_PythonMgr.debugMsgWide,
            self.m_PythonMgr.debugMsg,
            stuff
        )


class RedirectError:
    """Send Error Messages to Civ Engine"""

    def __init__(self):
        self.m_PythonMgr = CyPythonMgr()

    def write(self, stuff):
        """Write error message, handling unicode appropriately"""
        _write_unicode_safe(
            self.m_PythonMgr.errorMsgWide,
            self.m_PythonMgr.errorMsg,
            stuff
        )


def myExceptHook(exc_type, exc_value, exc_tb):
    """
    Custom exception hook with proper error handling.
    Safely formats and reports exceptions even if traceback formatting fails.
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

    try:
        sys.stderr.write(error_msg)
    except Exception:
        # Last resort - try to write minimal error info
        pass


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
    Optimized version with reduced redundancy and better memory usage.
    """
    if not cdUnit:
        return  # Input validation

    # Cache frequently used objects
    add_msg = CyIF.addCombatMessage
    get_text = TRNSLTR.getText

    # Process modifiers individually to handle attribute access safely
    if hasattr(cdUnit, 'iExtraCombatPercent') and cdUnit.iExtraCombatPercent:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_EXTRA_COMBAT_PERCENT", (cdUnit.iExtraCombatPercent * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iAnimalCombatModifierTA') and cdUnit.iAnimalCombatModifierTA:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_ANIMAL_COMBAT", (cdUnit.iAnimalCombatModifierTA * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iAIAnimalCombatModifierTA') and cdUnit.iAIAnimalCombatModifierTA:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_AI_ANIMAL_COMBAT", (cdUnit.iAIAnimalCombatModifierTA * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iAnimalCombatModifierAA') and cdUnit.iAnimalCombatModifierAA:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_ANIMAL_COMBAT", (cdUnit.iAnimalCombatModifierAA * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iAIAnimalCombatModifierAA') and cdUnit.iAIAnimalCombatModifierAA:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_AI_ANIMAL_COMBAT", (cdUnit.iAIAnimalCombatModifierAA * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iBarbarianCombatModifierTB') and cdUnit.iBarbarianCombatModifierTB:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_BARBARIAN_COMBAT", (cdUnit.iBarbarianCombatModifierTB * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iAIBarbarianCombatModifierTB') and cdUnit.iAIBarbarianCombatModifierTB:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_BARBARIAN_AI_COMBAT", (cdUnit.iAIBarbarianCombatModifierTB * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iBarbarianCombatModifierAB') and cdUnit.iBarbarianCombatModifierAB:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_BARBARIAN_COMBAT", (cdUnit.iBarbarianCombatModifierAB * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iAIBarbarianCombatModifierAB') and cdUnit.iAIBarbarianCombatModifierAB:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_BARBARIAN_AI_COMBAT", (cdUnit.iAIBarbarianCombatModifierAB * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iPlotDefenseModifier') and cdUnit.iPlotDefenseModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_PLOT_DEFENSE", (cdUnit.iPlotDefenseModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iFortifyModifier') and cdUnit.iFortifyModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_FORTIFY", (cdUnit.iFortifyModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iCityDefenseModifier') and cdUnit.iCityDefenseModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CITY_DEFENSE", (cdUnit.iCityDefenseModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iHillsAttackModifier') and cdUnit.iHillsAttackModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_HILLS_ATTACK", (cdUnit.iHillsAttackModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iHillsDefenseModifier') and cdUnit.iHillsDefenseModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_HILLS", (cdUnit.iHillsDefenseModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iFeatureAttackModifier') and cdUnit.iFeatureAttackModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_FEATURE_ATTACK", (cdUnit.iFeatureAttackModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iFeatureDefenseModifier') and cdUnit.iFeatureDefenseModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_FEATURE", (cdUnit.iFeatureDefenseModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iTerrainAttackModifier') and cdUnit.iTerrainAttackModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_TERRAIN_ATTACK", (cdUnit.iTerrainAttackModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iTerrainDefenseModifier') and cdUnit.iTerrainDefenseModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_TERRAIN", (cdUnit.iTerrainDefenseModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iCityAttackModifier') and cdUnit.iCityAttackModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CITY_ATTACK", (cdUnit.iCityAttackModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iDomainDefenseModifier') and cdUnit.iDomainDefenseModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_DOMAIN_DEFENSE", (cdUnit.iDomainDefenseModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iCityBarbarianDefenseModifier') and cdUnit.iCityBarbarianDefenseModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CITY_BARBARIAN_DEFENSE",
                       (cdUnit.iCityBarbarianDefenseModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iDefenseModifier') and cdUnit.iDefenseModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CLASS_DEFENSE", (cdUnit.iDefenseModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iAttackModifier') and cdUnit.iAttackModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CLASS_ATTACK", (cdUnit.iAttackModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iCombatModifierT') and cdUnit.iCombatModifierT:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CLASS_COMBAT", (cdUnit.iCombatModifierT * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iCombatModifierA') and cdUnit.iCombatModifierA:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CLASS_COMBAT", (cdUnit.iCombatModifierA * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iDomainModifierA') and cdUnit.iDomainModifierA:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CLASS_DOMAIN", (cdUnit.iDomainModifierA * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iDomainModifierT') and cdUnit.iDomainModifierT:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CLASS_DOMAIN", (cdUnit.iDomainModifierT * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iAnimalCombatModifierA') and cdUnit.iAnimalCombatModifierA:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CLASS_ANIMAL_COMBAT", (cdUnit.iAnimalCombatModifierA * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iAnimalCombatModifierT') and cdUnit.iAnimalCombatModifierT:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CLASS_ANIMAL_COMBAT", (cdUnit.iAnimalCombatModifierT * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iRiverAttackModifier') and cdUnit.iRiverAttackModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CLASS_RIVER_ATTACK", (cdUnit.iRiverAttackModifier * iChange,))
        add_msg(ePlayer, msg)

    if hasattr(cdUnit, 'iAmphibAttackModifier') and cdUnit.iAmphibAttackModifier:
        msg = get_text("TXT_KEY_COMBAT_MESSAGE_CLASS_AMPHIB_ATTACK", (cdUnit.iAmphibAttackModifier * iChange,))
        add_msg(ePlayer, msg)


def combatMessageBuilder(cdAttacker, cdDefender, iCombatOdds):
    """
    Builds combat messages between attacker and defender.
    Optimized for memory efficiency using list joining instead of concatenation.
    """
    if not cdAttacker or not cdDefender:
        return  # Input validation

    # Validate combat strength to prevent division issues
    attacker_str = cdAttacker.iCurrCombatStr if cdAttacker.iCurrCombatStr else 1
    defender_str = cdDefender.iCurrCombatStr if cdDefender.iCurrCombatStr else 1

    # Build combat message efficiently using list joining
    message_parts = []

    # Attacker info
    if cdAttacker.eOwner == cdAttacker.eVisualOwner:
        attacker_owner = GC.getPlayer(cdAttacker.eOwner).getName()
        message_parts.append("%s's " % attacker_owner)

    message_parts.append("%s (%.2f)" % (cdAttacker.sUnitName, attacker_str / 100.0))
    message_parts.append(" " + TRNSLTR.getText("TXT_KEY_COMBAT_MESSAGE_VS", ()) + " ")

    # Defender info
    if cdDefender.eOwner == cdDefender.eVisualOwner:
        defender_owner = GC.getPlayer(cdDefender.eOwner).getName()
        message_parts.append("%s's " % defender_owner)

    message_parts.append("%s (%.2f)" % (cdDefender.sUnitName, defender_str / 100.0))

    # Join all parts efficiently
    combat_message = "".join(message_parts)

    # Send main combat message to both players
    CyIF.addCombatMessage(cdAttacker.eOwner, combat_message)
    CyIF.addCombatMessage(cdDefender.eOwner, combat_message)

    # Send odds message
    odds_message = "%s %.1f%%" % (
        TRNSLTR.getText("TXT_KEY_COMBAT_MESSAGE_ODDS", ()),
        iCombatOdds / 10.0
    )
    CyIF.addCombatMessage(cdAttacker.eOwner, odds_message)
    CyIF.addCombatMessage(cdDefender.eOwner, odds_message)

    # Send detailed combat messages
    combatDetailMessageBuilder(cdAttacker, cdAttacker.eOwner, -1)
    combatDetailMessageBuilder(cdDefender, cdAttacker.eOwner, 1)
    combatDetailMessageBuilder(cdAttacker, cdDefender.eOwner, -1)
    combatDetailMessageBuilder(cdDefender, cdDefender.eOwner, 1)


def sendMessage(szTxt, iPlayer=None, iTime=DEFAULT_MESSAGE_TIME, szIcon=None,
                eColor=DEFAULT_MESSAGE_COLOR, iMapX=DEFAULT_MAP_COORDS,
                iMapY=DEFAULT_MAP_COORDS, bOffArrow=False, bOnArrow=False,
                eMsgType=0, szSound=None, bForce=True):
    """
    Centralized function for displaying messages in the message box.
    Enhanced with input validation and cleaner parameter handling.
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

    # Send the message with proper font formatting
    formatted_text = SR.aFontList[5] + szTxt
    CyIF.addMessage(iPlayer, bForce, iTime, formatted_text, szSound, eMsgType,
                    szIcon, eColor, iMapX, iMapY, bOffArrow, bOnArrow)


def sendImmediateMessage(szTxt, szSound=None):
    """
    Sends an immediate message to the interface.
    Enhanced with input validation.
    """
    if szTxt:
        formatted_text = SR.aFontList[5] + szTxt
        CyIF.addImmediateMessage(formatted_text, szSound)