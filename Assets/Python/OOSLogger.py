# OOS logger: writes the info contained in the sync checksum to a log file
from CvPythonExtensions import CyGlobalContext, YieldTypes, CommerceTypes, UnitAITypes
import os
import sys
import errno
import string

# Debug flag - set to True to emit errors to stderr
DEBUG_LOGGING = True


def safeConvertToStr(obj):
    """Safely convert any object to string, handling potential encoding issues."""
    result = None
    try:
        import TextUtil
        result = TextUtil.convertToStr(obj)
        # Test if the result can be used safely by attempting string operations
        # In Python 2.4, this will help catch unicode/str mixing issues
        str(result)
        return result
    except UnicodeError:
        # If TextUtil fails with unicode issues, try fallbacks on the result
        if result is not None:
            return _encodeFallback(result)
        else:
            return _encodeFallback(obj)
    except (ImportError, AttributeError):
        # TextUtil module missing or doesn't have convertToStr method
        return _encodeFallback(obj)
    except Exception:
        # Any other error from TextUtil
        return _encodeFallback(obj)


def _encodeFallback(obj):
    """Fallback encoding logic for string conversion."""
    try:
        # Future-proof: guard against accidental Py3 execution
        if sys.version_info[0] >= 3:
            return str(obj)

        # Simplified cross-version Unicode detection for Python 2
        unicode_type = type(u'')
        if isinstance(obj, unicode_type):
            return obj.encode('ascii', 'replace')

        # Duck-typing heuristic for Unicode-like objects
        if hasattr(obj, 'encode') and hasattr(obj, 'replace') and not hasattr(obj, 'decode'):
            # Unicode-like object, encode to ASCII with replacement
            return obj.encode('ascii', 'replace')
        elif hasattr(obj, 'decode'):
            # 8-bit str that might need decoding first
            try:
                return obj.decode('utf-8', 'replace').encode('ascii', 'replace')
            except UnicodeError:
                return obj.decode('latin-1', 'replace').encode('ascii', 'replace')
        else:
            # Not a string-like object, try direct conversion
            return str(obj)
    except (UnicodeError, AttributeError, TypeError):
        return "[Name conversion failed]"


# Precomputed frozenset of Windows reserved names for better performance
_RESERVED_NAMES = frozenset(['CON', 'PRN', 'AUX', 'NUL', 'CLOCK


def _isReservedName(filename):
    """Check if filename is a Windows reserved name."""
    # Normalize by trimming trailing dots/spaces before comparison
    normalized = filename.rstrip('. ').upper()
    base = normalized.split('.', 1)[0]  # Only split on first dot for efficiency
    return base in _RESERVED_NAMES


def sanitizeFilename(filename):
    """Remove or replace characters that are invalid in filenames on common OS."""

    # Use translate for better performance - create translation table
    invalid_chars = '<>:"/\\|?*'
    # Python 2.4 compatible translate table creation
    trans_table = string.maketrans(invalid_chars, '_' * len(invalid_chars))
    filename = filename.translate(trans_table)

    # Remove control characters (ASCII 0-31 and 127) and normalize whitespace
    cleaned_chars = []
    for char in filename:
        if ord(char) < 32 or ord(char) == 127:
            cleaned_chars.append('_')
        elif char.isspace():
            # Normalize all whitespace to single space, will be handled below
            cleaned_chars.append(' ')
        else:
            cleaned_chars.append(char)
    filename = ''.join(cleaned_chars)

    # Normalize multiple whitespace/underscores to single underscore
    import re
    filename = re.sub(r'[\s_]+', '_', filename)

    # Handle multiple leading dots (normalize to single safe prefix)
    had_leading_dots = filename.startswith('.')
    filename = filename.lstrip('.')
    if had_leading_dots:
        filename = '_' + filename

    # Handle Windows reserved names
    if _isReservedName(filename):
        filename = '_' + filename

    # Remove trailing dots and spaces (Windows issue)
    filename = filename.rstrip('. ')

    # Clamp length to Windows-safe limit (255 chars, leave some buffer)
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        # Guard against very long extensions
        if len(ext) > 10:
            ext = ext[:10]
        filename = name[:200 - len(ext)] + ext

        # Re-check reserved names after truncation
        if _isReservedName(filename):
            filename = '_' + filename

    # Ensure we have at least one character
    if not filename:
        filename = 'Player'

    return filename


def _writeGlobals(pFile, GAME, MAP):
    """Write global game data to log file."""
    SEP = "-----------------------------------------------------------------\n"
    pFile.write(2 * SEP + "\tGLOBALS\n" + 2 * SEP + "\n")

    pFile.write("Last MapRand Value: %d\n" % GAME.getMapRand().getSeed())
    pFile.write("Last SorenRand Value: %d\n" % GAME.getSorenRand().getSeed())
    pFile.write("Total num cities: %d\n" % GAME.getNumCities())
    pFile.write("Total population: %d\n" % GAME.getTotalPopulation())
    pFile.write("Total Deals: %d\n" % GAME.getNumDeals())
    pFile.write("Total owned plots: %d\n" % MAP.getOwnedPlots())
    pFile.write("Total num areas: %d\n\n\n" % MAP.getNumAreas())


def _writePlayerBasic(pFile, pPlayer, iPlayer, GAME, GC):
    """Write basic player data to log file."""
    SEP = "-----------------------------------------------------------------\n"
    pFile.write(2 * SEP + "%s player %d: %s\n" % (['NPC', 'Human'][pPlayer.isHuman()], iPlayer,
                                                  safeConvertToStr(pPlayer.getName())))
    pFile.write("  Civilization: %s\n" % safeConvertToStr(pPlayer.getCivilizationDescriptionKey()))
    pFile.write("  Alive: %s\n" % pPlayer.isAlive())
    pFile.write(2 * SEP + "\n\nBasic data:\n-----------\n")

    pFile.write("Player %d Score: %d\n" % (iPlayer, GAME.getPlayerScore(iPlayer)))
    pFile.write("Player %d Population: %d\n" % (iPlayer, pPlayer.getTotalPopulation()))
    pFile.write("Player %d Total Land: %d\n" % (iPlayer, pPlayer.getTotalLand()))
    pFile.write("Player %d Gold: %d\n" % (iPlayer, pPlayer.getGold()))
    pFile.write("Player %d Assets: %d\n" % (iPlayer, pPlayer.getAssets()))
    pFile.write("Player %d Power: %d\n" % (iPlayer, pPlayer.getPower()))
    pFile.write("Player %d Num Cities: %d\n" % (iPlayer, pPlayer.getNumCities()))
    pFile.write("Player %d Num Units: %d\n" % (iPlayer, pPlayer.getNumUnits()))
    pFile.write("Player %d Num Selection Groups: %d\n" % (iPlayer, pPlayer.getNumSelectionGroups()))
    pFile.write("Player %d Difficulty: %s\n" % (iPlayer, safeConvertToStr(
        GC.getHandicapInfo(pPlayer.getHandicapType()).getDescription())))
    pFile.write("Player %d State Religion: %s\n" % (iPlayer, safeConvertToStr(
        pPlayer.getStateReligionKey())))
    pFile.write("Player %d Culture: %d\n" % (iPlayer, pPlayer.getCulture()))


def _writeYieldsAndCommerce(pFile, pPlayer, iPlayer, GC):
    """Write yields and commerce data to log file."""
    pFile.write("\n\nYields:\n-------\n")
    for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
        pFile.write("Player %d %s Total Yield: %d\n" % (iPlayer, safeConvertToStr(
            GC.getYieldInfo(iYield).getDescription()), pPlayer.calculateTotalYield(iYield)))

    pFile.write("\n\nCommerce:\n---------\n")
    for iCommerce in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
        pFile.write("Player %d %s Total Commerce: %d\n" % (iPlayer, safeConvertToStr(
            GC.getCommerceInfo(iCommerce).getDescription()), pPlayer.getCommerceRate(
            CommerceTypes(iCommerce))))


def _writeCityInfo(pFile, pPlayer, iPlayer, GC):
    """Write city information to log file."""
    pFile.write("\n\nCity event history:\n-----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            bFirst = True
            for iEvent in xrange(GC.getNumEventInfos()):
                if pCity.isEventOccured(iEvent):
                    if bFirst:
                        pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getEventInfo(iEvent).getDescription()) + "\n")
            pCity, i = pPlayer.nextCity(i, False)

    pFile.write("\n\nCity Info:\n----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
            pFile.write("X: %d, Y: %d\n" % (pCity.getX(), pCity.getY()))
            pFile.write("Population: %d\n" % (pCity.getPopulation()))
            iCount = 0
            for iBuilding in xrange(GC.getNumBuildingInfos()):
                iCount += pCity.hasBuilding(iBuilding)
            pFile.write("Buildings: %d\n" % iCount)
            pFile.write("Improved Plots: %d\n" % (pCity.countNumImprovedPlots()))
            pFile.write("Tiles Worked: %d, Specialists: %d\n" % (pCity.getWorkingPopulation(),
                                                                 pCity.getSpecialistPopulation()))
            pFile.write("Great People: %d\n" % pCity.getNumGreatPeople())
            pFile.write("Good Health: %d, Bad Health: %d\n" % (pCity.goodHealth(), pCity.badHealth(False)))
            pFile.write("Happy Level: %d, Unhappy Level: %d\n" % (pCity.happyLevel(), pCity.unhappyLevel(0)))
            pFile.write("Food: %d\n" % pCity.getFood())
            pCity, i = pPlayer.nextCity(i, False)
    else:
        pFile.write("No Cities\n")


def _writeBonusAndImprovements(pFile, pPlayer, iPlayer, GC):
    """Write bonus and improvement information to log file."""
    pFile.write("\n\nBonus Info:\n-----------\n")
    for iBonus in xrange(GC.getNumBonusInfos()):
        szTemp = safeConvertToStr(GC.getBonusInfo(iBonus).getDescription())
        pFile.write("Player %d, %s, Number Available: %d\n" % (iPlayer, szTemp,
                                                               pPlayer.getNumAvailableBonuses(iBonus)))
        pFile.write("Player %d, %s, Import: %d\n" % (iPlayer, szTemp, pPlayer.getBonusImport(iBonus)))
        pFile.write("Player %d, %s, Export: %d\n\n" % (iPlayer, szTemp, pPlayer.getBonusExport(iBonus)))

    pFile.write("\n\nImprovement Info:\n-----------------\n")
    for iImprovement in xrange(GC.getNumImprovementInfos()):
        pFile.write("Player %d, %s, Improvement count: %d\n" % (iPlayer, safeConvertToStr(
            GC.getImprovementInfo(iImprovement).getDescription()), pPlayer.getImprovementCount(iImprovement)))

    pFile.write("\n\nBuilding Info:\n--------------------\n")
    for iBuilding in xrange(GC.getNumBuildingInfos()):
        pFile.write("Player %d, %s, Building class count plus making: %d\n" % (iPlayer,
                                                                               safeConvertToStr(
                                                                                   GC.getBuildingInfo(
                                                                                       iBuilding).getDescription()),
                                                                               pPlayer.getBuildingCountPlusMaking(
                                                                                   iBuilding)))

    pFile.write("\n\nUnit Class Info:\n--------------------\n")
    for iUnit in xrange(GC.getNumUnitInfos()):
        pFile.write("Player %d, %s, Unit class count plus training: %d\n" % (iPlayer,
                                                                             safeConvertToStr(
                                                                                 GC.getUnitInfo(
                                                                                     iUnit).getDescription()),
                                                                             pPlayer.getUnitCountPlusMaking(iUnit)))


def _writeUnitAIInfo(pFile, pPlayer, iPlayer, GC):
    """Write UnitAI type information to log file."""
    pFile.write("\n\nUnitAI Types Info:\n------------------\n")
    for iUnitAIType in xrange(int(UnitAITypes.NUM_UNITAI_TYPES)):
        try:
            unitai_info = GC.getUnitAIInfo(iUnitAIType)
            if hasattr(unitai_info, 'getDescription'):
                unitai_label = safeConvertToStr(unitai_info.getDescription())
            else:
                unitai_label = safeConvertToStr(unitai_info.getType())
        except AttributeError, e:
            unitai_label = "UnitAI_%d_ATTR_ERR_%s" % (iUnitAIType, str(e).replace(' ', '_')[:20])
        except Exception, e:
            # Include sanitized exception details for diagnosis
            error_msg = str(e).replace(' ', '_').replace('\n', '_')[:30]
            unitai_label = "UnitAI_%d_ERR_%s" % (iUnitAIType, error_msg)

        try:
            count = pPlayer.AI_totalUnitAIs(UnitAITypes(iUnitAIType))
        except Exception, e:
            count = -1  # Error indicator in count

        pFile.write("Player %d, %s, Unit AI Type count: %d\n" % (iPlayer, unitai_label, count))


def _writeCityReligionsAndCorporations(pFile, pPlayer, GC):
    """Write city religions and corporations to log file."""
    pFile.write("\n\nCity Religions:\n-----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            bFirst = True
            for iReligion in xrange(GC.getNumReligionInfos()):
                if pCity.isHasReligion(iReligion):
                    if bFirst:
                        pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getReligionInfo(iReligion).getDescription()) + "\n")
            pCity, i = pPlayer.nextCity(i, False)

    pFile.write("\n\nCity Corporations:\n-----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            bFirst = True
            for iCorporation in xrange(GC.getNumCorporationInfos()):
                if pCity.isHasCorporation(iCorporation):
                    if bFirst:
                        pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getCorporationInfo(iCorporation).getDescription()) + "\n")
            pCity, i = pPlayer.nextCity(i, False)


def _writeUnitInfo(pFile, pPlayer, iPlayer, GC):
    """Write unit information to log file."""
    pFile.write("\n\nUnit Info:\n----------\n")
    if pPlayer.getNumUnits():
        for pUnit in pPlayer.units():
            pFile.write("Player %d, Unit ID: %d, %s\n" % (iPlayer, pUnit.getID(),
                                                          safeConvertToStr(pUnit.getName())))
            pFile.write("X: %d, Y: %d\nDamage: %d\n" % (pUnit.getX(), pUnit.getY(), pUnit.getDamage()))
            pFile.write("Experience: %d\nLevel: %d\n" % (pUnit.getExperience(), pUnit.getLevel()))
            bFirst = True
            for j in xrange(GC.getNumPromotionInfos()):
                if pUnit.isHasPromotion(j):
                    if bFirst:
                        pFile.write("Promotions:\n")
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getPromotionInfo(j).getDescription()) + "\n")
            bFirst = True
            for j in xrange(GC.getNumUnitCombatInfos()):
                if pUnit.isHasUnitCombat(j):
                    if bFirst:
                        pFile.write("UnitCombats:\n")
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getUnitCombatInfo(j).getDescription()) + "\n")
    else:
        pFile.write("No Units\n")


def writeLog():
    import SystemPaths as SP
    GC = CyGlobalContext()
    MAP = GC.getMap()
    GAME = GC.getGame()
    iActivePlayer = GAME.getActivePlayer()
    playerName = safeConvertToStr(GC.getPlayer(iActivePlayer).getName())

    # Ensure logs directory exists - fully race-safe creation
    log_dir = os.path.join(SP.userDir, "Logs")
    try:
        os.makedirs(log_dir)
    except OSError, e:
        # Handle race condition where directory is created between calls or already exists
        if e.errno == errno.EEXIST:
            pass
        else:
            # If we can't create the directory for other reasons, try writing to user directory directly
            log_dir = SP.userDir

    # Create filename with player info, then sanitize the entire filename
    filename = "%s - Player %d - Turn %d OOSLog.txt" % (playerName, iActivePlayer, GAME.getGameTurn())
    filename = sanitizeFilename(filename)
    szName = os.path.join(log_dir, filename)

    # Initialize pFile as None for safer cleanup
    pFile = None
    try:
        pFile = open(szName, "w")
    except IOError:
        # If we can't open the file, silently fail (logging is optional)
        return

    try:
        # Backup current language
        iLanguage = GAME.getCurrentLanguage()
        # Force english language for logs
        GAME.setCurrentLanguage(0)

        try:
            # Write global data
            _writeGlobals(pFile, GAME, MAP)

            # Player data
            for iPlayer in xrange(GC.getMAX_PLAYERS()):
                pPlayer = GC.getPlayer(iPlayer)
                if pPlayer.isEverAlive():
                    _writePlayerBasic(pFile, pPlayer, iPlayer, GAME, GC)
                    _writeYieldsAndCommerce(pFile, pPlayer, iPlayer, GC)
                    _writeCityInfo(pFile, pPlayer, iPlayer, GC)
                    _writeBonusAndImprovements(pFile, pPlayer, iPlayer, GC)
                    _writeUnitAIInfo(pFile, pPlayer, iPlayer, GC)
                    _writeCityReligionsAndCorporations(pFile, pPlayer, GC)
                    _writeUnitInfo(pFile, pPlayer, iPlayer, GC)
                    # Space at end of player's info
                    pFile.write("\n\n")

        finally:
            # Restore current language even if an error occurs
            GAME.setCurrentLanguage(iLanguage)

    except IOError, e:
        # File I/O errors - disk full, permissions, etc.
        if DEBUG_LOGGING:
            sys.stderr.write("OOSLogger IOError: %s\n" % str(e))
    except OSError, e:
        # OS-level errors - path issues, etc.
        if DEBUG_LOGGING:
            sys.stderr.write("OOSLogger OSError: %s\n" % str(e))
    except Exception, e:
        # Any other unexpected error - fail silently to avoid crashing game
        if DEBUG_LOGGING:
            sys.stderr.write("OOSLogger Exception: %s\n" % str(e))
            import traceback
            traceback.print_exc()
    finally:
        # Always close the file if it was opened
        if pFile is not None:
            try:
                pFile.close()
            except:
                pass


# Unit tests for sanitizeFilename function
def _runTests():
    """Unit tests for sanitizeFilename edge cases - only run when DEBUG_LOGGING is True."""
    if not DEBUG_LOGGING:
        return

    test_cases = [
        ("CON.txt", "_CON.txt"),
        ("NUL", "_NUL"),
        ("my:name?.txt", "my_name_.txt"),
        ("..hidden", "_hidden"),
        ("trailing. ", "trailing"),
        ("multiple   spaces", "multiple_spaces"),
        ("control\x01char\x1f", "control_char_"),
        ("normal.txt", "normal.txt"),
        ("", "Player"),
        ("a" * 300 + ".txt", "a" * 196 + ".txt"),  # Should truncate to 200 chars
        ("COM1", "_COM1"),
        ("lpt9.doc", "_lpt9.doc"),
        ("CONIN$", "_CONIN$"),
        ("valid/\\<>:\"|?*name", "valid_________name"),
    ]

    for input_name, expected in test_cases:
        result = sanitizeFilename(input_name)
        if result == expected:
            sys.stderr.write("PASS: '%s' -> '%s'\n" % (input_name, result))
        else:
            sys.stderr.write("FAIL: '%s' -> '%s' (expected '%s')\n" % (input_name, result, expected))


# Run tests if DEBUG_LOGGING is enabled
_runTests(), 'CONIN


def _isReservedName(filename):
    """Check if filename is a Windows reserved name."""
    # Normalize by trimming trailing dots/spaces before comparison
    normalized = filename.rstrip('. ').upper()
    base = normalized.split('.', 1)[0]  # Only split on first dot for efficiency
    return base in _RESERVED_NAMES


def sanitizeFilename(filename):
    """Remove or replace characters that are invalid in filenames on common OS."""

    # Use translate for better performance - create translation table
    invalid_chars = '<>:"/\\|?*'
    # Python 2.4 compatible translate table creation
    trans_table = string.maketrans(invalid_chars, '_' * len(invalid_chars))
    filename = filename.translate(trans_table)

    # Remove control characters (ASCII 0-31 and 127) and normalize whitespace
    cleaned_chars = []
    for char in filename:
        if ord(char) < 32 or ord(char) == 127:
            cleaned_chars.append('_')
        elif char.isspace():
            # Normalize all whitespace to single space, will be handled below
            cleaned_chars.append(' ')
        else:
            cleaned_chars.append(char)
    filename = ''.join(cleaned_chars)

    # Normalize multiple whitespace/underscores to single underscore
    import re
    filename = re.sub(r'[\s_]+', '_', filename)

    # Handle multiple leading dots (normalize to single safe prefix)
    had_leading_dots = filename.startswith('.')
    filename = filename.lstrip('.')
    if had_leading_dots:
        filename = '_' + filename

    # Handle Windows reserved names
    if _isReservedName(filename):
        filename = '_' + filename

    # Remove trailing dots and spaces (Windows issue)
    filename = filename.rstrip('. ')

    # Clamp length to Windows-safe limit (255 chars, leave some buffer)
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        # Guard against very long extensions
        if len(ext) > 10:
            ext = ext[:10]
        filename = name[:200 - len(ext)] + ext

        # Re-check reserved names after truncation
        if _isReservedName(filename):
            filename = '_' + filename

    # Ensure we have at least one character
    if not filename:
        filename = 'Player'

    return filename


def _writeGlobals(pFile, GAME, MAP):
    """Write global game data to log file."""
    SEP = "-----------------------------------------------------------------\n"
    pFile.write(2 * SEP + "\tGLOBALS\n" + 2 * SEP + "\n")

    pFile.write("Last MapRand Value: %d\n" % GAME.getMapRand().getSeed())
    pFile.write("Last SorenRand Value: %d\n" % GAME.getSorenRand().getSeed())
    pFile.write("Total num cities: %d\n" % GAME.getNumCities())
    pFile.write("Total population: %d\n" % GAME.getTotalPopulation())
    pFile.write("Total Deals: %d\n" % GAME.getNumDeals())
    pFile.write("Total owned plots: %d\n" % MAP.getOwnedPlots())
    pFile.write("Total num areas: %d\n\n\n" % MAP.getNumAreas())


def _writePlayerBasic(pFile, pPlayer, iPlayer, GAME, GC):
    """Write basic player data to log file."""
    SEP = "-----------------------------------------------------------------\n"
    pFile.write(2 * SEP + "%s player %d: %s\n" % (['NPC', 'Human'][pPlayer.isHuman()], iPlayer,
                                                  safeConvertToStr(pPlayer.getName())))
    pFile.write("  Civilization: %s\n" % safeConvertToStr(pPlayer.getCivilizationDescriptionKey()))
    pFile.write("  Alive: %s\n" % pPlayer.isAlive())
    pFile.write(2 * SEP + "\n\nBasic data:\n-----------\n")

    pFile.write("Player %d Score: %d\n" % (iPlayer, GAME.getPlayerScore(iPlayer)))
    pFile.write("Player %d Population: %d\n" % (iPlayer, pPlayer.getTotalPopulation()))
    pFile.write("Player %d Total Land: %d\n" % (iPlayer, pPlayer.getTotalLand()))
    pFile.write("Player %d Gold: %d\n" % (iPlayer, pPlayer.getGold()))
    pFile.write("Player %d Assets: %d\n" % (iPlayer, pPlayer.getAssets()))
    pFile.write("Player %d Power: %d\n" % (iPlayer, pPlayer.getPower()))
    pFile.write("Player %d Num Cities: %d\n" % (iPlayer, pPlayer.getNumCities()))
    pFile.write("Player %d Num Units: %d\n" % (iPlayer, pPlayer.getNumUnits()))
    pFile.write("Player %d Num Selection Groups: %d\n" % (iPlayer, pPlayer.getNumSelectionGroups()))
    pFile.write("Player %d Difficulty: %s\n" % (iPlayer, safeConvertToStr(
        GC.getHandicapInfo(pPlayer.getHandicapType()).getDescription())))
    pFile.write("Player %d State Religion: %s\n" % (iPlayer, safeConvertToStr(
        pPlayer.getStateReligionKey())))
    pFile.write("Player %d Culture: %d\n" % (iPlayer, pPlayer.getCulture()))


def _writeYieldsAndCommerce(pFile, pPlayer, iPlayer, GC):
    """Write yields and commerce data to log file."""
    pFile.write("\n\nYields:\n-------\n")
    for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
        pFile.write("Player %d %s Total Yield: %d\n" % (iPlayer, safeConvertToStr(
            GC.getYieldInfo(iYield).getDescription()), pPlayer.calculateTotalYield(iYield)))

    pFile.write("\n\nCommerce:\n---------\n")
    for iCommerce in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
        pFile.write("Player %d %s Total Commerce: %d\n" % (iPlayer, safeConvertToStr(
            GC.getCommerceInfo(iCommerce).getDescription()), pPlayer.getCommerceRate(
            CommerceTypes(iCommerce))))


def _writeCityInfo(pFile, pPlayer, iPlayer, GC):
    """Write city information to log file."""
    pFile.write("\n\nCity event history:\n-----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            bFirst = True
            for iEvent in xrange(GC.getNumEventInfos()):
                if pCity.isEventOccured(iEvent):
                    if bFirst:
                        pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getEventInfo(iEvent).getDescription()) + "\n")
            pCity, i = pPlayer.nextCity(i, False)

    pFile.write("\n\nCity Info:\n----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
            pFile.write("X: %d, Y: %d\n" % (pCity.getX(), pCity.getY()))
            pFile.write("Population: %d\n" % (pCity.getPopulation()))
            iCount = 0
            for iBuilding in xrange(GC.getNumBuildingInfos()):
                iCount += pCity.hasBuilding(iBuilding)
            pFile.write("Buildings: %d\n" % iCount)
            pFile.write("Improved Plots: %d\n" % (pCity.countNumImprovedPlots()))
            pFile.write("Tiles Worked: %d, Specialists: %d\n" % (pCity.getWorkingPopulation(),
                                                                 pCity.getSpecialistPopulation()))
            pFile.write("Great People: %d\n" % pCity.getNumGreatPeople())
            pFile.write("Good Health: %d, Bad Health: %d\n" % (pCity.goodHealth(), pCity.badHealth(False)))
            pFile.write("Happy Level: %d, Unhappy Level: %d\n" % (pCity.happyLevel(), pCity.unhappyLevel(0)))
            pFile.write("Food: %d\n" % pCity.getFood())
            pCity, i = pPlayer.nextCity(i, False)
    else:
        pFile.write("No Cities\n")


def _writeBonusAndImprovements(pFile, pPlayer, iPlayer, GC):
    """Write bonus and improvement information to log file."""
    pFile.write("\n\nBonus Info:\n-----------\n")
    for iBonus in xrange(GC.getNumBonusInfos()):
        szTemp = safeConvertToStr(GC.getBonusInfo(iBonus).getDescription())
        pFile.write("Player %d, %s, Number Available: %d\n" % (iPlayer, szTemp,
                                                               pPlayer.getNumAvailableBonuses(iBonus)))
        pFile.write("Player %d, %s, Import: %d\n" % (iPlayer, szTemp, pPlayer.getBonusImport(iBonus)))
        pFile.write("Player %d, %s, Export: %d\n\n" % (iPlayer, szTemp, pPlayer.getBonusExport(iBonus)))

    pFile.write("\n\nImprovement Info:\n-----------------\n")
    for iImprovement in xrange(GC.getNumImprovementInfos()):
        pFile.write("Player %d, %s, Improvement count: %d\n" % (iPlayer, safeConvertToStr(
            GC.getImprovementInfo(iImprovement).getDescription()), pPlayer.getImprovementCount(iImprovement)))

    pFile.write("\n\nBuilding Info:\n--------------------\n")
    for iBuilding in xrange(GC.getNumBuildingInfos()):
        pFile.write("Player %d, %s, Building class count plus making: %d\n" % (iPlayer,
                                                                               safeConvertToStr(
                                                                                   GC.getBuildingInfo(
                                                                                       iBuilding).getDescription()),
                                                                               pPlayer.getBuildingCountPlusMaking(
                                                                                   iBuilding)))

    pFile.write("\n\nUnit Class Info:\n--------------------\n")
    for iUnit in xrange(GC.getNumUnitInfos()):
        pFile.write("Player %d, %s, Unit class count plus training: %d\n" % (iPlayer,
                                                                             safeConvertToStr(
                                                                                 GC.getUnitInfo(
                                                                                     iUnit).getDescription()),
                                                                             pPlayer.getUnitCountPlusMaking(iUnit)))


def _writeUnitAIInfo(pFile, pPlayer, iPlayer, GC):
    """Write UnitAI type information to log file."""
    pFile.write("\n\nUnitAI Types Info:\n------------------\n")
    for iUnitAIType in xrange(int(UnitAITypes.NUM_UNITAI_TYPES)):
        try:
            unitai_info = GC.getUnitAIInfo(iUnitAIType)
            if hasattr(unitai_info, 'getDescription'):
                unitai_label = safeConvertToStr(unitai_info.getDescription())
            else:
                unitai_label = safeConvertToStr(unitai_info.getType())
        except AttributeError, e:
            unitai_label = "UnitAI_%d_ATTR_ERR_%s" % (iUnitAIType, str(e).replace(' ', '_')[:20])
        except Exception, e:
            # Include sanitized exception details for diagnosis
            error_msg = str(e).replace(' ', '_').replace('\n', '_')[:30]
            unitai_label = "UnitAI_%d_ERR_%s" % (iUnitAIType, error_msg)

        try:
            count = pPlayer.AI_totalUnitAIs(UnitAITypes(iUnitAIType))
        except Exception, e:
            count = -1  # Error indicator in count

        pFile.write("Player %d, %s, Unit AI Type count: %d\n" % (iPlayer, unitai_label, count))


def _writeCityReligionsAndCorporations(pFile, pPlayer, GC):
    """Write city religions and corporations to log file."""
    pFile.write("\n\nCity Religions:\n-----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            bFirst = True
            for iReligion in xrange(GC.getNumReligionInfos()):
                if pCity.isHasReligion(iReligion):
                    if bFirst:
                        pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getReligionInfo(iReligion).getDescription()) + "\n")
            pCity, i = pPlayer.nextCity(i, False)

    pFile.write("\n\nCity Corporations:\n-----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            bFirst = True
            for iCorporation in xrange(GC.getNumCorporationInfos()):
                if pCity.isHasCorporation(iCorporation):
                    if bFirst:
                        pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getCorporationInfo(iCorporation).getDescription()) + "\n")
            pCity, i = pPlayer.nextCity(i, False)


def _writeUnitInfo(pFile, pPlayer, iPlayer, GC):
    """Write unit information to log file."""
    pFile.write("\n\nUnit Info:\n----------\n")
    if pPlayer.getNumUnits():
        for pUnit in pPlayer.units():
            pFile.write("Player %d, Unit ID: %d, %s\n" % (iPlayer, pUnit.getID(),
                                                          safeConvertToStr(pUnit.getName())))
            pFile.write("X: %d, Y: %d\nDamage: %d\n" % (pUnit.getX(), pUnit.getY(), pUnit.getDamage()))
            pFile.write("Experience: %d\nLevel: %d\n" % (pUnit.getExperience(), pUnit.getLevel()))
            bFirst = True
            for j in xrange(GC.getNumPromotionInfos()):
                if pUnit.isHasPromotion(j):
                    if bFirst:
                        pFile.write("Promotions:\n")
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getPromotionInfo(j).getDescription()) + "\n")
            bFirst = True
            for j in xrange(GC.getNumUnitCombatInfos()):
                if pUnit.isHasUnitCombat(j):
                    if bFirst:
                        pFile.write("UnitCombats:\n")
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getUnitCombatInfo(j).getDescription()) + "\n")
    else:
        pFile.write("No Units\n")


def writeLog():
    import SystemPaths as SP
    GC = CyGlobalContext()
    MAP = GC.getMap()
    GAME = GC.getGame()
    iActivePlayer = GAME.getActivePlayer()
    playerName = safeConvertToStr(GC.getPlayer(iActivePlayer).getName())

    # Ensure logs directory exists - fully race-safe creation
    log_dir = os.path.join(SP.userDir, "Logs")
    try:
        os.makedirs(log_dir)
    except OSError, e:
        # Handle race condition where directory is created between calls or already exists
        if e.errno == errno.EEXIST:
            pass
        else:
            # If we can't create the directory for other reasons, try writing to user directory directly
            log_dir = SP.userDir

    # Create filename with player info, then sanitize the entire filename
    filename = "%s - Player %d - Turn %d OOSLog.txt" % (playerName, iActivePlayer, GAME.getGameTurn())
    filename = sanitizeFilename(filename)
    szName = os.path.join(log_dir, filename)

    # Initialize pFile as None for safer cleanup
    pFile = None
    try:
        pFile = open(szName, "w")
    except IOError:
        # If we can't open the file, silently fail (logging is optional)
        return

    try:
        # Backup current language
        iLanguage = GAME.getCurrentLanguage()
        # Force english language for logs
        GAME.setCurrentLanguage(0)

        try:
            # Write global data
            _writeGlobals(pFile, GAME, MAP)

            # Player data
            for iPlayer in xrange(GC.getMAX_PLAYERS()):
                pPlayer = GC.getPlayer(iPlayer)
                if pPlayer.isEverAlive():
                    _writePlayerBasic(pFile, pPlayer, iPlayer, GAME, GC)
                    _writeYieldsAndCommerce(pFile, pPlayer, iPlayer, GC)
                    _writeCityInfo(pFile, pPlayer, iPlayer, GC)
                    _writeBonusAndImprovements(pFile, pPlayer, iPlayer, GC)
                    _writeUnitAIInfo(pFile, pPlayer, iPlayer, GC)
                    _writeCityReligionsAndCorporations(pFile, pPlayer, GC)
                    _writeUnitInfo(pFile, pPlayer, iPlayer, GC)
                    # Space at end of player's info
                    pFile.write("\n\n")

        finally:
            # Restore current language even if an error occurs
            GAME.setCurrentLanguage(iLanguage)

    except IOError, e:
        # File I/O errors - disk full, permissions, etc.
        if DEBUG_LOGGING:
            sys.stderr.write("OOSLogger IOError: %s\n" % str(e))
    except OSError, e:
        # OS-level errors - path issues, etc.
        if DEBUG_LOGGING:
            sys.stderr.write("OOSLogger OSError: %s\n" % str(e))
    except Exception, e:
        # Any other unexpected error - fail silently to avoid crashing game
        if DEBUG_LOGGING:
            sys.stderr.write("OOSLogger Exception: %s\n" % str(e))
            import traceback
            traceback.print_exc()
    finally:
        # Always close the file if it was opened
        if pFile is not None:
            try:
                pFile.close()
            except:
                pass


# Unit tests for sanitizeFilename function
def _testSanitizeFilename():
    """Unit tests for sanitizeFilename edge cases."""
    test_cases = [
        ("CON.txt", "_CON.txt"),
        ("NUL", "_NUL"),
        ("my:name?.txt", "my_name_.txt"),
        ("..hidden", "_hidden"),
        ("trailing. ", "trailing"),
        ("multiple   spaces", "multiple_spaces"),
        ("control\x01char\x1f", "control_char_"),
        ("normal.txt", "normal.txt"),
        ("", "Player"),
        ("a" * 300 + ".txt", "a" * 196 + ".txt"),  # Should truncate to 200 chars
        ("COM1", "_COM1"),
        ("lpt9.doc", "_lpt9.doc"),
        ("CONIN$", "_CONIN$"),
        ("valid/\\<>:\"|?*name", "valid_________name"),
    ]

    if DEBUG_LOGGING:
        for input_name, expected in test_cases:
            result = sanitizeFilename(input_name)
            if result == expected:
                sys.stderr.write("PASS: '%s' -> '%s'\n" % (input_name, result))
            else:
                sys.stderr.write("FAIL: '%s' -> '%s' (expected '%s')\n" % (input_name, result, expected))


# Run tests if DEBUG_LOGGING is enabled
if DEBUG_LOGGING:
    _testSanitizeFilename(), 'CONOUT


def _isReservedName(filename):
    """Check if filename is a Windows reserved name."""
    # Normalize by trimming trailing dots/spaces before comparison
    normalized = filename.rstrip('. ').upper()
    base = normalized.split('.', 1)[0]  # Only split on first dot for efficiency
    return base in _RESERVED_NAMES


def sanitizeFilename(filename):
    """Remove or replace characters that are invalid in filenames on common OS."""

    # Use translate for better performance - create translation table
    invalid_chars = '<>:"/\\|?*'
    # Python 2.4 compatible translate table creation
    trans_table = string.maketrans(invalid_chars, '_' * len(invalid_chars))
    filename = filename.translate(trans_table)

    # Remove control characters (ASCII 0-31 and 127) and normalize whitespace
    cleaned_chars = []
    for char in filename:
        if ord(char) < 32 or ord(char) == 127:
            cleaned_chars.append('_')
        elif char.isspace():
            # Normalize all whitespace to single space, will be handled below
            cleaned_chars.append(' ')
        else:
            cleaned_chars.append(char)
    filename = ''.join(cleaned_chars)

    # Normalize multiple whitespace/underscores to single underscore
    import re
    filename = re.sub(r'[\s_]+', '_', filename)

    # Handle multiple leading dots (normalize to single safe prefix)
    had_leading_dots = filename.startswith('.')
    filename = filename.lstrip('.')
    if had_leading_dots:
        filename = '_' + filename

    # Handle Windows reserved names
    if _isReservedName(filename):
        filename = '_' + filename

    # Remove trailing dots and spaces (Windows issue)
    filename = filename.rstrip('. ')

    # Clamp length to Windows-safe limit (255 chars, leave some buffer)
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        # Guard against very long extensions
        if len(ext) > 10:
            ext = ext[:10]
        filename = name[:200 - len(ext)] + ext

        # Re-check reserved names after truncation
        if _isReservedName(filename):
            filename = '_' + filename

    # Ensure we have at least one character
    if not filename:
        filename = 'Player'

    return filename


def _writeGlobals(pFile, GAME, MAP):
    """Write global game data to log file."""
    SEP = "-----------------------------------------------------------------\n"
    pFile.write(2 * SEP + "\tGLOBALS\n" + 2 * SEP + "\n")

    pFile.write("Last MapRand Value: %d\n" % GAME.getMapRand().getSeed())
    pFile.write("Last SorenRand Value: %d\n" % GAME.getSorenRand().getSeed())
    pFile.write("Total num cities: %d\n" % GAME.getNumCities())
    pFile.write("Total population: %d\n" % GAME.getTotalPopulation())
    pFile.write("Total Deals: %d\n" % GAME.getNumDeals())
    pFile.write("Total owned plots: %d\n" % MAP.getOwnedPlots())
    pFile.write("Total num areas: %d\n\n\n" % MAP.getNumAreas())


def _writePlayerBasic(pFile, pPlayer, iPlayer, GAME, GC):
    """Write basic player data to log file."""
    SEP = "-----------------------------------------------------------------\n"
    pFile.write(2 * SEP + "%s player %d: %s\n" % (['NPC', 'Human'][pPlayer.isHuman()], iPlayer,
                                                  safeConvertToStr(pPlayer.getName())))
    pFile.write("  Civilization: %s\n" % safeConvertToStr(pPlayer.getCivilizationDescriptionKey()))
    pFile.write("  Alive: %s\n" % pPlayer.isAlive())
    pFile.write(2 * SEP + "\n\nBasic data:\n-----------\n")

    pFile.write("Player %d Score: %d\n" % (iPlayer, GAME.getPlayerScore(iPlayer)))
    pFile.write("Player %d Population: %d\n" % (iPlayer, pPlayer.getTotalPopulation()))
    pFile.write("Player %d Total Land: %d\n" % (iPlayer, pPlayer.getTotalLand()))
    pFile.write("Player %d Gold: %d\n" % (iPlayer, pPlayer.getGold()))
    pFile.write("Player %d Assets: %d\n" % (iPlayer, pPlayer.getAssets()))
    pFile.write("Player %d Power: %d\n" % (iPlayer, pPlayer.getPower()))
    pFile.write("Player %d Num Cities: %d\n" % (iPlayer, pPlayer.getNumCities()))
    pFile.write("Player %d Num Units: %d\n" % (iPlayer, pPlayer.getNumUnits()))
    pFile.write("Player %d Num Selection Groups: %d\n" % (iPlayer, pPlayer.getNumSelectionGroups()))
    pFile.write("Player %d Difficulty: %s\n" % (iPlayer, safeConvertToStr(
        GC.getHandicapInfo(pPlayer.getHandicapType()).getDescription())))
    pFile.write("Player %d State Religion: %s\n" % (iPlayer, safeConvertToStr(
        pPlayer.getStateReligionKey())))
    pFile.write("Player %d Culture: %d\n" % (iPlayer, pPlayer.getCulture()))


def _writeYieldsAndCommerce(pFile, pPlayer, iPlayer, GC):
    """Write yields and commerce data to log file."""
    pFile.write("\n\nYields:\n-------\n")
    for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
        pFile.write("Player %d %s Total Yield: %d\n" % (iPlayer, safeConvertToStr(
            GC.getYieldInfo(iYield).getDescription()), pPlayer.calculateTotalYield(iYield)))

    pFile.write("\n\nCommerce:\n---------\n")
    for iCommerce in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
        pFile.write("Player %d %s Total Commerce: %d\n" % (iPlayer, safeConvertToStr(
            GC.getCommerceInfo(iCommerce).getDescription()), pPlayer.getCommerceRate(
            CommerceTypes(iCommerce))))


def _writeCityInfo(pFile, pPlayer, iPlayer, GC):
    """Write city information to log file."""
    pFile.write("\n\nCity event history:\n-----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            bFirst = True
            for iEvent in xrange(GC.getNumEventInfos()):
                if pCity.isEventOccured(iEvent):
                    if bFirst:
                        pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getEventInfo(iEvent).getDescription()) + "\n")
            pCity, i = pPlayer.nextCity(i, False)

    pFile.write("\n\nCity Info:\n----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
            pFile.write("X: %d, Y: %d\n" % (pCity.getX(), pCity.getY()))
            pFile.write("Population: %d\n" % (pCity.getPopulation()))
            iCount = 0
            for iBuilding in xrange(GC.getNumBuildingInfos()):
                iCount += pCity.hasBuilding(iBuilding)
            pFile.write("Buildings: %d\n" % iCount)
            pFile.write("Improved Plots: %d\n" % (pCity.countNumImprovedPlots()))
            pFile.write("Tiles Worked: %d, Specialists: %d\n" % (pCity.getWorkingPopulation(),
                                                                 pCity.getSpecialistPopulation()))
            pFile.write("Great People: %d\n" % pCity.getNumGreatPeople())
            pFile.write("Good Health: %d, Bad Health: %d\n" % (pCity.goodHealth(), pCity.badHealth(False)))
            pFile.write("Happy Level: %d, Unhappy Level: %d\n" % (pCity.happyLevel(), pCity.unhappyLevel(0)))
            pFile.write("Food: %d\n" % pCity.getFood())
            pCity, i = pPlayer.nextCity(i, False)
    else:
        pFile.write("No Cities\n")


def _writeBonusAndImprovements(pFile, pPlayer, iPlayer, GC):
    """Write bonus and improvement information to log file."""
    pFile.write("\n\nBonus Info:\n-----------\n")
    for iBonus in xrange(GC.getNumBonusInfos()):
        szTemp = safeConvertToStr(GC.getBonusInfo(iBonus).getDescription())
        pFile.write("Player %d, %s, Number Available: %d\n" % (iPlayer, szTemp,
                                                               pPlayer.getNumAvailableBonuses(iBonus)))
        pFile.write("Player %d, %s, Import: %d\n" % (iPlayer, szTemp, pPlayer.getBonusImport(iBonus)))
        pFile.write("Player %d, %s, Export: %d\n\n" % (iPlayer, szTemp, pPlayer.getBonusExport(iBonus)))

    pFile.write("\n\nImprovement Info:\n-----------------\n")
    for iImprovement in xrange(GC.getNumImprovementInfos()):
        pFile.write("Player %d, %s, Improvement count: %d\n" % (iPlayer, safeConvertToStr(
            GC.getImprovementInfo(iImprovement).getDescription()), pPlayer.getImprovementCount(iImprovement)))

    pFile.write("\n\nBuilding Info:\n--------------------\n")
    for iBuilding in xrange(GC.getNumBuildingInfos()):
        pFile.write("Player %d, %s, Building class count plus making: %d\n" % (iPlayer,
                                                                               safeConvertToStr(
                                                                                   GC.getBuildingInfo(
                                                                                       iBuilding).getDescription()),
                                                                               pPlayer.getBuildingCountPlusMaking(
                                                                                   iBuilding)))

    pFile.write("\n\nUnit Class Info:\n--------------------\n")
    for iUnit in xrange(GC.getNumUnitInfos()):
        pFile.write("Player %d, %s, Unit class count plus training: %d\n" % (iPlayer,
                                                                             safeConvertToStr(
                                                                                 GC.getUnitInfo(
                                                                                     iUnit).getDescription()),
                                                                             pPlayer.getUnitCountPlusMaking(iUnit)))


def _writeUnitAIInfo(pFile, pPlayer, iPlayer, GC):
    """Write UnitAI type information to log file."""
    pFile.write("\n\nUnitAI Types Info:\n------------------\n")
    for iUnitAIType in xrange(int(UnitAITypes.NUM_UNITAI_TYPES)):
        try:
            unitai_info = GC.getUnitAIInfo(iUnitAIType)
            if hasattr(unitai_info, 'getDescription'):
                unitai_label = safeConvertToStr(unitai_info.getDescription())
            else:
                unitai_label = safeConvertToStr(unitai_info.getType())
        except AttributeError, e:
            unitai_label = "UnitAI_%d_ATTR_ERR_%s" % (iUnitAIType, str(e).replace(' ', '_')[:20])
        except Exception, e:
            # Include sanitized exception details for diagnosis
            error_msg = str(e).replace(' ', '_').replace('\n', '_')[:30]
            unitai_label = "UnitAI_%d_ERR_%s" % (iUnitAIType, error_msg)

        try:
            count = pPlayer.AI_totalUnitAIs(UnitAITypes(iUnitAIType))
        except Exception, e:
            count = -1  # Error indicator in count

        pFile.write("Player %d, %s, Unit AI Type count: %d\n" % (iPlayer, unitai_label, count))


def _writeCityReligionsAndCorporations(pFile, pPlayer, GC):
    """Write city religions and corporations to log file."""
    pFile.write("\n\nCity Religions:\n-----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            bFirst = True
            for iReligion in xrange(GC.getNumReligionInfos()):
                if pCity.isHasReligion(iReligion):
                    if bFirst:
                        pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getReligionInfo(iReligion).getDescription()) + "\n")
            pCity, i = pPlayer.nextCity(i, False)

    pFile.write("\n\nCity Corporations:\n-----------\n")
    if pPlayer.getNumCities():
        pCity, i = pPlayer.firstCity(False)
        while pCity:
            bFirst = True
            for iCorporation in xrange(GC.getNumCorporationInfos()):
                if pCity.isHasCorporation(iCorporation):
                    if bFirst:
                        pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getCorporationInfo(iCorporation).getDescription()) + "\n")
            pCity, i = pPlayer.nextCity(i, False)


def _writeUnitInfo(pFile, pPlayer, iPlayer, GC):
    """Write unit information to log file."""
    pFile.write("\n\nUnit Info:\n----------\n")
    if pPlayer.getNumUnits():
        for pUnit in pPlayer.units():
            pFile.write("Player %d, Unit ID: %d, %s\n" % (iPlayer, pUnit.getID(),
                                                          safeConvertToStr(pUnit.getName())))
            pFile.write("X: %d, Y: %d\nDamage: %d\n" % (pUnit.getX(), pUnit.getY(), pUnit.getDamage()))
            pFile.write("Experience: %d\nLevel: %d\n" % (pUnit.getExperience(), pUnit.getLevel()))
            bFirst = True
            for j in xrange(GC.getNumPromotionInfos()):
                if pUnit.isHasPromotion(j):
                    if bFirst:
                        pFile.write("Promotions:\n")
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getPromotionInfo(j).getDescription()) + "\n")
            bFirst = True
            for j in xrange(GC.getNumUnitCombatInfos()):
                if pUnit.isHasUnitCombat(j):
                    if bFirst:
                        pFile.write("UnitCombats:\n")
                        bFirst = False
                    pFile.write("\t" + safeConvertToStr(GC.getUnitCombatInfo(j).getDescription()) + "\n")
    else:
        pFile.write("No Units\n")


def writeLog():
    import SystemPaths as SP
    GC = CyGlobalContext()
    MAP = GC.getMap()
    GAME = GC.getGame()
    iActivePlayer = GAME.getActivePlayer()
    playerName = safeConvertToStr(GC.getPlayer(iActivePlayer).getName())

    # Ensure logs directory exists - fully race-safe creation
    log_dir = os.path.join(SP.userDir, "Logs")
    try:
        os.makedirs(log_dir)
    except OSError, e:
        # Handle race condition where directory is created between calls or already exists
        if e.errno == errno.EEXIST:
            pass
        else:
            # If we can't create the directory for other reasons, try writing to user directory directly
            log_dir = SP.userDir

    # Create filename with player info, then sanitize the entire filename
    filename = "%s - Player %d - Turn %d OOSLog.txt" % (playerName, iActivePlayer, GAME.getGameTurn())
    filename = sanitizeFilename(filename)
    szName = os.path.join(log_dir, filename)

    # Initialize pFile as None for safer cleanup
    pFile = None
    try:
        pFile = open(szName, "w")
    except IOError:
        # If we can't open the file, silently fail (logging is optional)
        return

    try:
        # Backup current language
        iLanguage = GAME.getCurrentLanguage()
        # Force english language for logs
        GAME.setCurrentLanguage(0)

        try:
            # Write global data
            _writeGlobals(pFile, GAME, MAP)

            # Player data
            for iPlayer in xrange(GC.getMAX_PLAYERS()):
                pPlayer = GC.getPlayer(iPlayer)
                if pPlayer.isEverAlive():
                    _writePlayerBasic(pFile, pPlayer, iPlayer, GAME, GC)
                    _writeYieldsAndCommerce(pFile, pPlayer, iPlayer, GC)
                    _writeCityInfo(pFile, pPlayer, iPlayer, GC)
                    _writeBonusAndImprovements(pFile, pPlayer, iPlayer, GC)
                    _writeUnitAIInfo(pFile, pPlayer, iPlayer, GC)
                    _writeCityReligionsAndCorporations(pFile, pPlayer, GC)
                    _writeUnitInfo(pFile, pPlayer, iPlayer, GC)
                    # Space at end of player's info
                    pFile.write("\n\n")

        finally:
            # Restore current language even if an error occurs
            GAME.setCurrentLanguage(iLanguage)

    except IOError, e:
        # File I/O errors - disk full, permissions, etc.
        if DEBUG_LOGGING:
            sys.stderr.write("OOSLogger IOError: %s\n" % str(e))
    except OSError, e:
        # OS-level errors - path issues, etc.
        if DEBUG_LOGGING:
            sys.stderr.write("OOSLogger OSError: %s\n" % str(e))
    except Exception, e:
        # Any other unexpected error - fail silently to avoid crashing game
        if DEBUG_LOGGING:
            sys.stderr.write("OOSLogger Exception: %s\n" % str(e))
            import traceback
            traceback.print_exc()
    finally:
        # Always close the file if it was opened
        if pFile is not None:
            try:
                pFile.close()
            except:
                pass


# Unit tests for sanitizeFilename function
def _testSanitizeFilename():
    """Unit tests for sanitizeFilename edge cases."""
    test_cases = [
        ("CON.txt", "_CON.txt"),
        ("NUL", "_NUL"),
        ("my:name?.txt", "my_name_.txt"),
        ("..hidden", "_hidden"),
        ("trailing. ", "trailing"),
        ("multiple   spaces", "multiple_spaces"),
        ("control\x01char\x1f", "control_char_"),
        ("normal.txt", "normal.txt"),
        ("", "Player"),
        ("a" * 300 + ".txt", "a" * 196 + ".txt"),  # Should truncate to 200 chars
        ("COM1", "_COM1"),
        ("lpt9.doc", "_lpt9.doc"),
        ("CONIN$", "_CONIN$"),
        ("valid/\\<>:\"|?*name", "valid_________name"),
    ]

    if DEBUG_LOGGING:
        for input_name, expected in test_cases:
            result = sanitizeFilename(input_name)
            if result == expected:
                sys.stderr.write("PASS: '%s' -> '%s'\n" % (input_name, result))
            else:
                sys.stderr.write("FAIL: '%s' -> '%s' (expected '%s')\n" % (input_name, result, expected))


# Run tests if DEBUG_LOGGING is enabled
if DEBUG_LOGGING:
    _testSanitizeFilename()] +
                             ['COM%d' % i for i in range(1, 10)] +
                             ['LPT%d' % i for i in range(1, 10)])

    def _isReservedName(filename):
        """Check if filename is a Windows reserved name."""
        # Normalize by trimming trailing dots/spaces before comparison
        normalized = filename.rstrip('. ').upper()
        base = normalized.split('.', 1)[0]  # Only split on first dot for efficiency
        return base in _RESERVED_NAMES


    def sanitizeFilename(filename):
        """Remove or replace characters that are invalid in filenames on common OS."""

        # Use translate for better performance - create translation table
        invalid_chars = '<>:"/\\|?*'
        # Python 2.4 compatible translate table creation
        trans_table = string.maketrans(invalid_chars, '_' * len(invalid_chars))
        filename = filename.translate(trans_table)

        # Remove control characters (ASCII 0-31 and 127) and normalize whitespace
        cleaned_chars = []
        for char in filename:
            if ord(char) < 32 or ord(char) == 127:
                cleaned_chars.append('_')
            elif char.isspace():
                # Normalize all whitespace to single space, will be handled below
                cleaned_chars.append(' ')
            else:
                cleaned_chars.append(char)
        filename = ''.join(cleaned_chars)

        # Normalize multiple whitespace/underscores to single underscore
        import re
        filename = re.sub(r'[\s_]+', '_', filename)

        # Handle multiple leading dots (normalize to single safe prefix)
        had_leading_dots = filename.startswith('.')
        filename = filename.lstrip('.')
        if had_leading_dots:
            filename = '_' + filename

        # Handle Windows reserved names
        if _isReservedName(filename):
            filename = '_' + filename

        # Remove trailing dots and spaces (Windows issue)
        filename = filename.rstrip('. ')

        # Clamp length to Windows-safe limit (255 chars, leave some buffer)
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            # Guard against very long extensions
            if len(ext) > 10:
                ext = ext[:10]
            filename = name[:200 - len(ext)] + ext

            # Re-check reserved names after truncation
            if _isReservedName(filename):
                filename = '_' + filename

        # Ensure we have at least one character
        if not filename:
            filename = 'Player'

        return filename


    def _writeGlobals(pFile, GAME, MAP):
        """Write global game data to log file."""
        SEP = "-----------------------------------------------------------------\n"
        pFile.write(2 * SEP + "\tGLOBALS\n" + 2 * SEP + "\n")

        pFile.write("Last MapRand Value: %d\n" % GAME.getMapRand().getSeed())
        pFile.write("Last SorenRand Value: %d\n" % GAME.getSorenRand().getSeed())
        pFile.write("Total num cities: %d\n" % GAME.getNumCities())
        pFile.write("Total population: %d\n" % GAME.getTotalPopulation())
        pFile.write("Total Deals: %d\n" % GAME.getNumDeals())
        pFile.write("Total owned plots: %d\n" % MAP.getOwnedPlots())
        pFile.write("Total num areas: %d\n\n\n" % MAP.getNumAreas())


    def _writePlayerBasic(pFile, pPlayer, iPlayer, GAME, GC):
        """Write basic player data to log file."""
        SEP = "-----------------------------------------------------------------\n"
        pFile.write(2 * SEP + "%s player %d: %s\n" % (['NPC', 'Human'][pPlayer.isHuman()], iPlayer,
                                                      safeConvertToStr(pPlayer.getName())))
        pFile.write("  Civilization: %s\n" % safeConvertToStr(pPlayer.getCivilizationDescriptionKey()))
        pFile.write("  Alive: %s\n" % pPlayer.isAlive())
        pFile.write(2 * SEP + "\n\nBasic data:\n-----------\n")

        pFile.write("Player %d Score: %d\n" % (iPlayer, GAME.getPlayerScore(iPlayer)))
        pFile.write("Player %d Population: %d\n" % (iPlayer, pPlayer.getTotalPopulation()))
        pFile.write("Player %d Total Land: %d\n" % (iPlayer, pPlayer.getTotalLand()))
        pFile.write("Player %d Gold: %d\n" % (iPlayer, pPlayer.getGold()))
        pFile.write("Player %d Assets: %d\n" % (iPlayer, pPlayer.getAssets()))
        pFile.write("Player %d Power: %d\n" % (iPlayer, pPlayer.getPower()))
        pFile.write("Player %d Num Cities: %d\n" % (iPlayer, pPlayer.getNumCities()))
        pFile.write("Player %d Num Units: %d\n" % (iPlayer, pPlayer.getNumUnits()))
        pFile.write("Player %d Num Selection Groups: %d\n" % (iPlayer, pPlayer.getNumSelectionGroups()))
        pFile.write("Player %d Difficulty: %s\n" % (iPlayer, safeConvertToStr(
            GC.getHandicapInfo(pPlayer.getHandicapType()).getDescription())))
        pFile.write("Player %d State Religion: %s\n" % (iPlayer, safeConvertToStr(
            pPlayer.getStateReligionKey())))
        pFile.write("Player %d Culture: %d\n" % (iPlayer, pPlayer.getCulture()))


    def _writeYieldsAndCommerce(pFile, pPlayer, iPlayer, GC):
        """Write yields and commerce data to log file."""
        pFile.write("\n\nYields:\n-------\n")
        for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
            pFile.write("Player %d %s Total Yield: %d\n" % (iPlayer, safeConvertToStr(
                GC.getYieldInfo(iYield).getDescription()), pPlayer.calculateTotalYield(iYield)))

        pFile.write("\n\nCommerce:\n---------\n")
        for iCommerce in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
            pFile.write("Player %d %s Total Commerce: %d\n" % (iPlayer, safeConvertToStr(
                GC.getCommerceInfo(iCommerce).getDescription()), pPlayer.getCommerceRate(
                CommerceTypes(iCommerce))))


    def _writeCityInfo(pFile, pPlayer, iPlayer, GC):
        """Write city information to log file."""
        pFile.write("\n\nCity event history:\n-----------\n")
        if pPlayer.getNumCities():
            pCity, i = pPlayer.firstCity(False)
            while pCity:
                bFirst = True
                for iEvent in xrange(GC.getNumEventInfos()):
                    if pCity.isEventOccured(iEvent):
                        if bFirst:
                            pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                            bFirst = False
                        pFile.write("\t" + safeConvertToStr(GC.getEventInfo(iEvent).getDescription()) + "\n")
                pCity, i = pPlayer.nextCity(i, False)

        pFile.write("\n\nCity Info:\n----------\n")
        if pPlayer.getNumCities():
            pCity, i = pPlayer.firstCity(False)
            while pCity:
                pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                pFile.write("X: %d, Y: %d\n" % (pCity.getX(), pCity.getY()))
                pFile.write("Population: %d\n" % (pCity.getPopulation()))
                iCount = 0
                for iBuilding in xrange(GC.getNumBuildingInfos()):
                    iCount += pCity.hasBuilding(iBuilding)
                pFile.write("Buildings: %d\n" % iCount)
                pFile.write("Improved Plots: %d\n" % (pCity.countNumImprovedPlots()))
                pFile.write("Tiles Worked: %d, Specialists: %d\n" % (pCity.getWorkingPopulation(),
                                                                     pCity.getSpecialistPopulation()))
                pFile.write("Great People: %d\n" % pCity.getNumGreatPeople())
                pFile.write("Good Health: %d, Bad Health: %d\n" % (pCity.goodHealth(), pCity.badHealth(False)))
                pFile.write("Happy Level: %d, Unhappy Level: %d\n" % (pCity.happyLevel(), pCity.unhappyLevel(0)))
                pFile.write("Food: %d\n" % pCity.getFood())
                pCity, i = pPlayer.nextCity(i, False)
        else:
            pFile.write("No Cities\n")


    def _writeBonusAndImprovements(pFile, pPlayer, iPlayer, GC):
        """Write bonus and improvement information to log file."""
        pFile.write("\n\nBonus Info:\n-----------\n")
        for iBonus in xrange(GC.getNumBonusInfos()):
            szTemp = safeConvertToStr(GC.getBonusInfo(iBonus).getDescription())
            pFile.write("Player %d, %s, Number Available: %d\n" % (iPlayer, szTemp,
                                                                   pPlayer.getNumAvailableBonuses(iBonus)))
            pFile.write("Player %d, %s, Import: %d\n" % (iPlayer, szTemp, pPlayer.getBonusImport(iBonus)))
            pFile.write("Player %d, %s, Export: %d\n\n" % (iPlayer, szTemp, pPlayer.getBonusExport(iBonus)))

        pFile.write("\n\nImprovement Info:\n-----------------\n")
        for iImprovement in xrange(GC.getNumImprovementInfos()):
            pFile.write("Player %d, %s, Improvement count: %d\n" % (iPlayer, safeConvertToStr(
                GC.getImprovementInfo(iImprovement).getDescription()), pPlayer.getImprovementCount(iImprovement)))

        pFile.write("\n\nBuilding Info:\n--------------------\n")
        for iBuilding in xrange(GC.getNumBuildingInfos()):
            pFile.write("Player %d, %s, Building class count plus making: %d\n" % (iPlayer,
                                                                                   safeConvertToStr(
                                                                                       GC.getBuildingInfo(
                                                                                           iBuilding).getDescription()),
                                                                                   pPlayer.getBuildingCountPlusMaking(
                                                                                       iBuilding)))

        pFile.write("\n\nUnit Class Info:\n--------------------\n")
        for iUnit in xrange(GC.getNumUnitInfos()):
            pFile.write("Player %d, %s, Unit class count plus training: %d\n" % (iPlayer,
                                                                                 safeConvertToStr(
                                                                                     GC.getUnitInfo(
                                                                                         iUnit).getDescription()),
                                                                                 pPlayer.getUnitCountPlusMaking(iUnit)))


    def _writeUnitAIInfo(pFile, pPlayer, iPlayer, GC):
        """Write UnitAI type information to log file."""
        pFile.write("\n\nUnitAI Types Info:\n------------------\n")
        for iUnitAIType in xrange(int(UnitAITypes.NUM_UNITAI_TYPES)):
            try:
                unitai_info = GC.getUnitAIInfo(iUnitAIType)
                if hasattr(unitai_info, 'getDescription'):
                    unitai_label = safeConvertToStr(unitai_info.getDescription())
                else:
                    unitai_label = safeConvertToStr(unitai_info.getType())
            except AttributeError, e:
                unitai_label = "UnitAI_%d_ATTR_ERR_%s" % (iUnitAIType, str(e).replace(' ', '_')[:20])
            except Exception, e:
                # Include sanitized exception details for diagnosis
                error_msg = str(e).replace(' ', '_').replace('\n', '_')[:30]
                unitai_label = "UnitAI_%d_ERR_%s" % (iUnitAIType, error_msg)

            try:
                count = pPlayer.AI_totalUnitAIs(UnitAITypes(iUnitAIType))
            except Exception, e:
                count = -1  # Error indicator in count

            pFile.write("Player %d, %s, Unit AI Type count: %d\n" % (iPlayer, unitai_label, count))


    def _writeCityReligionsAndCorporations(pFile, pPlayer, GC):
        """Write city religions and corporations to log file."""
        pFile.write("\n\nCity Religions:\n-----------\n")
        if pPlayer.getNumCities():
            pCity, i = pPlayer.firstCity(False)
            while pCity:
                bFirst = True
                for iReligion in xrange(GC.getNumReligionInfos()):
                    if pCity.isHasReligion(iReligion):
                        if bFirst:
                            pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                            bFirst = False
                        pFile.write("\t" + safeConvertToStr(GC.getReligionInfo(iReligion).getDescription()) + "\n")
                pCity, i = pPlayer.nextCity(i, False)

        pFile.write("\n\nCity Corporations:\n-----------\n")
        if pPlayer.getNumCities():
            pCity, i = pPlayer.firstCity(False)
            while pCity:
                bFirst = True
                for iCorporation in xrange(GC.getNumCorporationInfos()):
                    if pCity.isHasCorporation(iCorporation):
                        if bFirst:
                            pFile.write("City: %s\n" % safeConvertToStr(pCity.getName()))
                            bFirst = False
                        pFile.write(
                            "\t" + safeConvertToStr(GC.getCorporationInfo(iCorporation).getDescription()) + "\n")
                pCity, i = pPlayer.nextCity(i, False)


    def _writeUnitInfo(pFile, pPlayer, iPlayer, GC):
        """Write unit information to log file."""
        pFile.write("\n\nUnit Info:\n----------\n")
        if pPlayer.getNumUnits():
            for pUnit in pPlayer.units():
                pFile.write("Player %d, Unit ID: %d, %s\n" % (iPlayer, pUnit.getID(),
                                                              safeConvertToStr(pUnit.getName())))
                pFile.write("X: %d, Y: %d\nDamage: %d\n" % (pUnit.getX(), pUnit.getY(), pUnit.getDamage()))
                pFile.write("Experience: %d\nLevel: %d\n" % (pUnit.getExperience(), pUnit.getLevel()))
                bFirst = True
                for j in xrange(GC.getNumPromotionInfos()):
                    if pUnit.isHasPromotion(j):
                        if bFirst:
                            pFile.write("Promotions:\n")
                            bFirst = False
                        pFile.write("\t" + safeConvertToStr(GC.getPromotionInfo(j).getDescription()) + "\n")
                bFirst = True
                for j in xrange(GC.getNumUnitCombatInfos()):
                    if pUnit.isHasUnitCombat(j):
                        if bFirst:
                            pFile.write("UnitCombats:\n")
                            bFirst = False
                        pFile.write("\t" + safeConvertToStr(GC.getUnitCombatInfo(j).getDescription()) + "\n")
        else:
            pFile.write("No Units\n")


    def writeLog():
        import SystemPaths as SP
        GC = CyGlobalContext()
        MAP = GC.getMap()
        GAME = GC.getGame()
        iActivePlayer = GAME.getActivePlayer()
        playerName = safeConvertToStr(GC.getPlayer(iActivePlayer).getName())

        # Ensure logs directory exists - fully race-safe creation
        log_dir = os.path.join(SP.userDir, "Logs")
        try:
            os.makedirs(log_dir)
        except OSError, e:
            # Handle race condition where directory is created between calls or already exists
            if e.errno == errno.EEXIST:
                pass
            else:
                # If we can't create the directory for other reasons, try writing to user directory directly
                log_dir = SP.userDir

        # Create filename with player info, then sanitize the entire filename
        filename = "%s - Player %d - Turn %d OOSLog.txt" % (playerName, iActivePlayer, GAME.getGameTurn())
        filename = sanitizeFilename(filename)
        szName = os.path.join(log_dir, filename)

        # Initialize pFile as None for safer cleanup
        pFile = None
        try:
            pFile = open(szName, "w")
        except IOError:
            # If we can't open the file, silently fail (logging is optional)
            return

        try:
            # Backup current language
            iLanguage = GAME.getCurrentLanguage()
            # Force english language for logs
            GAME.setCurrentLanguage(0)

            try:
                # Write global data
                _writeGlobals(pFile, GAME, MAP)

                # Player data
                for iPlayer in xrange(GC.getMAX_PLAYERS()):
                    pPlayer = GC.getPlayer(iPlayer)
                    if pPlayer.isEverAlive():
                        _writePlayerBasic(pFile, pPlayer, iPlayer, GAME, GC)
                        _writeYieldsAndCommerce(pFile, pPlayer, iPlayer, GC)
                        _writeCityInfo(pFile, pPlayer, iPlayer, GC)
                        _writeBonusAndImprovements(pFile, pPlayer, iPlayer, GC)
                        _writeUnitAIInfo(pFile, pPlayer, iPlayer, GC)
                        _writeCityReligionsAndCorporations(pFile, pPlayer, GC)
                        _writeUnitInfo(pFile, pPlayer, iPlayer, GC)
                        # Space at end of player's info
                        pFile.write("\n\n")

            finally:
                # Restore current language even if an error occurs
                GAME.setCurrentLanguage(iLanguage)

        except IOError, e:
            # File I/O errors - disk full, permissions, etc.
            if DEBUG_LOGGING:
                sys.stderr.write("OOSLogger IOError: %s\n" % str(e))
        except OSError, e:
            # OS-level errors - path issues, etc.
            if DEBUG_LOGGING:
                sys.stderr.write("OOSLogger OSError: %s\n" % str(e))
        except Exception, e:
            # Any other unexpected error - fail silently to avoid crashing game
            if DEBUG_LOGGING:
                sys.stderr.write("OOSLogger Exception: %s\n" % str(e))
                import traceback
                traceback.print_exc()
        finally:
            # Always close the file if it was opened
            if pFile is not None:
                try:
                    pFile.close()
                except:
                    pass


    # Unit tests for sanitizeFilename function
    def _testSanitizeFilename():
        """Unit tests for sanitizeFilename edge cases."""
        test_cases = [
            ("CON.txt", "_CON.txt"),
            ("NUL", "_NUL"),
            ("my:name?.txt", "my_name_.txt"),
            ("..hidden", "_hidden"),
            ("trailing. ", "trailing"),
            ("multiple   spaces", "multiple_spaces"),
            ("control\x01char\x1f", "control_char_"),
            ("normal.txt", "normal.txt"),
            ("", "Player"),
            ("a" * 300 + ".txt", "a" * 196 + ".txt"),  # Should truncate to 200 chars
            ("COM1", "_COM1"),
            ("lpt9.doc", "_lpt9.doc"),
            ("CONIN$", "_CONIN$"),
            ("valid/\\<>:\"|?*name", "valid_________name"),
        ]

        if DEBUG_LOGGING:
            for input_name, expected in test_cases:
                result = sanitizeFilename(input_name)
                if result == expected:
                    sys.stderr.write("PASS: '%s' -> '%s'\n" % (input_name, result))
                else:
                    sys.stderr.write("FAIL: '%s' -> '%s' (expected '%s')\n" % (input_name, result, expected))


    # Run tests if DEBUG_LOGGING is enabled
    if DEBUG_LOGGING:
        _testSanitizeFilename()