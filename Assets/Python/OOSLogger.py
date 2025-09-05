# OOS logger: writes the info contained in the sync checksum to a log file
# Memory-optimized version for 32-bit Python 2.4 (Civ4 C2C)
from CvPythonExtensions import CyGlobalContext, YieldTypes, CommerceTypes, UnitAITypes


def writeLog():
    import SystemPaths as SP
    import TextUtil
    import gc
    import os

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
        except OSError as e:
            import errno
            if e.errno != errno.EEXIST:
                raise
    szFileName = os.path.join(log_dir, "%s - Player %d - Turn %d OOSLog.txt" % (
        safeName, iActivePlayer, GAME.getGameTurn()))

    pFile = open(szFileName, "wb")
    w = lambda s: pFile.write(s.encode('utf-8', 'replace'))
    try:

    class HybridGC:
        def __init__(self):
            self.last_gc_player = -1
            self.base_interval = 6  # Increased from 4
            self.min_interval = 2
            self.pressure_factor = 1.3

        def should_collect(self, player_index, output_buffer):
            """Multi-factor decision for garbage collection"""
            # Never collect too frequently
            if (player_index - self.last_gc_player) < self.min_interval:
                return False

            # Check various conditions
            interval_trigger = (player_index % self.base_interval) == 0

            # Memory pressure check
            counts = gc.get_count()
            thresholds = gc.get_threshold()
            pressure_trigger = counts[0] > (thresholds[0] * self.pressure_factor)

            # Buffer size check (estimate)
            buffer_samples = output_buffer[-10:] if len(output_buffer) >= 10 else output_buffer
            avg_string_size = sum(len(s) for s in buffer_samples) / max(len(buffer_samples), 1)
            estimated_buffer_size = avg_string_size * len(output_buffer)
            buffer_trigger = estimated_buffer_size > 100000  # 100KB threshold

            return interval_trigger or pressure_trigger or buffer_trigger

        def collect(self, player_index):
            """Perform targeted collection"""
            # Collect generation 0 first (most efficient for our use case)
            collected_gen0 = gc.collect(0)

            # If that didn't free much, do a full collection
            if collected_gen0 < 100:  # Adjust threshold as needed
                collected_full = gc.collect()
                total_collected = collected_gen0 + collected_full
            else:
                total_collected = collected_gen0

            self.last_gc_player = player_index
            return total_collected

    # Initialize the garbage collector
    hybrid_gc = HybridGC()

    # Reusable separator constant
    SEP = "-----------------------------------------------------------------\n"
    SEP2 = SEP + SEP

    # Backup current language
    iLanguage = GAME.getCurrentLanguage()
    # Force english language for logs
    GAME.setCurrentLanguage(0)

    try:
        # Global data section
        w(SEP2)
        w("\tGLOBALS\n")
        w(SEP2)
        w("\n")

        # Use direct formatting to avoid temporary strings
        w("Last MapRand Value: %d\n" % GAME.getMapRand().getSeed())
        w("Last SorenRand Value: %d\n" % GAME.getSorenRand().getSeed())
        w("Total num cities: %d\n" % GAME.getNumCities())
        w("Total Deals: %d\n" % GAME.getNumDeals())
        w("Total owned plots: %d\n" % MAP.getOwnedPlots())
        w("Total num areas: %d\n\n\n" % MAP.getNumAreas())

        # Player data - process each player
        for iPlayer in xrange(GC.getMAX_PLAYERS()):
            pPlayer = GC.getPlayer(iPlayer)
            if not pPlayer.isEverAlive():
                continue

            # Cache frequently used values
            playerName = TextUtil.convertToStr(pPlayer.getName())
            isHuman = pPlayer.isHuman()

            # Header
            w(SEP2)
            if isHuman:
                w("Human player %d: %s\n" % (iPlayer, playerName))
            else:
                w("NPC player %d: %s\n" % (iPlayer, playerName))
            try:
                from CvPythonExtensions import CyTranslator
                civ = CyTranslator().getText(pPlayer.getCivilizationDescriptionKey(), ())
            except Exception:
                civ = TextUtil.convertToStr(pPlayer.getCivilizationDescriptionKey())
            w("  Civilization: %s\n" % civ)
            w("  Alive: %s\n" % pPlayer.isAlive())
            w(SEP2)
            w("\n\nBasic data:\n-----------\n")

            # Basic data - batch similar operations
            w("Player %d Score: %d\n" % (iPlayer, GAME.getPlayerScore(iPlayer)))
            w("Player %d Population: %d\n" % (iPlayer, pPlayer.getTotalPopulation()))
            w("Player %d Total Land: %d\n" % (iPlayer, pPlayer.getTotalLand()))
            w("Player %d Gold: %d\n" % (iPlayer, pPlayer.getGold()))
            w("Player %d Assets: %d\n" % (iPlayer, pPlayer.getAssets()))
            w("Player %d Power: %d\n" % (iPlayer, pPlayer.getPower()))
            w("Player %d Num Cities: %d\n" % (iPlayer, pPlayer.getNumCities()))
            w("Player %d Num Units: %d\n" % (iPlayer, pPlayer.getNumUnits()))
            w("Player %d Num Selection Groups: %d\n" % (iPlayer, pPlayer.getNumSelectionGroups()))
            w("Player %d Difficulty: %d\n" % (iPlayer, pPlayer.getHandicapType()))

            # State religion - check actual religion type to ensure else branch can trigger
            stateReligionType = pPlayer.getStateReligion()
            if stateReligionType != -1:  # -1 represents NO_RELIGION
                stateReligionKey = pPlayer.getStateReligionKey()
                try:
                    # Use direct religion info for better performance and clarity
                    stateReligionStr = GC.getReligionInfo(stateReligionType).getDescription()
                except Exception:
                    # Fallback to key translation if direct access fails
                    try:
                        from CvPythonExtensions import CyTranslator
                        stateReligionStr = CyTranslator().getText(stateReligionKey, ())
                    except Exception:
                        # Final fallback to key conversion
                        stateReligionStr = TextUtil.convertToStr(stateReligionKey)
                output.append("Player %d State Religion: %s\n" % (iPlayer, stateReligionStr))
            else:
                output.append("Player %d State Religion: None\n" % iPlayer)

            w("Player %d Culture: %d\n" % (iPlayer, pPlayer.getCulture()))

            # Yields section
            w("\n\nYields:\n-------\n")
            for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
                yieldDesc = TextUtil.convertToStr(GC.getYieldInfo(iYield).getDescription())
                w(
                    "Player %d %s Total Yield: %d\n" % (iPlayer, yieldDesc, pPlayer.calculateTotalYield(iYield)))

            # Commerce section
            w("\n\nCommerce:\n---------\n")
            for iCommerce in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
                commerceDesc = TextUtil.convertToStr(GC.getCommerceInfo(iCommerce).getDescription())
                w("Player %d %s Total Commerce: %d\n" % (iPlayer, commerceDesc,
                                                                     pPlayer.getCommerceRate(CommerceTypes(iCommerce))))

            # Process cities if any exist
            if pPlayer.getNumCities():
                # City event history
                w("\n\nCity event history:\n-----------\n")
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
                        w("City: %s\n" % cityName)
                        for item in cityEvents:
                            w(item)

                    pCity, i = pPlayer.nextCity(i, False)

                # City info section
                w("\n\nCity Info:\n----------\n")
                pCity, i = pPlayer.firstCity(False)
                while pCity:
                    w("City: %s\n" % TextUtil.convertToStr(pCity.getName()))
                    w("X: %d, Y: %d\n" % (pCity.getX(), pCity.getY()))
                    w("Population: %d\n" % pCity.getPopulation())

                    # Count buildings efficiently
                    iBuildingCount = 0
                    for iBuilding in xrange(GC.getNumBuildingInfos()):
                        if pCity.hasBuilding(iBuilding):
                            iBuildingCount += 1

                    w("Buildings: %d\n" % iBuildingCount)
                    w("Improved Plots: %d\n" % pCity.countNumImprovedPlots())
                    w("Tiles Worked: %d, Specialists: %d\n" % (pCity.getWorkingPopulation(),
                                                                           pCity.getSpecialistPopulation()))
                    w("Great People: %d\n" % pCity.getNumGreatPeople())
                    w("Good Health: %d, Bad Health: %d\n" % (pCity.goodHealth(), pCity.badHealth(False)))
                    w("Happy Level: %d, Unhappy Level: %d\n" % (pCity.happyLevel(), pCity.unhappyLevel(0)))
                    w("Food: %d\n" % pCity.getFood())
                    pCity, i = pPlayer.nextCity(i, False)
            else:
                w("\n\nCity Info:\n----------\nNo Cities\n")

            # Bonus info section
            w("\n\nBonus Info:\n-----------\n")
            for iBonus in xrange(GC.getNumBonusInfos()):
                bonusDesc = TextUtil.convertToStr(GC.getBonusInfo(iBonus).getDescription())
                w("Player %d, %s, Number Available: %d\n" % (iPlayer, bonusDesc,
                                                                         pPlayer.getNumAvailableBonuses(iBonus)))
                w("Player %d, %s, Import: %d\n" % (iPlayer, bonusDesc, pPlayer.getBonusImport(iBonus)))
                w("Player %d, %s, Export: %d\n\n" % (iPlayer, bonusDesc, pPlayer.getBonusExport(iBonus)))

            # Improvement info section
            w("\n\nImprovement Info:\n-----------------\n")
            for iImprovement in xrange(GC.getNumImprovementInfos()):
                improvementDesc = TextUtil.convertToStr(GC.getImprovementInfo(iImprovement).getDescription())
                w("Player %d, %s, Improvement count: %d\n" % (iPlayer, improvementDesc,
                                                                          pPlayer.getImprovementCount(iImprovement)))

            # Building info section
            w("\n\nBuilding Info:\n--------------------\n")
            for iBuilding in xrange(GC.getNumBuildingInfos()):
                buildingDesc = TextUtil.convertToStr(GC.getBuildingInfo(iBuilding).getDescription())
                w("Player %d, %s, Building count plus making: %d\n" % (iPlayer, buildingDesc,
                                                                                         pPlayer.getBuildingCountPlusMaking(
                                                                                             iBuilding)))

            # Unit class info section
            w("\n\nUnit Class Info:\n--------------------\n")
            for iUnit in xrange(GC.getNumUnitInfos()):
                unitDesc = TextUtil.convertToStr(GC.getUnitInfo(iUnit).getDescription())
                w("Player %d, %s, Unit count plus making: %d\n" % (iPlayer, unitDesc,
                                                                                       pPlayer.getUnitCountPlusMaking(
                                                                                           iUnit)))

            # UnitAI types info section
            w("\n\nUnitAI Types Info:\n------------------\n")
            for iUnitAIType in xrange(int(UnitAITypes.NUM_UNITAI_TYPES)):
                unitAIType = GC.getUnitAIInfo(iUnitAIType).getType()
                w("Player %d, %s, Unit AI Type count: %d\n" % (iPlayer, unitAIType, pPlayer.AI_totalUnitAIs(
                    UnitAITypes(iUnitAIType))))

            # Process city religions if cities exist
            if pPlayer.getNumCities():
                w("\n\nCity Religions:\n-----------\n")
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
                        w("City: %s\n" % cityName)
                        for item in cityReligions:
                            w(item)

                    pCity, i = pPlayer.nextCity(i, False)

                # Process city corporations
                w("\n\nCity Corporations:\n-----------\n")
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
                        w("City: %s\n" % cityName)
                        for item in cityCorporations:
                            w(item)

                    pCity, i = pPlayer.nextCity(i, False)

            # Unit info section
            w("\n\nUnit Info:\n----------\n")
            if pPlayer.getNumUnits():
                for pUnit in pPlayer.units():
                    w("Player %d, Unit ID: %d, %s\n" % (iPlayer, pUnit.getID(),
                                                                    TextUtil.convertToStr(pUnit.getName())))
                    w("X: %d, Y: %d\nDamage: %d\n" % (pUnit.getX(), pUnit.getY(), pUnit.getDamage()))
                    w("Experience: %d\nLevel: %d\n" % (pUnit.getExperience(), pUnit.getLevel()))

                    # Collect promotions
                    unitPromotions = []
                    for j in xrange(GC.getNumPromotionInfos()):
                        if pUnit.isHasPromotion(j):
                            unitPromotions.append(
                                "\t%s\n" % TextUtil.convertToStr(GC.getPromotionInfo(j).getDescription()))

                    if unitPromotions:
                        w("Promotions:\n")
                        for item in unitPromotions:
                            w(item)

                    # Collect unit combats
                    unitCombats = []
                    for j in xrange(GC.getNumUnitCombatInfos()):
                        if pUnit.isHasUnitCombat(j):
                            unitCombats.append(
                                "\t%s\n" % TextUtil.convertToStr(GC.getUnitCombatInfo(j).getDescription()))

                    if unitCombats:
                        w("UnitCombats:\n")
                        for item in unitCombats:
                            w(item)
            else:
                w("No Units\n")

            # Space at end of player's info
            w("\n\n")

            # Intelligent garbage collection based on memory pressure
            if hybrid_gc.should_collect(iPlayer, output):
                collected = hybrid_gc.collect(iPlayer)

                # Close the file (already written during streaming)
                pFile.close()

    finally:
    # Close file if it was opened
    if 'pFile' in locals() and not pFile.closed:
        pFile.close()
    # Restore original language
    GAME.setCurrentLanguage(iLanguage)
    gc.collect()