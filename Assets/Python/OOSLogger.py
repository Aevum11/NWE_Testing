# OOS logger: writes the info contained in the sync checksum to a log file
from CvPythonExtensions import CyGlobalContext, YieldTypes, CommerceTypes, UnitAITypes
import os


def safeConvertToStr(obj):
    """Safely convert any object to string, handling potential encoding issues."""
    try:
        import TextUtil
        result = TextUtil.convertToStr(obj)
        # Test if the result can be used safely by attempting string operations
        # In Python 2.4, this will help catch unicode/str mixing issues
        temp = str(result)
        return result
    except (UnicodeError, UnicodeDecodeError, UnicodeEncodeError):
        # If TextUtil fails with unicode issues, try fallbacks
        try:
            if hasattr(obj, 'encode'):
                # It's likely a unicode object, encode to ASCII with replacement
                return obj.encode('ascii', 'replace')
            else:
                # Not a unicode object, try direct conversion
                return str(obj)
        except:
            return "[Name conversion failed]"
    except (ImportError, AttributeError):
        # TextUtil module missing or doesn't have convertToStr method
        try:
            return str(obj)
        except:
            return "[Name conversion failed]"
    except:
        # Any other error from TextUtil
        try:
            return str(obj)
        except:
            return "[Name conversion failed]"


def writeLog():
    import SystemPaths as SP
    GC = CyGlobalContext()
    MAP = GC.getMap()
    GAME = GC.getGame()
    iActivePlayer = GAME.getActivePlayer()
    szName = safeConvertToStr(GC.getActivePlayer().getName())

    # Ensure logs directory exists
    log_dir = SP.userDir + "\\Logs"
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    except OSError:
        # If we can't create the directory, try writing to user directory directly
        log_dir = SP.userDir

    szName = log_dir + "\\%s - Player %d - Turn %d OOSLog.txt" % (szName, iActivePlayer, GAME.getGameTurn())

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

                    log_content.append(2 * SEP + "%s player %d: %s\n" % (['NPC', 'Human'][pPlayer.isHuman()], iPlayer,
                                                                         TextUtil.convertToStr(pPlayer.getName())))
                    log_content.append(
                        "  Civilization: %s\n" % TextUtil.convertToStr(pPlayer.getCivilizationDescriptionKey()))
                    log_content.append("  Alive: %s\n" % pPlayer.isAlive())

                    log_content.append(2 * SEP + "\n\nBasic data:\n-----------\n")

                    log_content.append("Player %d Score: %d\n" % (iPlayer, GAME.getPlayerScore(iPlayer)))
                    log_content.append("Player %d Population: %d\n" % (iPlayer, pPlayer.getTotalPopulation()))
                    log_content.append("Player %d Total Land: %d\n" % (iPlayer, pPlayer.getTotalLand()))
                    log_content.append("Player %d Gold: %d\n" % (iPlayer, pPlayer.getGold()))
                    log_content.append("Player %d Assets: %d\n" % (iPlayer, pPlayer.getAssets()))
                    log_content.append("Player %d Power: %d\n" % (iPlayer, pPlayer.getPower()))
                    log_content.append("Player %d Num Cities: %d\n" % (iPlayer, pPlayer.getNumCities()))
                    log_content.append("Player %d Num Units: %d\n" % (iPlayer, pPlayer.getNumUnits()))
                    log_content.append(
                        "Player %d Num Selection Groups: %d\n" % (iPlayer, pPlayer.getNumSelectionGroups()))
                    log_content.append("Player %d Difficulty: %d\n" % (iPlayer, pPlayer.getHandicapType()))
                    log_content.append("Player %d State Religion: %s\n" % (iPlayer, TextUtil.convertToStr(
                        pPlayer.getStateReligionKey())))
                    log_content.append("Player %d Culture: %d\n" % (iPlayer, pPlayer.getCulture()))

                    log_content.append("\n\nYields:\n-------\n")

                    for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
                        log_content.append("Player %d %s Total Yield: %d\n" % (iPlayer, TextUtil.convertToStr(
                            GC.getYieldInfo(iYield).getDescription()), pPlayer.calculateTotalYield(iYield)))

                    log_content.append("\n\nCommerce:\n---------\n")

                    for iCommerce in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
                        log_content.append("Player %d %s Total Commerce: %d\n" % (iPlayer, TextUtil.convertToStr(
                            GC.getCommerceInfo(iCommerce).getDescription()), pPlayer.getCommerceRate(
                            CommerceTypes(iCommerce))))

                    log_content.append("\n\nCity event history:\n-----------\n")

                    if pPlayer.getNumCities():
                        pCity, i = pPlayer.firstCity(False)
                        while pCity:
                            bFirst = True
                            for iEvent in xrange(GC.getNumEventInfos()):
                                if pCity.isEventOccured(iEvent):
                                    if bFirst:
                                        log_content.append("City: %s\n" % TextUtil.convertToStr(pCity.getName()))
                                        bFirst = False
                                    log_content.append(
                                        "\t" + TextUtil.convertToStr(GC.getEventInfo(iEvent).getDescription()) + "\n")
                            pCity, i = pPlayer.nextCity(i, False)

                    log_content.append("\n\nCity Info:\n----------\n")

                    if pPlayer.getNumCities():
                        pCity, i = pPlayer.firstCity(False)
                        while pCity:
                            log_content.append("City: %s\n" % TextUtil.convertToStr(pCity.getName()))
                            log_content.append("X: %d, Y: %d\n" % (pCity.getX(), pCity.getY()))
                            log_content.append("Population: %d\n" % (pCity.getPopulation()))
                            iCount = 0
                            for iBuilding in xrange(GC.getNumBuildingInfos()):
                                iCount += pCity.hasBuilding(iBuilding)
                            log_content.append("Buildings: %d\n" % iCount)
                            log_content.append("Improved Plots: %d\n" % (pCity.countNumImprovedPlots()))
                            log_content.append("Tiles Worked: %d, Specialists: %d\n" % (pCity.getWorkingPopulation(),
                                                                                        pCity.getSpecialistPopulation()))
                            log_content.append("Great People: %d\n" % pCity.getNumGreatPeople())
                            log_content.append(
                                "Good Health: %d, Bad Health: %d\n" % (pCity.goodHealth(), pCity.badHealth(False)))
                            log_content.append(
                                "Happy Level: %d, Unhappy Level: %d\n" % (pCity.happyLevel(), pCity.unhappyLevel(0)))
                            log_content.append("Food: %d\n" % pCity.getFood())
                            pCity, i = pPlayer.nextCity(i, False)
                    else:
                        log_content.append("No Cities")

                    log_content.append("\n\nBonus Info:\n-----------\n")

                    for iBonus in xrange(GC.getNumBonusInfos()):
                        szTemp = TextUtil.convertToStr(GC.getBonusInfo(iBonus).getDescription())
                        log_content.append("Player %d, %s, Number Available: %d\n" % (iPlayer, szTemp,
                                                                                      pPlayer.getNumAvailableBonuses(
                                                                                          iBonus)))
                        log_content.append(
                            "Player %d, %s, Import: %d\n" % (iPlayer, szTemp, pPlayer.getBonusImport(iBonus)))
                        log_content.append(
                            "Player %d, %s, Export: %d\n\n" % (iPlayer, szTemp, pPlayer.getBonusExport(iBonus)))

                    log_content.append("\n\nImprovement Info:\n-----------------\n")

                    for iImprovement in xrange(GC.getNumImprovementInfos()):
                        log_content.append("Player %d, %s, Improvement count: %d\n" % (iPlayer, TextUtil.convertToStr(
                            GC.getImprovementInfo(iImprovement).getDescription()), pPlayer.getImprovementCount(
                            iImprovement)))

                    log_content.append("\n\nBuilding Info:\n--------------------\n")

                    for iBuilding in xrange(GC.getNumBuildingInfos()):
                        log_content.append("Player %d, %s, Building class count plus making: %d\n" % (iPlayer,
                                                                                                      TextUtil.convertToStr(
                                                                                                          GC.getBuildingInfo(
                                                                                                              iBuilding).getDescription()),
                                                                                                      pPlayer.getBuildingCountPlusMaking(
                                                                                                          iBuilding)))

                    log_content.append("\n\nUnit Class Info:\n--------------------\n")

                    for iUnit in xrange(GC.getNumUnitInfos()):
                        log_content.append("Player %d, %s, Unit class count plus training: %d\n" % (iPlayer,
                                                                                                    TextUtil.convertToStr(
                                                                                                        GC.getUnitInfo(
                                                                                                            iUnit).getDescription()),
                                                                                                    pPlayer.getUnitCountPlusMaking(
                                                                                                        iUnit)))

                    log_content.append("\n\nUnitAI Types Info:\n------------------\n")

                    for iUnitAIType in xrange(int(UnitAITypes.NUM_UNITAI_TYPES)):
                        log_content.append("Player %d, %s, Unit AI Type count: %d\n" % (iPlayer, GC.getUnitAIInfo(
                            iUnitAIType).getType(), pPlayer.AI_totalUnitAIs(UnitAITypes(iUnitAIType))))

                    log_content.append("\n\nCity Religions:\n-----------\n")

                    if pPlayer.getNumCities():
                        pCity, i = pPlayer.firstCity(False)
                        while pCity:
                            bFirst = True
                            for iReligion in xrange(GC.getNumReligionInfos()):
                                if pCity.isHasReligion(iReligion):
                                    if bFirst:
                                        log_content.append("City: %s\n" % TextUtil.convertToStr(pCity.getName()))
                                        bFirst = False
                                    log_content.append("\t" + TextUtil.convertToStr(
                                        GC.getReligionInfo(iReligion).getDescription()) + "\n")
                            pCity, i = pPlayer.nextCity(i, False)

                    log_content.append("\n\nCity Corporations:\n-----------\n")

                    if pPlayer.getNumCities():
                        pCity, i = pPlayer.firstCity(False)
                        while pCity:
                            bFirst = True
                            for iCorporation in xrange(GC.getNumCorporationInfos()):
                                if pCity.isHasCorporation(iCorporation):
                                    if bFirst:
                                        log_content.append("City: %s\n" % TextUtil.convertToStr(pCity.getName()))
                                        bFirst = False
                                    log_content.append("\t" + TextUtil.convertToStr(
                                        GC.getCorporationInfo(iCorporation).getDescription()) + "\n")
                            pCity, i = pPlayer.nextCity(i, False)

                    log_content.append("\n\nUnit Info:\n----------\n")

                    if pPlayer.getNumUnits():
                        for pUnit in pPlayer.units():
                            log_content.append("Player %d, Unit ID: %d, %s\n" % (iPlayer, pUnit.getID(),
                                                                                 TextUtil.convertToStr(
                                                                                     pUnit.getName())))
                            log_content.append(
                                "X: %d, Y: %d\nDamage: %d\n" % (pUnit.getX(), pUnit.getY(), pUnit.getDamage()))
                            log_content.append(
                                "Experience: %d\nLevel: %d\n" % (pUnit.getExperience(), pUnit.getLevel()))
                            bFirst = True
                            for j in xrange(GC.getNumPromotionInfos()):
                                if pUnit.isHasPromotion(j):
                                    if bFirst:
                                        log_content.append("Promotions:\n")
                                        bFirst = False
                                    log_content.append(
                                        "\t" + TextUtil.convertToStr(GC.getPromotionInfo(j).getDescription()) + "\n")
                            bFirst = True
                            for j in xrange(GC.getNumUnitCombatInfos()):
                                if pUnit.isHasUnitCombat(j):
                                    if bFirst:
                                        log_content.append("UnitCombats:\n")
                                        bFirst = False
                                    log_content.append(
                                        "\t" + TextUtil.convertToStr(GC.getUnitCombatInfo(j).getDescription()) + "\n")
                    else:
                        log_content.append("No Units")
                    # Space at end of player's info
                    log_content.append("\n\n")

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