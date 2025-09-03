# OOS logger: writes the info contained in the sync checksum to a log file
# Memory-optimized version for 32-bit Python 2.4 (Civ4 C2C)
from CvPythonExtensions import CyGlobalContext, YieldTypes, CommerceTypes, UnitAITypes


def writeLog():
    import SystemPaths as SP
    import TextUtil
    import gc

    GC = CyGlobalContext()
    MAP = GC.getMap()
    GAME = GC.getGame()
    iActivePlayer = GAME.getActivePlayer()

    # Convert name once and reuse; derive from iActivePlayer to avoid API ambiguity
    pActive = GC.getPlayer(iActivePlayer)
    szPlayerName = TextUtil.convertToStr(pActive.getName())
    # Filesystem-safe filename and portable path
    safeName = ''.join(c if (c.isalnum() or c in (' ', '-', '_', '.')) else '_' for c in szPlayerName)
    log_dir = os.path.join(SP.userDir, "Logs")
    if not os.path.isdir(log_dir):
        try:
            os.makedirs(log_dir)
        except OSError:
            pass  # best effort
    szFileName = os.path.join(log_dir, "%s - Player %d - Turn %d OOSLog.txt" % (
        safeName, iActivePlayer, GAME.getGameTurn()))

    # Use list to buffer output - more memory efficient than string concatenation
    output = []

    # Reusable separator constant
    SEP = "-----------------------------------------------------------------\n"
    SEP2 = SEP + SEP

    # Backup current language
    iLanguage = GAME.getCurrentLanguage()
    # Force english language for logs
    GAME.setCurrentLanguage(0)

    try:
        # Global data section
        output.append(SEP2)
        output.append("\tGLOBALS\n")
        output.append(SEP2)
        output.append("\n")

        # Use direct formatting to avoid temporary strings
        output.append("MapRand Seed: %d\n" % GAME.getMapRand().getSeed())
        output.append("SorenRand Seed: %d\n" % GAME.getSorenRand().getSeed())
        output.append("Total num cities: %d\n" % GAME.getNumCities())
        output.append("Total population: %d\n" % GAME.getTotalPopulation())
        output.append("Total Deals: %d\n" % GAME.getNumDeals())
        output.append("Total owned plots: %d\n" % MAP.getOwnedPlots())
        output.append("Total num areas: %d\n\n\n" % MAP.getNumAreas())

        # Player data - process each player
        for iPlayer in xrange(GC.getMAX_PLAYERS()):
            pPlayer = GC.getPlayer(iPlayer)
            if not pPlayer.isEverAlive():
                continue

            # Cache frequently used values
            playerName = TextUtil.convertToStr(pPlayer.getName())
            isHuman = pPlayer.isHuman()

            # Header
            output.append(SEP2)
            if isHuman:
                output.append("Human player %d: %s\n" % (iPlayer, playerName))
            else:
                output.append("NPC player %d: %s\n" % (iPlayer, playerName))
            output.append("  Civilization: %s\n" % TextUtil.convertToStr(pPlayer.getCivilizationDescriptionKey()))
            output.append("  Alive: %s\n" % pPlayer.isAlive())
            output.append(SEP2)
            output.append("\n\nBasic data:\n-----------\n")

            # Basic data - batch similar operations
            output.append("Player %d Score: %d\n" % (iPlayer, GAME.getPlayerScore(iPlayer)))
            output.append("Player %d Population: %d\n" % (iPlayer, pPlayer.getTotalPopulation()))
            output.append("Player %d Total Land: %d\n" % (iPlayer, pPlayer.getTotalLand()))
            output.append("Player %d Gold: %d\n" % (iPlayer, pPlayer.getGold()))
            output.append("Player %d Assets: %d\n" % (iPlayer, pPlayer.getAssets()))
            output.append("Player %d Power: %d\n" % (iPlayer, pPlayer.getPower()))
            output.append("Player %d Num Cities: %d\n" % (iPlayer, pPlayer.getNumCities()))
            output.append("Player %d Num Units: %d\n" % (iPlayer, pPlayer.getNumUnits()))
            output.append("Player %d Num Selection Groups: %d\n" % (iPlayer, pPlayer.getNumSelectionGroups()))
            output.append("Player %d Difficulty: %d\n" % (iPlayer, pPlayer.getHandicapType()))

            # State religion - handle potential None
            stateReligion = pPlayer.getStateReligionKey()
            if stateReligion:
                output.append("Player %d State Religion: %s\n" % (iPlayer, TextUtil.convertToStr(stateReligion)))
            else:
                output.append("Player %d State Religion: None\n" % iPlayer)

            output.append("Player %d Culture: %d\n" % (iPlayer, pPlayer.getCulture()))

            # Yields section
            output.append("\n\nYields:\n-------\n")
            for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
                yieldDesc = TextUtil.convertToStr(GC.getYieldInfo(iYield).getDescription())
                output.append(
                    "Player %d %s Total Yield: %d\n" % (iPlayer, yieldDesc, pPlayer.calculateTotalYield(iYield)))

            # Commerce section
            output.append("\n\nCommerce:\n---------\n")
            for iCommerce in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
                commerceDesc = TextUtil.convertToStr(GC.getCommerceInfo(iCommerce).getDescription())
                output.append("Player %d %s Total Commerce: %d\n" % (iPlayer, commerceDesc,
                                                                     pPlayer.getCommerceRate(CommerceTypes(iCommerce))))

            # Process cities if any exist
            if pPlayer.getNumCities():
                # City event history
                output.append("\n\nCity event history:\n-----------\n")
                pCity, i = pPlayer.firstCity(False)
                while pCity:
                    cityEvents = []
                    cityName = None

                    # Collect events for this city
                    for iEvent in xrange(GC.getNumEventInfos()):
                        if pCity.isEventOccured(iEvent):
                            if cityName is None:
                                cityName = TextUtil.convertToStr(pCity.getName())
                            cityEvents.append(
                                "\t%s\n" % TextUtil.convertToStr(GC.getEventInfo(iEvent).getDescription()))

                    # Write if events found
                    if cityEvents:
                        output.append("City: %s\n" % cityName)
                        output.extend(cityEvents)

                    pCity, i = pPlayer.nextCity(i, False)

                # City info section
                output.append("\n\nCity Info:\n----------\n")
                pCity, i = pPlayer.firstCity(False)
                while pCity:
                    output.append("City: %s\n" % TextUtil.convertToStr(pCity.getName()))
                    output.append("X: %d, Y: %d\n" % (pCity.getX(), pCity.getY()))
                    output.append("Population: %d\n" % pCity.getPopulation())

                    # Count buildings efficiently
                    iBuildingCount = 0
                    for iBuilding in xrange(GC.getNumBuildingInfos()):
                        if pCity.hasBuilding(iBuilding):
                            iBuildingCount += 1

                    output.append("Buildings: %d\n" % iBuildingCount)
                    output.append("Improved Plots: %d\n" % pCity.countNumImprovedPlots())
                    output.append("Tiles Worked: %d, Specialists: %d\n" % (pCity.getWorkingPopulation(),
                                                                           pCity.getSpecialistPopulation()))
                    output.append("Great People: %d\n" % pCity.getNumGreatPeople())
                    output.append("Good Health: %d, Bad Health: %d\n" % (pCity.goodHealth(), pCity.badHealth(False)))
                    output.append("Happy Level: %d, Unhappy Level: %d\n" % (pCity.happyLevel(), pCity.unhappyLevel(0)))
                    output.append("Food: %d\n" % pCity.getFood())
                    pCity, i = pPlayer.nextCity(i, False)
            else:
                output.append("\n\nCity Info:\n----------\nNo Cities\n")

            # Bonus info section
            output.append("\n\nBonus Info:\n-----------\n")
            for iBonus in xrange(GC.getNumBonusInfos()):
                bonusDesc = TextUtil.convertToStr(GC.getBonusInfo(iBonus).getDescription())
                output.append("Player %d, %s, Number Available: %d\n" % (iPlayer, bonusDesc,
                                                                         pPlayer.getNumAvailableBonuses(iBonus)))
                output.append("Player %d, %s, Import: %d\n" % (iPlayer, bonusDesc, pPlayer.getBonusImport(iBonus)))
                output.append("Player %d, %s, Export: %d\n\n" % (iPlayer, bonusDesc, pPlayer.getBonusExport(iBonus)))

            # Improvement info section
            output.append("\n\nImprovement Info:\n-----------------\n")
            for iImprovement in xrange(GC.getNumImprovementInfos()):
                improvementDesc = TextUtil.convertToStr(GC.getImprovementInfo(iImprovement).getDescription())
                output.append("Player %d, %s, Improvement count: %d\n" % (iPlayer, improvementDesc,
                                                                          pPlayer.getImprovementCount(iImprovement)))

            # Building info section
            output.append("\n\nBuilding Info:\n--------------------\n")
            for iBuilding in xrange(GC.getNumBuildingInfos()):
                buildingDesc = TextUtil.convertToStr(GC.getBuildingInfo(iBuilding).getDescription())
                output.append("Player %d, %s, Building count plus making: %d\n" % (iPlayer, buildingDesc,
                                                                                         pPlayer.getBuildingCountPlusMaking(
                                                                                             iBuilding)))

            # Unit class info section
            output.append("\n\nUnit Class Info:\n--------------------\n")
            for iUnit in xrange(GC.getNumUnitInfos()):
                unitDesc = TextUtil.convertToStr(GC.getUnitInfo(iUnit).getDescription())
                output.append("Player %d, %s, Unit count plus making: %d\n" % (iPlayer, unitDesc,
                                                                                       pPlayer.getUnitCountPlusMaking(
                                                                                           iUnit)))

            # UnitAI types info section
            output.append("\n\nUnitAI Types Info:\n------------------\n")
            for iUnitAIType in xrange(int(UnitAITypes.NUM_UNITAI_TYPES)):
                unitAIType = GC.getUnitAIInfo(iUnitAIType).getType()
                output.append("Player %d, %s, Unit AI Type count: %d\n" % (iPlayer, unitAIType, pPlayer.AI_totalUnitAIs(
                    UnitAITypes(iUnitAIType))))

            # Process city religions if cities exist
            if pPlayer.getNumCities():
                output.append("\n\nCity Religions:\n-----------\n")
                pCity, i = pPlayer.firstCity(False)
                while pCity:
                    cityReligions = []
                    cityName = None

                    for iReligion in xrange(GC.getNumReligionInfos()):
                        if pCity.isHasReligion(iReligion):
                            if cityName is None:
                                cityName = TextUtil.convertToStr(pCity.getName())
                            cityReligions.append(
                                "\t%s\n" % TextUtil.convertToStr(GC.getReligionInfo(iReligion).getDescription()))

                    if cityReligions:
                        output.append("City: %s\n" % cityName)
                        output.extend(cityReligions)

                    pCity, i = pPlayer.nextCity(i, False)

                # Process city corporations
                output.append("\n\nCity Corporations:\n-----------\n")
                pCity, i = pPlayer.firstCity(False)
                while pCity:
                    cityCorporations = []
                    cityName = None

                    for iCorporation in xrange(GC.getNumCorporationInfos()):
                        if pCity.isHasCorporation(iCorporation):
                            if cityName is None:
                                cityName = TextUtil.convertToStr(pCity.getName())
                            cityCorporations.append(
                                "\t%s\n" % TextUtil.convertToStr(GC.getCorporationInfo(iCorporation).getDescription()))

                    if cityCorporations:
                        output.append("City: %s\n" % cityName)
                        output.extend(cityCorporations)

                    pCity, i = pPlayer.nextCity(i, False)

            # Unit info section
            output.append("\n\nUnit Info:\n----------\n")
            if pPlayer.getNumUnits():
                for pUnit in pPlayer.units():
                    output.append("Player %d, Unit ID: %d, %s\n" % (iPlayer, pUnit.getID(),
                                                                    TextUtil.convertToStr(pUnit.getName())))
                    output.append("X: %d, Y: %d\nDamage: %d\n" % (pUnit.getX(), pUnit.getY(), pUnit.getDamage()))
                    output.append("Experience: %d\nLevel: %d\n" % (pUnit.getExperience(), pUnit.getLevel()))

                    # Collect promotions
                    unitPromotions = []
                    for j in xrange(GC.getNumPromotionInfos()):
                        if pUnit.isHasPromotion(j):
                            unitPromotions.append(
                                "\t%s\n" % TextUtil.convertToStr(GC.getPromotionInfo(j).getDescription()))

                    if unitPromotions:
                        output.append("Promotions:\n")
                        output.extend(unitPromotions)

                    # Collect unit combats
                    unitCombats = []
                    for j in xrange(GC.getNumUnitCombatInfos()):
                        if pUnit.isHasUnitCombat(j):
                            unitCombats.append(
                                "\t%s\n" % TextUtil.convertToStr(GC.getUnitCombatInfo(j).getDescription()))

                    if unitCombats:
                        output.append("UnitCombats:\n")
                        output.extend(unitCombats)
            else:
                output.append("No Units\n")

            # Space at end of player's info
            output.append("\n\n")

            # Force garbage collection after each player to free memory
            if iPlayer % 4 == 3:  # Every 4 players
                gc.collect()

        # Write all data at once - more efficient than multiple writes
        pFile = open(szFileName, "wb")
        try:
            # Join and encode once
            pFile.write((''.join(output)).encode('utf-8', 'replace'))
        finally:
            pFile.close()

        # Clear the output buffer
        del output

    finally:
        # Always restore language
        GAME.setCurrentLanguage(iLanguage)

    # Final garbage collection
    gc.collect()