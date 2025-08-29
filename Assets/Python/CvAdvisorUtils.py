## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## Memory-optimized version for 32-bit Caveman2Cosmos mod

from CvPythonExtensions import *

# Pre-cache global references to save repeated lookups
GC = CyGlobalContext()
GAME = GC.getGame()
TRNSLTR = CyTranslator()

# Pre-cache frequently used methods for direct access
_getPlayer = GC.getPlayer
_getTeam = GC.getTeam
_getNumBuildingInfos = GC.getNumBuildingInfos
_getBuildingInfo = GC.getBuildingInfo
_getCorporationInfo = GC.getCorporationInfo
_getUnitInfo = GC.getUnitInfo
_getNumUnitInfos = GC.getNumUnitInfos
_getReligionInfo = GC.getReligionInfo
_getBonusInfo = GC.getBonusInfo
_getNumBonusInfos = GC.getNumBonusInfos
_getInfoTypeForString = GC.getInfoTypeForString

# Pre-cache game methods
_isNetworkMultiPlayer = GAME.isNetworkMultiPlayer
_getElapsedGameTurns = GAME.getElapsedGameTurns
_getActivePlayer = GAME.getActivePlayer
_isCorporationFounded = GAME.isCorporationFounded
_getGameTurn = GAME.getGameTurn

# Pre-cache translator method
_getText = TRNSLTR.getText

# Use tuples for immutable data - saves memory vs lists
lPopulation = (
    (2000000000, FeatTypes.FEAT_POPULATION_2_BILLION, "TXT_KEY_FEAT_2_BILLION"),
    (1000000000, FeatTypes.FEAT_POPULATION_1_BILLION, "TXT_KEY_FEAT_1_BILLION"),
    (500000000, FeatTypes.FEAT_POPULATION_500_MILLION, "TXT_KEY_FEAT_500_MILLION"),
    (200000000, FeatTypes.FEAT_POPULATION_200_MILLION, "TXT_KEY_FEAT_200_MILLION"),
    (100000000, FeatTypes.FEAT_POPULATION_100_MILLION, "TXT_KEY_FEAT_100_MILLION"),
    (50000000, FeatTypes.FEAT_POPULATION_50_MILLION, "TXT_KEY_FEAT_50_MILLION"),
    (20000000, FeatTypes.FEAT_POPULATION_20_MILLION, "TXT_KEY_FEAT_20_MILLION"),
    (10000000, FeatTypes.FEAT_POPULATION_10_MILLION, "TXT_KEY_FEAT_10_MILLION"),
    (5000000, FeatTypes.FEAT_POPULATION_5_MILLION, "TXT_KEY_FEAT_5_MILLION"),
    (2000000, FeatTypes.FEAT_POPULATION_2_MILLION, "TXT_KEY_FEAT_2_MILLION"),
    (1000000, FeatTypes.FEAT_POPULATION_1_MILLION, "TXT_KEY_FEAT_1_MILLION"),
    (500000, FeatTypes.FEAT_POPULATION_HALF_MILLION, "TXT_KEY_FEAT_HALF_MILLION")
)

# Pre-cache string constants
_TXT_ACCOMPLISHED_OK = "TXT_KEY_FEAT_ACCOMPLISHED_OK"
_TXT_ACCOMPLISHED_MORE = "TXT_KEY_FEAT_ACCOMPLISHED_MORE"
_TXT_POPUP_DEMAND_AGREE = "TXT_KEY_POPUP_DEMAND_AGREE"
_TXT_POPUP_DEMAND_REFUSE = "TXT_KEY_POPUP_DEMAND_REFUSE"
_TXT_POPUP_DEMAND_EXAMINE = "TXT_KEY_POPUP_DEMAND_EXAMINE"
_TXT_KEY_OR = "TXT_KEY_OR"

g_iAdvisorNags = 0
g_listNoLiberateCities = []
lCorporations = []
lBonus = []
unitCombatFeats = []


def resetNoLiberateCities():
    """Reset global caches - optimized with pre-cached lookups"""
    global g_listNoLiberateCities, lCorporations, lBonus, unitCombatFeats

    # Clear lists
    g_listNoLiberateCities = []
    lCorporations = []
    lBonus = []

    # Build corporations list - use xrange for Python 2.4 compatibility
    for iI in xrange(_getNumBuildingInfos()):
        CvBuildingInfo = _getBuildingInfo(iI)
        eCorporation = CvBuildingInfo.getFoundsCorporation()
        if eCorporation == -1 or _isCorporationFounded(eCorporation):
            continue

        bonuses = _getCorporationInfo(eCorporation).getPrereqBonuses()
        if not bonuses:
            continue

        # Check if any unit has this building
        iUnit = -1
        for iUnitX in xrange(_getNumUnitInfos()):
            if _getUnitInfo(iUnitX).getHasBuilding(iI):
                iUnit = iUnitX
                break

        if iUnit == -1:
            continue

        # Gather tech prereqs efficiently
        techs = []
        iTech = CvBuildingInfo.getPrereqAndTech()
        if iTech > -1:
            techs.append(iTech)
        # Extend is more efficient than multiple appends
        techs.extend(CvBuildingInfo.getPrereqAndTechs())

        if techs:  # Only add if has tech prereqs
            lCorporations.append((eCorporation, tuple(techs), iUnit, bonuses))

    # Build bonus lists - use sets for O(1) lookup
    lLuxury = []
    lFood = []
    for i in xrange(_getNumBonusInfos()):
        info = _getBonusInfo(i)
        if info.getHappiness() > 0:
            lLuxury.append(i)
        if info.getHealth() > 0:
            lFood.append(i)

    # Convert to tuples for memory efficiency
    if lLuxury:
        lLuxury = tuple(lLuxury)
    if lFood:
        lFood = tuple(lFood)

    # Build bonus feat list with tuples
    iCopper = _getInfoTypeForString("BONUS_COPPER_ORE")
    if iCopper > -1:
        lBonus.append((FeatTypes.FEAT_COPPER_CONNECTED, (iCopper,), "TXT_KEY_FEAT_COPPER_CONNECTED"))

    iHorse = _getInfoTypeForString("BONUS_HORSE")
    if iHorse > -1:
        lBonus.append((FeatTypes.FEAT_HORSE_CONNECTED, (iHorse,), "TXT_KEY_FEAT_HORSE_CONNECTED"))

    iIron = _getInfoTypeForString("BONUS_IRON_ORE")
    if iIron > -1:
        lBonus.append((FeatTypes.FEAT_IRON_CONNECTED, (iIron,), "TXT_KEY_FEAT_IRON_CONNECTED"))

    if lLuxury:
        lBonus.append((FeatTypes.FEAT_LUXURY_CONNECTED, lLuxury, "TXT_KEY_FEAT_LUXURY_CONNECTED"))
    if lFood:
        lBonus.append((FeatTypes.FEAT_FOOD_CONNECTED, lFood, "TXT_KEY_FEAT_FOOD_CONNECTED"))

    # Convert to tuple for memory efficiency
    lBonus = tuple(lBonus)

    # Build unit combat feats as tuple of tuples
    unitCombatFeats = (
        (_getInfoTypeForString("UNITCOMBAT_ARCHER"), FeatTypes.FEAT_UNITCOMBAT_ARCHER,
         "TXT_KEY_FEAT_UNITCOMBAT_ARCHER"),
        (_getInfoTypeForString("UNITCOMBAT_MOUNTED"), FeatTypes.FEAT_UNITCOMBAT_MOUNTED,
         "TXT_KEY_FEAT_UNITCOMBAT_MOUNTED"),
        (_getInfoTypeForString("UNITCOMBAT_MELEE"), FeatTypes.FEAT_UNITCOMBAT_MELEE, "TXT_KEY_FEAT_UNITCOMBAT_MELEE"),
        (_getInfoTypeForString("UNITCOMBAT_SIEGE"), FeatTypes.FEAT_UNITCOMBAT_SIEGE, "TXT_KEY_FEAT_UNITCOMBAT_SIEGE"),
        (_getInfoTypeForString("UNITCOMBAT_GUN"), FeatTypes.FEAT_UNITCOMBAT_GUN, "TXT_KEY_FEAT_UNITCOMBAT_GUN"),
        (_getInfoTypeForString("UNITCOMBAT_HELICOPTER"), FeatTypes.FEAT_UNITCOMBAT_HELICOPTER,
         "TXT_KEY_FEAT_UNITCOMBAT_HELICOPTER"),
        (_getInfoTypeForString("UNITCOMBAT_MOTILITY_NAVAL"), FeatTypes.FEAT_UNITCOMBAT_NAVAL,
         "TXT_KEY_FEAT_UNITCOMBAT_NAVAL")
    )


def _createFeatPopup(iPlayer, eFeat, iCityID, szText):
    """Helper to create feat popup - reduces code duplication"""
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setData1(eFeat)
    popupInfo.setData2(iCityID)
    popupInfo.setText(szText)
    popupInfo.setOnClickedPythonCallback("featAccomplishedOnClickedCallback")
    popupInfo.setOnFocusPythonCallback("featAccomplishedOnFocusCallback")
    popupInfo.addPythonButton(_getText(_TXT_ACCOMPLISHED_OK, ()), "")
    popupInfo.addPythonButton(_getText(_TXT_ACCOMPLISHED_MORE, ()), "")
    popupInfo.addPopup(iPlayer)


def unitBuiltFeats(CyCity, CyUnit):
    """Check unit-related feats when unit is built - optimized"""
    iPlayer = CyCity.getOwner()
    CyPlayer = _getPlayer(iPlayer)

    # Pre-cache common checks
    bShowPopup = (not _isNetworkMultiPlayer() and
                  _getElapsedGameTurns() != 0 and
                  iPlayer == _getActivePlayer() and
                  CyPlayer.isOption(PlayerOptionTypes.PLAYEROPTION_ADVISOR_POPUPS))

    if bShowPopup:
        iCityID = CyCity.getID()
    else:
        iCityID = -1

    # Check unit combat feats
    for iCombat, eFeat, szTxt in unitCombatFeats:
        if not CyPlayer.isFeatAccomplished(eFeat) and CyUnit.isHasUnitCombat(iCombat):
            CyPlayer.setFeatAccomplished(eFeat, True)
            if bShowPopup:
                _createFeatPopup(iPlayer, eFeat, iCityID,
                                 _getText(szTxt, (CyUnit.getNameKey(), CyCity.getNameKey())))

    # Check privateer feat
    if not CyPlayer.isFeatAccomplished(FeatTypes.FEAT_UNIT_PRIVATEER):
        if (_getUnitInfo(CyUnit.getUnitType()).isHiddenNationality() and
                CyUnit.getDomainType() == DomainTypes.DOMAIN_SEA):
            CyPlayer.setFeatAccomplished(FeatTypes.FEAT_UNIT_PRIVATEER, True)
            if bShowPopup:
                _createFeatPopup(iPlayer, FeatTypes.FEAT_UNIT_PRIVATEER, iCityID,
                                 _getText("TXT_KEY_FEAT_UNIT_PRIVATEER",
                                          (CyUnit.getNameKey(), CyCity.getNameKey())))

    # Check spy feat
    if not CyPlayer.isFeatAccomplished(FeatTypes.FEAT_UNIT_SPY):
        if _getUnitInfo(CyUnit.getUnitType()).isSpy():
            CyPlayer.setFeatAccomplished(FeatTypes.FEAT_UNIT_SPY, True)
            if bShowPopup:
                _createFeatPopup(iPlayer, FeatTypes.FEAT_UNIT_SPY, iCityID,
                                 _getText("TXT_KEY_FEAT_UNIT_SPY",
                                          (CyUnit.getNameKey(), CyCity.getNameKey())))


def endTurnFeats(iPlayer):
    """Check end-of-turn feats - optimized with early exits and caching"""
    global g_iAdvisorNags
    g_iAdvisorNags = 0

    CyPlayer = _getPlayer(iPlayer)
    CyCity0 = CyPlayer.getCapitalCity()
    if CyCity0 is None:
        return

    # Pre-cache popup check
    bShowPopup = (not _isNetworkMultiPlayer() and
                  iPlayer == _getActivePlayer() and
                  CyPlayer.isOption(PlayerOptionTypes.PLAYEROPTION_ADVISOR_POPUPS))

    # Population feat - early exit on first accomplished
    lRealPopulation = CyPlayer.getRealPopulation()
    for pop_threshold, eFeat, szKey in lPopulation:
        if CyPlayer.isFeatAccomplished(eFeat):
            break
        if lRealPopulation > pop_threshold:
            CyPlayer.setFeatAccomplished(eFeat, True)
            if bShowPopup:
                _createFeatPopup(iPlayer, eFeat, -1,
                                 _getText(szKey, (CyPlayer.getCivilizationDescriptionKey(),)))
            break

    # Trade Route - use generator for efficiency
    if not CyPlayer.isFeatAccomplished(FeatTypes.FEAT_TRADE_ROUTE):
        for CyCityX in CyPlayer.cities():
            if not CyCityX.isCapital() and CyCityX.isConnectedToCapital(iPlayer):
                CyPlayer.setFeatAccomplished(FeatTypes.FEAT_TRADE_ROUTE, True)
                if bShowPopup:
                    _createFeatPopup(iPlayer, FeatTypes.FEAT_TRADE_ROUTE, CyCityX.getID(),
                                     _getText("TXT_KEY_FEAT_TRADE_ROUTE", (CyCityX.getNameKey(),)))
                break

    # First Bonuses - cache hasBonus checks
    for eFeat, bonuses, szKey in lBonus:
        if not CyPlayer.isFeatAccomplished(eFeat):
            for iBonus in bonuses:
                if CyCity0.hasBonus(iBonus):
                    CyPlayer.setFeatAccomplished(eFeat, True)
                    if bShowPopup:
                        _createFeatPopup(iPlayer, eFeat, CyCity0.getID(),
                                         _getText(szKey, (_getBonusInfo(iBonus).getTextKey(),)))
                    break

    # Corporations - optimized iteration
    if not CyPlayer.isFeatAccomplished(FeatTypes.FEAT_CORPORATION_ENABLED):
        global lCorporations
        eTeam = CyPlayer.getTeam()
        pTeam = _getTeam(eTeam)

        i = 0
        while i < len(lCorporations):
            eCorp, techs, iUnit, bonuses = lCorporations[i]

            if _isCorporationFounded(eCorp):
                del lCorporations[i]
                continue

            # Check if all techs are available
            bHasAllTechs = True
            for iTech in techs:
                if not pTeam.isHasTech(iTech):
                    bHasAllTechs = False
                    break

            if bHasAllTechs:
                CyPlayer.setFeatAccomplished(FeatTypes.FEAT_CORPORATION_ENABLED, True)

                if bShowPopup:
                    # Build bonus list efficiently
                    bonus_parts = []
                    for j, eBonus in enumerate(bonuses):
                        bonus_parts.append(_getBonusInfo(eBonus).getDescription())
                        if j < len(bonuses) - 1:
                            bonus_parts.append(_getText(_TXT_KEY_OR, ()))

                    _createFeatPopup(iPlayer, FeatTypes.FEAT_CORPORATION_ENABLED, CyCity0.getID(),
                                     _getText("TXT_KEY_FEAT_CORPORATION_ENABLED",
                                              (_getCorporationInfo(eCorp).getTextKey(),
                                               _getUnitInfo(iUnit).getTextKey(),
                                               "".join(bonus_parts))))
                break
            i += 1


def _createAdvisorPopup(iCityID, iData2, iData3, szText, szCallback):
    """Helper to create advisor popup - reduces code duplication"""
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setData1(iCityID)
    popupInfo.setData2(iData2)
    popupInfo.setData3(iData3)
    popupInfo.setText(szText)
    popupInfo.setOnClickedPythonCallback(szCallback)
    popupInfo.setOnFocusPythonCallback("cityWarningOnFocusCallback")
    popupInfo.addPythonButton(_getText(_TXT_POPUP_DEMAND_AGREE, ()), "")
    popupInfo.addPythonButton(_getText(_TXT_POPUP_DEMAND_REFUSE, ()), "")
    popupInfo.addPythonButton(_getText(_TXT_POPUP_DEMAND_EXAMINE, ()), "")
    popupInfo.addPopup(_getActivePlayer())


def cityAdvise(CyCity, iPlayer):
    """City advisor - heavily optimized with early exits and caching"""
    global g_iAdvisorNags

    # Early exit conditions
    if g_iAdvisorNags > 1 or CyCity.isDisorder():
        return

    CyPlayer = _getPlayer(iPlayer)
    if not CyPlayer.isOption(PlayerOptionTypes.PLAYEROPTION_ADVISOR_POPUPS):
        return

    # Cache frequently used values
    iTurn = _getGameTurn()
    iTurnFounded = CyCity.getGameTurnFounded()
    iTurnMod = iTurnFounded % 40
    iCityID = CyCity.getID()

    # Liberation check
    if iTurn % 40 == iTurnMod and iCityID not in g_listNoLiberateCities:
        iPlayerX = CyCity.getLiberationPlayer(False)
        if iPlayerX != -1:
            CyPlayerX = _getPlayer(iPlayerX)
            teamX = CyPlayerX.getTeam()
            if (_getTeam(CyPlayer.getTeam()).isHasMet(teamX) and
                    not _getTeam(teamX).isAtWarWith(_getTeam(_getActivePlayer()).getID())):
                _createAdvisorPopup(iCityID, 0, 0,
                                    _getText("TXT_KEY_POPUP_LIBERATION_DEMAND",
                                             (CyCity.getNameKey(),
                                              CyPlayerX.getCivilizationDescriptionKey(),
                                              CyPlayerX.getNameKey())),
                                    "liberateOnClickedCallback")
                g_listNoLiberateCities.append(iCityID)
                g_iAdvisorNags += 1
                return

        elif (CyPlayer.canSplitEmpire() and
              CyPlayer.canSplitArea(CyCity.area().getID()) and
              CyCity.AI_cityValue() < 0):

            _createAdvisorPopup(iCityID, 0, 0,
                                _getText("TXT_KEY_POPUP_COLONY_DEMAND", (CyCity.getNameKey(),)),
                                "colonyOnClickedCallback")
            g_listNoLiberateCities.append(iCityID)
            g_iAdvisorNags += 1
            return

    # Production checks - only if producing
    if not CyCity.isProduction():
        return

    # Cache common production checks
    bIsProductionUnit = CyCity.isProductionUnit()
    bIsProductionBuilding = CyCity.isProductionBuilding()
    iQueueLength = CyCity.getOrderQueueLength()

    if iQueueLength > 1:
        return

    # Unit production advice
    if not bIsProductionUnit:
        _checkUnitProductionAdvice(CyCity, CyPlayer, iTurn, iTurnMod, iCityID, iPlayer)

    # Building production advice  
    if not bIsProductionBuilding:
        _checkBuildingProductionAdvice(CyCity, iTurn, iTurnMod, iCityID)


def _checkUnitProductionAdvice(CyCity, CyPlayer, iTurn, iTurnMod, iCityID, iPlayer):
    """Check unit production advice - extracted for clarity"""
    global g_iAdvisorNags

    CyArea = CyCity.area()
    iAreaID = CyArea.getID()

    # Settler advice
    if ((iTurn + 3) % 40 == iTurnMod and
            _getElapsedGameTurns() < 200 and
            CyCity.getPopulation() > 2 and
            not CyPlayer.AI_isFinancialTrouble() and
            not CyPlayer.AI_totalAreaUnitAIs(CyArea, UnitAITypes.UNITAI_SETTLE) and
            CyArea.getBestFoundValue(iPlayer) > 0):

        eBestUnit = _findBestUnit(CyCity, CyPlayer, CyArea, UnitAITypes.UNITAI_SETTLE, DomainTypes.DOMAIN_LAND)
        if eBestUnit > -1:
            _createAdvisorPopup(iCityID, OrderTypes.ORDER_TRAIN, eBestUnit,
                                _getText("TXT_KEY_POPUP_UNIT_SETTLE_DEMAND",
                                         (_getUnitInfo(eBestUnit).getTextKey(),)),
                                "cityWarningOnClickedCallback")
            g_iAdvisorNags += 1
            return

    # Worker advice
    if ((iTurn + 15) % 40 == iTurnMod and
            CyCity.getPopulation() > 1 and
            not CyCity.countNumImprovedPlots() and
            CyCity.AI_countBestBuilds(CyArea) > 3):

        eBestUnit = _findBestUnit(CyCity, CyPlayer, CyArea, UnitAITypes.UNITAI_WORKER, DomainTypes.DOMAIN_LAND)
        if eBestUnit > -1:
            _createAdvisorPopup(iCityID, OrderTypes.ORDER_TRAIN, eBestUnit,
                                _getText("TXT_KEY_POPUP_UNIT_WORKER_DEMAND",
                                         (CyCity.getNameKey(), _getUnitInfo(eBestUnit).getTextKey())),
                                "cityWarningOnClickedCallback")
            g_iAdvisorNags += 1
            return

    # Defense advice
    if ((iTurn + 27) % 40 == iTurnMod and
            not CyCity.plot().getNumDefenders(iPlayer)):

        eBestUnit = _findBestDefender(CyCity, CyPlayer, CyArea)
        if eBestUnit > -1:
            _createAdvisorPopup(iCityID, OrderTypes.ORDER_TRAIN, eBestUnit,
                                _getText("TXT_KEY_POPUP_UNIT_DEFENSE_DEMAND",
                                         (CyCity.getNameKey(), _getUnitInfo(eBestUnit).getTextKey())),
                                "cityWarningOnClickedCallback")
            g_iAdvisorNags += 1
            return

    # Missionary advice
    if ((iTurn + 36) % 40 == iTurnMod and
            not CyPlayer.AI_totalAreaUnitAIs(CyArea, UnitAITypes.UNITAI_MISSIONARY) and
            not _getTeam(CyPlayer.getTeam()).isAtWar(False)):

        eStateReligion = CyPlayer.getStateReligion()
        if (eStateReligion != -1 and
                CyPlayer.getHasReligionCount(eStateReligion) < CyPlayer.getNumCities() / 2):

            eBestUnit = _findBestMissionary(CyCity, CyPlayer, CyArea, eStateReligion)
            if eBestUnit > -1:
                _createAdvisorPopup(iCityID, OrderTypes.ORDER_TRAIN, eBestUnit,
                                    _getText("TXT_KEY_POPUP_MISSIONARY_DEMAND",
                                             (_getReligionInfo(eStateReligion).getTextKey(),
                                              _getUnitInfo(eBestUnit).getTextKey(),
                                              CyCity.getNameKey())),
                                    "cityWarningOnClickedCallback")
                g_iAdvisorNags += 1


def _checkBuildingProductionAdvice(CyCity, iTurn, iTurnMod, iCityID):
    """Check building production advice - extracted for clarity"""
    global g_iAdvisorNags

    # Map turn offsets to building checks - more efficient than multiple if statements
    checks = (
        (6, CyCity.healthRate(False, 0) < 0, "getHealth", "TXT_KEY_POPUP_UNHEALTHY_CITIZENS_DEMAND",
         "TXT_KEY_POPUP_UNHEALTHY_DO_SO_NEXT", "TXT_KEY_POPUP_UNHEALTHY_REFUSE", "TXT_KEY_POPUP_UNHEALTHY_EXAMINE"),
        (9, CyCity.angryPopulation(0) > 0, "getHappiness", "TXT_KEY_POPUP_UNHAPPY_CITIZENS_DEMAND",
         "TXT_KEY_POPUP_UNHAPPY_DO_SO_NEXT", "TXT_KEY_POPUP_UNHAPPY_REFUSE", "TXT_KEY_POPUP_UNHEALTHY_EXAMINE"),
        (12, iTurn < 100 and _getTeam(_getPlayer(CyCity.getOwner()).getTeam()).getHasMetCivCount(
            True) > 0 and not CyCity.getBuildingDefense(),
         "getDefenseModifier", "TXT_KEY_POPUP_BUILDING_DEFENSE_DEMAND",
         _TXT_POPUP_DEMAND_AGREE, _TXT_POPUP_DEMAND_REFUSE, _TXT_POPUP_DEMAND_EXAMINE),
        (18, CyCity.getMaintenance() >= 8, "getMaintenanceModifier", "TXT_KEY_POPUP_MAINTENANCE_DEMAND",
         _TXT_POPUP_DEMAND_AGREE, _TXT_POPUP_DEMAND_REFUSE, _TXT_POPUP_DEMAND_EXAMINE),
        (21, CyCity.getCommerceRate(CommerceTypes.COMMERCE_CULTURE) < 10 and not CyCity.isOccupation(),
         "getCommerceChangeCulture", "TXT_KEY_POPUP_CULTURE_DEMAND",
         _TXT_POPUP_DEMAND_AGREE, _TXT_POPUP_DEMAND_REFUSE, _TXT_POPUP_DEMAND_EXAMINE),
        (24, CyCity.getBaseCommerceRate(CommerceTypes.COMMERCE_GOLD) > 10,
         "getCommerceModifierGold", "TXT_KEY_POPUP_GOLD_DEMAND",
         _TXT_POPUP_DEMAND_AGREE, _TXT_POPUP_DEMAND_REFUSE, _TXT_POPUP_DEMAND_EXAMINE),
        (30, CyCity.getBaseCommerceRate(CommerceTypes.COMMERCE_RESEARCH) > 10,
         "getCommerceModifierResearch", "TXT_KEY_POPUP_RESEARCH_DEMAND",
         _TXT_POPUP_DEMAND_AGREE, _TXT_POPUP_DEMAND_REFUSE, _TXT_POPUP_DEMAND_EXAMINE),
    )

    for offset, condition, attr_name, txt_key, btn1, btn2, btn3 in checks:
        if (iTurn + offset) % 40 == iTurnMod and condition:
            iBestBuilding = _findBestBuildingByAttribute(CyCity, attr_name)
            if iBestBuilding > -1:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setData1(iCityID)
                popupInfo.setData2(OrderTypes.ORDER_CONSTRUCT)
                popupInfo.setData3(iBestBuilding)
                popupInfo.setText(_getText(txt_key, (CyCity.getNameKey(),
                                                     _getBuildingInfo(iBestBuilding).getTextKey())))
                popupInfo.setOnClickedPythonCallback("cityWarningOnClickedCallback")
                popupInfo.setOnFocusPythonCallback("cityWarningOnFocusCallback")
                popupInfo.addPythonButton(_getText(btn1, ()), "")
                popupInfo.addPythonButton(_getText(btn2, ()), "")
                popupInfo.addPythonButton(_getText(btn3, ()), "")
                popupInfo.addPopup(_getActivePlayer())
                g_iAdvisorNags += 1
                return

    # Special case for water food
    if (iTurn + 33) % 40 == iTurnMod and CyCity.countNumWaterPlots() > 10:
        iBestBuilding = _findBestWaterFoodBuilding(CyCity)
        if iBestBuilding > -1:
            _createAdvisorPopup(iCityID, OrderTypes.ORDER_CONSTRUCT, iBestBuilding,
                                _getText("TXT_KEY_POPUP_WATER_FOOD_DEMAND",
                                         (CyCity.getNameKey(),
                                          _getBuildingInfo(iBestBuilding).getTextKey())),
                                "cityWarningOnClickedCallback")
            g_iAdvisorNags += 1


def _findBestUnit(CyCity, CyPlayer, CyArea, eUnitAI, eDomain):
    """Find best unit for given AI type - optimized helper"""
    iBestValue = 0
    eBestUnit = -1

    for iUnit in xrange(_getNumUnitInfos()):
        if (not isLimitedUnit(iUnit) and
                _getUnitInfo(iUnit).getDomainType() == eDomain and
                CyCity.canTrain(iUnit, False, False, False, False) and
                CyCity.getFirstUnitOrder(iUnit) == -1):

            iValue = CyPlayer.AI_unitValue(iUnit, eUnitAI, CyArea)
            if iValue > iBestValue:
                iBestValue = iValue
                eBestUnit = iUnit

    return eBestUnit


def _findBestDefender(CyCity, CyPlayer, CyArea):
    """Find best defender unit - specialized for defense"""
    iBestValue = 0
    eBestUnit = -1

    for iUnit in xrange(_getNumUnitInfos()):
        if (not isLimitedUnit(iUnit) and
                _getUnitInfo(iUnit).getDomainType() == DomainTypes.DOMAIN_LAND and
                CyCity.canTrain(iUnit, False, False, False, False)):

            # Weight defense more heavily
            iValue = (CyPlayer.AI_unitValue(iUnit, UnitAITypes.UNITAI_CITY_DEFENSE, CyArea) * 2 +
                      CyPlayer.AI_unitValue(iUnit, UnitAITypes.UNITAI_ATTACK, CyArea))

            if iValue > iBestValue:
                iBestValue = iValue
                eBestUnit = iUnit

    return eBestUnit


def _findBestMissionary(CyCity, CyPlayer, CyArea, eReligion):
    """Find best missionary unit for religion"""
    iBestValue = 0
    iBestUnit = -1

    for iUnit in xrange(_getNumUnitInfos()):
        CvUnitInfo = _getUnitInfo(iUnit)
        if (CvUnitInfo.getDomainType() == DomainTypes.DOMAIN_LAND and
                CvUnitInfo.getReligionSpreads(eReligion) and
                CyCity.canTrain(iUnit, False, False, False, False)):

            iValue = CyPlayer.AI_unitValue(iUnit, UnitAITypes.UNITAI_MISSIONARY, CyArea)
            if iValue > iBestValue:
                iBestValue = iValue
                iBestUnit = iUnit

    return iBestUnit


def _findBestBuildingByAttribute(CyCity, attr_name):
    """Find best building by attribute - generic helper"""
    iBestValue = 0
    iBestBuilding = -1

    # Special handling for different attribute types
    if attr_name == "getMaintenanceModifier":
        # For maintenance, lower is better
        for iBuilding in xrange(_getNumBuildingInfos()):
            if not isLimitedWonder(iBuilding):
                iValue = getattr(_getBuildingInfo(iBuilding), attr_name)()
                if iValue < iBestValue and CyCity.canConstruct(iBuilding, False, False, False):
                    iBestValue = iValue
                    iBestBuilding = iBuilding

    elif attr_name == "getCommerceChangeCulture":
        # Special case for culture commerce
        for iBuilding in xrange(_getNumBuildingInfos()):
            if not isLimitedWonder(iBuilding):
                iValue = _getBuildingInfo(iBuilding).getCommerceChange(CommerceTypes.COMMERCE_CULTURE)
                if iValue > iBestValue and CyCity.canConstruct(iBuilding, False, False, False):
                    iBestValue = iValue
                    iBestBuilding = iBuilding

    elif attr_name == "getCommerceModifierGold":
        # Special case for gold commerce modifier
        for iBuilding in xrange(_getNumBuildingInfos()):
            if not isLimitedWonder(iBuilding):
                iValue = _getBuildingInfo(iBuilding).getCommerceModifier(CommerceTypes.COMMERCE_GOLD)
                if iValue > iBestValue and CyCity.canConstruct(iBuilding, False, False, False):
                    iBestValue = iValue
                    iBestBuilding = iBuilding

    elif attr_name == "getCommerceModifierResearch":
        # Special case for research commerce modifier
        for iBuilding in xrange(_getNumBuildingInfos()):
            if not isLimitedWonder(iBuilding):
                iValue = _getBuildingInfo(iBuilding).getCommerceModifier(CommerceTypes.COMMERCE_RESEARCH)
                if iValue > iBestValue and CyCity.canConstruct(iBuilding, False, False, False):
                    iBestValue = iValue
                    iBestBuilding = iBuilding

    else:
        # Generic attribute handling
        for iBuilding in xrange(_getNumBuildingInfos()):
            if not isLimitedWonder(iBuilding):
                iValue = getattr(_getBuildingInfo(iBuilding), attr_name)()
                if iValue > iBestValue and CyCity.canConstruct(iBuilding, False, False, False):
                    iBestValue = iValue
                    iBestBuilding = iBuilding

    return iBestBuilding


def _findBestWaterFoodBuilding(CyCity):
    """Find best building for water food production"""
    iBestValue = 0
    iBestBuilding = -1

    for iBuilding in xrange(_getNumBuildingInfos()):
        if not isLimitedWonder(iBuilding):
            CvBuildingInfo = _getBuildingInfo(iBuilding)
            for entry in CvBuildingInfo.getPlotYieldChange():
                if (entry.iType == PlotTypes.PLOT_OCEAN and
                        entry.iIndex == YieldTypes.YIELD_FOOD and
                        entry.iValue > iBestValue and
                        CyCity.canConstruct(iBuilding, False, False, False)):
                    iBestValue = entry.iValue
                    iBestBuilding = iBuilding
                    break

    return iBestBuilding