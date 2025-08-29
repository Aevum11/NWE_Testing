## TechWindowWide - Memory Optimized Version
##
## Originally by SirRethcir: Techanzeige hinzugefügt
## Enhanced by Roamty, Caesium, Guarav
## Memory Optimized for 32-bit Python 2.4
##
## Copyright (c) 2008 The BUG Mod.

from CvPythonExtensions import *
import BugCore

# Cache global objects to reduce lookups
GC = CyGlobalContext()
TRNSLTR = CyTranslator()
TechWindowOpt = BugCore.game.TechWindow

# Pre-cache frequently used constants
WIDGET_GENERAL = WidgetTypes.WIDGET_GENERAL
WIDGET_CLOSE_SCREEN = WidgetTypes.WIDGET_CLOSE_SCREEN
WIDGET_PEDIA_JUMP_TO_TECH = WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH
WIDGET_PEDIA_JUMP_TO_UNIT = WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT
WIDGET_PEDIA_JUMP_TO_BUILDING = WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING
WIDGET_PEDIA_JUMP_TO_PROJECT = WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT
WIDGET_PEDIA_JUMP_TO_PROMOTION = WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION
WIDGET_PEDIA_JUMP_TO_IMPROVEMENT = WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT
WIDGET_PEDIA_JUMP_TO_BONUS = WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS
WIDGET_PEDIA_JUMP_TO_CIVIC = WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC
WIDGET_PEDIA_JUMP_TO_DERIVED_TECH = WidgetTypes.WIDGET_PEDIA_JUMP_TO_DERIVED_TECH
WIDGET_HELP_IMPROVEMENT = WidgetTypes.WIDGET_HELP_IMPROVEMENT

POPUP_IMMEDIATE = PopupStates.POPUPSTATE_IMMEDIATE
PANEL_STYLE_MAIN = PanelStyles.PANEL_STYLE_MAIN
PANEL_STYLE_MAIN_TAN15 = PanelStyles.PANEL_STYLE_MAIN_TAN15
PANEL_STYLE_IN = PanelStyles.PANEL_STYLE_IN
BUTTON_STYLE_STANDARD = ButtonStyles.BUTTON_STYLE_STANDARD
BUTTON_SIZE_CUSTOM = GenericButtonSizes.BUTTON_SIZE_CUSTOM
FONT_GAME = FontTypes.GAME_FONT
FONT_TITLE = FontTypes.TITLE_FONT
NOTIFY_CLICKED = NotifyCode.NOTIFY_CLICKED
KB_RETURN = int(InputTypes.KB_RETURN)


class CvTechSplashScreen:
    "Splash screen for techs - Memory Optimized"

    # Use __slots__ to reduce memory overhead per instance
    __slots__ = ('nScreenId', 'iTech', 'nWidgetCount', 'nTechs', '_widget_cache',
                 'WIDGET_ID', 'SCREEN_NAME', 'EXIT_ID', 'EXIT_TEXT',
                 'X_SCREEN', 'Y_SCREEN', 'W_SCREEN', 'H_SCREEN',
                 'Z_BACKGROUND', 'Z_CONTROLS', 'DZ', 'Z_HELP_AREA', 'W_HELP_AREA',
                 'iMarginSpace', 'X_MAIN_PANEL', 'Y_MAIN_PANEL', 'W_MAIN_PANEL', 'H_MAIN_PANEL',
                 'X_UPPER_PANEL', 'Y_UPPER_PANEL', 'W_UPPER_PANEL', 'H_UPPER_PANEL',
                 'X_TITLE', 'Y_TITLE', 'W_ICON', 'H_ICON',
                 'X_ICON_PANEL', 'Y_ICON_PANEL', 'W_ICON_PANEL', 'H_ICON_PANEL',
                 'X_ICON', 'Y_ICON', 'X_QUOTE', 'Y_QUOTE', 'W_QUOTE', 'H_QUOTE',
                 'X_LOWER_PANEL', 'Y_LOWER_PANEL', 'W_LOWER_PANEL', 'H_LOWER_PANEL',
                 'H_ALLOWS_PANEL', 'H_ALLOWS_SPACE',
                 'X_SPECIAL_PANEL', 'Y_SPECIAL_PANEL', 'W_SPECIAL_PANEL', 'H_SPECIAL_PANEL',
                 'X_ALLOWS_PANELSIR', 'Y_ALLOWS_PANELSIR', 'W_ALLOWS_PANELSIR', 'H_ALLOWS_PANELSIR',
                 'X_ALLOWS_PANEL', 'Y_ALLOWS_PANEL', 'W_ALLOWS_PANEL',
                 'Y_ALLOWS_PANEL2', 'Y_ALLOWS_PANEL3', 'Y_ALLOWS_PANEL4',
                 'X_EXIT', 'Y_EXIT', 'W_EXIT', 'H_EXIT')

    def __init__(self, iScreenID):
        self.nScreenId = iScreenID
        self.iTech = -1
        self.nWidgetCount = 0
        self._widget_cache = []  # Pre-allocate widget names

        # widget names
        self.WIDGET_ID = "TechSplashScreenWidget"
        self.SCREEN_NAME = "TechSplashScreen"
        self.EXIT_ID = "TechSplashExit"

        # Initialize all layout constants at once
        self.X_SCREEN = 17
        self.Y_SCREEN = 27
        self.W_SCREEN = 1024
        self.H_SCREEN = 768
        self.Z_BACKGROUND = -1.1
        self.Z_CONTROLS = self.Z_BACKGROUND - 0.2
        self.DZ = -0.2
        self.Z_HELP_AREA = self.Z_CONTROLS - 2
        self.W_HELP_AREA = 200

        # Panels
        self.iMarginSpace = 15
        self.X_MAIN_PANEL = 17
        self.Y_MAIN_PANEL = 25
        self.W_MAIN_PANEL = 996
        self.H_MAIN_PANEL = 725

        # Upper Panel
        self.X_UPPER_PANEL = self.X_MAIN_PANEL + self.iMarginSpace
        self.Y_UPPER_PANEL = self.Y_MAIN_PANEL + self.iMarginSpace
        self.W_UPPER_PANEL = self.W_MAIN_PANEL - (self.iMarginSpace * 2)
        self.H_UPPER_PANEL = 200

        self.X_TITLE = self.X_MAIN_PANEL + (self.W_MAIN_PANEL / 2)
        self.Y_TITLE = self.Y_UPPER_PANEL - 20

        self.W_ICON = 96
        self.H_ICON = 96

        self.X_ICON_PANEL = self.X_UPPER_PANEL + self.iMarginSpace + 2
        self.Y_ICON_PANEL = self.Y_UPPER_PANEL + self.iMarginSpace + 30
        self.W_ICON_PANEL = 160
        self.H_ICON_PANEL = 105

        self.X_ICON = self.X_ICON_PANEL + self.W_ICON_PANEL / 2 - self.W_ICON / 2
        self.Y_ICON = self.Y_ICON_PANEL + self.H_ICON_PANEL / 2 - self.H_ICON / 2

        self.X_QUOTE = 550
        self.Y_QUOTE = self.Y_ICON - 25
        self.W_QUOTE = 455
        self.H_QUOTE = 135

        # Lower Panel
        self.X_LOWER_PANEL = self.X_MAIN_PANEL + self.iMarginSpace
        self.Y_LOWER_PANEL = self.Y_UPPER_PANEL + self.H_UPPER_PANEL
        self.W_LOWER_PANEL = self.W_MAIN_PANEL - (self.iMarginSpace * 2)
        self.H_LOWER_PANEL = 360

        self.H_ALLOWS_PANEL = 80
        self.H_ALLOWS_SPACE = 28

        self.X_SPECIAL_PANEL = self.X_LOWER_PANEL + self.iMarginSpace + 10
        self.Y_SPECIAL_PANEL = self.Y_LOWER_PANEL + self.iMarginSpace + 20
        self.W_SPECIAL_PANEL = self.W_LOWER_PANEL - 650 - self.iMarginSpace
        self.H_SPECIAL_PANEL = 290 + self.H_ALLOWS_PANEL + self.H_ALLOWS_SPACE

        self.X_ALLOWS_PANELSIR = self.X_LOWER_PANEL + self.iMarginSpace
        self.Y_ALLOWS_PANELSIR = self.Y_SPECIAL_PANEL + self.H_SPECIAL_PANEL + self.H_ALLOWS_SPACE
        self.W_ALLOWS_PANELSIR = self.W_LOWER_PANEL / 2 - self.iMarginSpace
        self.H_ALLOWS_PANELSIR = 80

        self.X_ALLOWS_PANEL = self.X_LOWER_PANEL + self.iMarginSpace + self.W_SPECIAL_PANEL
        self.Y_ALLOWS_PANEL = self.Y_SPECIAL_PANEL
        self.W_ALLOWS_PANEL = self.W_LOWER_PANEL - 330 - self.iMarginSpace
        self.Y_ALLOWS_PANEL2 = self.Y_SPECIAL_PANEL + self.H_ALLOWS_PANEL + self.H_ALLOWS_SPACE
        self.Y_ALLOWS_PANEL3 = self.Y_SPECIAL_PANEL + 2 * (self.H_ALLOWS_PANEL + self.H_ALLOWS_SPACE)
        self.Y_ALLOWS_PANEL4 = self.Y_SPECIAL_PANEL + 3 * (self.H_ALLOWS_PANEL + self.H_ALLOWS_SPACE)

        # Contents
        self.X_EXIT = self.X_MAIN_PANEL + (self.W_MAIN_PANEL / 2) - 70
        self.Y_EXIT = self.Y_MAIN_PANEL + self.H_MAIN_PANEL - 26
        self.W_EXIT = 120
        self.H_EXIT = 30

    def interfaceScreen(self, iTech):
        self.EXIT_TEXT = TRNSLTR.getText("TXT_KEY_SCREEN_CONTINUE", ())
        self.nTechs = GC.getNumTechInfos()
        self.iTech = iTech
        self.nWidgetCount = 0

        # Pre-allocate widget cache for this tech
        if not self._widget_cache:
            max_widgets = 50  # Estimate max widgets needed
            self._widget_cache = [None] * max_widgets
            for i in xrange(max_widgets):
                self._widget_cache[i] = "%s%d" % (self.WIDGET_ID, i * self.nTechs + self.iTech)

        # Get screen and tech info once
        screen = self.getScreen()
        techInfo = GC.getTechInfo(self.iTech)

        # Setup screen
        screen.setSound(techInfo.getSound())
        screen.showScreen(POPUP_IMMEDIATE, False)
        screen.enableWorldSounds(False)

        # Background
        screen.addDDSGFC("TechSplashBackground",
                         CyArtFileMgr().getInterfaceArtInfo("TEMP_BG2").getPath(),
                         0, 0, self.W_SCREEN, self.H_SCREEN, WIDGET_GENERAL, -1, -1)
        screen.showWindowBackground(True)
        screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)

        # Create panels efficiently
        self._createPanels(screen)

        # Add content
        self._addContent(screen, techInfo)

    def _createPanels(self, screen):
        """Create all panels efficiently"""
        # Icon Panel with glow
        screen.addPanel("IconPanelGlow", "", "", True, True,
                        self.X_ICON_PANEL, self.Y_ICON_PANEL,
                        self.W_ICON_PANEL, self.H_ICON_PANEL, PANEL_STYLE_MAIN_TAN15)
        screen.setStyle("IconPanelGlow", "Panel_TechDiscoverGlow_Style")

        # Text Panel
        screen.addPanel("TechSplashTextPanel", "", "", True, True,
                        self.X_LOWER_PANEL + self.iMarginSpace, self.Y_LOWER_PANEL,
                        self.W_LOWER_PANEL - (self.iMarginSpace * 2), self.H_LOWER_PANEL,
                        PANEL_STYLE_MAIN)
        screen.setStyle("TechSplashTextPanel", "Panel_TanT_Style")

        # Exit Button
        screen.setButtonGFC("Exit", self.EXIT_TEXT, "",
                            self.X_EXIT, self.Y_EXIT, self.W_EXIT, self.H_EXIT,
                            WIDGET_CLOSE_SCREEN, -1, -1, BUTTON_STYLE_STANDARD)

        # Special Panel
        screen.addPanel("TechSplashSpecialPanel", "", "", True, True,
                        self.X_SPECIAL_PANEL + self.iMarginSpace, self.Y_SPECIAL_PANEL,
                        self.W_SPECIAL_PANEL - (self.iMarginSpace * 2),
                        self.H_SPECIAL_PANEL + 5, PANEL_STYLE_IN)
        screen.setStyle("TechSplashSpecialPanel", "Panel_Black25_Style")

        # Allows Panels - create all at once
        panelName = self.getNextWidgetName()
        screen.addPanel(panelName, "", "", False, True,
                        self.X_ALLOWS_PANEL + self.iMarginSpace, self.Y_ALLOWS_PANEL,
                        self.W_ALLOWS_PANEL - (self.iMarginSpace * 2),
                        self.H_ALLOWS_PANEL, PANEL_STYLE_IN)
        screen.setStyle(panelName, "Panel_Black25_Style")

        for panel_id, y_pos in (("SIR2", self.Y_ALLOWS_PANEL2),
                                ("SIR3", self.Y_ALLOWS_PANEL3),
                                ("SIR4", self.Y_ALLOWS_PANEL4)):
            screen.addPanel(panel_id, "", "", False, True,
                            self.X_ALLOWS_PANEL + self.iMarginSpace, y_pos,
                            self.W_ALLOWS_PANEL - (self.iMarginSpace * 2),
                            self.H_ALLOWS_PANEL, PANEL_STYLE_IN)
            screen.setStyle(panel_id, "Panel_Black25_Style")

    def _addContent(self, screen, techInfo):
        """Add all content to panels"""
        # Title
        szTech = techInfo.getDescription()
        screen.setLabel(self.getNextWidgetName(), "Background",
                        "<font=4>" + szTech.upper(), 1 << 2,
                        self.X_TITLE, self.Y_TITLE, self.Z_CONTROLS,
                        FONT_GAME, WIDGET_GENERAL, -1, -1)

        # Tech Icon
        screen.addDDSGFC(self.getNextWidgetName(), techInfo.getButton(),
                         self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON,
                         WIDGET_PEDIA_JUMP_TO_TECH, self.iTech, 2)

        # Tech Quote
        szTechQuote = techInfo.getQuote()
        iTextOffset = 0
        if TechWindowOpt.isShowCivilopediaText():
            szTechQuote = "%s\n\n%s" % (szTechQuote, techInfo.getCivilopedia())
        else:
            iTextOffset = 20

        screen.addMultilineText("Text", szTechQuote,
                                self.X_QUOTE, self.Y_QUOTE + iTextOffset,
                                self.W_QUOTE, self.H_QUOTE - iTextOffset,
                                WIDGET_GENERAL, -1, -1, 1 << 0)

        # Special abilities
        szSpecialTitle = "<font=3b>" + TRNSLTR.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ())
        screen.setText("SpecialTitle", "", szSpecialTitle, 1 << 0,
                       self.X_SPECIAL_PANEL + self.iMarginSpace,
                       self.Y_SPECIAL_PANEL - 20, 0, FONT_TITLE,
                       WIDGET_GENERAL, -1, -1)

        szSpecialText = CyGameTextMgr().getTechHelp(self.iTech, True, False, False, True, -1)[1:]
        screen.addMultilineText(self.getNextWidgetName(), szSpecialText,
                                self.X_SPECIAL_PANEL + 20, self.Y_SPECIAL_PANEL + 20,
                                self.W_SPECIAL_PANEL - 50, self.H_SPECIAL_PANEL - 30,
                                WIDGET_GENERAL, -1, -1, 1 << 0)

        # Add all tech-enabled items
        self._addTechItems(screen)

    def _addTechItems(self, screen):
        """Add all items enabled by this tech"""
        # Cache panel name once
        panelName = self.nWidgetCount - 1  # Use cached widget name index

        # Pre-cache tech lists for efficiency
        num_techs = GC.getNumTechInfos()

        # Leads To Techs - Title
        szLeadsToTitle = "<font=3b>%s:" % TRNSLTR.getText("TXT_KEY_PEDIA_LEADS_TO", ())
        screen.setText("AllowsTitleSIR", "", szLeadsToTitle, 1 << 0,
                       self.X_ALLOWS_PANEL + self.iMarginSpace,
                       self.Y_ALLOWS_PANEL4 - 20, 0, FONT_TITLE,
                       WIDGET_GENERAL, -1, -1)

        # Find techs that require this tech
        for j in xrange(num_techs):
            tech_j = GC.getTechInfo(j)

            # Check OR prerequisites
            for k in xrange(tech_j.getNumPrereqOrTechs()):
                if self.iTech == tech_j.getPrereqOrTechs(k):
                    screen.attachImageButton("SIR4", "", tech_j.getButton(),
                                             BUTTON_SIZE_CUSTOM,
                                             WIDGET_PEDIA_JUMP_TO_DERIVED_TECH,
                                             j, self.iTech, False)
                    break

            # Check AND prerequisites
            for k in xrange(tech_j.getNumPrereqAndTechs()):
                if self.iTech == tech_j.getPrereqAndTechs(k):
                    screen.attachImageButton("SIR4", "", tech_j.getButton(),
                                             BUTTON_SIZE_CUSTOM,
                                             WIDGET_PEDIA_JUMP_TO_DERIVED_TECH,
                                             j, self.iTech, False)
                    break

        # Units Enabled
        szUnitsTitle = "<font=3b>%s:" % TRNSLTR.getText("TXT_KEY_PEDIA_UNITS_ENABLED", ())
        screen.setText("UnitsTitle", "", szUnitsTitle, 1 << 0,
                       self.X_ALLOWS_PANEL + self.iMarginSpace,
                       self.Y_ALLOWS_PANEL - 20, 0, FONT_TITLE,
                       WIDGET_GENERAL, -1, -1)

        # Use cached widget name for panel
        panel_widget = self._widget_cache[panelName] if panelName < len(
            self._widget_cache) else self.getNextWidgetName()

        for iUnit in xrange(GC.getNumUnitInfos()):
            if isTechRequiredForUnit(self.iTech, iUnit):
                screen.attachImageButton(panel_widget, "",
                                         GC.getUnitInfo(iUnit).getButton(),
                                         BUTTON_SIZE_CUSTOM,
                                         WIDGET_PEDIA_JUMP_TO_UNIT,
                                         iUnit, 1, False)

        # Buildings Enabled
        szBuildingsTitle = "<font=3b>%s:" % TRNSLTR.getText("TXT_KEY_PEDIA_BUILDINGS_ENABLED", ())
        screen.setText("BuildingsTitle", "", szBuildingsTitle, 1 << 0,
                       self.X_ALLOWS_PANEL + self.iMarginSpace,
                       self.Y_ALLOWS_PANEL2 - 20, 0, FONT_TITLE,
                       WIDGET_GENERAL, -1, -1)

        for eLoopBuilding in xrange(GC.getNumBuildingInfos()):
            if isTechRequiredForBuilding(self.iTech, eLoopBuilding):
                screen.attachImageButton("SIR2", "",
                                         GC.getBuildingInfo(eLoopBuilding).getButton(),
                                         BUTTON_SIZE_CUSTOM,
                                         WIDGET_PEDIA_JUMP_TO_BUILDING,
                                         eLoopBuilding, 1, False)

        # Improvements, Projects, Promotions, etc.
        szImprovesTitle = "<font=3b>%s:" % TRNSLTR.getText("TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT", ())
        screen.setText("ImprovesTitle", "", szImprovesTitle, 1 << 0,
                       self.X_ALLOWS_PANEL + self.iMarginSpace,
                       self.Y_ALLOWS_PANEL3 - 20, 0, FONT_TITLE,
                       WIDGET_GENERAL, -1, -1)

        # Projects
        for j in xrange(GC.getNumProjectInfos()):
            if isTechRequiredForProject(self.iTech, j):
                screen.attachImageButton("SIR3", "",
                                         GC.getProjectInfo(j).getButton(),
                                         BUTTON_SIZE_CUSTOM,
                                         WIDGET_PEDIA_JUMP_TO_PROJECT,
                                         j, 1, False)

        # Promotions
        for j in xrange(GC.getNumPromotionInfos()):
            if GC.getPromotionInfo(j).getTechPrereq() == self.iTech:
                screen.attachImageButton("SIR3", "",
                                         GC.getPromotionInfo(j).getButton(),
                                         BUTTON_SIZE_CUSTOM,
                                         WIDGET_PEDIA_JUMP_TO_PROMOTION,
                                         j, 1, False)

        # Builds and Improvements
        num_features = GC.getNumFeatureInfos()
        for j in xrange(GC.getNumBuildInfos()):
            buildInfo = GC.getBuildInfo(j)
            bTechFound = 0

            if buildInfo.getTechPrereq() == -1:
                # Check feature techs
                for k in xrange(num_features):
                    if buildInfo.getFeatureTech(k) == self.iTech:
                        bTechFound = 1
                        break
            elif buildInfo.getTechPrereq() == self.iTech:
                bTechFound = 1

            if bTechFound == 1:
                improvement = buildInfo.getImprovement()
                if improvement == -1:
                    screen.attachImageButton("SIR3", "",
                                             buildInfo.getButton(),
                                             BUTTON_SIZE_CUSTOM,
                                             WIDGET_HELP_IMPROVEMENT,
                                             j, 1, False)
                else:
                    screen.attachImageButton("SIR3", "",
                                             buildInfo.getButton(),
                                             BUTTON_SIZE_CUSTOM,
                                             WIDGET_PEDIA_JUMP_TO_IMPROVEMENT,
                                             improvement, 1, False)

        # Bonuses
        for j in xrange(GC.getNumBonusInfos()):
            if GC.getBonusInfo(j).getTechReveal() == self.iTech:
                screen.attachImageButton("SIR3", "",
                                         GC.getBonusInfo(j).getButton(),
                                         BUTTON_SIZE_CUSTOM,
                                         WIDGET_PEDIA_JUMP_TO_BONUS,
                                         j, 1, False)

        # Civics
        for j in xrange(GC.getNumCivicInfos()):
            if GC.getCivicInfo(j).getTechPrereq() == self.iTech:
                screen.attachImageButton("SIR3", "",
                                         GC.getCivicInfo(j).getButton(),
                                         BUTTON_SIZE_CUSTOM,
                                         WIDGET_PEDIA_JUMP_TO_CIVIC,
                                         j, 1, False)

    def getNextWidgetName(self):
        """Returns a unique widget name from cache or creates new"""
        if self.nWidgetCount < len(self._widget_cache) and self._widget_cache[self.nWidgetCount]:
            szName = self._widget_cache[self.nWidgetCount]
        else:
            szName = "%s%d" % (self.WIDGET_ID, self.nWidgetCount * self.nTechs + self.iTech)
            if self.nWidgetCount < len(self._widget_cache):
                self._widget_cache[self.nWidgetCount] = szName

        self.nWidgetCount += 1
        return szName

    def getScreen(self):
        """Returns the screen object"""
        return CyGInterfaceScreen(self.SCREEN_NAME + str(self.iTech), self.nScreenId)

    def handleInput(self, inputClass):
        """Handle user input"""
        if inputClass.getData() == KB_RETURN:
            self.getScreen().hideScreen()
            return 1
        if inputClass.getNotifyCode() == NOTIFY_CLICKED:
            if inputClass.getFunctionName() == self.EXIT_ID:
                self.getScreen().hideScreen()
            return 1
        return 0

    def update(self, fDelta):
        """Update callback - no action needed"""
        return