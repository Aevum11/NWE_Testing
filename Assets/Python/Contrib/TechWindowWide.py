## TechWindowWide
##
## Originally by SirRethcir: Techanzeige hinzugefÃ¼gt
## Enhanced by Roamty, Caesium, Guarav
## Memory-optimized version for 32-bit Python 2.4
##
## Copyright (c) 2008 The BUG Mod.

from CvPythonExtensions import *

# BUG Options
import BugCore

TechWindowOpt = BugCore.game.TechWindow

# Cache global context and translator once
GC = CyGlobalContext()
TRNSLTR = CyTranslator()

# Pre-cache frequently used strings to avoid repeated object creation
_STR_EMPTY = ""
_STR_FONT_TAG = u"<font=%s>%s</font>"
_STR_BACKGROUND = "Background"
_STR_PANEL_STYLE_BLACK = "Panel_Black25_Style"
_STR_PANEL_STYLE_TAN = "Panel_TanT_Style"
_STR_PANEL_STYLE_DAWN = "Panel_DawnBottom_Style"
_STR_PANEL_STYLE_TECH = "Panel_TechDiscover_Style"
_STR_PANEL_STYLE_TECH_GLOW = "Panel_TechDiscoverGlow_Style"


class CvTechSplashScreen:
    "Splash screen for techs"

    def __init__(self, iScreenID):
        self.nScreenId = iScreenID
        self.iTech = -1
        self.nWidgetCount = 0

        # widget names - store as class constants
        self.WIDGET_ID = "TechSplashScreenWidget"
        self.SCREEN_NAME = "TechSplashScreen"
        self.EXIT_ID = "TechSplashExit"

        # Pre-calculate frequently used coordinates
        self.X_SCREEN = 17
        self.Y_SCREEN = 27
        self.W_SCREEN = 1024
        self.H_SCREEN = 768
        self.Z_BACKGROUND = -1.1
        self.Z_CONTROLS = -1.3  # Pre-calculated from Z_BACKGROUND - 0.2
        self.DZ = -0.2
        self.Z_HELP_AREA = -3.3  # Pre-calculated from Z_CONTROLS - 2
        self.W_HELP_AREA = 200

        # Panels
        self.iMarginSpace = 15
        self.iMarginSpace2 = 30  # Pre-calculate 2 * margin

        self.X_MAIN_PANEL = 17
        self.Y_MAIN_PANEL = 25
        self.W_MAIN_PANEL = 996
        self.H_MAIN_PANEL = 725

        # Upper Panel - pre-calculate derived values
        self.X_UPPER_PANEL = 32  # X_MAIN_PANEL + iMarginSpace
        self.Y_UPPER_PANEL = 40  # Y_MAIN_PANEL + iMarginSpace
        self.W_UPPER_PANEL = 966  # W_MAIN_PANEL - 30
        self.H_UPPER_PANEL = 320

        self.X_TITLE = 515  # X_MAIN_PANEL + W_MAIN_PANEL / 2
        self.Y_TITLE = 52  # Y_UPPER_PANEL + 12

        self.W_ICON = 96
        self.H_ICON = 96

        self.X_ICON_PANEL = 49  # X_UPPER_PANEL + iMarginSpace + 2
        self.Y_ICON_PANEL = 88  # Y_UPPER_PANEL + iMarginSpace + 33
        self.W_ICON_PANEL = 160
        self.H_ICON_PANEL = 135

        self.X_ICON = 81  # Pre-calculated icon center position
        self.Y_ICON = 120  # Pre-calculated icon center position

        self.X_QUOTE = 224  # X_UPPER_PANEL + W_ICON_PANEL + 30
        self.Y_QUOTE = 120  # Same as Y_ICON
        self.W_QUOTE = 725
        self.H_QUOTE = 200  # Pre-calculated quote height

        # Lower Panel - pre-calculate all positions
        self.X_LOWER_PANEL = 32  # X_MAIN_PANEL + iMarginSpace
        self.Y_LOWER_PANEL = 360  # Y_UPPER_PANEL + H_UPPER_PANEL
        self.W_LOWER_PANEL = 966  # W_MAIN_PANEL - 30
        self.H_LOWER_PANEL = 360

        self.H_ALLOWS_PANEL = 80
        self.H_ALLOWS_SPACE = 28

        self.X_SPECIAL_PANEL = 47  # X_LOWER_PANEL + iMarginSpace
        self.Y_SPECIAL_PANEL = 395  # Y_LOWER_PANEL + iMarginSpace + 20
        self.W_SPECIAL_PANEL = 483  # W_LOWER_PANEL/2 - iMarginSpace
        self.H_SPECIAL_PANEL = 188  # 2 * H_ALLOWS_PANEL + H_ALLOWS_SPACE

        self.X_ALLOWS_PANELSIR = 47
        self.Y_ALLOWS_PANELSIR = 611  # Y_SPECIAL_PANEL + H_SPECIAL_PANEL + H_ALLOWS_SPACE
        self.W_ALLOWS_PANELSIR = 483
        self.H_ALLOWS_PANELSIR = 80

        self.X_ALLOWS_PANEL = 530  # X_LOWER_PANEL + iMarginSpace + W_SPECIAL_PANEL
        self.Y_ALLOWS_PANEL = 395
        self.W_ALLOWS_PANEL = 483
        self.Y_ALLOWS_PANEL2 = 503  # Y_SPECIAL_PANEL + H_ALLOWS_PANEL + H_ALLOWS_SPACE
        self.Y_ALLOWS_PANEL3 = 611  # Y_SPECIAL_PANEL + 2 * (H_ALLOWS_PANEL + H_ALLOWS_SPACE)

        # Contents
        self.X_EXIT = 452  # X_MAIN_PANEL + W_MAIN_PANEL/2 - 55
        self.Y_EXIT = 705  # Y_MAIN_PANEL + H_MAIN_PANEL - 45
        self.W_EXIT = 120
        self.H_EXIT = 30

        # Pre-cache widget type constants to avoid repeated lookups
        self.WIDGET_GENERAL = WidgetTypes.WIDGET_GENERAL
        self.WIDGET_CLOSE = WidgetTypes.WIDGET_CLOSE_SCREEN
        self.WIDGET_PEDIA_JUMP_TECH = WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH
        self.WIDGET_PEDIA_JUMP_DERIVED = WidgetTypes.WIDGET_PEDIA_JUMP_TO_DERIVED_TECH
        self.WIDGET_PEDIA_JUMP_UNIT = WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT
        self.WIDGET_PEDIA_JUMP_BUILDING = WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING
        self.WIDGET_PEDIA_JUMP_PROJECT = WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT
        self.WIDGET_PEDIA_JUMP_PROMOTION = WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION
        self.WIDGET_PEDIA_JUMP_IMPROVEMENT = WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT
        self.WIDGET_PEDIA_JUMP_BONUS = WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS
        self.WIDGET_PEDIA_JUMP_CIVIC = WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC
        self.WIDGET_HELP_IMPROVEMENT = WidgetTypes.WIDGET_HELP_IMPROVEMENT

        # Pre-cache panel styles
        self.PANEL_STYLE_MAIN = PanelStyles.PANEL_STYLE_MAIN
        self.PANEL_STYLE_DAWNBOTTOM = PanelStyles.PANEL_STYLE_DAWNBOTTOM
        self.PANEL_STYLE_MAIN_TAN15 = PanelStyles.PANEL_STYLE_MAIN_TAN15
        self.PANEL_STYLE_IN = PanelStyles.PANEL_STYLE_IN

        # Pre-cache button style
        self.BUTTON_STYLE_STANDARD = ButtonStyles.BUTTON_STYLE_STANDARD
        self.BUTTON_SIZE_CUSTOM = GenericButtonSizes.BUTTON_SIZE_CUSTOM

    def interfaceScreen(self, iTech):
        self.iTech = iTech
        self.nWidgetCount = 0

        # Cache frequently accessed values
        screen = self.getScreen()
        techInfo = GC.getTechInfo(iTech)

        # Cache tech info methods that will be called multiple times
        techButton = techInfo.getButton()
        techDescription = techInfo.getDescription()
        techQuote = techInfo.getQuote()

        # Pre-cache translated strings
        self.EXIT_TEXT = TRNSLTR.getText("TXT_KEY_SCREEN_CONTINUE", ())
        self.nTechs = GC.getNumTechInfos()

        # Setup screen
        screen.setSound(techInfo.getSound())
        screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
        screen.enableWorldSounds(False)
        screen.showWindowBackground(False)
        screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)

        # Create all panels using cached values
        self._createPanels(screen)

        # Add content using cached tech info
        self._addContent(screen, techInfo, techButton, techDescription, techQuote)

    def _createPanels(self, screen):
        """Create all UI panels with optimized parameters"""
        # Main Panel
        screen.addPanel("TechSplashMainPanel", _STR_EMPTY, _STR_EMPTY, True, True,
                        self.X_MAIN_PANEL, self.Y_MAIN_PANEL, self.W_MAIN_PANEL, self.H_MAIN_PANEL,
                        self.PANEL_STYLE_MAIN)

        # Top Panel
        szHeaderPanel = "TechSplashHeaderPanel"
        screen.addPanel(szHeaderPanel, _STR_EMPTY, _STR_EMPTY, True, True,
                        self.X_UPPER_PANEL, self.Y_UPPER_PANEL, self.W_UPPER_PANEL, self.H_UPPER_PANEL,
                        self.PANEL_STYLE_DAWNBOTTOM)
        screen.setStyle(szHeaderPanel, _STR_PANEL_STYLE_DAWN)

        # Icon Panels - reuse calculated dimensions
        w_icon_bg = 936  # Pre-calculated: W_UPPER_PANEL - 30
        screen.addPanel("IconPanel", _STR_EMPTY, _STR_EMPTY, True, True,
                        self.X_ICON_PANEL, self.Y_ICON_PANEL, w_icon_bg, 256,
                        self.PANEL_STYLE_MAIN_TAN15)
        screen.setStyle("IconPanel", _STR_PANEL_STYLE_TECH)

        screen.addPanel("IconPanelGlow", _STR_EMPTY, _STR_EMPTY, True, True,
                        self.X_ICON_PANEL, self.Y_ICON_PANEL, self.W_ICON_PANEL, self.H_ICON_PANEL,
                        self.PANEL_STYLE_MAIN_TAN15)
        screen.setStyle("IconPanelGlow", _STR_PANEL_STYLE_TECH_GLOW)

        # Bottom Panel
        x_text = 47  # Pre-calculated: X_LOWER_PANEL + iMarginSpace
        w_text = 936  # Pre-calculated: W_LOWER_PANEL - 30
        screen.addPanel("TechSplashTextPanel", _STR_EMPTY, _STR_EMPTY, True, True,
                        x_text, self.Y_LOWER_PANEL, w_text, self.H_LOWER_PANEL, self.PANEL_STYLE_MAIN)
        screen.setStyle("TechSplashTextPanel", _STR_PANEL_STYLE_TAN)

        # Exit Button
        screen.setButtonGFC("Exit", self.EXIT_TEXT, _STR_EMPTY,
                            self.X_EXIT, self.Y_EXIT, self.W_EXIT, self.H_EXIT,
                            self.WIDGET_CLOSE, -1, -1, self.BUTTON_STYLE_STANDARD)

        # Special and Allows Panels - use optimized positions
        self._createContentPanels(screen)

    def _createContentPanels(self, screen):
        """Create content panels with pre-calculated positions"""
        # Calculate once
        x_special = 62  # X_SPECIAL_PANEL + iMarginSpace
        w_special = 453  # W_SPECIAL_PANEL - 30
        x_allows = 545  # X_ALLOWS_PANEL + iMarginSpace
        w_allows = 453  # W_ALLOWS_PANEL - 30

        # Special Panel
        screen.addPanel("TechSplashSpecialPanel", _STR_EMPTY, _STR_EMPTY, True, True,
                        x_special, self.Y_SPECIAL_PANEL, w_special, self.H_SPECIAL_PANEL,
                        self.PANEL_STYLE_IN)
        screen.setStyle("TechSplashSpecialPanel", _STR_PANEL_STYLE_BLACK)

        # Allows Panels - reuse panel creation logic
        panels = [
            ("SIR", 62, self.Y_ALLOWS_PANELSIR, w_special, self.H_ALLOWS_PANELSIR),
            (self.getNextWidgetName(), x_allows, self.Y_ALLOWS_PANEL, w_allows, self.H_ALLOWS_PANEL),
            ("SIR2", x_allows, self.Y_ALLOWS_PANEL2, w_allows, self.H_ALLOWS_PANEL),
            ("SIR3", x_allows, self.Y_ALLOWS_PANEL3, w_allows, self.H_ALLOWS_PANEL)
        ]

        for name, x, y, w, h in panels:
            screen.addPanel(name, _STR_EMPTY, _STR_EMPTY, False, True,
                            x, y, w, h, self.PANEL_STYLE_IN)
            screen.setStyle(name, _STR_PANEL_STYLE_BLACK)

    def _addContent(self, screen, techInfo, techButton, techDescription, techQuote):
        """Add content to panels with cached values"""
        # Title - use pre-formatted string
        szTech = _STR_FONT_TAG % ("4", techDescription.upper())
        screen.setLabel(self.getNextWidgetName(), _STR_BACKGROUND, szTech, 4,
                        self.X_TITLE, self.Y_TITLE, self.Z_CONTROLS, FontTypes.GAME_FONT,
                        self.WIDGET_GENERAL, -1, -1)

        # Tech Icon
        screen.addDDSGFC(self.getNextWidgetName(), techButton,
                         self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON,
                         self.WIDGET_PEDIA_JUMP_TECH, self.iTech, 2)

        # Tech Quote
        iTextOffset = 0
        if TechWindowOpt.isShowCivilopediaText():
            techQuote = "%s\n\n%s" % (techQuote, techInfo.getCivilopedia())
        else:
            iTextOffset = 20

        screen.addMultilineText("Text", techQuote,
                                self.X_QUOTE, self.Y_QUOTE + iTextOffset, self.W_QUOTE,
                                self.H_QUOTE - iTextOffset, self.WIDGET_GENERAL, -1, -1, 1)

        # Add special abilities and allows content
        self._addSpecialAbilities(screen)
        self._addAllowsContent(screen, techInfo)

    def _addSpecialAbilities(self, screen):
        """Add special abilities section"""
        # Special Title
        szTitle = _STR_FONT_TAG % ("3b", TRNSLTR.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()))
        screen.setText("SpecialTitle", _STR_EMPTY, szTitle, 1,
                       62, 375, 0, FontTypes.TITLE_FONT, self.WIDGET_GENERAL, -1, -1)

        # Special Text
        szSpecialText = CyGameTextMgr().getTechHelp(self.iTech, True, False, False, True, -1)[1:]
        screen.addMultilineText(self.getNextWidgetName(), szSpecialText,
                                57, 400, 463, 168, self.WIDGET_GENERAL, -1, -1, 1)

    def _addAllowsContent(self, screen, techInfo):
        """Add all allows content with optimized loops"""
        # Cache frequently used methods
        getButton = lambda info: info.getButton()
        attachButton = screen.attachImageButton

        # Pre-calculate title positions
        title_x = 62
        title_y_leads = 591
        title_y_units = 375
        title_y_buildings = 483
        title_y_improve = 591

        # Leads To
        szTitle = _STR_FONT_TAG % ("3b", "%s:" % TRNSLTR.getText("TXT_KEY_PEDIA_LEADS_TO", ()))
        screen.setText("AllowsTitleSIR", _STR_EMPTY, szTitle, 1,
                       title_x, title_y_leads, 0, FontTypes.TITLE_FONT, self.WIDGET_GENERAL, -1, -1)

        # Process leads-to techs
        iTech = self.iTech
        for j in xrange(GC.getNumTechInfos()):
            techJ = GC.getTechInfo(j)
            # Check OR prerequisites
            for iPrereq in techJ.getPrereqOrTechs():
                if iPrereq == iTech:
                    attachButton("SIR", _STR_EMPTY, getButton(techJ),
                                 self.BUTTON_SIZE_CUSTOM, self.WIDGET_PEDIA_JUMP_DERIVED, j, iTech, False)
                    break
            # Check AND prerequisites
            for iPrereq in techJ.getPrereqAndTechs():
                if iPrereq == iTech:
                    attachButton("SIR", _STR_EMPTY, getButton(techJ),
                                 self.BUTTON_SIZE_CUSTOM, self.WIDGET_PEDIA_JUMP_DERIVED, j, iTech, False)
                    break

        # Units Enabled
        szTitle = _STR_FONT_TAG % ("3b", "%s:" % TRNSLTR.getText("TXT_KEY_PEDIA_UNITS_ENABLED", ()))
        screen.setText("UnitsTitle", _STR_EMPTY, szTitle, 1,
                       545, title_y_units, 0, FontTypes.TITLE_FONT, self.WIDGET_GENERAL, -1, -1)

        panelName = "TechSplashScreenWidget0"  # Pre-calculated first widget name
        for iUnit in xrange(GC.getNumUnitInfos()):
            if isTechRequiredForUnit(iTech, iUnit):
                attachButton(panelName, _STR_EMPTY, getButton(GC.getUnitInfo(iUnit)),
                             self.BUTTON_SIZE_CUSTOM, self.WIDGET_PEDIA_JUMP_UNIT, iUnit, 1, False)

        # Buildings Enabled
        szTitle = _STR_FONT_TAG % ("3b", "%s:" % TRNSLTR.getText("TXT_KEY_PEDIA_BUILDINGS_ENABLED", ()))
        screen.setText("BuildingsTitle", _STR_EMPTY, szTitle, 1,
                       545, title_y_buildings, 0, FontTypes.TITLE_FONT, self.WIDGET_GENERAL, -1, -1)

        for eLoopBuilding in xrange(GC.getNumBuildingInfos()):
            if isTechRequiredForBuilding(iTech, eLoopBuilding):
                attachButton("SIR2", _STR_EMPTY, getButton(GC.getBuildingInfo(eLoopBuilding)),
                             self.BUTTON_SIZE_CUSTOM, self.WIDGET_PEDIA_JUMP_BUILDING, eLoopBuilding, 1, False)

        # Improvements and other items
        szTitle = _STR_FONT_TAG % ("3b", "%s:" % TRNSLTR.getText("TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT", ()))
        screen.setText("ImprovesTitle", _STR_EMPTY, szTitle, 1,
                       545, title_y_improve, 0, FontTypes.TITLE_FONT, self.WIDGET_GENERAL, -1, -1)

        self._addImprovementContent(screen, attachButton, getButton)

    def _addImprovementContent(self, screen, attachButton, getButton):
        """Add improvement-related content"""
        iTech = self.iTech

        # Projects
        for j in xrange(GC.getNumProjectInfos()):
            if isTechRequiredForProject(iTech, j):
                attachButton("SIR3", _STR_EMPTY, getButton(GC.getProjectInfo(j)),
                             self.BUTTON_SIZE_CUSTOM, self.WIDGET_PEDIA_JUMP_PROJECT, j, 1, False)

        # Promotions
        for j in xrange(GC.getNumPromotionInfos()):
            if GC.getPromotionInfo(j).getTechPrereq() == iTech:
                attachButton("SIR3", _STR_EMPTY, getButton(GC.getPromotionInfo(j)),
                             self.BUTTON_SIZE_CUSTOM, self.WIDGET_PEDIA_JUMP_PROMOTION, j, 1, False)

        # Improvements/Builds
        numFeatures = GC.getNumFeatureInfos()
        for j in xrange(GC.getNumBuildInfos()):
            buildInfo = GC.getBuildInfo(j)
            bTechFound = 0

            if buildInfo.getTechPrereq() == iTech:
                bTechFound = 1
            elif buildInfo.getTechPrereq() == -1:
                # Check feature techs
                for k in xrange(numFeatures):
                    if buildInfo.getFeatureTech(k) == iTech:
                        bTechFound = 1
                        break

            if bTechFound == 1:
                improvement = buildInfo.getImprovement()
                if improvement == -1:
                    attachButton("SIR3", _STR_EMPTY, getButton(buildInfo),
                                 self.BUTTON_SIZE_CUSTOM, self.WIDGET_HELP_IMPROVEMENT, j, 1, False)
                else:
                    attachButton("SIR3", _STR_EMPTY, getButton(buildInfo),
                                 self.BUTTON_SIZE_CUSTOM, self.WIDGET_PEDIA_JUMP_IMPROVEMENT, improvement, 1, False)

        # Bonuses
        for j in xrange(GC.getNumBonusInfos()):
            if GC.getBonusInfo(j).getTechReveal() == iTech:
                attachButton("SIR3", _STR_EMPTY, getButton(GC.getBonusInfo(j)),
                             self.BUTTON_SIZE_CUSTOM, self.WIDGET_PEDIA_JUMP_BONUS, j, 1, False)

        # Civics
        for j in xrange(GC.getNumCivicInfos()):
            if GC.getCivicInfo(j).getTechPrereq() == iTech:
                attachButton("SIR3", _STR_EMPTY, getButton(GC.getCivicInfo(j)),
                             self.BUTTON_SIZE_CUSTOM, self.WIDGET_PEDIA_JUMP_CIVIC, j, 1, False)

    def getNextWidgetName(self):
        """Returns a unique widget name - optimized version"""
        # Pre-calculate the name to avoid multiple operations
        szName = "%s%d" % (self.WIDGET_ID, self.nWidgetCount * self.nTechs + self.iTech)
        self.nWidgetCount += 1
        return szName

    def getScreen(self):
        """Returns the screen object - optimized with string formatting"""
        return CyGInterfaceScreen("%s%d" % (self.SCREEN_NAME, self.iTech), self.nScreenId)

    def handleInput(self, inputClass):
        """Handle user input"""
        data = inputClass.getData()
        if data == int(InputTypes.KB_RETURN):
            self.getScreen().hideScreen()
            return 1
        if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
            if inputClass.getFunctionName() == self.EXIT_ID:
                self.getScreen().hideScreen()
            return 1
        return 0

    def update(self, fDelta):
        """Update method - no operation needed"""
        return