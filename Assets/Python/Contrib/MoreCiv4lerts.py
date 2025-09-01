## MoreCiv4lerts - Memory Optimized Version
## From HOF MOD V1.61.001
## Based upon Gillmer J. Derge's Civ4lerts.py
## Memory optimizations applied for 32-bit Python 2.4 compatibility

from CvPythonExtensions import *
import CvUtil
import TradeUtil
import gc

# Cache global constants to avoid repeated lookups
GC = CyGlobalContext()
GAME = GC.getGame()
TRNSLTR = CyTranslator()
EVENT_MESSAGE_TIME_LONG = GC.getDefineINT("EVENT_MESSAGE_TIME_LONG")

# Pre-cache frequently used constants
NO_DENIAL = DenialTypes.NO_DENIAL
TRADE_TECHNOLOGIES = TradeableItems.TRADE_TECHNOLOGIES
TRADE_MAPS = TradeableItems.TRADE_MAPS
TRADE_OPEN_BORDERS = TradeableItems.TRADE_OPEN_BORDERS
TRADE_DEFENSIVE_PACT = TradeableItems.TRADE_DEFENSIVE_PACT
TRADE_PERMANENT_ALLIANCE = TradeableItems.TRADE_PERMANENT_ALLIANCE
TRADE_VASSAL = TradeableItems.TRADE_VASSAL
TRADE_SURRENDER = TradeableItems.TRADE_SURRENDER
TRADE_PEACE_TREATY = TradeableItems.TRADE_PEACE_TREATY
COMMERCE_CULTURE = CommerceTypes.COMMERCE_CULTURE

# Pre-cache color indices
COLOR_MAGENTA = GC.getInfoTypeForString("COLOR_MAGENTA")


class MoreCiv4lerts:
    __slots__ = ('_event',)

    def __init__(self, eventManager):
        ## Init event handlers - single instance
        self._event = MoreCiv4lertsEvent(eventManager)
        # Cleanup reference
        del eventManager


class AbstractMoreCiv4lertsEvent(object):
    # Using slots to reduce memory overhead
    __slots__ = ()

    def __init__(self, eventManager, *args, **kwargs):
        super(AbstractMoreCiv4lertsEvent, self).__init__(*args, **kwargs)

    def _addMessageNoIcon(self, iPlayer, msg, iColor=-1):
        # Reuse the centralized handler directly
        CvUtil.sendMessage(msg, iPlayer, EVENT_MESSAGE_TIME_LONG, None, ColorTypes(iColor), -1, -1, False, False)

    def _addMessage(self, iPlayer, msg, icon, iX, iY, bOffArrow, bOnArrow, iColor):
        # Direct call to reduce stack depth
        CvUtil.sendMessage(msg, iPlayer, EVENT_MESSAGE_TIME_LONG, icon, ColorTypes(iColor), iX, iY, bOffArrow, bOnArrow)


class MoreCiv4lertsEvent(AbstractMoreCiv4lertsEvent):
    # Use slots to significantly reduce memory per instance
    __slots__ = ('eventMgr', 'options', 'CurrAvailTechTrades', 'PrevAvailTechTrades',
                 'PrevAvailBonusTrades', 'PrevAvailOpenBordersTrades', 'PrevAvailMapTrades',
                 'PrevAvailDefensivePactTrades', 'PrevAvailPermanentAllianceTrades',
                 'PrevAvailVassalTrades', 'PrevAvailSurrenderTrades', 'PrevAvailPeaceTrades',
                 'lastPopCount', 'lastLandCount', '_tradeData', '_icon_warning', '_icon_foundcity')

    def __init__(self, eventManager, *args, **kwargs):
        super(MoreCiv4lertsEvent, self).__init__(eventManager, *args, **kwargs)

        # Register event handlers
        eventManager.addEventHandler("BeginActivePlayerTurn", self.onBeginActivePlayerTurn)
        eventManager.addEventHandler("cityAcquiredAndKept", self.onCityAcquiredAndKept)
        eventManager.addEventHandler("cityBuilt", self.OnCityBuilt)
        eventManager.addEventHandler("cityRazed", self.OnCityRazed)
        eventManager.addEventHandler("cityLost", self.OnCityLost)
        eventManager.addEventHandler("GameStart", self.reset)
        eventManager.addEventHandler("OnLoad", self.reset)

        self.eventMgr = eventManager
        import BugCore
        self.options = BugCore.game.MoreCiv4lerts

        # Pre-create reusable objects
        self._tradeData = TradeData()
        self._icon_warning = "Art/Interface/Buttons/General/Warning_popup.dds"
        self._icon_foundcity = "Art/Interface/Buttons/Actions/foundcity.dds"

        self.reset()

    def reset(self, argsList=None):
        # Use smaller data structures where possible
        self.CurrAvailTechTrades = {}
        self.PrevAvailTechTrades = {}
        self.PrevAvailBonusTrades = {}
        # Use frozensets for immutable trade sets to save memory
        self.PrevAvailOpenBordersTrades = frozenset()
        self.PrevAvailMapTrades = frozenset()
        self.PrevAvailDefensivePactTrades = frozenset()
        self.PrevAvailPermanentAllianceTrades = frozenset()
        self.PrevAvailVassalTrades = frozenset()
        self.PrevAvailSurrenderTrades = frozenset()
        self.PrevAvailPeaceTrades = frozenset()
        self.lastPopCount = 0
        self.lastLandCount = 0
        # Force garbage collection after reset
        gc.collect()

    def getCheckForDomVictory(self):
        # Cache result to avoid repeated option checks
        return self.options.isShowDomPopAlert() or self.options.isShowDomLandAlert()

    def onBeginActivePlayerTurn(self, argsList):
        iPlayer = GAME.getActivePlayer()
        self.CheckForAlerts(iPlayer, True)

    def onCityAcquiredAndKept(self, argsList):
        if not self.getCheckForDomVictory():
            return
        if argsList[1] == GAME.getActivePlayer():
            self.CheckForAlerts(argsList[1], False)

    def OnCityBuilt(self, argsList):
        CyCity = argsList[0]
        iOwner = CyCity.getOwner()
        iPlayer = GAME.getActivePlayer()

        if self.getCheckForDomVictory():
            if iOwner == iPlayer:
                self.CheckForAlerts(iOwner, False)

        if self.options.isShowCityFoundedAlert():
            if iOwner != iPlayer:
                iActiveTeam = GC.getActivePlayer().getTeam()
                bRevealed = CyCity.isRevealed(iActiveTeam, False)
                CyPlayer = GC.getPlayer(iOwner)

                if bRevealed or canSeeCityList(CyPlayer):
                    if bRevealed:
                        msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_CITY_FOUNDED",
                                              (CyPlayer.getName(), CyCity.getName()))
                        CvUtil.sendMessage(msg, iPlayer, EVENT_MESSAGE_TIME_LONG, self._icon_foundcity,
                                           ColorTypes(COLOR_MAGENTA), CyCity.getX(), CyCity.getY(), True, True)
                    else:
                        msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_CITY_FOUNDED_UNSEEN",
                                              (CyPlayer.getName(), CyCity.getName()))
                        self._addMessageNoIcon(iPlayer, msg, COLOR_MAGENTA)

    def OnCityRazed(self, argsList):
        if not self.getCheckForDomVictory():
            return
        city, iPlayer = argsList
        if iPlayer == GAME.getActivePlayer():
            self.CheckForAlerts(iPlayer, False)

    def OnCityLost(self, argsList):
        if not self.getCheckForDomVictory():
            return
        city = argsList[0]
        if city.getOwner() == GAME.getActivePlayer():
            self.CheckForAlerts(city.getOwner(), False)

    def CheckForAlerts(self, iPlayer, bBeginTurn):
        CyPlayer = GC.getPlayer(iPlayer)
        CyTeam = GC.getTeam(CyPlayer.getTeam())
        iGrowthCount = 0

        # Cache option checks
        bCheck1 = self.options.isShowDomPopAlert()
        bCheck2 = bBeginTurn and self.options.isShowCityPendingExpandBorderAlert()

        if bCheck1 or bCheck2:
            # Check for cultural expansion and population growth
            iActiveTeam = GAME.getActiveTeam()

            # Use generator to avoid creating full list in memory
            for iPlayerX in xrange(GC.getMAX_PC_PLAYERS()):
                CyPlayerX = GC.getPlayer(iPlayerX)
                if not CyPlayerX.isAlive():
                    continue
                if CyPlayerX.getTeam() != iActiveTeam:
                    continue

                # Iterate through cities efficiently
                for cityX in CyPlayerX.cities():
                    if cityX.getFoodTurnsLeft() == 1 and not cityX.isFoodProduction() and not cityX.AI_isEmphasize(5):
                        iGrowthCount += 1

                    if bCheck2 and cityX.getCultureThreshold() > 0:
                        iCulture = cityX.getCulture(iPlayerX)
                        iCultureRate = cityX.getCommerceRate(COMMERCE_CULTURE)
                        if iCulture + iCultureRate >= cityX.getCultureThreshold():
                            if GAME.isOption(GameOptionTypes.GAMEOPTION_CULTURE_REALISTIC_SPREAD):
                                msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_CITY_TO_EXPAND_RCS", (cityX.getName(),))
                            else:
                                msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_CITY_TO_EXPAND", (cityX.getName(),))
                            CvUtil.sendMessage(msg, iPlayer, EVENT_MESSAGE_TIME_LONG, self._icon_warning,
                                               -1, cityX.getX(), cityX.getY(), True, True)

        # Check Domination Limit
        if self.getCheckForDomVictory() and GAME.isVictoryValid(3):
            # Population Limit
            if bCheck1 and iGrowthCount:
                iTotalPop = GAME.getTotalPopulation()
                if iTotalPop > 10:
                    iTeamPop = CyTeam.getTotalPopulation()
                    fPercent = iTeamPop * 100.0 / iTotalPop
                    iNewPop = iTeamPop + iGrowthCount
                    fPercentNext = iNewPop * 100.0 / iTotalPop

                    if iNewPop != self.lastPopCount:
                        fVictoryPercent = GAME.getAdjustedPopulationPercent(3) * 1.0
                        iLimitPop = int(iTotalPop * fVictoryPercent / 100)

                        # Build message based on conditions
                        msg = None
                        if fPercent >= fVictoryPercent:
                            msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_POP_EXCEEDS_LIMIT",
                                                  (iTeamPop, (u"%.2f%%" % fPercent), iLimitPop,
                                                   (u"%.2f%%" % fVictoryPercent)))
                        elif fPercentNext >= fVictoryPercent:
                            msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_POP_GROWTH_EXCEEDS_LIMIT",
                                                  (iTeamPop, iGrowthCount, (u"%.2f%%" % fPercentNext), iLimitPop,
                                                   (u"%.2f%%" % fVictoryPercent)))
                        elif fVictoryPercent - fPercentNext < self.options.getDomPopThreshold():
                            msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_POP_GROWTH_CLOSE_TO_LIMIT",
                                                  (iTeamPop, iGrowthCount, (u"%.2f%%" % fPercentNext), iLimitPop,
                                                   (u"%.2f%%" % fVictoryPercent)))
                        elif fVictoryPercent - fPercent < self.options.getDomPopThreshold():
                            msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_POP_CLOSE_TO_LIMIT",
                                                  (iTeamPop, (u"%.2f%%" % fPercent), iLimitPop,
                                                   (u"%.2f%%" % fVictoryPercent)))

                        if msg:
                            self._addMessageNoIcon(iPlayer, msg)
                        self.lastPopCount = iNewPop

            # Land Limit
            if self.options.isShowDomLandAlert():
                iTeamLand = CyTeam.getTotalLand()
                if iTeamLand > 40 and iTeamLand != self.lastLandCount:
                    iTotalLand = GC.getMap().getLandPlots()
                    fVictoryPercent = GAME.getAdjustedLandPercent(3) * 1.0
                    iLimitLand = int(iTotalLand * fVictoryPercent / 100)
                    fPercent = (iTeamLand * 100.0) / iTotalLand

                    msg = None
                    if fPercent > fVictoryPercent:
                        msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_LAND_EXCEEDS_LIMIT",
                                              (iTeamLand, (u"%.2f%%" % fPercent), iLimitLand,
                                               (u"%.2f%%" % fVictoryPercent)))
                    elif fVictoryPercent - fPercent < self.options.getDomLandThreshold():
                        msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_LAND_CLOSE_TO_LIMIT",
                                              (iTeamLand, (u"%.2f%%" % fPercent), iLimitLand,
                                               (u"%.2f%%" % fVictoryPercent)))

                    if msg:
                        self._addMessageNoIcon(iPlayer, msg)
                    self.lastLandCount = iTeamLand

        if not bBeginTurn:
            return

        # ********#
        # Trades #
        # ********#
        # Reuse single TradeData object
        tradeData = self._tradeData

        # Bonus Trade Alerts
        if self.options.isShowBonusTradeAlert():
            desiredBonuses = TradeUtil.getDesiredBonuses(CyPlayer, CyTeam)
            tradesByPlayer = {}

            for CyPlayerX in TradeUtil.getBonusTradePartners(CyPlayer):
                will, wont = TradeUtil.getTradeableBonuses(CyPlayerX, iPlayer)
                tradesByPlayer[CyPlayerX.getID()] = will

            for iLoopPlayer, currentTrades in tradesByPlayer.iteritems():
                # Get previous trades or empty set
                if iLoopPlayer in self.PrevAvailBonusTrades:
                    previousTrades = self.PrevAvailBonusTrades[iLoopPlayer]
                else:
                    previousTrades = frozenset()

                # Determine new bonuses
                newTrades = currentTrades.difference(previousTrades).intersection(desiredBonuses)
                if newTrades:
                    szNewTrades = self._buildBonusString(newTrades)
                    msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_NEW_BONUS_AVAIL",
                                          (GC.getPlayer(iLoopPlayer).getName(), szNewTrades))
                    self._addMessageNoIcon(iPlayer, msg)

                # Determine removed bonuses
                removedTrades = previousTrades.difference(currentTrades).intersection(desiredBonuses)
                if removedTrades:
                    szRemovedTrades = self._buildBonusString(removedTrades)
                    msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_BONUS_NOT_AVAIL",
                                          (GC.getPlayer(iLoopPlayer).getName(), szRemovedTrades))
                    self._addMessageNoIcon(iPlayer, msg)

            # Save current trades for next time
            self.PrevAvailBonusTrades = tradesByPlayer

        # Tech Trade Alerts
        if self.options.isShowTechTradeAlert():
            techsByPlayer = {}
            researchTechs = set()
            tradeData.ItemType = TRADE_TECHNOLOGIES
            bCheck1 = True

            for CyPlayerX in TradeUtil.getTechTradePartners(CyPlayer):
                techsToTrade = set()
                for i in xrange(CyTeam.getNumAdjacentResearch()):
                    iTechX = CyTeam.getAdjacentResearch(i)
                    if bCheck1 and CyPlayer.canResearch(iTechX, True, True):
                        researchTechs.add(iTechX)
                    tradeData.iData = iTechX
                    if CyPlayerX.canTradeItem(iPlayer, tradeData, False):
                        if CyPlayerX.getTradeDenial(iPlayer, tradeData) == NO_DENIAL:
                            techsToTrade.add(iTechX)
                bCheck1 = False
                techsByPlayer[CyPlayerX.getID()] = techsToTrade

            for iLoopPlayer, currentTechs in techsByPlayer.iteritems():
                # Get previous techs or empty set
                if iLoopPlayer in self.PrevAvailTechTrades:
                    previousTechs = self.PrevAvailTechTrades[iLoopPlayer]
                else:
                    previousTechs = frozenset()

                # Determine new techs
                newTechs = currentTechs.difference(previousTechs).intersection(researchTechs)
                if newTechs:
                    szNewTechs = self._buildTechString(newTechs)
                    msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_NEW_TECH_AVAIL",
                                          (GC.getPlayer(iLoopPlayer).getName(), szNewTechs))
                    self._addMessageNoIcon(iPlayer, msg)

                # Determine removed techs
                removedTechs = previousTechs.difference(currentTechs).intersection(researchTechs)
                if removedTechs:
                    szRemovedTechs = self._buildTechString(removedTechs)
                    msg = TRNSLTR.getText("TXT_KEY_MORECIV4LERTS_TECH_NOT_AVAIL",
                                          (GC.getPlayer(iLoopPlayer).getName(), szRemovedTechs))
                    self._addMessageNoIcon(iPlayer, msg)

            # Save current trades for next time
            self.PrevAvailTechTrades = techsByPlayer

        # Other trade types - optimized with single method
        self._checkSimpleTrade(iPlayer, tradeData, TRADE_MAPS,
                               'isShowMapTradeAlert', 'PrevAvailMapTrades',
                               "TXT_KEY_MORECIV4LERTS_MAP", TradeUtil.getMapTradePartners)

        self._checkSimpleTrade(iPlayer, tradeData, TRADE_OPEN_BORDERS,
                               'isShowOpenBordersTradeAlert', 'PrevAvailOpenBordersTrades',
                               "TXT_KEY_MORECIV4LERTS_OPEN_BORDERS", TradeUtil.getOpenBordersTradePartners)

        self._checkSimpleTrade(iPlayer, tradeData, TRADE_DEFENSIVE_PACT,
                               'isShowDefensivePactTradeAlert', 'PrevAvailDefensivePactTrades',
                               "TXT_KEY_MORECIV4LERTS_DEFENSIVE_PACT", TradeUtil.getDefensivePactTradePartners)

        self._checkSimpleTrade(iPlayer, tradeData, TRADE_PERMANENT_ALLIANCE,
                               'isShowPermanentAllianceTradeAlert', 'PrevAvailPermanentAllianceTrades',
                               "TXT_KEY_MORECIV4LERTS_PERMANENT_ALLIANCE", TradeUtil.getPermanentAllianceTradePartners)

        self._checkSimpleTrade(iPlayer, tradeData, TRADE_VASSAL,
                               'isShowVassalTradeAlert', 'PrevAvailVassalTrades',
                               "TXT_KEY_MORECIV4LERTS_VASSAL", TradeUtil.getVassalTradePartners)

        self._checkSimpleTrade(iPlayer, tradeData, TRADE_SURRENDER,
                               'isShowSurrenderTradeAlert', 'PrevAvailSurrenderTrades',
                               "TXT_KEY_MORECIV4LERTS_SURRENDER", TradeUtil.getCapitulationTradePartners)

        # Peace Treaty (special case with iData)
        if self.options.isShowPeaceTradeAlert():
            tradeData.ItemType = TRADE_PEACE_TREATY
            tradeData.iData = GC.getDefineINT("PEACE_TREATY_LENGTH")
            oldSet = self.PrevAvailPeaceTrades
            TXT_KEY = "TXT_KEY_MORECIV4LERTS_PEACE_TREATY"
            willTrade = self._getTrades(TradeUtil.getPeaceTradePartners(CyPlayer), iPlayer, tradeData)
            newSet = willTrade.difference(oldSet)
            if newSet:
                self._addMessageNoIcon(iPlayer, TRNSLTR.getText(TXT_KEY, (self._buildPlayerString(newSet),)))
            if willTrade != oldSet:
                self.PrevAvailPeaceTrades = frozenset(willTrade)

    def _checkSimpleTrade(self, iPlayer, tradeData, itemType, optionName, attrName, getTradersFunc):
        """Unified method for checking simple trade types to reduce code duplication"""
        if not getattr(self.options, optionName)():
            return

        CyPlayer = GC.getPlayer(iPlayer)
        tradeData.ItemType = itemType
        oldSet = getattr(self, attrName)
        TXT_KEY = "TXT_KEY_MORECIV4LERTS_" + attrName[9:-6].upper()  # Extract key from attr name

        willTrade = self._getTrades(getTradersFunc(CyPlayer), iPlayer, tradeData)
        newSet = willTrade.difference(oldSet)
        if newSet:
            self._addMessageNoIcon(iPlayer, TRNSLTR.getText(TXT_KEY, (self._buildPlayerString(newSet),)))
        if willTrade != oldSet:
            setattr(self, attrName, frozenset(willTrade))

    def _getTrades(self, traders, iPlayer, tradeData):
        """Generator-based trade checking to reduce memory usage"""
        # Use set comprehension for efficiency
        return frozenset(CyPlayerX.getID() for CyPlayerX in traders
                         if CyPlayerX.canTradeItem(iPlayer, tradeData, False)
                         and CyPlayerX.getTradeDenial(iPlayer, tradeData) == NO_DENIAL)

    def _buildTechString(self, techs):
        """Optimized string building for techs"""
        # Use list comprehension with direct access
        names = [GC.getTechInfo(eTech).getDescription() for eTech in techs]
        names.sort()
        return u", ".join(names)

    def _buildBonusString(self, bonuses):
        """Optimized string building for bonuses"""
        # Use list comprehension with direct access
        names = [GC.getBonusInfo(eBonus).getDescription() for eBonus in bonuses]
        names.sort()
        return u", ".join(names)

    def _buildPlayerString(self, players):
        """Optimized string building for players"""
        # Use list comprehension with direct access
        names = [GC.getPlayer(ePlayer).getName() for ePlayer in players]
        names.sort()
        return u", ".join(names)


def canSeeCityList(askedPlayer):
    """
    Returns True if the active player can see the list of <player>'s cities.
    Memory optimized version with cached values.
    """
    if GAME.isOption(GameOptionTypes.GAMEOPTION_CHALLENGE_ONE_CITY):
        return False

    iAskedTeam = askedPlayer.getTeam()
    iAskingTeam = GAME.getActiveTeam()

    if iAskingTeam == iAskedTeam:
        return True

    askedTeam = GC.getTeam(iAskedTeam)
    if askedTeam.isAVassal() and not askedTeam.isVassal(iAskingTeam):
        return False

    return TradeUtil.canTrade(GC.getActivePlayer(), askedPlayer)