# DynamicCivNames
#
# by jdog5000
# Version 1.0 - Memory Optimized
#
# French compatibility from calvitix
#

from CvPythonExtensions import *
from CvEventInterface import getEventManager
import TextUtil
# --------- Revolution mod -------------
import SdToolKit as SDTK
import RevUtils

# Cache global references once
GC = CyGlobalContext()
GAME = GC.getGame()
TRNSLTR = CyTranslator()

# Module state
bEnabled = False
femaleLeaders = None  # Will be initialized as tuple
_cached_strings = {}  # Cache for frequently used strings
_info_type_cache = {}  # Cache for getInfoTypeForString calls


def _get_info_type(key):
    """Cached version of getInfoTypeForString to reduce repeated lookups"""
    if key not in _info_type_cache:
        _info_type_cache[key] = GC.getInfoTypeForString(key)
    return _info_type_cache[key]


def _get_cached_text(key, default_args=()):
    """Cache frequently used translation texts"""
    cache_key = (key, default_args)
    if cache_key not in _cached_strings:
        _cached_strings[cache_key] = TRNSLTR.getText(key, default_args)
    return _cached_strings[cache_key]


def init():
    global bEnabled, femaleLeaders
    if bEnabled:
        return

    EM = getEventManager()
    # Register event handlers
    EM.addEventHandler("BeginPlayerTurn", onBeginPlayerTurn)
    EM.addEventHandler("setPlayerAlive", onSetPlayerAlive)
    EM.addEventHandler("cityAcquiredAndKept", onCityAcquiredAndKept)
    EM.addEventHandler("cityBuilt", onCityBuilt)
    EM.addEventHandler("vassalState", onVassalState)
    EM.addEventHandler("addTeam", onAddTeam)

    # Use tuple instead of list for immutable data - saves memory
    femaleLeaders = (
        _get_info_type("LEADER_BOUDICA"),
        _get_info_type("LEADER_ELIZABETH"),
        _get_info_type("LEADER_HATSHEPSUT"),
        _get_info_type("LEADER_VICTORIA"),
        _get_info_type("LEADER_ATOTOZTLI"),
        _get_info_type("LEADER_CLEOPATRA"),
        _get_info_type("LEADER_DIDO"),
        _get_info_type("LEADER_JOANOFARC"),
        _get_info_type("LEADER_NEFERTITI"),
        _get_info_type("LEADER_THEODORA"),
        _get_info_type("LEADER_WU")
    )

    # Initialize players if needed
    if not GAME.isFinalInitialized or GAME.getGameTurn() == GAME.getStartTurn():
        max_players = GC.getMAX_PC_PLAYERS()
        for i in xrange(max_players):
            player = GC.getPlayer(i)
            if player.isAlive():
                onSetPlayerAlive([i, True])

    bEnabled = True


def uninit():
    global bEnabled, _cached_strings, _info_type_cache
    if not bEnabled:
        return

    EM = getEventManager()
    # Unregister event handlers
    EM.removeEventHandler("BeginPlayerTurn", onBeginPlayerTurn)
    EM.removeEventHandler("setPlayerAlive", onSetPlayerAlive)
    EM.removeEventHandler("cityAcquiredAndKept", onCityAcquiredAndKept)
    EM.removeEventHandler("cityBuilt", onCityBuilt)
    EM.removeEventHandler("vassalState", onVassalState)
    EM.removeEventHandler("addTeam", onAddTeam)

    # Reset all player names
    max_players = GC.getMAX_PC_PLAYERS()
    for i in xrange(max_players):
        if GC.getPlayer(i).isAlive():
            resetName(i)

    # Clear caches
    _cached_strings.clear()
    _info_type_cache.clear()

    bEnabled = False


def blankHandler(playerID, netUserData, popupReturn):
    """Dummy handler to take the second event for popup"""
    return


def onBeginPlayerTurn(argsList):
    iPlayer = argsList[1]

    # Find previous living player
    iPrevPlayer = iPlayer - 1
    while iPrevPlayer >= 0:
        if GC.getPlayer(iPrevPlayer).isAlive():
            break
        iPrevPlayer -= 1

    if iPrevPlayer < 0:
        iPrevPlayer = GC.getBARBARIAN_PLAYER()

    if not (0 <= iPrevPlayer < GC.getMAX_PC_PLAYERS()):
        return

    pPlayer = GC.getPlayer(iPrevPlayer)
    if not pPlayer.isAlive():
        return

    # Check for anarchy
    if pPlayer.isAnarchy():
        setNewNameByCivics(iPrevPlayer)
        return

    # Check for civic changes
    if SDTK.sdObjectExists("Revolution", pPlayer):
        prevCivics = SDTK.sdObjectGetVal("Revolution", pPlayer, 'CivicList')
        if prevCivics is not None:
            num_civics = GC.getNumCivicOptionInfos()
            for i in xrange(num_civics):
                if prevCivics[i] != pPlayer.getCivics(i):
                    setNewNameByCivics(iPrevPlayer)
                    return

        # Check revolution graduation
        revTurn = SDTK.sdObjectGetVal("Revolution", pPlayer, 'RevolutionTurn')
        if revTurn is not None:
            if GAME.getGameTurn() - revTurn == 30 and pPlayer.getNumCities() > 0:
                setNewNameByCivics(iPrevPlayer)
                return

    # Check barbarian civ graduation
    if SDTK.sdObjectExists("BarbarianCiv", pPlayer):
        barbTurn = SDTK.sdObjectGetVal("BarbarianCiv", pPlayer, 'SpawnTurn')
        if barbTurn is not None and GAME.getGameTurn() - barbTurn == 30:
            setNewNameByCivics(iPrevPlayer)
            return

    # Check tribe graduation
    if (not SDTK.sdObjectExists("BarbarianCiv", pPlayer) and
            'Tribe' in pPlayer.getCivilizationDescription(0) and
            (pPlayer.getCurrentEra() > 0 or pPlayer.getTotalPopulation() >= 3)):
        setNewNameByCivics(iPrevPlayer)


def onCityAcquiredAndKept(argsList):
    iPlayer = argsList[1]
    owner = GC.getPlayer(iPlayer)
    if (owner.isAlive() and not owner.isNPC() and
            owner.getNumCities() < 5 and owner.getNumMilitaryUnits() > 0):
        setNewNameByCivics(iPlayer)


def onCityBuilt(argsList):
    owner = GC.getPlayer(argsList[0].getOwner())
    if (owner.isAlive() and not owner.isNPC() and
            owner.getNumCities() < 5 and owner.getNumMilitaryUnits() > 0):
        setNewNameByCivics(owner.getID())


def onVassalState(argsList):
    iVassal = argsList[1]
    max_players = GC.getMAX_PC_PLAYERS()
    for iPlayer in xrange(max_players):
        if GC.getPlayer(iPlayer).getTeam() == iVassal:
            setNewNameByCivics(iPlayer)


def setNewNameByCivics(iPlayer):
    newCivDesc, newCivShort, newCivAdj = newNameByCivics(iPlayer)

    pPlayer = GC.getPlayer(iPlayer)
    if newCivDesc != pPlayer.getCivilizationDescription(0):
        szMessage = TRNSLTR.getText("TXT_KEY_MOD_DCN_NEWCIV_NAME_DESC", (newCivDesc,))
        CyInterface().addMessage(iPlayer, False, GC.getEVENT_MESSAGE_TIME(),
                                 szMessage, None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, None,
                                 _get_info_type("COLOR_HIGHLIGHT_TEXT"), -1, -1, False, False)

    pPlayer.setCivName(newCivDesc, newCivShort, newCivAdj)


def onSetPlayerAlive(argsList):
    iPlayerID = argsList[0]
    bNewValue = argsList[1]

    if bNewValue and iPlayerID < GC.getMAX_PC_PLAYERS():
        pPlayer = GC.getPlayer(iPlayerID)
        newCivDesc, newCivShort, newCivAdj = nameForNewPlayer(iPlayerID)
        pPlayer.setCivName(newCivDesc, newCivShort, newCivAdj)


def onAddTeam(argsList):
    eTeam1 = argsList[0]
    eTeam2 = argsList[1]
    max_players = GC.getMAX_PC_PLAYERS()

    for i in xrange(max_players):
        pPlayer = GC.getPlayer(i)
        if pPlayer.isAlive():
            team = pPlayer.getTeam()
            if team == eTeam1 or team == eTeam2:
                setNewNameByCivics(i)


def nameForNewPlayer(iPlayer):
    """Assigns a new name to a recently created player"""
    pPlayer = GC.getPlayer(iPlayer)
    curShort = pPlayer.getCivilizationShortDescription(0)
    curDesc = pPlayer.getCivilizationDescription(0)
    curAdj = pPlayer.getCivilizationAdjective(0)

    if not pPlayer.isAlive():
        return [_get_cached_text("TXT_KEY_MOD_DCN_REFUGEES", ()) % curAdj, curShort, curAdj]

    # Find current era
    currentEra = 0
    max_players = GC.getMAX_PC_PLAYERS()
    for i in xrange(max_players):
        era = GC.getPlayer(i).getCurrentEra()
        if era > currentEra:
            currentEra = era

    if pPlayer.isRebel():
        # Cache these strings
        sLiberation = _get_cached_text("TXT_KEY_MOD_DCN_LIBERATION_FRONT", ()).replace('%s', '').strip()
        sGuerillas = _get_cached_text("TXT_KEY_MOD_DCN_GUERILLAS", ()).replace('%s', '').strip()
        sRebels = _get_cached_text("TXT_KEY_MOD_DCN_REBELS", ()).replace('%s', '').strip()

        # Check if already has rebel name
        if sLiberation in curDesc or sGuerillas in curDesc or sRebels in curDesc:
            newName = curDesc
        elif currentEra > 5 and GAME.getSorenRandNum(100, 'Rev: Naming') < 30:
            newName = _get_cached_text("TXT_KEY_MOD_DCN_LIBERATION_FRONT", ()) % curAdj
        elif currentEra > 4 and GAME.getSorenRandNum(100, 'Rev: Naming') < 30:
            newName = _get_cached_text("TXT_KEY_MOD_DCN_GUERILLAS", ()) % curAdj
        else:
            cityString = SDTK.sdObjectGetVal("Revolution", pPlayer, 'CapitalName')

            if cityString is not None and len(cityString) < 10:
                try:
                    if cityString in curAdj or cityString in curShort:
                        newName = _get_cached_text("TXT_KEY_MOD_DCN_THE_REBELS_OF", ()) % TextUtil.convertToStr(
                            cityString)
                    else:
                        newName = _get_cached_text("TXT_KEY_MOD_DCN_REBELS_OF", ()) % (curAdj, TextUtil.convertToStr(
                            cityString))
                except:
                    newName = _get_cached_text("TXT_KEY_MOD_DCN_REBELS", ()) % curAdj
            else:
                newName = _get_cached_text("TXT_KEY_MOD_DCN_REBELS", ()) % curAdj

        return [newName, curShort, curAdj]

    # Check for barbarian civ
    barbTurn = None
    if SDTK.sdObjectExists("BarbarianCiv", pPlayer):
        barbTurn = SDTK.sdObjectGetVal("BarbarianCiv", pPlayer, 'SpawnTurn')

    if barbTurn is not None and GAME.getGameTurn() - barbTurn < 20:
        numCities = SDTK.sdObjectGetVal("BarbarianCiv", pPlayer, 'NumCities')
        cityString = SDTK.sdObjectGetVal("BarbarianCiv", pPlayer, 'CapitalName')

        if pPlayer.isMinorCiv():
            if currentEra > 2:
                newName = _get_cached_text("TXT_KEY_MOD_DCN_NATION", ()) % curAdj
            elif currentEra == 2:
                newName = _get_cached_text("TXT_KEY_MOD_DCN_CITY_STATE", ()) % curAdj
            elif GAME.getSorenRandNum(100, "Naming") < (70 - 40 * currentEra):
                newName = _get_cached_text("TXT_KEY_MOD_DCN_TRIBE", ()) % curAdj
            else:
                newName = _get_cached_text("TXT_KEY_MOD_DCN_CITY_STATE", ()) % curAdj

        elif currentEra < 4:
            if SDTK.sdObjectGetVal('BarbarianCiv', pPlayer, 'BarbStyle') != 'Military':
                if numCities == 1:
                    newName = _get_cached_text("TXT_KEY_MOD_DCN_CITY_STATE", ()) % curAdj
                else:
                    newName = _get_cached_text("TXT_KEY_MOD_DCN_EMPIRE", ()) % curAdj

                if numCities < 3 and cityString is not None and len(cityString) < 10:
                    newName += _get_cached_text("TXT_KEY_MOD_DCN_OF_CITY", ()) % cityString

            elif pPlayer.getNumMilitaryUnits() > 7 * numCities:
                newName = _get_cached_text("TXT_KEY_MOD_DCN_HORDE", ()) % curAdj
            elif cityString is None or len(cityString) > 9:
                newName = _get_cached_text("TXT_KEY_MOD_DCN_WARRIOR_STATE", ()) % curAdj
            elif cityString in curAdj or cityString in curShort:
                newName = _get_cached_text("TXT_KEY_MOD_DCN_THE_WARRIORS_OF", ()) % cityString
            else:
                newName = _get_cached_text("TXT_KEY_MOD_DCN_WARRIORS_OF", ()) % (curAdj, cityString)
        else:
            newName = _get_cached_text("TXT_KEY_MOD_DCN_EMPIRE", ()) % curAdj
            if numCities < 3 and cityString is not None and len(cityString) < 10:
                newName += _get_cached_text("TXT_KEY_MOD_DCN_OF_CITY", ()) % cityString

        return [newName, curShort, curAdj]

    # Early game naming
    if GAME.getGameTurn() == GAME.getStartTurn() and GAME.getCurrentEra() < 1:
        return [_get_cached_text("TXT_KEY_MOD_DCN_TRIBE", ()) % curAdj, curShort, curAdj]

    return newNameByCivics(iPlayer)


def newNameByCivics(iPlayer):
    """Assigns a new name to a player based on their civics choices"""
    pPlayer = GC.getPlayer(iPlayer)
    capital = pPlayer.getCapitalCity()
    pTeam = GC.getTeam(pPlayer.getTeam())

    # Get city string if capital exists
    cityString = None
    if capital:
        try:
            # Optimize string operations
            cityString = pPlayer.getCivilizationDescription(0)
            cityString += "&" + TextUtil.convertToStr(capital.getName())
            cityString = cityString.split('&', 1)[-1]
        except:
            pass

    curDesc = pPlayer.getCivilizationDescription(0)
    curShort = pPlayer.getCivilizationShortDescription(0)
    curAdj = pPlayer.getCivilizationAdjective(0)

    # Get original description
    origDesc = ""
    civType = pPlayer.getCivilizationType()
    if civType >= 0:
        origDesc = GC.getCivilizationInfo(civType).getDescription()

    # Language check
    bFrench = GAME.getCurrentLanguage() == 1

    # Cache civic lookups
    eGovCivic = pPlayer.getCivics(_get_info_type("CIVICOPTION_GOVERNMENT"))
    ePowerCivic = pPlayer.getCivics(_get_info_type("CIVICOPTION_POWER"))

    # Pre-calculate frequently used civic types
    monarchy_type = _get_info_type("CIVIC_MONARCHY")
    despotism_type = _get_info_type("CIVIC_DESPOTISM")
    totalitarian_type = _get_info_type("CIVIC_TOTALITARIANISM")
    federalism_type = _get_info_type("CIVIC_FEDERALISM")
    legislature_type = _get_info_type("CIVIC_LEGISLATURE")

    bNoRealElections = (eGovCivic == monarchy_type or
                        eGovCivic == despotism_type or
                        eGovCivic == totalitarian_type)

    bFederal = (eGovCivic == federalism_type and ePowerCivic == legislature_type)
    bConfederation = (not bFederal and eGovCivic == federalism_type)

    bPacifist = (pPlayer.getCivics(_get_info_type("CIVICOPTION_MILITARY")) ==
                 _get_info_type("CIVIC_PACIFISM"))

    newName = curDesc

    # Check barbarian turn
    barbTurn = None
    if SDTK.sdObjectExists("BarbarianCiv", pPlayer):
        barbTurn = SDTK.sdObjectGetVal("BarbarianCiv", pPlayer, 'SpawnTurn')

    # Early returns for special cases
    if not pPlayer.isAlive():
        return [_get_cached_text("TXT_KEY_MOD_DCN_REFUGEES", ()) % curAdj, curShort, curAdj]

    if pPlayer.isRebel():
        return [curDesc, curShort, curAdj]

    if pPlayer.isMinorCiv() and barbTurn is not None:
        return [curDesc, curShort, curAdj]

    if barbTurn is not None and GAME.getGameTurn() - barbTurn < 20 and pPlayer.getNumCities() < 4:
        return [curDesc, curShort, curAdj]

    # Team naming
    numMembers = pTeam.getNumMembers()
    if numMembers > 1:
        iLeader = pTeam.getLeaderID()

        if numMembers == 2:
            newName = GC.getPlayer(iLeader).getCivilizationAdjective(0) + "-"
            max_players = GC.getMAX_PC_PLAYERS()
            for idx in xrange(max_players):
                if idx != iLeader and GC.getPlayer(idx).getTeam() == pTeam.getID():
                    newName += GC.getPlayer(idx).getCivilizationAdjective(0)
                    break
            newName += _get_cached_text("TXT_KEY_MOD_DCN_ALLIANCE", ())
        else:
            newName = GC.getPlayer(iLeader).getCivilizationAdjective(0)[0:4]
            max_players = GC.getMAX_PC_PLAYERS()
            for idx in xrange(max_players):
                if idx != iLeader and GC.getPlayer(idx).getTeam() == pTeam.getID():
                    newName += GC.getPlayer(idx).getCivilizationAdjective(0)[0:3]
            newName += _get_cached_text("TXT_KEY_MOD_DCN_ALLIANCE", ())

        return [newName, curShort, curAdj]

    # Cache frequently used text keys
    sSocRep = _get_cached_text("TXT_KEY_MOD_DCN_SOC_REP", ()).replace('%s', '').strip()
    sPeoplesRep = _get_cached_text("TXT_KEY_MOD_DCN_PEOPLES_REP", ()).replace('%s', '').strip()

    # Anarchy naming
    if pPlayer.isAnarchy and pPlayer.getAnarchyTurns() > 1:
        if (iPlayer + pPlayer.getNumCities()) % 2 == 1:
            newName = _get_cached_text("TXT_KEY_MOD_DCN_PROVISIONAL_GOV", ()) % curAdj
        else:
            newName = _get_cached_text("TXT_KEY_MOD_DCN_PROVISIONAL_AUTH", ()) % curAdj
        return [newName, curShort, curAdj]

    # Post-anarchy naming
    if (not pPlayer.isAnarchy or pPlayer.getAnarchyTurns() < 2) and "Provisional" in curDesc:
        if eGovCivic == monarchy_type:
            newName = curAdj + ' ' + _get_cached_text("TXT_KEY_MOD_DCN_KINGDOM", ())
        elif eGovCivic == _get_info_type("CIVIC_REPUBLIC"):
            newName = _get_cached_text("TXT_KEY_MOD_DCN_REPUBLIC", ()) % curAdj
        else:
            newName = curAdj + ' Nation'
        return [newName, curShort, curAdj]

    # Main naming logic
    if isCommunism(pPlayer):
        if RevUtils.isCanDoElections(pPlayer) and not bNoRealElections:
            if sSocRep in curDesc or sPeoplesRep in curDesc:
                newName = curDesc
            elif GAME.getSorenRandNum(100, 'Rev: Naming') < 50:
                newName = _get_cached_text("TXT_KEY_MOD_DCN_SOC_REP", ()) % curShort
            else:
                newName = _get_cached_text("TXT_KEY_MOD_DCN_PEOPLES_REP", ()) % curShort
        elif RevUtils.getDemocracyLevel(pPlayer)[0] == -8:
            if _get_cached_text("TXT_KEY_MOD_DCN_RUSSIAN_MATCH", ()) in curAdj:
                curAdj = _get_cached_text("TXT_KEY_MOD_DCN_SOVIET", ())
            newName = _get_cached_text("TXT_KEY_MOD_DCN_UNION", ()) % curAdj
        else:
            newName = _get_cached_text("TXT_KEY_MOD_DCN_PEOPLES_REP", ()) % curShort

    elif RevUtils.isCanDoElections(pPlayer) and not bNoRealElections:
        # Process democratic names
        newName = _processRepublicName(pPlayer, curDesc, curShort, curAdj,
                                       cityString, bFederal, bConfederation)

    elif RevUtils.getDemocracyLevel(pPlayer)[0] == -8:
        # Process empire names
        newName = _processEmpireName(curDesc, curShort, curAdj, bFrench)

    else:
        # Process kingdom names
        newName = _processKingdomName(pPlayer, pTeam, curDesc, curShort, curAdj,
                                      cityString, bFrench)

    # Add pacifist modifier if needed
    if bPacifist:
        szPacifist = _get_cached_text("TXT_KEY_MOD_DCN_PACIFIST", ())
        if szPacifist not in newName and GAME.getSorenRandNum(100, 'Rev: Naming') < 50:
            szPacifist = _get_cached_text("TXT_KEY_MOD_DCN_PEACEFUL", ())

        if szPacifist not in newName:
            if bFrench:
                newName = newName + ' ' + szPacifist
            else:
                newName = szPacifist + ' ' + newName

    return [newName, curShort, curAdj]


def _processRepublicName(pPlayer, curDesc, curShort, curAdj, cityString, bFederal, bConfederation):
    """Process republic-style names"""
    sRepOf = _get_cached_text("TXT_KEY_MOD_DCN_REPUBLIC_OF", ()).replace('%s', '').strip()
    sRepublic = _get_cached_text("TXT_KEY_MOD_DCN_REPUBLIC", ())

    numCities = pPlayer.getNumCities()

    if numCities == 1:
        free_text = _get_cached_text("TXT_KEY_MOD_DCN_FREE", ())
        if (curDesc.startswith(free_text) or
                ((sRepOf in curDesc or sRepublic in curDesc) and cityString in curDesc)):
            return curDesc

        rand_val = GAME.getSorenRandNum(100, 'Rev: Naming')
        if rand_val < 40:
            return _get_cached_text("TXT_KEY_MOD_DCN_FREE_STATE", ()) % curAdj
        elif cityString is None or not cityString or len(cityString) > 9:
            return _get_cached_text("TXT_KEY_MOD_DCN_FREE_REPUBLIC", ()) % curAdj
        elif cityString in curAdj or cityString in curShort:
            return _get_cached_text("TXT_KEY_MOD_DCN_THE_REPUBLIC_OF_CITY", ()) % cityString
        else:
            return _get_cached_text("TXT_KEY_MOD_DCN_REPUBLIC_OF_CITY", ()) % (curAdj, cityString)

    # Multiple cities
    free_text = _get_cached_text("TXT_KEY_MOD_DCN_FREE", ())
    new_text = _get_cached_text("TXT_KEY_MOD_DCN_NEW", ())

    if (not bFederal and not bConfederation and sRepublic in curDesc and
            sPeoplesRep not in curDesc and sSocRep not in curDesc and
            curDesc.startswith(free_text)):
        if len(curDesc) < 17 and GAME.getSorenRandNum(100, 'Rev: Naming') < 20 and new_text not in curDesc:
            return new_text + curDesc
        else:
            return curDesc

    if bFederal:
        if pPlayer.getCivilizationType() == _get_info_type("CIVILIZATION_AMERICA"):
            return _get_cached_text("TXT_KEY_MOD_DCN_UNITED_STATES", ()) % curShort
        elif GAME.getSorenRandNum(100, 'Rev: Naming') < 50:
            return _get_cached_text("TXT_KEY_MOD_DCN_FEDERATED_STATES", ()) % curShort
        else:
            return _get_cached_text("TXT_KEY_MOD_DCN_FEDERATION", ()) % curAdj

    if bConfederation:
        if GAME.getSorenRandNum(100, 'Rev: Naming') < 50:
            return _get_cached_text("TXT_KEY_MOD_DCN_CONFEDERATION", ()) % curAdj
        else:
            return _get_cached_text("TXT_KEY_MOD_DCN_CONFEDERATION_STATES", ()) % curShort

    # Standard republic
    rand_val = GAME.getSorenRandNum(100, 'Rev: Naming')
    if rand_val < 50:
        newName = _get_cached_text("TXT_KEY_MOD_DCN_REPUBLIC", ()) % curAdj
    elif rand_val < 67:
        newName = _get_cached_text("TXT_KEY_MOD_DCN_THE_COMMONWEALTH_OF", ()) % curShort
    else:
        newName = _get_cached_text("TXT_KEY_MOD_DCN_THE_REPUBLIC_OF", ()) % curShort

    # Add "Free" prefix if appropriate
    if (RevUtils.isFreeSpeech(pPlayer) and RevUtils.getLaborFreedom(pPlayer)[0] > 9 and
            len(newName) < 16 and free_text not in newName and new_text not in newName):
        newName = free_text + ' ' + newName

    return newName


def _processEmpireName(curDesc, curShort, curAdj, bFrench):
    """Process empire-style names"""
    if _get_cached_text("TXT_KEY_MOD_DCN_GERMAN_MATCH", ()) in curAdj:
        empString = _get_cached_text("TXT_KEY_MOD_DCN_REICH", ())
    else:
        empString = _get_cached_text("TXT_KEY_MOD_DCN_PLAIN_EMPIRE", ())

    if empString in curDesc:
        return curDesc

    reich_text = _get_cached_text("TXT_KEY_MOD_DCN_REICH", ())
    if GAME.getSorenRandNum(100, 'Rev: Naming') < 70 and reich_text not in empString:
        return _get_cached_text("TXT_KEY_MOD_DCN_THE_BLANK_OF", ()) % (empString, curShort)
    elif bFrench:
        return empString + ' ' + curAdj
    else:
        return curAdj + ' ' + empString


def _processKingdomName(pPlayer, pTeam, curDesc, curShort, curAdj, cityString, bFrench):
    """Process kingdom-style names"""
    sGreat = _get_cached_text("TXT_KEY_MOD_DCN_GREAT_KINGDOM", ()).replace('%s', '').strip()

    numCities = pPlayer.getNumCities()

    # Determine kingdom type
    if numCities < 3:
        sKingdom = _get_cached_text("TXT_KEY_MOD_DCN_PRINCIPALITY", ())
    elif pPlayer.getLeaderType() in femaleLeaders:
        sKingdom = _get_cached_text("TXT_KEY_MOD_DCN_QUEENDOM", ())
    else:
        sKingdom = _get_cached_text("TXT_KEY_MOD_DCN_KINGDOM", ())

    playerEra = pPlayer.getCurrentEra()

    if RevUtils.getDemocracyLevel(pPlayer)[0] == -6:
        if pTeam.isAVassal():
            sKingdom = _get_cached_text("TXT_KEY_MOD_DCN_DUCHY", ())
        else:
            # Check for specific civilizations
            persian = _get_cached_text("TXT_KEY_MOD_DCN_PERSIAN_MATCH", ())
            ottoman = _get_cached_text("TXT_KEY_MOD_DCN_OTTOMAN_MATCH", ())
            sumerian = _get_cached_text("TXT_KEY_MOD_DCN_SUMERIAN_MATCH", ())
            arabian = _get_cached_text("TXT_KEY_MOD_DCN_ARABIAN_MATCH", ())

            if persian in curAdj or ottoman in curAdj or sumerian in curAdj:
                sKingdom = _get_cached_text("TXT_KEY_MOD_DCN_SULTANATE", ())
            elif arabian in curAdj:
                sKingdom = _get_cached_text("TXT_KEY_MOD_DCN_CALIPHATE", ())

        if numCities < 4:
            if cityString is not None and 0 < len(cityString) < 10:
                if cityString in curAdj or cityString in curShort:
                    return _get_cached_text("TXT_KEY_MOD_DCN_THE_BLANK_OF_CITY", ()) % (sKingdom, cityString)
                elif bFrench:
                    return _get_cached_text("TXT_KEY_MOD_DCN_BLANK_OF_CITY", ()) % (sKingdom, curAdj, cityString)
                else:
                    return _get_cached_text("TXT_KEY_MOD_DCN_BLANK_OF_CITY", ()) % (curAdj, sKingdom, cityString)
            elif bFrench:
                return sKingdom + ' ' + curAdj
            else:
                return curAdj + ' ' + sKingdom

        # Check for great kingdom
        playerRank = GAME.getPlayerRank(pPlayer.getID())
        totalPlayers = GAME.countCivPlayersAlive()

        if playerRank < totalPlayers / 7 and not pTeam.isAVassal():
            if sGreat in curDesc or GAME.getSorenRandNum(100, 'Rev: Naming') < 40:
                if bFrench:
                    return _get_cached_text("TXT_KEY_MOD_DCN_GREAT_KINGDOM", ()) % (sKingdom, curAdj)
                else:
                    return _get_cached_text("TXT_KEY_MOD_DCN_GREAT_KINGDOM", ()) % (curAdj, sKingdom)

        # Standard kingdom
        sOf = _get_cached_text("TXT_KEY_MOD_DCN_THE_BLANK_OF", ()).replace('%s', '')
        if sKingdom in curDesc and (sOf not in curDesc or numCities < 6) and sGreat not in curDesc:
            return curDesc
        elif GAME.getSorenRandNum(100, 'Rev: Naming') >= 50:
            return _get_cached_text("TXT_KEY_MOD_DCN_THE_BLANK_OF", ()) % (sKingdom, curShort)
        elif bFrench:
            return sKingdom + ' ' + curAdj
        else:
            return curAdj + ' ' + sKingdom

    elif RevUtils.getDemocracyLevel(pPlayer)[0] == -10 or playerEra == 0:
        # Very early or despotic
        empString = _get_cached_text("TXT_KEY_MOD_DCN_PLAIN_EMPIRE", ())
        if playerEra < 2 and numCities < 3:
            empString = _get_cached_text("TXT_KEY_MOD_DCN_PLAIN_CITY_STATE", ())

        if pTeam.isAVassal():
            rand_val = GAME.getSorenRandNum(100, 'Rev: Naming')
            if rand_val < 50:
                empString = _get_cached_text("TXT_KEY_MOD_DCN_FIEFDOM", ())
            elif rand_val < 75:
                empString = _get_cached_text("TXT_KEY_MOD_DCN_PROTECTORATE", ())
            else:
                empString = _get_cached_text("TXT_KEY_MOD_DCN_TERRITORY", ())

        if empString in curDesc and GAME.getGameTurn() != 0:
            return curDesc
        elif GAME.getSorenRandNum(100, 'Rev: Naming') >= 50:
            return _get_cached_text("TXT_KEY_MOD_DCN_THE_BLANK_OF", ()) % (empString, curShort)
        elif bFrench:
            return empString + ' ' + curAdj
        else:
            return curAdj + ' ' + empString

    # Add holy modifier if needed
    sHoly = _get_cached_text("TXT_KEY_MOD_DCN_HOLY", ()) + ' '
    holy_hre = _get_cached_text("TXT_KEY_MOD_DCN_HOLY_HRE_MATCH", ())

    if RevUtils.getReligiousFreedom(pPlayer)[0] < -9:
        if len(newName) < 16 and sHoly not in newName and sGreat not in newName and not newName.startswith(holy_hre):
            newName = sHoly + newName
    elif newName.startswith(sHoly) and not origDesc.startswith(sHoly):
        newName = newName[len(sHoly):]

    return newName


def resetName(iPlayer):
    """Reset player name to original civilization name"""
    pPlayer = GC.getPlayer(iPlayer)
    civType = pPlayer.getCivilizationType()
    if civType >= 0:
        civInfo = GC.getCivilizationInfo(civType)
        origAdj = civInfo.getAdjective(0)
        origDesc = civInfo.getDescription()
        origShort = civInfo.getShortDescription(0)
        pPlayer.setCivName(origDesc, origShort, origAdj)


def isCommunism(pPlayer):
    """Check if player has communism civic"""
    if pPlayer is None or not pPlayer.isAlive():
        return False

    num_civics = GC.getNumCivicInfos()
    for i in xrange(num_civics):
        civicInfo = GC.getCivicInfo(i)
        if civicInfo.isCommunism() and pPlayer.isCivic(i):
            return True

    return False