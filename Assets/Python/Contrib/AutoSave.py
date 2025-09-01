## AutoSave - Optimized for Memory Efficiency
# Python 2.4 compatible - Caveman2Cosmos mod for Civilization IV
from CvPythonExtensions import *
import TextUtil

# Single global context initialization - avoid redundant calls
GC = CyGlobalContext()
CyIF = CyInterface()
GAME = GC.getGame()
MAP = GC.getMap()

TRNSLTR = CyTranslator()

# Module-level variables to reduce redundancy
_saveDir = None
options = None

# Pre-computed replacement tuples for efficiency
# Using tuples saves memory vs lists (immutable, less overhead)
DIACRITICS_MAP = (
    # Lowercase replacements
    ('Ã ', 'a'), ('Ã¢', 'a'), ('Ã¤', 'a'), ('Ã¡', 'a'), ('Ã£', 'a'), ('Ã¥', 'a'),
    ('Ã§', 'c'),
    ('Ã©', 'e'), ('Ã¨', 'e'), ('Ãª', 'e'), ('Ã«', 'e'),
    ('Ã®', 'i'), ('Ã¯', 'i'), ('Ã­', 'i'),
    ('Ã´', 'o'), ('Ã¶', 'o'), ('Ã²', 'o'), ('Ã³', 'o'), ('Ãµ', 'o'),
    ('Ã¹', 'u'), ('Ã»', 'u'), ('Ã¼', 'u'), ('Ãº', 'u'),
    ('Ã¿', 'y'),
    ('Ã±', 'n'),
    # Uppercase replacements
    ('Ã€', 'A'), ('Ã‚', 'A'), ('Ã„', 'A'), ('Ã', 'A'), ('Ãƒ', 'A'), ('Ã…', 'A'),
    ('Ã‡', 'C'),
    ('Ã‰', 'E'), ('Ãˆ', 'E'), ('ÃŠ', 'E'), ('Ã‹', 'E'),
    ('ÃŽ', 'I'), ('Ã', 'I'), ('Ã', 'I'),
    ('Ã"', 'O'), ('Ã–', 'O'), ('Ã'', 'O'), ('Ã"', 'O'), ('Ã•', 'O'),
('Ã™', 'U'), ('Ã›', 'U'), ('Ãœ', 'U'), ('Ãš', 'U'),
    ('Å¸', 'Y'),
    ('Ã'', 'N')
     )


def remove_diacritics(in_text):
    """Optimized diacritics removal - single encoding pass"""
    # Single encoding attempt - avoid multiple try/except overhead
    try:
        text = in_text.encode("utf-8")
    except:
        text = in_text.encode("ascii", "ignore")

    # Single pass replacement using pre-computed map
    for old, new in DIACRITICS_MAP:
        text = text.replace(old, new)

    return text


def cleanNpc():
    """Optimized NPC cleaning - reduced redundancy"""
    iTurn = GAME.getGameTurn()
    # Bitwise operation is faster than modulo for power-of-2 checks
    # but keeping modulo for clarity and 30 is not power of 2
    if iTurn % 30 != 0:
        return

    # Check npcclean flag efficiently
    if not globals().get('npcclean', False):
        return

    # Process players 40-42 in a loop to avoid code duplication
    for iPlayer in (40, 41, 42):
        pPlayer = GC.getPlayer(iPlayer)
        pUnit, loop = pPlayer.firstUnit(False)
        while pUnit:
            # Remove debug prints to save memory and I/O overhead
            # Only print if absolutely necessary for debugging
            pUnit.kill(False, -1)
            pUnit, loop = pPlayer.nextUnit(loop, False)

    # Send message to human players
    szMessage = TRNSLTR.getText("TXT_KEY_MOD_KILL_ANIMALS_DESC", ())
    for iPlayer in xrange(GC.getMAX_PLAYERS()):
        pPlayer = GC.getPlayer(iPlayer)
        if pPlayer.isHuman():
            CyIF.addMessage(iPlayer, False, GC.getEVENT_MESSAGE_TIME(),
                            szMessage, None, InterfaceMessageTypes.MESSAGE_TYPE_INFO,
                            None, GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"),
                            -1, -1, False, False)


def init():
    """Initialize AutoSave module"""
    global _saveDir, options

    import SystemPaths as SP
    _saveDir = SP.userDir + "\\Saves"

    import BugCore
    options = BugCore.game.AutoSave

    # Single import and event registration
    import CvEventInterface
    em = CvEventInterface.eventManager
    em.addEventHandler("MapRegen", onMapRegen)
    em.addEventHandler("endTurnReady", onEndTurnReady)
    em.addEventHandler("GameEnd", onGameEnd)


def onMapRegen(argsList):
    """Handle map regeneration event"""
    autoSave("[Start]", 0)


def onEndTurnReady(argsList):
    """Handle end turn ready event"""
    iTurn = argsList[0]
    inter = options.getInterval()
    if inter > 0 and iTurn % inter == 0:
        autoSave("[Late]", iTurn)


def onGameEnd(argsList):
    """Handle game end event"""
    autoSave("[End]", argsList[0])


def save(type, prefix, iTurn):
    """Optimized save function using list join for string building"""
    # Use list for efficient string building
    path_parts = [_saveDir, "\\", type, "\\"]

    if prefix:
        path_parts.append(prefix)
        path_parts.append("'")

    # Cache frequently accessed objects
    CyPlayer = GC.getActivePlayer()

    # Build filename components
    if iTurn:
        path_parts.append("#")
        path_parts.append(str(iTurn))
    else:
        path_parts.append(MAP.getMapScriptName())

    path_parts.append('-')

<<<<<<< Updated upstream
	GAME.saveGame(str(dir))
	print "AutoSave.save\n\t%s" % dir
=======
    # Use cached player name/leader
    if options.isUsePlayerName():
        path_parts.append(CyPlayer.getName()[:8])
    else:
        path_parts.append(GC.getLeaderHeadInfo(CyPlayer.getLeaderType()).getText()[:8])

    # Add game state info - minimize function calls
    path_parts.append('-')
    path_parts.append(GC.getEraInfo(GAME.getCurrentEra()).getText()[:8])
    path_parts.append('-')
    path_parts.append(GC.getGameSpeedInfo(GAME.getGameSpeedType()).getText()[:5])
    path_parts.append('-')
    path_parts.append(GC.getWorldInfo(MAP.getWorldSize()).getText()[:5])
    path_parts.append('-')
    path_parts.append(GC.getHandicapInfo(CyPlayer.getHandicapType()).getText()[:5])
    path_parts.append(".CivBeyondSwordSave")

    # Single join operation - much more efficient than concatenation
    dir = ''.join(path_parts)

    # Apply diacritics removal
    dir = remove_diacritics(dir)

    # Check NPC clean flag - using globals() to avoid NameError
    if globals().get('npcclean', False):
        cleanNpc()

    # Save the game
    GAME.saveGame(str(dir))

>>>>>>> Stashed changes

def autoSave(prefix="", iTurn=None):
    """Optimized autoSave with early returns"""
    # Early return check - single evaluation
    if not options:
        return

    # Check save type permissions - optimized conditions
    if prefix == "[Start]":
        if not options.isCreateStartSave():
            return
    elif prefix == "[End]":
        if not options.isCreateEndSave():
            return
    elif prefix == "[Exit]":
        if not options.isCreateExitSave():
            return
    elif prefix == "[Late]":
        if not options.isCreateLateSave():
            return

    # Get turn number if not provided
    if iTurn is None:
        iTurn = GAME.getGameTurn()

    # Determine save type - optimized with early checks
    if GAME.isGameMultiPlayer():
        if GAME.isHotSeat():
            type = "hotseat"
        elif GAME.isPbem():
            type = "pbem"
        elif GAME.isPitboss():
            type = "pitboss"
        else:
            type = "multi"
    else:
        type = "single"

    # Append auto folder
    type = type + "\\auto"

    # Call save function
    save(type, prefix, iTurn)