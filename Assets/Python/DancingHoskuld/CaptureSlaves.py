## CaptureSlaves.py - Memory-optimized version for 32-bit Caveman2Cosmos
## Optimization approach:
## - Pre-cache all string lookups and global references at module initialization
## - Use local variables to minimize repeated lookups
## - Delete unused variables immediately to free memory
## - Consolidate similar operations to reduce function calls
## - Avoid creating intermediate variables when not needed
## - Use direct method references to avoid repeated attribute lookups

from CvPythonExtensions import *
import BugUtil
import CvUtil

# Pre-cached global references (initialized once in init())
_GC = None
_GAME = None
_TRNSLTR = None
_CyInterface = None
_ColorTypes = None

# Pre-cached domain and unit type constants
_DOMAIN_LAND = -1

# Pre-cached unit types (all initialized in init() to avoid repeated string lookups)
_UNIT_CAPTIVE_NEANDERTHAL = -1
_UNIT_CAPTIVE_MILITARY = -1
_UNIT_CAPTIVE_CIVILIAN = -1
_UNIT_FREED_SLAVE = -1
_UNIT_CAPTIVE_IMMIGRANT = -1
_UNIT_STORY_TELLER = -1
_UNIT_EARLY_MERCHANT_C2C = -1
_UNIT_HEALER = -1

# Pre-cached specialist types
_SPECIALIST_SETTLED_SLAVE = -1
_SPECIALIST_SETTLED_SLAVE_FOOD = -1
_SPECIALIST_SETTLED_SLAVE_PRODUCTION = -1
_SPECIALIST_SETTLED_SLAVE_COMMERCE = -1
_SPECIALIST_SETTLED_SLAVE_HEALTH = -1
_SPECIALIST_SETTLED_SLAVE_ENTERTAINMENT = -1
_SPECIALIST_SETTLED_SLAVE_TUTOR = -1
_SPECIALIST_SETTLED_SLAVE_MILITARY = -1

# Pre-cached unitcombat type
_UNITCOMBAT_SPECIES_NEANDERTHAL = -1

# Pre-cached message strings (loaded once)
_MSG_NEANDERTHAL_CAPTIVE = None
_MSG_MILITARY_CAPTIVE = None
_MSG_CIVILIAN_CAPTIVE = None
_MSG_FREED_SLAVES_AS = None
_MSG_FREED_SLAVES_AS_IMMIGRANTS = None

# Pre-cached icon path to avoid repeated string creation
_SERFDOM_ICON = 'Art/Interface/Buttons/Civics/Serfdom.dds'
_COLOR_ID = 44

# Pre-cached method references for frequently called functions
_getPlayer = None
_getSorenRandNum = None
_sendMessage = None


def init():
    """Initialize all cached references and constants."""
    global _GC, _GAME, _TRNSLTR, _CyInterface, _ColorTypes
    global _DOMAIN_LAND
    global _UNIT_CAPTIVE_NEANDERTHAL, _UNIT_CAPTIVE_MILITARY, _UNIT_CAPTIVE_CIVILIAN
    global _UNIT_FREED_SLAVE, _UNIT_CAPTIVE_IMMIGRANT, _UNIT_STORY_TELLER
    global _UNIT_EARLY_MERCHANT_C2C, _UNIT_HEALER
    global _SPECIALIST_SETTLED_SLAVE, _SPECIALIST_SETTLED_SLAVE_FOOD
    global _SPECIALIST_SETTLED_SLAVE_PRODUCTION, _SPECIALIST_SETTLED_SLAVE_COMMERCE
    global _SPECIALIST_SETTLED_SLAVE_HEALTH, _SPECIALIST_SETTLED_SLAVE_ENTERTAINMENT
    global _SPECIALIST_SETTLED_SLAVE_TUTOR, _SPECIALIST_SETTLED_SLAVE_MILITARY
    global _UNITCOMBAT_SPECIES_NEANDERTHAL
    global _MSG_NEANDERTHAL_CAPTIVE, _MSG_MILITARY_CAPTIVE, _MSG_CIVILIAN_CAPTIVE
    global _MSG_FREED_SLAVES_AS, _MSG_FREED_SLAVES_AS_IMMIGRANTS
    global _getPlayer, _getSorenRandNum, _sendMessage

    # Cache global objects once
    _GC = CyGlobalContext()
    _GAME = _GC.getGame()
    _TRNSLTR = CyTranslator()
    _CyInterface = CyInterface()
    _ColorTypes = ColorTypes

    # Cache method references to avoid repeated attribute lookups
    _getPlayer = _GC.getPlayer
    _getSorenRandNum = _GAME.getSorenRandNum
    _sendMessage = CvUtil.sendMessage

    # Cache all string lookups once at initialization
    # This avoids repeated expensive string comparisons
    getInfoType = _GC.getInfoTypeForString

    # Domains
    _DOMAIN_LAND = getInfoType('DOMAIN_LAND')

    # Unit types - single lookup per type
    _UNIT_CAPTIVE_NEANDERTHAL = getInfoType('UNIT_CAPTIVE_NEANDERTHAL')
    _UNIT_CAPTIVE_MILITARY = getInfoType('UNIT_CAPTIVE_MILITARY')
    _UNIT_CAPTIVE_CIVILIAN = getInfoType('UNIT_CAPTIVE_CIVILIAN')
    _UNIT_FREED_SLAVE = getInfoType('UNIT_FREED_SLAVE')
    _UNIT_CAPTIVE_IMMIGRANT = getInfoType('UNIT_CAPTIVE_IMMIGRANT')
    _UNIT_STORY_TELLER = getInfoType('UNIT_STORY_TELLER')
    _UNIT_EARLY_MERCHANT_C2C = getInfoType('UNIT_EARLY_MERCHANT_C2C')
    _UNIT_HEALER = getInfoType('UNIT_HEALER')

    # Specialist types
    _SPECIALIST_SETTLED_SLAVE = getInfoType('SPECIALIST_SETTLED_SLAVE')
    _SPECIALIST_SETTLED_SLAVE_FOOD = getInfoType('SPECIALIST_SETTLED_SLAVE_FOOD')
    _SPECIALIST_SETTLED_SLAVE_PRODUCTION = getInfoType('SPECIALIST_SETTLED_SLAVE_PRODUCTION')
    _SPECIALIST_SETTLED_SLAVE_COMMERCE = getInfoType('SPECIALIST_SETTLED_SLAVE_COMMERCE')
    _SPECIALIST_SETTLED_SLAVE_HEALTH = getInfoType('SPECIALIST_SETTLED_SLAVE_HEALTH')
    _SPECIALIST_SETTLED_SLAVE_ENTERTAINMENT = getInfoType('SPECIALIST_SETTLED_SLAVE_ENTERTAINMENT')
    _SPECIALIST_SETTLED_SLAVE_TUTOR = getInfoType('SPECIALIST_SETTLED_SLAVE_TUTOR')
    _SPECIALIST_SETTLED_SLAVE_MILITARY = getInfoType('SPECIALIST_SETTLED_SLAVE_MILITARY')

    # Unit combat types
    _UNITCOMBAT_SPECIES_NEANDERTHAL = getInfoType('UNITCOMBAT_SPECIES_NEANDERTHAL')

    # Pre-cache translated messages
    getText = _TRNSLTR.getText
    _MSG_NEANDERTHAL_CAPTIVE = getText("TXT_KEY_MSG_NEANDERTHAL_CAPTIVE", ())
    _MSG_MILITARY_CAPTIVE = getText("TXT_KEY_MSG_MILITARY_CAPTIVE", ())
    _MSG_CIVILIAN_CAPTIVE = "TXT_KEY_MSG_CIVILIAN_CAPTIVE"  # Used with BugUtil.getText
    _MSG_FREED_SLAVES_AS = "TXT_KEY_MSG_FREED_SLAVES_AS"
    _MSG_FREED_SLAVES_AS_IMMIGRANTS = "TXT_KEY_MSG_FREED_SLAVES_AS_IMMIGRANTS"

    # Clear the local reference to free memory
    del getInfoType
    del getText


def onCombatResult(argsList):
    """Handle combat results and potential captive capture."""
    CyUnitW, CyUnitL = argsList

    # Early exit conditions combined in single check
    if (not CyUnitW.isMadeAttack() or CyUnitL.isAnimal() or
            CyUnitL.getDomainType() != _DOMAIN_LAND or
            CyUnitW.getDomainType() != _DOMAIN_LAND or
            CyUnitL.getCaptureUnitType() != -1):
        return

    # Calculate capture chance
    iChance = CyUnitW.captureProbabilityTotal() - CyUnitL.captureResistanceTotal()

    BugUtil.info("CaptureSlaves: Chance to capture a captive is %d (%d - %d)",
                 iChance, CyUnitW.captureProbabilityTotal(), CyUnitL.captureResistanceTotal())

    if iChance <= _getSorenRandNum(100, "Slave"):  # 0-99
        return

    # Determine unit type and message
    if CyUnitL.isHasUnitCombat(_UNITCOMBAT_SPECIES_NEANDERTHAL):
        iUnit = _UNIT_CAPTIVE_NEANDERTHAL
        sMessage = _MSG_NEANDERTHAL_CAPTIVE
    else:
        iUnit = _UNIT_CAPTIVE_MILITARY
        sMessage = _MSG_MILITARY_CAPTIVE

    # Create the captive unit
    iPlayerW = CyUnitW.getOwner()
    X = CyUnitW.getX()
    Y = CyUnitW.getY()

    CyPlayer = _getPlayer(iPlayerW)
    CyUnit = CyPlayer.initUnit(iUnit, X, Y, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)

    if CyUnitW.isHiddenNationality():
        CyUnit.doHNCapture()

    if iPlayerW == _GAME.getActivePlayer():
        _sendMessage(sMessage, iPlayerW, 8, _SERFDOM_ICON, _ColorTypes(_COLOR_ID), X, Y, True, True)


def onCityRazed(argsList):
    """Handle city razing and slave/captive generation."""
    CyCity, iPlayer = argsList
    if not CyCity:
        return

    # Cache frequently used values as locals for faster access
    CyPlayer = _getPlayer(iPlayer)
    bHuman = CyPlayer.isHuman()
    sCityName = CyCity.getName()
    X = CyCity.getX()
    Y = CyCity.getY()

    # Cache method references for repeated calls
    getFreeSpecialistCount = CyCity.getFreeSpecialistCount
    changeFreeSpecialistCount = CyCity.changeFreeSpecialistCount
    initUnit = CyPlayer.initUnit
    addMessage = _CyInterface.addMessage
    getText = BugUtil.getText

    # Get all specialist counts at once to minimize function calls
    iCountSettled = getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE)
    iCountFood = getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_FOOD)
    iCountProd = getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_PRODUCTION)
    iCountCom = getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_COMMERCE)
    iCountHealth = getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_HEALTH)
    iCountEntertain = getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_ENTERTAINMENT)
    iCountTutor = getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_TUTOR)
    iCountMilitary = getFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_MILITARY)

    # Process slaves that can become population or immigrants
    # Calculate once and reuse
    iCount = iCountSettled + iCountFood + iCountCom + iCountTutor + iCountMilitary
    iCountNewPop = iCount / 3  # Integer division in Python 2
    iCount = iCount - 3 * iCountNewPop

    # Process freed slaves
    if iCount > 0:
        for i in xrange(iCount):
            initUnit(_UNIT_FREED_SLAVE, X, Y, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)

        if bHuman:
            sMessage = getText(_MSG_FREED_SLAVES_AS,
                               (sCityName, _GC.getUnitInfo(_UNIT_FREED_SLAVE).getDescription(), iCount))
            addMessage(iPlayer, False, 15, sMessage, '', 0, _SERFDOM_ICON, _ColorTypes(_COLOR_ID), X, Y, True, True)

    # Process immigrants
    if iCountNewPop > 0:
        for i in xrange(iCountNewPop):
            initUnit(_UNIT_CAPTIVE_IMMIGRANT, X, Y, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)

        if bHuman:
            sMessage = getText(_MSG_FREED_SLAVES_AS_IMMIGRANTS, (iCountNewPop * 3, sCityName, iCountNewPop))
            addMessage(iPlayer, False, 15, sMessage, '', 0, _SERFDOM_ICON, _ColorTypes(_COLOR_ID), X, Y, True, True)

    # Remove slaves efficiently - combine operations where possible
    if iCountSettled > 0:
        changeFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE, -iCountSettled)
    if iCountFood > 0:
        changeFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_FOOD, -iCountFood)
    if iCountCom > 0:
        changeFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_COMMERCE, -iCountCom)
    if iCountTutor > 0:
        changeFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_TUTOR, -iCountTutor)
    if iCountMilitary > 0:
        changeFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_MILITARY, -iCountMilitary)

    # Convert production slaves to merchants
    if iCountProd > 0:
        for i in xrange(iCountProd):
            initUnit(_UNIT_EARLY_MERCHANT_C2C, X, Y, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
        changeFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_PRODUCTION, -iCountProd)

        if bHuman:
            sMessage = getText(_MSG_FREED_SLAVES_AS,
                               (sCityName, _GC.getUnitInfo(_UNIT_EARLY_MERCHANT_C2C).getDescription(), iCountProd))
            addMessage(iPlayer, False, 15, sMessage, '', 0, _SERFDOM_ICON, _ColorTypes(_COLOR_ID), X, Y, True, True)

    # Convert health slaves to healers
    if iCountHealth > 0:
        for i in xrange(iCountHealth):
            initUnit(_UNIT_HEALER, X, Y, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
        changeFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_HEALTH, -iCountHealth)

        if bHuman:
            sMessage = getText(_MSG_FREED_SLAVES_AS,
                               (sCityName, _GC.getUnitInfo(_UNIT_HEALER).getDescription(), iCountHealth))
            addMessage(iPlayer, False, 15, sMessage, '', 0, _SERFDOM_ICON, _ColorTypes(_COLOR_ID), X, Y, True, True)

    # Convert entertainment slaves to story tellers
    if iCountEntertain > 0:
        for i in xrange(iCountEntertain):
            initUnit(_UNIT_STORY_TELLER, X, Y, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
        changeFreeSpecialistCount(_SPECIALIST_SETTLED_SLAVE_ENTERTAINMENT, -iCountEntertain)

        if bHuman:
            sMessage = getText(_MSG_FREED_SLAVES_AS,
                               (sCityName, _GC.getUnitInfo(_UNIT_STORY_TELLER).getDescription(), iCountEntertain))
            addMessage(iPlayer, False, 15, sMessage, '', 0, _SERFDOM_ICON, _ColorTypes(_COLOR_ID), X, Y, True, True)

    # Convert population to captives
    iCount = 0
    iPop = CyCity.getPopulation()

    if iPop == 1:
        if _getSorenRandNum(100, "Slave") < 66:
            initUnit(_UNIT_CAPTIVE_CIVILIAN, X, Y, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
            iCount = 1
    else:
        iCivilianCitizenUnits = (iPop + 1) / 2  # Integer division in Python 2
        for loop in xrange(iCivilianCitizenUnits):
            initUnit(_UNIT_CAPTIVE_CIVILIAN, X, Y, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
        iCount = iCivilianCitizenUnits

    if bHuman and iCount:
        sMessage = getText(_MSG_CIVILIAN_CAPTIVE, iCount)
        addMessage(iPlayer, False, 15, sMessage, '', 0, _SERFDOM_ICON, _ColorTypes(_COLOR_ID), X, Y, True, True)

    # Clear local references to allow garbage collection
    del CyCity, CyPlayer