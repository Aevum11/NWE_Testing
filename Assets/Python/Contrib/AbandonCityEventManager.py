# ------------------------------------------------------------------------
# Can't abandon last city without the "Require Complete Kill" gameoption.
# Memory-optimized version for 32-bit Python 2.4 environment
# ------------------------------------------------------------------------
from CvPythonExtensions import *
from operator import itemgetter
import CvScreensInterface

# globals - reduced to single reference
CD = None


# Entry point
def onHotKeyStart(argsList):
    import CvScreenEnums
    screen = CyGInterfaceScreen("MainInterface", CvScreenEnums.MAIN_INTERFACE)
    startCityDemolish(screen, screen.getXResolution(), screen.getYResolution())
    del screen  # Immediate cleanup


def startCityDemolish(screen, xRes, yRes):
    if not CyInterface().isCityScreenUp():
        return

    GC = CyGlobalContext()
    GAME = GC.getGame()
    CyCity = CyInterface().getHeadSelectedCity()
    iPlayer = CyCity.getOwner()

    if iPlayer != GAME.getActivePlayer():
        del GC, GAME, CyCity  # Clean up early
        return

    global CD
    CD = CityDemolish()

    # Initialize only essential data
    CD.iPlayer = iPlayer
    CD.CyPlayer = GC.getPlayer(iPlayer)
    CD.CyCity = CyCity

    # Check abandon city eligibility
    if GAME.isOption(GameOptionTypes.GAMEOPTION_NO_CITY_RAZING):
        CD.bAbandonCity = False
    elif not GAME.isOption(GameOptionTypes.GAMEOPTION_EXP_COMPLETE_KILLS) and CD.CyPlayer.getNumCities() < 2:
        CD.bAbandonCity = False
    else:
        CD.bAbandonCity = True

    # Store minimal required data
    CD.iconUnhappy = u'%c' % GAME.getSymbolID(FontSymbols.UNHAPPY_CHAR)
    CD.fFactorGS = GC.getGameSpeedInfo(GAME.getGameSpeedType()).getHammerCostPercent() / 100.0
    CD.iAbandonTrigger = GC.getNumBuildingInfos()

    # Create popup and clean up
    CD.createPopup(screen, xRes, yRes, GC)
    del GC, GAME  # Clean up references


class CityDemolish:
    # Use __slots__ to reduce memory overhead
    __slots__ = ('iPlayer', 'CyPlayer', 'CyCity', 'bAbandonCity', 'iconUnhappy',
                 'fFactorGS', 'iAbandonTrigger', 'iSelected', 'bListHidden',
                 'updateTooltip', 'iconGold', 'xListTooltip', 'xywBtn0',
                 'fGoldMod', 'iSum', 'iAbandonGold', 'szAbandon', 'aList')

    def __init__(self):
        GC = CyGlobalContext()
        self.iSelected = None
        self.bListHidden = False
        self.updateTooltip = CvScreensInterface.mainInterface.updateTooltip
        self.iconGold = u'%c' % GC.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()
        del GC  # Clean up immediately

    def createPopup(self, screen, xRes, yRes, GC):
        # Font setup based on resolution
        if xRes > 1700:
            aFontList = ("<font=4b>", "<font=3b>", "<font=2b>")
            uFont = "<font=3b>"
            iconSize = 28
        elif xRes > 1400:
            aFontList = ("<font=4>", "<font=3>", "<font=2>")
            uFont = "<font=2b>"
            iconSize = 24
        else:
            aFontList = ("<font=3b>", "<font=2b>", "<font=1b>")
            uFont = "<font=1b>"
            iconSize = 20

        TRNSLTR = CyTranslator()
        PRE = "CityDemolish|"

        # Build header text using string list then join (more efficient)
        szTextParts = []
        szTextParts.append(aFontList[0])
        szTextParts.append(TRNSLTR.getText("TXT_KEY_ABANDON_CITY_HEADER1", ()))
        szTextParts.append('</font>\n\n')
        szTextParts.append(aFontList[1])
        szTextParts.append(TRNSLTR.getText("TXT_KEY_ABANDON_CITY_HEADER2", ()))
        szTextParts.append('</font>\n\n')
        szTextParts.append(aFontList[2])
        szTextParts.append(TRNSLTR.getText("TXT_KEY_ABANDON_CITY_HEADER3", ()))
        szText = ''.join(szTextParts)
        del szTextParts  # Clean up list

        # Widget constants (store once)
        iWidGen = WidgetTypes.WIDGET_GENERAL
        iPanelMain = PanelStyles.PANEL_STYLE_MAIN
        iBtnStd = ButtonStyles.BUTTON_STYLE_STANDARD

        # Create UI elements
        dx = xRes / 3
        dy = 300
        xStart = xRes - dx * 2
        self.xListTooltip = xStart - 30
        y = (yRes - dy) / 2

        screen.addPanel(PRE + "Bkgr", "", "", False, False, -8, -8, xRes + 16, yRes + 16,
                        PanelStyles.PANEL_STYLE_MAIN_BLACK50)
        screen.setImageButton(PRE + "Exit0", "", 0, 0, xRes, yRes, iWidGen, 0, 0)
        screen.addPanel(PRE + "Main", "", "", False, False, xStart, y, dx, dy, iPanelMain)

        x = xStart + 8
        y += 8
        screen.addMultilineText(PRE + "Text", szText, x, y, dx - 12, 194, iWidGen, 0, 0, 1 << 0)

        y += 202
        dx -= 16
        self.xywBtn0 = (x, y, dx)  # Use tuple instead of list
        screen.setButtonGFC(PRE + "Btn0", "****", "", x, y, dx, 32, iWidGen, 0, 0, iBtnStd)

        y += 40
        szOK = TRNSLTR.getText("TXT_KEY_MAIN_MENU_OK", ())
        szCancel = TRNSLTR.getText("TXT_KEY_POPUP_CANCEL", ())
        screen.setButtonGFC(PRE + "Btn1", szOK, "", x, y, dx, 32, iWidGen, 0, 0, iBtnStd)
        screen.hide(PRE + "Btn1")
        screen.setButtonGFC(PRE + "Exit1", szCancel, "", x, y, dx, 32, iWidGen, 0, 0, iBtnStd)

        # Cleanup text variables
        del szText, szOK, szCancel

        # Create list panels
        screen.addPanel(PRE + "ListBkgr", "", "", False, False, 40, 24, xStart - 60, yRes - 48, iPanelMain)
        screen.addScrollPanel(PRE + "List", "", 40, 32, xStart - 60, yRes - 100, iPanelMain)
        screen.setStyle(PRE + "List", "ScrollPanel_Alt_Style")

        # Calculate gold modifier
        fGoldMod = 0.09 * (GC.getDefineINT("BUILDING_PRODUCTION_PERCENT") / 100.0) * self.fFactorGS
        self.fGoldMod = fGoldMod

        # Build list efficiently
        self._buildBuildingList(screen, GC, PRE, uFont, iconSize, fGoldMod, iWidGen)

        # Clean up references
        del TRNSLTR, aFontList, uFont

    def _buildBuildingList(self, screen, GC, PRE, uFont, iconSize, fGoldMod, iWidGen):
        """Separate method to build building list to allow better memory management"""
        CyCity = self.CyCity
        CyTeam = GC.getTeam(self.CyPlayer.getTeam())

        # Use generator to process buildings without storing all at once
        aList = []
        iSum = 0

        for iType in xrange(GC.getNumBuildingInfos()):
            if not CyCity.hasBuilding(iType) or CyCity.isFreeBuilding(iType):
                continue

            if isWorldWonder(iType) or isTeamWonder(iType):
                continue

            CvBuildingInfo = GC.getBuildingInfo(iType)

            # Check if building is protected
            if (CvBuildingInfo.isNukeImmune() or CvBuildingInfo.isAutoBuild() or
                    CvBuildingInfo.isCapital() or CvBuildingInfo.getGlobalReligionCommerce() > 0):
                continue

            iGold = CvBuildingInfo.getProductionCost()
            if iGold < 0:
                iGold = 0
            elif iGold != 0:
                iGold = int(iGold * fGoldMod)

            # Store as tuple (immutable, less memory)
            aList.append((CvBuildingInfo.getDescription(), CvBuildingInfo.getButton(), iType, iGold))
            iSum += iGold

        self.iSum = iSum

        # Display list
        name = PRE + "List"
        iFontGame = FontTypes.GAME_FONT
        x = y = 8
        dy = iconSize + 2

        screen.setTextAt(name + "Top0", name, "****", 1 << 0, x, y, 0, iFontGame, iWidGen, 0, 0)

        # Handle abandon city option
        if self.bAbandonCity:
            y += dy
            iFactorGS = self.fFactorGS
            iEra = self.CyPlayer.getCurrentEra()
            self.iAbandonGold = int(iSum - CyCity.getPopulation() * 13.37 * iFactorGS * (iEra + 1) * (iEra + 1))

            # Build abandon text efficiently
            TRNSLTR = CyTranslator()
            szParts = [uFont, TRNSLTR.getText("TXT_KEY_ABANDON_CITY", ())]

            if self.iAbandonGold:
                if self.iAbandonGold < 0:
                    szParts.append(" (<color=197,0,0>")
                else:
                    szParts.append(" (")
                szParts.append(str(self.iAbandonGold))
                if self.iAbandonGold < 0:
                    szParts.append("</color>")
                szParts.append(" ")
                szParts.append(self.iconGold)
                szParts.append(")")

            self.szAbandon = ''.join(szParts)
            del szParts, TRNSLTR  # Clean up

            screen.setTextAt(name + "Top1", name, self.szAbandon, 1 << 0, x, y, 0, iFontGame, iWidGen, 0, 0)

        # Display buildings if any
        if aList:
            aList.sort(key=itemgetter(0))
            iconUnhappy = self.iconUnhappy
            iconGold = self.iconGold
            aNameList = []

            for i, entry in enumerate(aList):
                szText, szBtn, iType, iGold = entry
                szBtn = '<img=%s size=%d></img>' % (szBtn, iconSize)

                # Build text efficiently with list
                szParts = [szText]

                if iGold:
                    szParts.append(" (")
                    if iGold < 0:
                        szParts.append("<color=197,0,0>")
                    szParts.append(str(iGold))
                    if iGold < 0:
                        szParts.append("</color>")
                    szParts.append(" ")
                    szParts.append(iconGold)

                if GC.getBuildingInfo(iType).getReligionType() >= 0:
                    if iGold:
                        szParts.append(", 1")
                    else:
                        szParts.append(" (1")
                    szParts.append(iconUnhappy)
                    szParts.append(")")
                elif iGold:
                    szParts.append(")")

                szFullText = ''.join(szParts)
                aNameList.append(szFullText)

                y += dy
                screen.setTextAt(name + "Btn" + str(iType), name, szBtn, 1 << 0, x, y, 0, iFontGame, iWidGen, i, 0)
                screen.setTextAt(name + str(iType), name, uFont + szFullText, 1 << 0, x + iconSize + 2, y + 2, 0,
                                 iFontGame, iWidGen, i, 0)

            # Store as tuple (immutable)
            self.aList = tuple(aNameList)
            del aNameList  # Clean up mutable list
        else:
            self.aList = ()  # Empty tuple

        del aList  # Clean up list

    def doIt(self, iSelected):
        GC = CyGlobalContext()
        iPlayer = self.iPlayer
        CyPlayer = self.CyPlayer
        CyCity = self.CyCity
        iCity = CyCity.getID()

        if iSelected == -1:
            # Abandon city logic
            self._abandonCity(GC, iPlayer, CyPlayer, CyCity, iCity)
        else:
            # Sell building
            CvBuildingInfo = GC.getBuildingInfo(iSelected)
            iGold = int(CvBuildingInfo.getProductionCost() * self.fGoldMod)
            CyMessageControl().sendModNetMessage(903, iPlayer, iCity, iSelected, iGold)
            CyAudioGame().Play2DSound("AS2D_DISCOVERBONUS")
            del CvBuildingInfo

        del GC  # Clean up

    def _abandonCity(self, GC, iPlayer, CyPlayer, CyCity, iCity):
        """Separate abandon city logic for better memory management"""
        X = CyCity.getX()
        Y = CyCity.getY()

        iCulturePercent = CyCity.calculateCulturePercent(iPlayer)
        iPopulation = CyCity.getPopulation()
        iOwnCulturePop = iPopulation * iCulturePercent / 100
        iForeignPop = iPopulation - iOwnCulturePop

        # Judge
        BUILDING_COURTHOUSE = GC.getInfoTypeForString("BUILDING_COURTHOUSE")
        if CyCity.isActiveBuilding(BUILDING_COURTHOUSE):
            UNIT_JUDGE = GC.getInfoTypeForString("UNIT_JUDGE")
            CyMessageControl().sendModNetMessage(905, iPlayer, iCity, -1, UNIT_JUDGE)
            del UNIT_JUDGE
        del BUILDING_COURTHOUSE

        # Tribal Guardian
        iExp = -1
        UNIT_TRIBAL = GC.getInfoTypeForString("UNIT_TRIBAL_GUARDIAN")
        if UNIT_TRIBAL > -1:
            CyPlot = CyCity.plot()
            iNumUnits = CyPlot.getNumUnits()
            for i in xrange(iNumUnits - 1, -1, -1):
                CyUnit = CyPlot.getUnit(i)
                if CyUnit.getUnitType() == UNIT_TRIBAL:
                    iExp = CyUnit.getExperience()
                    CyMessageControl().sendModNetMessage(902, iPlayer, CyUnit.getID(), 0, 0)
                    break
            del CyPlot, CyUnit
        del UNIT_TRIBAL

        CyTeam = GC.getTeam(CyPlayer.getTeam())

        # Settler creation
        if iOwnCulturePop > 0 or iForeignPop > 2:
            self._createSettler(GC, CyCity, CyTeam, iPlayer, iCity, iExp, iOwnCulturePop, iForeignPop)

        # Captives
        if iForeignPop > 0:
            self._createCaptives(GC, CyCity, iPlayer, iCity, iPopulation, iForeignPop)

        # Immigrants
        if iOwnCulturePop > 0:
            UNIT_IMMIGRANT = GC.getInfoTypeForString("UNIT_IMMIGRANT")
            for i in xrange(iOwnCulturePop):
                CyMessageControl().sendModNetMessage(905, iPlayer, iCity, -1, UNIT_IMMIGRANT)
            del UNIT_IMMIGRANT

        # Merchants
        self._createMerchants(GC, CyCity, CyTeam, iPlayer, iCity)

        # Holy city penalties
        if CyCity.isHolyCity():
            self._handleHolyCityPenalties(GC, CyCity, iPlayer)

        # Abandon the city
        CyMessageControl().sendModNetMessage(904, iPlayer, iCity, 0, self.iAbandonGold)
        CyAudioGame().Play2DSound("AS2D_DISCOVERBONUS")

        del CyTeam  # Clean up

    def _createSettler(self, GC, CyCity, CyTeam, iPlayer, iCity, iExp, iOwnCulturePop, iForeignPop):
        """Create settler unit efficiently"""
        # Use tuple instead of list for immutable data
        aSettlerTypes = (
            GC.getInfoTypeForString("UNIT_AIRSETTLER"),
            GC.getInfoTypeForString("UNIT_PIONEER"),
            GC.getInfoTypeForString("UNIT_COLONIST"),
            GC.getInfoTypeForString("UNIT_SETTLER"),
            GC.getInfoTypeForString("UNIT_TRIBE"),
            GC.getInfoTypeForString("UNIT_BAND")
        )

        for iUnit in aSettlerTypes:
            if iUnit < 0:
                continue

            CvUnitInfo = GC.getUnitInfo(iUnit)

            # Check prerequisites
            if not self._checkUnitPrereqs(CvUnitInfo, CyTeam, CyCity):
                continue

            # Found valid settler
            CyMessageControl().sendModNetMessage(906, iPlayer, iCity, iExp, iUnit)
            break

        del aSettlerTypes, CvUnitInfo  # Clean up

    def _checkUnitPrereqs(self, CvUnitInfo, CyTeam, CyCity):
        """Check unit prerequisites - returns False if any fail"""
        # Tech prereq
        iTech = CvUnitInfo.getPrereqAndTech()
        if iTech > -1 and not CyTeam.isHasTech(iTech):
            return False

        for iTech in CvUnitInfo.getPrereqAndTechs():
            if not CyTeam.isHasTech(iTech):
                return False

        # Building prereq
        for i in xrange(CvUnitInfo.getNumPrereqAndBuildings()):
            if not CyCity.isActiveBuilding(CvUnitInfo.getPrereqAndBuilding(i)):
                return False

        # Bonus prereq
        iBonus = CvUnitInfo.getPrereqAndBonus()
        if iBonus > -1 and not CyCity.getNumBonuses(iBonus):
            return False

        for iBonus in CvUnitInfo.getPrereqOrBonuses():
            if not CyCity.getNumBonuses(iBonus):
                return False

        return True

    def _createCaptives(self, GC, CyCity, iPlayer, iCity, iPopulation, iForeignPop):
        """Create captive units"""
        if iPopulation > 1 or GC.getGame().getSorenRandNum(2, "50%"):
            iCaptives = (iForeignPop + 1) / 2
        else:
            iCaptives = iForeignPop / 2

        if iCaptives > 0:
            UNIT_CAPTIVE = GC.getInfoTypeForString("UNIT_CAPTIVE_CIVILIAN")
            for i in xrange(iCaptives):
                CyMessageControl().sendModNetMessage(905, iPlayer, iCity, -1, UNIT_CAPTIVE)

            # Attitude penalty
            iCulturalOwner = CyCity.findHighestCulture()
            if iCulturalOwner not in (-1, iPlayer):
                CyMessageControl().sendModNetMessage(901, iPlayer, iCulturalOwner, 1, 1)

            del UNIT_CAPTIVE

    def _createMerchants(self, GC, CyCity, CyTeam, iPlayer, iCity):
        """Create merchant units efficiently"""
        fModifierGS = self.fFactorGS

        # Regular merchants - use tuple
        aMerchantTypes = (
            GC.getInfoTypeForString("UNIT_FREIGHT"),
            GC.getInfoTypeForString("UNIT_SUPPLY_TRAIN"),
            GC.getInfoTypeForString("UNIT_TRADE_CARAVAN"),
            GC.getInfoTypeForString("UNIT_EARLY_MERCHANT_C2C")
        )

        for iUnit in aMerchantTypes:
            if iUnit < 0:
                continue

            CvUnitInfo = GC.getUnitInfo(iUnit)
            if not self._checkUnitPrereqs(CvUnitInfo, CyTeam, CyCity):
                continue

            fCost = CvUnitInfo.getProductionCost() * fModifierGS
            if fCost < 1:
                break

            iNum = int(self.iSum / fCost)
            for i in xrange(iNum):
                CyMessageControl().sendModNetMessage(905, iPlayer, iCity, -1, iUnit)
            break

        del aMerchantTypes, CvUnitInfo

        # Food merchants - use tuple
        aFoodTypes = (
            GC.getInfoTypeForString("UNIT_FOOD_FREIGHT"),
            GC.getInfoTypeForString("UNIT_FOOD_SUPPLY_TRAIN"),
            GC.getInfoTypeForString("UNIT_FOOD_CARAVAN"),
            GC.getInfoTypeForString("UNIT_EARLY_FOOD_MERCHANT_C2C")
        )

        iFood = CyCity.getFood()
        for iUnit in aFoodTypes:
            if iUnit < 0:
                continue

            CvUnitInfo = GC.getUnitInfo(iUnit)
            if not self._checkUnitPrereqs(CvUnitInfo, CyTeam, CyCity):
                continue

            fCost = CvUnitInfo.getProductionCost() * fModifierGS
            iNum = int(iFood / fCost)
            for i in xrange(iNum):
                CyMessageControl().sendModNetMessage(905, iPlayer, iCity, -1, iUnit)
            break

        del aFoodTypes, CvUnitInfo

    def _handleHolyCityPenalties(self, GC, CyCity, iPlayer):
        """Handle holy city destruction penalties"""
        GAME = GC.getGame()
        for iReligion in xrange(GC.getNumReligionInfos()):
            if not CyCity.isHolyCityByType(iReligion):
                continue

            for iOtherPlayer in xrange(GC.getMAX_PC_PLAYERS()):
                if iOtherPlayer == iPlayer:
                    continue

                CyOtherPlayer = GC.getPlayer(iOtherPlayer)
                if CyOtherPlayer.isAlive() and CyOtherPlayer.getStateReligion() == iReligion:
                    CyMessageControl().sendModNetMessage(901, iPlayer, iOtherPlayer, 0, 1)
                del CyOtherPlayer
        del GAME

    def handleInput(self, screen, szSplit, iNotifyCode, szFlag, ID, iData1):
        print
        "ACEM - handleInput"

        if iNotifyCode == NotifyCode.NOTIFY_CURSOR_MOVE_ON:
            if szSplit[0] in ("List", "ListBtn"):
                szText = CyGameTextMgr().getBuildingHelp(ID, True, self.CyCity, False, False, False)
                self.updateTooltip(screen, szText, self.xListTooltip)

        elif iNotifyCode == NotifyCode.NOTIFY_CLICKED:
            if szSplit[0] == "Exit":
                exitCityDemolish(screen)
                return

            if szSplit[0] == "Btn":
                if not ID:
                    if szFlag == "MOUSE_RBUTTONUP" and iData1:
                        x, y, w = self.xywBtn0
                        screen.setButtonGFC("CityDemolish|Btn0", "****", "", x, y, w, 30,
                                            WidgetTypes.WIDGET_GENERAL, 0, 0, ButtonStyles.BUTTON_STYLE_STANDARD)
                        self.iSelected = None
                    elif self.bListHidden:
                        screen.show("CityDemolish|List")
                        screen.show("CityDemolish|ListBkgr")
                        self.bListHidden = False
                    else:
                        screen.hide("CityDemolish|List")
                        screen.hide("CityDemolish|ListBkgr")
                        self.bListHidden = True
                elif ID == 1 and szFlag == "MOUSE_LBUTTONUP":
                    iSelected = self.iSelected
                    if iSelected is not None:
                        self.doIt(iSelected)
                    exitCityDemolish(screen)

            elif szSplit[0] == "ListTop":
                x, y, w = self.xywBtn0
                if ID:
                    screen.setButtonGFC("CityDemolish|Btn0", self.szAbandon, "", x, y, w, 30,
                                        WidgetTypes.WIDGET_GENERAL, 1, 0, ButtonStyles.BUTTON_STYLE_STANDARD)
                    self.iSelected = -1
                else:
                    screen.setButtonGFC("CityDemolish|Btn0", "****", "", x, y, w, 30,
                                        WidgetTypes.WIDGET_GENERAL, 0, 0, ButtonStyles.BUTTON_STYLE_STANDARD)
                    self.iSelected = None

            elif szSplit[0] in ("List", "ListBtn"):
                if szFlag == "MOUSE_RBUTTONUP":
                    CvScreensInterface.pediaJumpToBuilding([ID])
                else:
                    x, y, w = self.xywBtn0
                    screen.setButtonGFC("CityDemolish|Btn0", self.aList[iData1], "", x, y, w, 30,
                                        WidgetTypes.WIDGET_GENERAL, 1, 0, ButtonStyles.BUTTON_STYLE_STANDARD)
                    self.iSelected = ID

            # Update button visibility
            if self.iSelected is None:
                screen.hide("CityDemolish|Btn1")
                screen.show("CityDemolish|Exit1")
            else:
                screen.hide("CityDemolish|Exit1")
                screen.show("CityDemolish|Btn1")


def exitCityDemolish(screen):
    """Clean up and exit the city demolish screen"""
    PRE = "CityDemolish|"
    widgets = ("Bkgr", "Exit0", "Exit1", "Main", "Text", "Btn0", "Btn1", "List", "ListBkgr")

    for widget in widgets:
        screen.deleteWidget(PRE + widget)

    global CD
    CD = None  # Release the object for garbage collection
    del widgets  # Clean up tuple reference