# OOS logger: writes the info contained in the sync checksum to a log file
from CvPythonExtensions import CyGlobalContext, YieldTypes, CommerceTypes, UnitAITypes
import os


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
        # Safer short-circuit: explicit unicode check when available
        try:
            # Try to access unicode type safely
            unicode_type = type(u'')
            if isinstance(obj, unicode_type):
                return obj.encode('ascii', 'replace')
        except NameError:
            # unicode not available, fall back to duck-typing heuristic
            pass

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


def _isReservedName(filename):
    """Check if filename is a Windows reserved name."""
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + ['COM%d' % i for i in range(1, 10)] + ['LPT%d' % i for i in
                                                                                           range(1, 10)]
    name_upper = filename.upper()
    return name_upper in reserved_names or name_upper.split('.')[0] in reserved_names


def sanitizeFilename(filename):
    """Remove or replace characters that are invalid in filenames on common OS."""

    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove control characters (ASCII 0-31 and 127)
    filename = ''.join(char if ord(char) >= 32 and ord(char) != 127 else '_' for char in filename)

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


def writeLog():
    import SystemPaths as SP
    GC = CyGlobalContext()
    MAP = GC.getMap()
    GAME = GC.getGame()
    iActivePlayer = GAME.getActivePlayer()
    playerName = safeConvertToStr(GC.getPlayer(iActivePlayer).getName())

    # Ensure logs directory exists
    log_dir = os.path.join(SP.userDir, "Logs")
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    except OSError:
        # If we can't create the directory, try writing to user directory directly
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
        SEP = "-----------------------------------------------------------------\n"

        # Backup current language
        iLanguage = GAME.getCurrentLanguage()
        # Force english language for logs
        GAME.setCurrentLanguage(0)

        try:
            # Global data
            pFile.write(2 * SEP + "\tGLOBALS\n" + 2 * SEP + "\n")

            pFile.write("Last MapRand Value: %d\n" % GAME.getMapRand().getSeed())
            pFile.write("Last SorenRand Value: %d\n" % GAME.getSorenRand().getSeed())

            pFile.write("Total num cities: %d\n" % GAME.getNumCities())
            pFile.write("Total population: %d\n" % GAME.getTotalPopulation())
            pFile.write("Total Deals: %d\n" % GAME.getNumDeals())

            pFile.write("Total owned plots: %d\n" % MAP.getOwnedPlots())
            pFile.write("Total num areas: %d\n\n\n" % MAP.getNumAreas())

            # Player data
            for iPlayer in xrange(GC.getMAX_PLAYERS()):
                pPlayer = GC.getPlayer(iPlayer)
                if pPlayer.isEverAlive():

                    pFile.write(2 * SEP + "%s player %d: %s\n" % (['NPC', 'Human'][pPlayer.isHuman()], iPlayer,
                                                                  safeConvertToStr(pPlayer.getName())))
                    pFile.write(
                        "  Civilization: %s\n" % safeConvertToStr(pPlayer.getCivilizationDescriptionKey()))
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
                    pFile.write(
                        "Player %d Num Selection Groups: %d\n" % (iPlayer, pPlayer.getNumSelectionGroups()))
                    pFile.write("Player %d Difficulty: %s\n" % (iPlayer, safeConvertToStr(
                        GC.getHandicapInfo(pPlayer.getHandicapType()).getDescription())))
                    pFile.write("Player %d State Religion: %s\n" % (iPlayer, safeConvertToStr(
                        pPlayer.getStateReligionKey())))
                    pFile.write("Player %d Culture: %d\n" % (iPlayer, pPlayer.getCulture()))

                    pFile.write("\n\nYields:\n-------\n")

                    for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
                        pFile.write("Player %d %s Total Yield: %d\n" % (iPlayer, safeConvertToStr(
                            GC.getYieldInfo(iYield).getDescription()), pPlayer.calculateTotalYield(iYield)))

                    pFile.write("\n\nCommerce:\n---------\n")

                    for iCommerce in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
                        pFile.write("Player %d %s Total Commerce: %d\n" % (iPlayer, safeConvertToStr(
                            GC.getCommerceInfo(iCommerce).getDescription()), pPlayer.getCommerceRate(
                            CommerceTypes(iCommerce))))

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
                                    pFile.write(
                                        "\t" + safeConvertToStr(GC.getEventInfo(iEvent).getDescription()) + "\n")
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
                            pFile.write(
                                "Good Health: %d, Bad Health: %d\n" % (pCity.goodHealth(), pCity.badHealth(False)))
                            pFile.write(
                                "Happy Level: %d, Unhappy Level: %d\n" % (pCity.happyLevel(), pCity.unhappyLevel(0)))
                            pFile.write("Food: %d\n" % pCity.getFood())
                            pCity, i = pPlayer.nextCity(i, False)
                    else:
                        pFile.write("No Cities\n")

                    pFile.write("\n\nBonus Info:\n-----------\n")

                    for iBonus in xrange(GC.getNumBonusInfos()):
                        szTemp = safeConvertToStr(GC.getBonusInfo(iBonus).getDescription())
                        pFile.write("Player %d, %s, Number Available: %d\n" % (iPlayer, szTemp,
                                                                               pPlayer.getNumAvailableBonuses(
                                                                                   iBonus)))
                        pFile.write(
                            "Player %d, %s, Import: %d\n" % (iPlayer, szTemp, pPlayer.getBonusImport(iBonus)))
                        pFile.write(
                            "Player %d, %s, Export: %d\n\n" % (iPlayer, szTemp, pPlayer.getBonusExport(iBonus)))

                    pFile.write("\n\nImprovement Info:\n-----------------\n")

                    for iImprovement in xrange(GC.getNumImprovementInfos()):
                        pFile.write("Player %d, %s, Improvement count: %d\n" % (iPlayer, safeConvertToStr(
                            GC.getImprovementInfo(iImprovement).getDescription()), pPlayer.getImprovementCount(
                            iImprovement)))

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
                                                                                             pPlayer.getUnitCountPlusMaking(
                                                                                                 iUnit)))

                    pFile.write("\n\nUnitAI Types Info:\n------------------\n")

                    for iUnitAIType in xrange(int(UnitAITypes.NUM_UNITAI_TYPES)):
                        try:
                            unitai_info = GC.getUnitAIInfo(iUnitAIType)
                            if hasattr(unitai_info, 'getDescription'):
                                unitai_label = safeConvertToStr(unitai_info.getDescription())
                            else:
                                unitai_label = safeConvertToStr(unitai_info.getType())
                        except AttributeError:
                            unitai_label = "UnitAI_%d" % iUnitAIType
                        except Exception:
                            # Don't skip logging entirely; use placeholder with error indication
                            unitai_label = "UnitAI_%d_ERROR" % iUnitAIType

                        try:
                            count = pPlayer.AI_totalUnitAIs(UnitAITypes(iUnitAIType))
                        except Exception:
                            count = -1  # Error indicator in count

                        pFile.write("Player %d, %s, Unit AI Type count: %d\n" % (iPlayer, unitai_label, count))

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
                                    pFile.write("\t" + safeConvertToStr(
                                        GC.getReligionInfo(iReligion).getDescription()) + "\n")
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
                                    pFile.write("\t" + safeConvertToStr(
                                        GC.getCorporationInfo(iCorporation).getDescription()) + "\n")
                            pCity, i = pPlayer.nextCity(i, False)

                    pFile.write("\n\nUnit Info:\n----------\n")

                    if pPlayer.getNumUnits():
                        for pUnit in pPlayer.units():
                            pFile.write("Player %d, Unit ID: %d, %s\n" % (iPlayer, pUnit.getID(),
                                                                          safeConvertToStr(
                                                                              pUnit.getName())))
                            pFile.write(
                                "X: %d, Y: %d\nDamage: %d\n" % (pUnit.getX(), pUnit.getY(), pUnit.getDamage()))
                            pFile.write(
                                "Experience: %d\nLevel: %d\n" % (pUnit.getExperience(), pUnit.getLevel()))
                            bFirst = True
                            for j in xrange(GC.getNumPromotionInfos()):
                                if pUnit.isHasPromotion(j):
                                    if bFirst:
                                        pFile.write("Promotions:\n")
                                        bFirst = False
                                    pFile.write(
                                        "\t" + safeConvertToStr(GC.getPromotionInfo(j).getDescription()) + "\n")
                            bFirst = True
                            for j in xrange(GC.getNumUnitCombatInfos()):
                                if pUnit.isHasUnitCombat(j):
                                    if bFirst:
                                        pFile.write("UnitCombats:\n")
                                        bFirst = False
                                    pFile.write(
                                        "\t" + safeConvertToStr(GC.getUnitCombatInfo(j).getDescription()) + "\n")
                    else:
                        pFile.write("No Units\n")
                    # Space at end of player's info
                    pFile.write("\n\n")

        finally:
            # Restore current language even if an error occurs
            GAME.setCurrentLanguage(iLanguage)

    except IOError, e:
        # File I/O errors - disk full, permissions, etc.
        # Could log to Windows event log or create a simple error file, but for now fail silently
        pass
    except OSError, e:
        # OS-level errors - path issues, etc.
        pass
    except Exception, e:
        # Any other unexpected error - fail silently to avoid crashing game
        # In a development environment, you might want to uncomment the next line:
        # import traceback; traceback.print_exc()
        pass
    finally:
        # Always close the file if it was opened
        if pFile is not None:
            try:
                pFile.close()
            except:
                pass