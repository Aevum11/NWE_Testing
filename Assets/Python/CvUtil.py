#
# CvUtil - Memory-optimized for 32-bit Caveman2Cosmos
#
import sys  # for file ops

# For Civ game code access
from CvPythonExtensions import *
import ScreenResolution as SR

# globals - using direct references saves repeated lookups
GC = CyGlobalContext()
CyIF = CyInterface()
TRNSLTR = CyTranslator()

# Pre-cache frequently used methods to reduce attribute lookups
_addMessage = CyIF.addMessage
_addImmediateMessage = CyIF.addImmediateMessage
_addCombatMessage = CyIF.addCombatMessage
_getText = TRNSLTR.getText
_getPlayer = GC.getPlayer
_getGame = GC.getGame


# Event IDs - use generator pattern for lazy evaluation
def _event_id_generator():
    """Generator for event IDs - memory efficient lazy evaluation"""
    n = 10000
    while True:
        yield n
        n += 1


_event_gen = _event_id_generator()


def getNewEventID():
    """
    Defines a new event and returns its unique ID
    to be passed to BugEventManager.beginEvent(id).
    Uses generator for memory efficiency in 32-bit environment.
    """
    return _event_gen.next()


# Screen IDs - use generator pattern
BUG_FIRST_SCREEN = 1000


def _screen_id_generator():
    """Generator for screen IDs - memory efficient lazy evaluation"""
    n = BUG_FIRST_SCREEN
    while True:
        yield n
        n += 1


_screen_gen = _screen_id_generator()


def getNewScreenID():
    return _screen_gen.next()


# Popup defines - use immutable tuple to save memory
FONT_CENTER_JUSTIFY = 1 << 2
FONT_RIGHT_JUSTIFY = 1 << 1
FONT_LEFT_JUSTIFY = 1 << 0


class RedirectDebug:
    """Send Debug Messages to Civ Engine - optimized with __slots__"""
    __slots__ = ('m_PythonMgr',)

    def __init__(self):
        self.m_PythonMgr = CyPythonMgr()

    def write(self, stuff):
        # Direct method references save repeated lookups
        if isinstance(stuff, unicode):
            self.m_PythonMgr.debugMsgWide(stuff)
        else:
            self.m_PythonMgr.debugMsg(stuff)


class RedirectError:
    """Send Error Messages to Civ Engine - optimized with __slots__"""
    __slots__ = ('m_PythonMgr',)

    def __init__(self):
        self.m_PythonMgr = CyPythonMgr()

    def write(self, stuff):
        # Direct method references save repeated lookups
        if isinstance(stuff, unicode):
            self.m_PythonMgr.errorMsgWide(stuff)
        else:
            self.m_PythonMgr.errorMsg(stuff)


def myExceptHook(type, value, tb):
    import traceback  # lazy import saves memory if not used
    lines = traceback.format_exception(type, value, tb)
    sys.stderr.write("\n".join(lines))


# Combat message text keys - pre-intern strings to save memory
# Python 2.4 automatically interns string literals, leverage this
_COMBAT_MSG_KEYS = (
    ("TXT_KEY_COMBAT_MESSAGE_EXTRA_COMBAT_PERCENT", "iExtraCombatPercent"),
    ("TXT_KEY_COMBAT_MESSAGE_ANIMAL_COMBAT", "iAnimalCombatModifierTA"),
    ("TXT_KEY_COMBAT_MESSAGE_AI_ANIMAL_COMBAT", "iAIAnimalCombatModifierTA"),
    ("TXT_KEY_COMBAT_MESSAGE_ANIMAL_COMBAT", "iAnimalCombatModifierAA"),
    ("TXT_KEY_COMBAT_MESSAGE_AI_ANIMAL_COMBAT", "iAIAnimalCombatModifierAA"),
    ("TXT_KEY_COMBAT_MESSAGE_BARBARIAN_COMBAT", "iBarbarianCombatModifierTB"),
    ("TXT_KEY_COMBAT_MESSAGE_BARBARIAN_AI_COMBAT", "iAIBarbarianCombatModifierTB"),
    ("TXT_KEY_COMBAT_MESSAGE_BARBARIAN_COMBAT", "iBarbarianCombatModifierAB"),
    ("TXT_KEY_COMBAT_MESSAGE_BARBARIAN_AI_COMBAT", "iAIBarbarianCombatModifierAB"),
    ("TXT_KEY_COMBAT_MESSAGE_PLOT_DEFENSE", "iPlotDefenseModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_FORTIFY", "iFortifyModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_CITY_DEFENSE", "iCityDefenseModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_HILLS_ATTACK", "iHillsAttackModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_HILLS", "iHillsDefenseModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_FEATURE_ATTACK", "iFeatureAttackModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_FEATURE", "iFeatureDefenseModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_TERRAIN_ATTACK", "iTerrainAttackModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_TERRAIN", "iTerrainDefenseModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_CITY_ATTACK", "iCityAttackModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_DOMAIN_DEFENSE", "iDomainDefenseModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_CITY_BARBARIAN_DEFENSE", "iCityBarbarianDefenseModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_CLASS_DEFENSE", "iDefenseModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_CLASS_ATTACK", "iAttackModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_CLASS_COMBAT", "iCombatModifierT"),
    ("TXT_KEY_COMBAT_MESSAGE_CLASS_COMBAT", "iCombatModifierA"),
    ("TXT_KEY_COMBAT_MESSAGE_CLASS_DOMAIN", "iDomainModifierA"),
    ("TXT_KEY_COMBAT_MESSAGE_CLASS_DOMAIN", "iDomainModifierT"),
    ("TXT_KEY_COMBAT_MESSAGE_CLASS_ANIMAL_COMBAT", "iAnimalCombatModifierA"),
    ("TXT_KEY_COMBAT_MESSAGE_CLASS_ANIMAL_COMBAT", "iAnimalCombatModifierT"),
    ("TXT_KEY_COMBAT_MESSAGE_CLASS_RIVER_ATTACK", "iRiverAttackModifier"),
    ("TXT_KEY_COMBAT_MESSAGE_CLASS_AMPHIB_ATTACK", "iAmphibAttackModifier"),
)


def combatDetailMessageBuilder(cdUnit, ePlayer, iChange):
    """Optimized combat detail message builder using tuple iteration"""
    # Use getattr with default to avoid hasattr overhead
    # Direct iteration over tuple is more memory efficient than multiple if statements
    for text_key, attr_name in _COMBAT_MSG_KEYS:
        value = getattr(cdUnit, attr_name, 0)
        if value:
            # Single string format operation is more efficient
            msg = _getText(text_key, (value * iChange,))
            _addCombatMessage(ePlayer, msg)


def combatMessageBuilder(cdAttacker, cdDefender, iCombatOdds):
    """Optimized combat message builder with reduced string operations"""
    # Build attacker string
    attacker_parts = []
    if cdAttacker.eOwner == cdAttacker.eVisualOwner:
        attacker_parts.append("%s's " % _getPlayer(cdAttacker.eOwner).getName())
    attacker_parts.append("%s (%.2f)" % (cdAttacker.sUnitName, cdAttacker.iCurrCombatStr / 100.0))

    # Build defender string
    defender_parts = []
    if cdDefender.eOwner == cdDefender.eVisualOwner:
        defender_parts.append("%s's " % _getPlayer(cdDefender.eOwner).getName())
    defender_parts.append("%s (%.2f)" % (cdDefender.sUnitName, cdDefender.iCurrCombatStr / 100.0))

    # Join once instead of multiple concatenations
    vs_text = " %s " % _getText("TXT_KEY_COMBAT_MESSAGE_VS", ())
    combatMessage = "".join(attacker_parts) + vs_text + "".join(defender_parts)

    # Send main combat message
    _addCombatMessage(cdAttacker.eOwner, combatMessage)
    _addCombatMessage(cdDefender.eOwner, combatMessage)

    # Odds message - format once, send twice
    oddsMessage = "%s %.1f%%" % (_getText("TXT_KEY_COMBAT_MESSAGE_ODDS", ()), iCombatOdds / 10.0)
    _addCombatMessage(cdAttacker.eOwner, oddsMessage)
    _addCombatMessage(cdDefender.eOwner, oddsMessage)

    # Detail messages
    combatDetailMessageBuilder(cdAttacker, cdAttacker.eOwner, -1)
    combatDetailMessageBuilder(cdDefender, cdAttacker.eOwner, 1)
    combatDetailMessageBuilder(cdAttacker, cdDefender.eOwner, -1)
    combatDetailMessageBuilder(cdDefender, cdDefender.eOwner, 1)


# Pre-cache default values to avoid repeated object creation
_DEFAULT_TIME = 16
_DEFAULT_COLOR = -1
_DEFAULT_COORD = -1
_DEFAULT_MSG_TYPE = 0
_MSG_FONT_PREFIX = None  # Will be set on first use


def sendMessage(szTxt, iPlayer=None, iTime=_DEFAULT_TIME, szIcon=None,
                eColor=_DEFAULT_COLOR, iMapX=_DEFAULT_COORD, iMapY=_DEFAULT_COORD,
                bOffArrow=False, bOnArrow=False, eMsgType=_DEFAULT_MSG_TYPE,
                szSound=None, bForce=True):
    """Centralized function for displaying messages - optimized for memory"""
    if not szTxt:
        return

    if iPlayer is None:
        iPlayer = _getGame().getActivePlayer()
    if iPlayer == -1:
        return

    # Check AI autoplay
    if _getGame().getAIAutoPlay(iPlayer):
        szIcon = None
        iMapX = iMapY = iTime = _DEFAULT_COORD
        bForce = bOffArrow = bOnArrow = False

    # Cache font prefix on first use
    global _MSG_FONT_PREFIX
    if _MSG_FONT_PREFIX is None:
        _MSG_FONT_PREFIX = SR.aFontList[5]

    # Single message call with pre-cached font
    _addMessage(iPlayer, bForce, iTime, _MSG_FONT_PREFIX + szTxt,
                szSound, eMsgType, szIcon, eColor, iMapX, iMapY,
                bOffArrow, bOnArrow)


def sendImmediateMessage(szTxt, szSound=None):
    """Send immediate message - optimized"""
    if szTxt:
        # Cache font prefix on first use
        global _MSG_FONT_PREFIX
        if _MSG_FONT_PREFIX is None:
            _MSG_FONT_PREFIX = SR.aFontList[5]

        _addImmediateMessage(_MSG_FONT_PREFIX + szTxt, szSound)