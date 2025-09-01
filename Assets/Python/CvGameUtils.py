## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## Implementation of miscellaneous game functions
## Memory-optimized version for 32-bit Caveman2Cosmos mod

from CvPythonExtensions import *
import CvUtil

# Pre-cache global references to save repeated lookups
GC = CyGlobalContext()
GAME = GC.getGame()

# Pre-cache frequently used methods
_getPlayer = GC.getPlayer
_getTeam = GC.getTeam
_getMap = GC.getMap
_getBuildInfo = GC.getBuildInfo
_getProcessInfo = GC.getProcessInfo
_getImprovementInfo = GC.getImprovementInfo
_getReligionInfo = GC.getReligionInfo
_getCorporationInfo = GC.getCorporationInfo
_getCultureLevelInfo = GC.getCultureLevelInfo
_getRouteInfo = GC.getRouteInfo
_getBuildingInfo = GC.getBuildingInfo
_getYieldInfo = GC.getYieldInfo
_getCommerceInfo = GC.getCommerceInfo
_getUpkeepInfo = GC.getUpkeepInfo
_getCivicInfo = GC.getCivicInfo
_getInfoTypeForString = GC.getInfoTypeForString
_getDefineINT = GC.getDefineINT
_getNumReligionInfos = GC.getNumReligionInfos
_getNumCorporationInfos = GC.getNumCorporationInfos
_getNumBuildingInfos = GC.getNumBuildingInfos

# Pre-cache CyTranslator methods
TRNSLTR = CyTranslator()
_getText = TRNSLTR.getText

# Pre-cache CyGameTextMgr methods
GAME_TEXT_MGR = CyGameTextMgr()
_getProjectHelp = GAME_TEXT_MGR.getProjectHelp
_parseReligionInfo = GAME_TEXT_MGR.parseReligionInfo
_getBuildingHelp = GAME_TEXT_MGR.getBuildingHelp
_getTechHelp = GAME_TEXT_MGR.getTechHelp
_parseCivInfos = GAME_TEXT_MGR.parseCivInfos
_getPromotionHelp = GAME_TEXT_MGR.getPromotionHelp
_getFeatureHelp = GAME_TEXT_MGR.getFeatureHelp
_getTerrainHelp = GAME_TEXT_MGR.getTerrainHelp
_parseLeaderTraits = GAME_TEXT_MGR.parseLeaderTraits
_getImprovementHelp = GAME_TEXT_MGR.getImprovementHelp
_getBonusHelp = GAME_TEXT_MGR.getBonusHelp
_getSpecialistHelp = GAME_TEXT_MGR.getSpecialistHelp
_parseCorporationInfo = GAME_TEXT_MGR.parseCorporationInfo
_getUnitHelp = GAME_TEXT_MGR.getUnitHelp
_getSpecificUnitHelp = GAME_TEXT_MGR.getSpecificUnitHelp
_parseCivicInfo = GAME_TEXT_MGR.parseCivicInfo

# Pre-cache game methods
_getSorenRandNum = GAME.getSorenRandNum
_getEstimateEndTurn = GAME.getEstimateEndTurn
_getGameTurn = GAME.getGameTurn
_getHandicapType = GAME.getHandicapType
_getInitPopulation = GAME.getInitPopulation
_getMaxPopulation = GAME.getMaxPopulation
_getInitLand = GAME.getInitLand
_getMaxLand = GAME.getMaxLand
_getInitTech = GAME.getInitTech
_getMaxTech = GAME.getMaxTech
_getInitWonders = GAME.getInitWonders
_getMaxWonders = GAME.getMaxWonders
_GetWorldBuilderMode = GAME.GetWorldBuilderMode
_getModderGameOption = GAME.getModderGameOption

# Pre-cache constant strings to leverage Python's string interning
_NONE_TEXT = "TXT_KEY_CULTURELEVEL_NONE"
_BUILD_BONUS_PREFIX = "BUILD_BONUS_"
_ICON_BULLET = "[ICON_BULLET]"
_COLOR_WARNING = "[COLOR_WARNING_TEXT]"
_COLOR_BUILDING = "[COLOR_BUILDING_TEXT]"
_COLOR_SELECTED = "[COLOR_SELECTED_TEXT]"

# Pre-cache widget help bullet points as tuple (immutable, less memory)
_PYTHON_EVENTS = (
    "onFirstContact",
    "onChangeWar",
    "onVassalState",
    "onCityAcquired",
    "onCityBuilt",
    "onCultureExpansion",
    "onGoldenAge",
    "onEndGoldenAge",
    "onGreatPersonBorn",
    "onPlayerChangeStateReligion",
    "onReligionFounded",
    "onReligionSpread",
    "onReligionRemove",
    "onCorporationFounded",
    "onCorporationSpread",
    "onCorporationRemove",
    "onUnitCreated",
    "onUnitLost",
    "onUnitPromoted",
    "onBuildingBuilt",
    "onProjectBuilt",
    "onTechAcquired",
    "onImprovementBuilt",
    "onImprovementDestroyed",
    "onRouteBuilt",
    "onPlotRevealed"
)


class CvGameUtils:
    # Use __slots__ to reduce memory overhead by ~100-200 bytes per instance
    __slots__ = (
        'fScoreFreeMod', 'SCORE_POPULATION_FACTOR', 'SCORE_LAND_FACTOR',
        'SCORE_TECH_FACTOR', 'SCORE_WONDER_FACTOR', 'BASE_CAPTURE_GOLD',
        'CAPTURE_GOLD_PER_POP', 'CAPTURE_GOLD_RAND1', 'CAPTURE_GOLD_RAND2',
        'CAPTURE_GOLD_MAX_TURNS', 'iNationalMint', 'iHimejiCastle',
        '_process_map', '_cached_score_victory_pct', '_cached_score_handicap_pct_offset',
        '_cached_score_handicap_pct_per'
    )

    def __init__(self):
        # Cache all constants at initialization
        self.fScoreFreeMod = _getDefineINT("SCORE_FREE_PERCENT") / 100.0
        self.SCORE_POPULATION_FACTOR = _getDefineINT("SCORE_POPULATION_FACTOR")
        self.SCORE_LAND_FACTOR = _getDefineINT("SCORE_LAND_FACTOR")
        self.SCORE_TECH_FACTOR = _getDefineINT("SCORE_TECH_FACTOR")
        self.SCORE_WONDER_FACTOR = _getDefineINT("SCORE_WONDER_FACTOR")

        self.BASE_CAPTURE_GOLD = _getDefineINT("BASE_CAPTURE_GOLD")
        self.CAPTURE_GOLD_PER_POP = _getDefineINT("CAPTURE_GOLD_PER_POPULATION")
        self.CAPTURE_GOLD_RAND1 = _getDefineINT("CAPTURE_GOLD_RAND1")
        self.CAPTURE_GOLD_RAND2 = _getDefineINT("CAPTURE_GOLD_RAND2")
        self.CAPTURE_GOLD_MAX_TURNS = _getDefineINT("CAPTURE_GOLD_MAX_TURNS")

        self.iNationalMint = _getInfoTypeForString("BUILDING_NATIONAL_MINT")
        self.iHimejiCastle = _getInfoTypeForString("BUILDING_HIMEJI_SAMURAI_CASTLE")

        # Pre-cache score calculation constants
        self._cached_score_victory_pct = _getDefineINT("SCORE_VICTORY_PERCENT")
        self._cached_score_handicap_pct_offset = _getDefineINT("SCORE_HANDICAP_PERCENT_OFFSET")
        self._cached_score_handicap_pct_per = _getDefineINT("SCORE_HANDICAP_PERCENT_PER")

        # Pre-build process map for cannotMaintain - tuple uses less memory than dict
        self._process_map = (
            ("WEALTH", ("PROCESS_WEALTH_MEAGER", "PROCESS_WEALTH_LESSER", "PROCESS_WEALTH")),
            ("RESEARCH", ("PROCESS_RESEARCH_MEAGER", "PROCESS_RESEARCH_LESSER", "PROCESS_RESEARCH")),
            ("CULTURE", ("PROCESS_CULTURE_MEAGER", "PROCESS_CULTURE_LESSER", "PROCESS_CULTURE")),
            ("SPY", ("PROCESS_SPY_MEAGER", "PROCESS_SPY_LESSER", "PROCESS_SPY"))
        )

    def canBuild(self, argsList):
        iX, iY, iBuild, iPlayer = argsList

        # Bonus placing builds
        CyPlot = _getMap().plot(iX, iY)
        if CyPlot and CyPlot.getBonusType(-1) < 0 and not CyPlot.isWater():
            szType = _getBuildInfo(iBuild).getType()
            # Use string slicing instead of startswith for Python 2.4
            if szType[:12] == _BUILD_BONUS_PREFIX:
<<<<<<< Updated upstream
                iBonus = _getInfoTypeForString(szType[6:])
=======
                iBonus = _getInfoTypeForString(szType[12:])
>>>>>>> Stashed changes

                if (
                        iBonus > -1
                        and _getPlayer(iPlayer).getNumAvailableBonuses(iBonus)
                        and (
                        _getModderGameOption(ModderGameOptionTypes.MODDERGAMEOPTION_GREATER_GREAT_FARMER)
                        or _getMap().plot(iX, iY).canHaveBonus(iBonus, False)
                )): return 1

                return 0

        return -1

    def cannotMaintain(self, argsList):
        CyCity, iProcess = argsList
        if not CyCity:
<<<<<<< Updated upstream
            print
            "CyCity == None"
            print
            "CyCity, iProcess", argsList
=======
            print "CyCity == None"
            print "CyCity, iProcess", argsList
>>>>>>> Stashed changes
            return False

        TYPE = _getProcessInfo(iProcess).getType()

        # Quick check for underscore
        if TYPE.find("_") == -1:
            return False

        KEY = TYPE.split("_", 2)[1]  # Limit split for efficiency

        # Use pre-built tuple map
        for map_key, processes in self._process_map:
            if KEY == map_key:
                bFound = False
                CyTeam = _getTeam(CyCity.getTeam())
                for PROCESS in processes:
                    if bFound:
                        iProcess = _getInfoTypeForString(PROCESS)
                        if iProcess > -1:
                            iTech = _getProcessInfo(iProcess).getTechPrereq()
                            if iTech == -1 or CyTeam.isHasTech(iTech):
                                return True
                        return False
                    elif PROCESS == TYPE:
                        bFound = True
                break
        return False

    def calculateScore(self, argsList):
        iEndTurn = _getEstimateEndTurn()
        if not iEndTurn: return 0
        iPlayer, bFinal, bVictory = argsList

        # Pre-calculate common values
        if bFinal and bVictory:
            fTurnRatio = _getGameTurn() / float(iEndTurn)
        else:
            fTurnRatio = 0

        if bVictory:
            fVictory = (100 + self._cached_score_victory_pct) / 100.0
        else:
            fVictory = 1

        if bFinal:
            fFinal = (
                                 100 + self._cached_score_handicap_pct_offset + _getHandicapType() * self._cached_score_handicap_pct_per) / 100.0
        else:
            fFinal = 1

        CyPlayer = _getPlayer(iPlayer)
        score = 0
        fFreePercent = self.fScoreFreeMod

        # Pre-calculate multiplier for all score components
        base_multiplier = fVictory * fFinal

        # Population
        iInitial = _getInitPopulation()
        iMax = _getMaxPopulation()
        if fTurnRatio:
            if iInitial:
<<<<<<< Updated upstream
                iMax = iInitial * (iMax / iInitial) ** fTurnRatio
=======
                iMax = iInitial * (iMax / float(iInitial)) ** fTurnRatio
>>>>>>> Stashed changes
            else:
                iMax = iInitial + fTurnRatio * (iMax - iInitial)

        fFree = iMax * fFreePercent
        temp = self.SCORE_POPULATION_FACTOR * base_multiplier
        fDiv = fFree + iMax
        if fDiv:
            temp *= (CyPlayer.getPopScore() + fFree) / fDiv
        score += temp

        # Land
        iInitial = _getInitLand()
        iMax = _getMaxLand()
        if fTurnRatio:
            if iInitial:
<<<<<<< Updated upstream
                iMax = iInitial * (iMax / iInitial) ** fTurnRatio
=======
                iMax = iInitial * (iMax / float(iInitial)) ** fTurnRatio
>>>>>>> Stashed changes
            else:
                iMax = iInitial + fTurnRatio * (iMax - iInitial)

        fFree = iMax * fFreePercent
        temp = self.SCORE_LAND_FACTOR * base_multiplier
        fDiv = fFree + iMax
        if fDiv:
            temp *= (CyPlayer.getLandScore() + fFree) / fDiv
        score += temp

        # Tech
        iInitial = _getInitTech()
        iMax = _getMaxTech()
        if fTurnRatio:
            if iInitial:
<<<<<<< Updated upstream
                iMax = iInitial * (iMax / iInitial) ** fTurnRatio
=======
                iMax = iInitial * (iMax / float(iInitial)) ** fTurnRatio
>>>>>>> Stashed changes
            else:
                iMax = iInitial + fTurnRatio * (iMax - iInitial)

        fFree = iMax * fFreePercent
        temp = self.SCORE_TECH_FACTOR * base_multiplier
        fDiv = fFree + iMax
        if fDiv:
            temp *= (CyPlayer.getTechScore() + fFree) / fDiv
        score += temp

        # Wonder
        iInitial = _getInitWonders()
        iMax = _getMaxWonders()
        if fTurnRatio:
            iMax = iInitial + fTurnRatio * (iMax - iInitial)

        fFree = iMax * fFreePercent
        temp = self.SCORE_WONDER_FACTOR * base_multiplier
        fDiv = fFree + iMax
        if fDiv:
            temp *= (CyPlayer.getWondersScore() + fFree) / fDiv
        score += temp

        return int(score)

    def doPillageGold(self, argsList):
        CyPlot, CyUnit = argsList

        iPlayer = CyPlot.getOwner()
        if iPlayer > -1 and _getPlayer(iPlayer).hasBuilding(self.iHimejiCastle):
            return 0

        iTemp = _getImprovementInfo(CyPlot.getImprovementType()).getPillageGold()
        gold = _getSorenRandNum(iTemp, "Pillage Gold 1")
        gold += _getSorenRandNum(iTemp, "Pillage Gold 2")

        gold += CyUnit.getPillageChange() * gold / 100.0

        if _getPlayer(CyUnit.getOwner()).hasBuilding(self.iHimejiCastle):
            gold *= 2

        return int(gold)

    def doCityCaptureGold(self, argsList):
        CyCity, iOwnerNew = argsList

        if _getPlayer(CyCity.getOwner()).hasBuilding(self.iHimejiCastle):
            return 0

        gold = self.BASE_CAPTURE_GOLD

        gold += CyCity.getPopulation() * self.CAPTURE_GOLD_PER_POP
        gold += _getSorenRandNum(self.CAPTURE_GOLD_RAND1, "One")
        gold += _getSorenRandNum(self.CAPTURE_GOLD_RAND2, "Two")

        iMaxTurns = self.CAPTURE_GOLD_MAX_TURNS
        if iMaxTurns > 0:
            iTurns = _getGameTurn() - CyCity.getGameTurnAcquired()
            if iTurns > 0 and iTurns < iMaxTurns:
                gold *= 1.0 * iTurns / iMaxTurns

        if CyCity.isActiveBuilding(self.iNationalMint):
            gold *= 10

        return int(gold)

    def getWidgetHelp(self, argsList):
        eWidgetType, iData1, iData2, bOption = argsList

        if eWidgetType == WidgetTypes.WIDGET_HELP_RELIGION:
            if iData1 == -1:
                return _getText(_NONE_TEXT, ())

        elif eWidgetType == WidgetTypes.WIDGET_PYTHON:
            if iData1 == 1027:
                return _getText("TXT_KEY_WB_PLOT_DATA", ())
            elif iData1 == 1029:
                return self._getWidget1029Help(iData2)
            elif iData1 == 1041:
                return _getText("TXT_KEY_WB_KILL", ())
            elif iData1 == 1042:
                return _getText("TXT_KEY_MISSION_SKIP", ())
            elif iData1 == 1043:
                return self._getWidget1043Help(iData2)
            elif iData1 == 6785:
                return _getProjectHelp(iData2, False, None)
            elif iData1 == 6787:
                return _getProcessInfo(iData2).getDescription()
            elif iData1 == 6788:
                if iData2 == -1:
                    return _getText(_NONE_TEXT, ())
                return _getRouteInfo(iData2).getDescription()
            ## City Hover Text ##
            elif iData1 > 7199 and iData1 < 7300:
                return self._getCityHoverText(iData1 - 7200, iData2)
            ## Religion Widget Text##
            elif iData1 == 7869:
                return _parseReligionInfo(iData2, False)
            ## Building Widget Text##
            elif iData1 == 7870:
                return _getBuildingHelp(iData2, False, None, False, False, False)
            ## Tech Widget Text##
            elif iData1 == 7871:
                if iData2 == -1:
                    return _getText(_NONE_TEXT, ())
                return _getTechHelp(iData2, False, False, False, False, -1)
            ## Civilization Widget Text##
            elif iData1 == 7872:
                iCiv = iData2 % 10000
                return _parseCivInfos(iCiv, False)
            ## Promotion Widget Text##
            elif iData1 == 7873:
                return _getPromotionHelp(iData2, False)
            ## Feature Widget Text##
            elif iData1 == 7874:
                if iData2 == -1:
                    return _getText(_NONE_TEXT, ())
                iFeature = iData2 % 10000
                return _getFeatureHelp(iFeature, False)
            ## Terrain Widget Text##
            elif iData1 == 7875:
                return _getTerrainHelp(iData2, False)
            ## Leader Widget Text##
            elif iData1 == 7876:
                iLeader = iData2 % 10000
                return _parseLeaderTraits(iLeader, False, False)
            ## Improvement Widget Text##
            elif iData1 == 7877:
                if iData2 == -1:
                    return _getText(_NONE_TEXT, ())
                return _getImprovementHelp(iData2, False)
            ## Bonus Widget Text##
            elif iData1 == 7878:
                if iData2 == -1:
                    return _getText(_NONE_TEXT, ())
                return _getBonusHelp(iData2, False)
            ## Specialist Widget Text##
            elif iData1 == 7879:
                return _getSpecialistHelp(iData2, False)
            ## Yield Text##
            elif iData1 == 7880:
                return _getYieldInfo(iData2).getDescription()
            ## Commerce Text##
            elif iData1 == 7881:
                return _getCommerceInfo(iData2).getDescription()
            ## Build Text##
            elif iData1 == 7882:
                return _getBuildInfo(iData2).getDescription()
            ## Corporation Screen ##
            elif iData1 == 8201:
                return _parseCorporationInfo(iData2, False)
            ## Military Screen ##
            elif iData1 == 8202:
                if iData2 == -1:
                    return _getText("TXT_KEY_PEDIA_ALL_UNITS", ())
                return _getUnitHelp(iData2, False, False, False, None)
            elif iData1 > 8299 and iData1 < 8400:
                return self._getUnitHoverText(iData1 - 8300, iData2)
            ## Civics Screen ##
            elif iData1 == 8205 or iData1 == 8206:
                sText = _parseCivicInfo(iData2, False, True, False)
                if _getCivicInfo(iData2).getUpkeep() > -1:
                    sText += "\n" + _getUpkeepInfo(_getCivicInfo(iData2).getUpkeep()).getDescription()
                else:
                    sText += "\n" + _getText("TXT_KEY_CIVICS_SCREEN_NO_UPKEEP", ())
                return sText
        return ""

    def _getWidget1029Help(self, iData2):
        """Helper method for widget 1029 - optimized with string list building"""
        if iData2 == 0:
            # Build string list and join once instead of multiple concatenations
            text_parts = [_getText("TXT_KEY_WB_PYTHON", ()), "\n"]
            # Use pre-cached tuple of events
            for event in _PYTHON_EVENTS:
                text_parts.append(_ICON_BULLET)
                text_parts.append(event)
                text_parts.append("\n")
            # Remove last newline
            text_parts.pop()
            return "".join(text_parts)
        elif iData2 == 1:
            return _getText("TXT_KEY_WB_PLAYER_DATA", ())
        elif iData2 == 2:
            return _getText("TXT_KEY_WB_TEAM_DATA", ())
        elif iData2 == 3:
            return _getText("TXT_KEY_PEDIA_CATEGORY_TECH", ())
        elif iData2 == 4:
            return _getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ())
        elif iData2 == 5:
            return _getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + _getText("TXT_KEY_CONCEPT_CITIES", ())
        elif iData2 == 6:
            return _getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ())
        elif iData2 == 7:
            return _getText("TXT_KEY_WB_CITY_DATA2", ())
        elif iData2 == 8:
            return _getText("TXT_KEY_WB_BUILDINGS", ())
        elif iData2 == 9:
            return "Platy Builder\nVersion: 4.17b"
        elif iData2 == 10:
            return _getText("TXT_KEY_CONCEPT_EVENTS", ())
        elif iData2 == 11:
            return _getText("TXT_KEY_WB_RIVER_PLACEMENT", ())
        elif iData2 == 12:
            return _getText("TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT", ())
        elif iData2 == 13:
            return _getText("TXT_KEY_PEDIA_CATEGORY_BONUS", ())
        elif iData2 == 14:
            return _getText("TXT_KEY_WB_PLOT_TYPE", ())
        elif iData2 == 15:
            return _getText("TXT_KEY_CONCEPT_TERRAIN", ())
        elif iData2 == 16:
            return _getText("TXT_KEY_PEDIA_CATEGORY_ROUTES", ())
        elif iData2 == 17:
            return _getText("TXT_KEY_PEDIA_CATEGORY_FEATURE", ())
        elif iData2 == 18:
            return _getText("TXT_KEY_MISSION_BUILD_CITY", ())
        elif iData2 == 19:
            return _getText("TXT_KEY_WB_ADD_BUILDINGS", ())
        elif iData2 == 20:
            return _getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ())
        elif iData2 == 21:
            return _getText("TXT_KEY_CONCEPT_CORPORATIONS", ())
        elif iData2 == 22:
            return _getText("TXT_WORD_ESPIONAGE", ())
        elif iData2 == 23:
            return _getText("TXT_KEY_PITBOSS_GAME_OPTIONS", ())
        elif iData2 == 24:
            return _getText("TXT_KEY_WB_SENSIBILITY", ())
        elif iData2 == 27:
            return _getText("TXT_KEY_WB_ADD_UNITS", ())
        elif iData2 == 28:
            return _getText("TXT_KEY_WB_TERRITORY", ())
        elif iData2 == 29:
            return _getText("TXT_KEY_WB_ERASE_ALL_PLOTS", ())
        elif iData2 == 30:
            return _getText("TXT_KEY_WB_REPEATABLE", ())
        elif iData2 == 32:
            return _getText("TXT_KEY_WB_STARTING_PLOT", ())
        elif iData2 == 33:
            return _getText("TXT_KEY_INFO_SCREEN", ())
        elif iData2 == 34:
            return _getText("TXT_KEY_CONCEPT_TRADE", ())
        return ""

    def _getWidget1043Help(self, iData2):
        """Helper method for widget 1043"""
        if iData2 == 0:
            return _getText("TXT_KEY_WB_DONE", ())
        elif iData2 == 1:
            return _getText("TXT_KEY_WB_FORTIFY", ())
        elif iData2 == 2:
            return _getText("TXT_KEY_WB_WAIT", ())
        return ""

    def _getCityHoverText(self, iPlayer, iData2):
        """Optimized city hover text generation using list building"""
        pPlayer = _getPlayer(iPlayer)
        pCity = pPlayer.getCity(iData2)
        if _GetWorldBuilderMode():
            # Build text parts in a list for efficient joining
            text_parts = ["<font=3>"]

            # City name and population
            if pCity.isCapital():
                text_parts.append(_getText("[ICON_STAR]", ()))
            elif pCity.isGovernmentCenter():
                text_parts.append(_getText("[ICON_SILVER_STAR]", ()))
            text_parts.append(u"%s: %d<font=2>" % (pCity.getName(), pCity.getPopulation()))

            # Icons line
            icon_parts = []
            if pCity.isConnectedToCapital(iPlayer):
                icon_parts.append(_getText("[ICON_TRADE]", ()))

            # Religions
            for i in xrange(_getNumReligionInfos()):
                if pCity.isHolyCityByType(i):
                    icon_parts.append(u"%c" % _getReligionInfo(i).getHolyCityChar())
                elif pCity.isHasReligion(i):
                    icon_parts.append(u"%c" % _getReligionInfo(i).getChar())

            # Corporations
            for i in xrange(_getNumCorporationInfos()):
                if pCity.isHeadquartersByType(i):
                    icon_parts.append(u"%c" % _getCorporationInfo(i).getHeadquarterChar())
                elif pCity.isHasCorporation(i):
                    icon_parts.append(u"%c" % _getCorporationInfo(i).getChar())

            if icon_parts:
                text_parts.append("\n")
                text_parts.extend(icon_parts)

            # Defense
            iMaxDefense = pCity.getTotalDefense(False)
            if iMaxDefense > 0:
                text_parts.append(u"\n%s: " % _getText("[ICON_DEFENSE]", ()))
                iCurrent = pCity.getDefenseModifier(False)
                if iCurrent != iMaxDefense:
                    text_parts.append(u"%d/" % iCurrent)
                text_parts.append(u"%d%%" % iMaxDefense)

            # Food
            text_parts.append(u"\n%s: %d/%d" % (_getText("[ICON_FOOD]", ()), pCity.getFood(), pCity.growthThreshold()))
            iFoodGrowth = pCity.foodDifference(True)
            if iFoodGrowth != 0:
                text_parts.append(u" %+d" % iFoodGrowth)

            # Production
            if pCity.isProduction():
                text_parts.append(u"\n%s:" % _getText("[ICON_PRODUCTION]", ()))
                if not pCity.isProductionProcess():
                    text_parts.append(u" %d/%d" % (pCity.getProductionProgress(), pCity.getProductionNeeded()))
                    iProduction = pCity.getCurrentProductionDifference(False, True)
                    if iProduction != 0:
                        text_parts.append(u" %+d" % iProduction)
                text_parts.append(u" (%s)" % pCity.getProductionName())

            # Great People
            iGPRate = pCity.getGreatPeopleRate()
            iProgress = pCity.getGreatPeopleProgress()
            if iGPRate > 0 or iProgress > 0:
                text_parts.append(u"\n%s: %d/%d %+d" % (_getText("[ICON_GREATPEOPLE]", ()), iProgress,
                                                        pPlayer.greatPeopleThresholdNonMilitary(), iGPRate))

            # Culture
            if pCity.getCultureThreshold() > 0:
                text_parts.append(u"\n%s: %d/%d (%s)" % (_getText("[ICON_CULTURE]", ()), pCity.getCulture(iPlayer),
                                                         pCity.getCultureThreshold(), _getCultureLevelInfo(
                        pCity.getCultureLevel()).getDescription()))
            else:
                text_parts.append(u"\n%s: %d (%s)" % (_getText("[ICON_CULTURE]", ()), pCity.getCulture(iPlayer),
                                                      _getCultureLevelInfo(pCity.getCultureLevel()).getDescription()))

            # Commerce
            commerce_parts = []
            for i in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
                iAmount = pCity.getCommerceRateTimes100(i)
                if iAmount > 0:
                    commerce_parts.append(
                        u"%d.%02d%c" % (pCity.getCommerceRate(i), iAmount % 100, _getCommerceInfo(i).getChar()))

            if commerce_parts:
                text_parts.append("\n")
                text_parts.append(", ".join(commerce_parts))

            # Maintenance
            iMaintenance = pCity.getMaintenanceTimes100()
            if iMaintenance != 0:
                text_parts.append("\n")
                text_parts.append(_COLOR_WARNING)
                text_parts.append(_getText("INTERFACE_CITY_MAINTENANCE", ()))
                text_parts.append(" </color>")
                text_parts.append(u"-%d.%02d%c" % (iMaintenance / 100, iMaintenance % 100,
                                                   _getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()))

            # Buildings and Wonders - Collect buildings in lists to be sorted.
            lBuildings = []
            lWonders = []
            for i in xrange(_getNumBuildingInfos()):
                if pCity.hasBuilding(i):
                    if isLimitedWonder(i):
                        lWonders.append(_getBuildingInfo(i).getDescription())
                    else:
                        lBuildings.append(_getBuildingInfo(i).getDescription())

            if lBuildings:
                lBuildings.sort()
                text_parts.append("\n")
                text_parts.append(_COLOR_BUILDING)
                text_parts.append(_getText("TXT_KEY_WB_BUILDINGS", ()))
                text_parts.append(": </color>")
                text_parts.append(", ".join(lBuildings))

            if lWonders:
                lWonders.sort()
                text_parts.append("\n")
                text_parts.append(_COLOR_SELECTED)
                text_parts.append(_getText("TXT_KEY_CONCEPT_WONDERS", ()))
                text_parts.append(": </color>")
                text_parts.append(", ".join(lWonders))

            text_parts.append("</font>")
            return "".join(text_parts)
        return ""

    def _getUnitHoverText(self, iPlayer, iData2):
        """Optimized unit hover text"""
        pUnit = _getPlayer(iPlayer).getUnit(iData2)
        sText = _getSpecificUnitHelp(pUnit, True, False)
        if _GetWorldBuilderMode():
            # Use list building for efficiency
            text_parts = [
                sText,
                "\n", _getText("TXT_WORD_UNIT", ()), " ID: ", str(iData2),
                "\n", _getText("TXT_KEY_WB_GROUP", ()), " ID: ", str(pUnit.getGroupID()),
                "\nX: ", str(pUnit.getX()), ", Y: ", str(pUnit.getY()),
                "\n", _getText("TXT_KEY_WB_AREA_ID", ()), ": ", str(pUnit.plot().getArea())
            ]
            return "".join(text_parts)
        return sText