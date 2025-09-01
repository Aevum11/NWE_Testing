## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## Memory-optimized version for 32-bit Python 2.4

from CvPythonExtensions import *
from CvScreenEnums import *
import types
import weakref
import gc

# Lazy imports and deferred loading
import BugCore

AdvisorOpt = BugCore.game.Advisors

# Single global for active screen - saves memory vs multiple globals
g_iScreenActive = -2

# Use weak references for screen instances to allow GC when not in use
screenMap = {}
_deferred_screens = {}
_import_cache = {}


# Memory optimization: Cache common operations
def _get_active_player():
    return CyGame().getActivePlayer()


def _is_player_active():
    return _get_active_player() != -1


# Consolidate screen toggle functions
def toggleSetNoScreens():
    global g_iScreenActive
    print
    "SCREEN %s TURNED OFF" % (g_iScreenActive)
    toggleSetScreenOn((MAIN_INTERFACE,))


def toggleSetScreenOn(argsList):
    global g_iScreenActive
    if g_iScreenActive == -2:
        # Lazy import - only load when needed
        import ScreenResolution as SR
        if not SR.x:
            print
            "Fetch resolution setting from profileName.pfl"
            UserProfile = CyUserProfile()
            print
            "\nAll User Profiles:"
            for i in xrange(UserProfile.getNumProfileFiles()):
                print
                UserProfile.getProfileFileName(i)
            print
            "Current profile: " + UserProfile.getProfileName()
            szRes = UserProfile.getResolutionString(UserProfile.getResolution())
            szRes = szRes.split(" x ")
            SR.x = int(szRes[0])
            SR.y = int(szRes[1])
            print
            "Resolution: %dx%d" % (SR.x, SR.y)
            SR.calibrate()
    print
    "SCREEN %s TURNED ON" % (argsList[0])
    g_iScreenActive = argsList[0]


# Lazy-load main interface
mainInterface = None


def _get_main_interface():
    global mainInterface
    if mainInterface is None:
        import CvMainInterface
        mainInterface = CvMainInterface.CvMainInterface()
    return mainInterface


def showMainInterface():
    print
    "showMainInterface"
    _get_main_interface().interfaceScreen()


def reinitMainInterface():
    print
    "reinitMainInterface"
    global mainInterface
    import CvMainInterface
    # Clear old reference
    if mainInterface is not None:
        del mainInterface
        gc.collect()
    mainInterface = CvMainInterface.CvMainInterface()
    mainInterface.interfaceScreen()


def initMinimap():
    _get_main_interface().initMinimap()


def showParallelMapsScreenButton():
    _get_main_interface().showParallelMapsScreenButton()


def numPlotListButtons():
    return 0


# Generic screen display function to reduce code duplication
def _show_screen(screen_id, *args):
    if _is_player_active():
        screen = _get_screen(screen_id)
        if screen:
            if args:
                screen.interfaceScreen(*args)
            else:
                screen.interfaceScreen()


def _get_screen(screen_id):
    """Lazy load screens on demand"""
    if screen_id not in screenMap or screenMap[screen_id]() is None:
        _load_screen(screen_id)
    screen_ref = screenMap.get(screen_id)
    return screen_ref() if screen_ref else None


def _load_screen(screen_id):
    """Load screen module on demand"""
    if screen_id in _deferred_screens:
        module_name, class_name, args = _deferred_screens[screen_id]
        # Use cached imports
        if module_name not in _import_cache:
            _import_cache[module_name] = __import__(module_name)
        module = _import_cache[module_name]

        if class_name:
            screen_class = getattr(module, class_name)
            if args:
                screen = screen_class(*args)
            else:
                screen = screen_class()
        else:
            screen = module

        # Store as weak reference
        screenMap[screen_id] = weakref.ref(screen)
        # Remove from deferred list to save memory
        del _deferred_screens[screen_id]


# Consolidated show functions
def showTechChooser():
    _show_screen(TECH_CHOOSER, TECH_CHOOSER)


def showHallOfFame(argsList):
    screen = _get_screen(HALL_OF_FAME)
    if screen:
        screen.interfaceScreen(argsList[0])


def showCivicsScreen():
    _show_screen(CIVICS_SCREEN)


def showHeritageScreen():
    _show_screen(HERITAGE_SCREEN)


def showParallelMapsScreen():
    _show_screen(PARALLEL_MAPS_SCREEN)


def showReligionScreen():
    _show_screen(RELIGION_SCREEN)


def showCorporationScreen():
    _show_screen(CORPORATION_SCREEN)


# Options screen - lazy load
optionsScreen = None


def _get_options_screen():
    global optionsScreen
    if optionsScreen is None:
        import CvOptionsScreen
        optionsScreen = CvOptionsScreen.CvOptionsScreen()
    return optionsScreen


def showOptionsScreen():
    _get_options_screen().interfaceScreen()


def showForeignAdvisorScreen(argsList):
    _show_screen(FOREIGN_ADVISOR)


def showFinanceAdvisor():
    _show_screen(FINANCE_ADVISOR)


def showDomesticAdvisor(argsList):
    _show_screen(DOMESTIC_ADVISOR)


def showMilitaryAdvisor():
    _show_screen(MILITARY_ADVISOR)


def showEspionageAdvisor():
    _show_screen(ESPIONAGE_ADVISOR)


def showDawnOfMan(argsList):
    screen = _get_screen(DAWN_OF_MAN)
    if screen:
        screen.interfaceScreen(DAWN_OF_MAN)


def showIntroMovie(argsList):
    _show_screen(INTRO_MOVIE_SCREEN)


def showVictoryMovie(argsList):
    screen = _get_screen(VICTORY_MOVIE_SCREEN)
    if screen:
        screen.interfaceScreen(argsList[0])


def showWonderMovie(argsList):
    screen = _get_screen(WONDER_MOVIE_SCREEN)
    if screen:
        screen.interfaceScreen(argsList[0], argsList[1], argsList[2], WONDER_MOVIE_SCREEN)


def showEraMovie(argsList):
    screen = _get_screen(ERA_MOVIE_SCREEN)
    if screen:
        screen.interfaceScreen(argsList[0])


def showSpaceShip(argsList):
    if _is_player_active():
        screen = _get_screen(SPACE_SHIP_SCREEN)
        if screen:
            screen.interfaceScreen(argsList[0])


# Replay screen - lazy load
replayScreen = None


def showReplay(argsList):
    global replayScreen
    if argsList[0] > -1:
        CyGame().saveReplay(argsList[0])
    if replayScreen is None:
        import CvReplayScreen
        replayScreen = CvReplayScreen.CvReplayScreen(REPLAY_SCREEN)
    replayScreen.showScreen(argsList[4])


def showDanQuayleScreen(argsList):
    _show_screen(DAN_QUAYLE_SCREEN)


# UnVictory screen - lazy load
unVictoryScreen = None


def showUnVictoryScreen(argsList):
    global unVictoryScreen
    if unVictoryScreen is None:
        import CvUnVictoryScreen
        unVictoryScreen = CvUnVictoryScreen.CvUnVictoryScreen()
    unVictoryScreen.interfaceScreen()


def showTopCivs():
    screen = _get_screen(TOP_CIVS)
    if screen:
        screen.showScreen()


def showInfoScreen(argsList):
    if _is_player_active():
        screen = _get_screen(INFO_SCREEN)
        if screen:
            screen.interfaceScreen(argsList[0], argsList[1])


def showDebugInfoScreen():
    _show_screen(DEBUG_INFO_SCREEN)


def showDebugScreen():
    _show_screen(DEBUG_SCREEN)


def configTechSplash(option=None, value=None):
    if value is None:
        TechWindowOpt = BugCore.game.TechWindow
        if TechWindowOpt.isWideView():
            value = True

    if value:
        _deferred_screens[TECH_SPLASH] = ('TechWindowWide', 'CvTechSplashScreen', (TECH_SPLASH,))
    else:
        _deferred_screens[TECH_SPLASH] = ('TechWindow', 'CvTechSplashScreen', (TECH_SPLASH,))


def showTechSplash(argsList):
    if TECH_SPLASH not in screenMap:
        configTechSplash()
    screen = _get_screen(TECH_SPLASH)
    if screen:
        screen.interfaceScreen(argsList[0])


def showVictoryScreen():
    _show_screen(VICTORY_SCREEN)


# RevolutionWatchAdvisor - lazy load
revolutionWatchAdvisor = None


def createRevolutionWatchAdvisor():
    global revolutionWatchAdvisor
    if revolutionWatchAdvisor is None:
        import RevolutionWatchAdvisor
        revolutionWatchAdvisor = RevolutionWatchAdvisor.RevolutionWatchAdvisor()
        screenMap[REVOLUTION_WATCH_ADVISOR] = weakref.ref(revolutionWatchAdvisor)


def showRevolutionWatchAdvisor(argsList):
    if _is_player_active():
        createRevolutionWatchAdvisor()
        revolutionWatchAdvisor.interfaceScreen()


def isRevolutionWatchAdvisor():
    return revolutionWatchAdvisor and revolutionWatchAdvisor.isVisible()


def cityScreenRedraw():
    _get_main_interface().updateCityScreen()


def showBuildListScreen():
    _show_screen(BUILD_LIST_SCREEN)


def showForgetfulScreen():
    screen = _get_screen(FORGETFUL_SCREEN)
    if screen:
        screen.interfaceScreen(FORGETFUL_SCREEN)


# Pedia functions - consolidated
def linkToPedia(argsList):
    screen = _get_screen(PEDIA)
    if screen:
        screen.link(argsList)


def pediaShow():
    screen = _get_screen(PEDIA)
    if screen:
        screen.pediaShow()


def pediaBack():
    screen = _get_screen(PEDIA)
    if screen:
        screen.back()


def pediaForward():
    screen = _get_screen(PEDIA)
    if screen:
        screen.forward()


# Generic pedia jump function
def _pedia_jump(type_id, sub_type, index):
    screen = _get_screen(PEDIA)
    if screen:
        screen.pediaJump(type_id, sub_type, index)


def pediaJumpToBuilding(argsList):
    _pedia_jump(-3, "", argsList[0])


def pediaJumpToUnit(argsList):
    if argsList[0] > -1:
        _pedia_jump(-2, "", argsList[0])
    else:
        _pedia_jump(10, "UnitCombat", argsList[0] + 100000)


def pediaMain(argsList):
    _pedia_jump(-1, "", argsList[0])


def pediaShowHistorical(argsList):
    if argsList[0] == CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW:
        _pedia_jump(0, "NEW", argsList[1])
    else:
        _pedia_jump(0, "", argsList[1])


def pediaJumpToTech(argsList):
    _pedia_jump(1, "", argsList[0])


def pediaJumpToPromotion(argsList):
    _pedia_jump(4, "", argsList[0])


def pediaJumpToBonus(argsList):
    _pedia_jump(7, "", argsList[0])


def pediaJumpToTerrain(argsList):
    _pedia_jump(8, "Terrain", argsList[0])


def pediaJumpToFeature(argsList):
    _pedia_jump(8, "Feature", argsList[0])


def pediaJumpToImprovement(argsList):
    _pedia_jump(8, "Improvement", argsList[0])


def pediaJumpToTrait(argsList):
    _pedia_jump(9, "Trait", argsList[0])


def pediaJumpToCiv(argsList):
    _pedia_jump(9, "Civ", argsList[0])


def pediaJumpToLeader(argsList):
    _pedia_jump(9, "Leader", argsList[0])


def pediaJumpToCivic(argsList):
    _pedia_jump(9, "Civic", argsList[0])


def pediaJumpToReligion(argsList):
    _pedia_jump(9, "Religion", argsList[0])


def pediaJumpToHeritage(argsList):
    _pedia_jump(9, "Heritage", argsList[0])


def pediaJumpToProject(argsList):
    _pedia_jump(10, "Project", argsList[0])


def pediaJumpToSpecialist(argsList):
    _pedia_jump(10, "Specialist", argsList[0])


def pediaJumpToCorporation(argsList):
    _pedia_jump(10, "Corporation", argsList[0])


def pediaJumpToRoute(argsList):
    if argsList[0] > -1:
        _pedia_jump(8, "Route", argsList[0])
    else:
        _pedia_jump(10, "Build", argsList[0] + 100000)


def pediaJumpToEra(iEra):
    _pedia_jump(0, "Eras", iEra)


# Worldbuilder - lazy load
worldBuilderScreen = None
advancedStartScreen = None


def _get_world_builder():
    global worldBuilderScreen
    if worldBuilderScreen is None:
        import WorldBuilder
        worldBuilderScreen = WorldBuilder.WorldBuilder(WORLDBUILDER_SCREEN)
        screenMap[WORLDBUILDER_SCREEN] = weakref.ref(worldBuilderScreen)
    return worldBuilderScreen


def _get_advanced_start():
    global advancedStartScreen
    if advancedStartScreen is None:
        import CvAdvancedStartScreen
        advancedStartScreen = CvAdvancedStartScreen.CvAdvancedStartScreen()
    return advancedStartScreen


def showWorldBuilderScreen():
    print
    "showWorldBuilderScreen"
    if CyInterface().isInAdvancedStart():
        _get_advanced_start().interfaceScreen(ADVANCED_START_SCREEN)
    else:
        _get_world_builder().interfaceScreen()


def WorldBuilderExitCB():
    print
    "WorldBuilderExitCB"
    if CyInterface().isInAdvancedStart():
        CyInterface().setWorldBuilder(False)
    else:
        CyGame().exitWorldBuilder()


def hideWorldBuilderScreen():
    print
    "hideWorldBuilderScreen"
    if CyInterface().isInAdvancedStart():
        _get_advanced_start().killScreen()
    else:
        _get_world_builder().killScreen()
        toggleSetNoScreens()


def WorldBuilderToggleUnitEditCB():
    print
    "WorldBuilderToggleUnitEditCB"
    _get_world_builder().toggleUnitEditCB()


def WorldBuilderEraseCB():
    print
    "WorldBuilderEraseCB"
    _get_world_builder().eraseCB()


def WorldBuilderLandmarkCB():
    print
    "WorldBuilderLandmarkCB"
    _get_world_builder().landmarkModeCB()


def WorldBuilderToggleCityEditCB():
    print
    "WorldBuilderToggleCityEditCB"
    _get_world_builder().toggleCityEditCB()


def WorldBuilderNormalMapTabModeCB():
    print
    "WorldBuilderNormalMapTabModeCB"
    _get_world_builder().normalMapTabModeCB()


def WorldBuilderRevealTabModeCB():
    print
    "WorldBuilderRevealTabModeCB"
    _get_world_builder().revealTabModeCB()


def WorldBuilderDiplomacyModeCB():
    print
    "WorldBuilderDiplomacyModeCB"
    screen = _get_screen(WB_DIPLOMACY)
    if screen:
        screen.interfaceScreen(_get_active_player(), False)


def WorldBuilderRevealAllCB():
    print
    "WorldBuilderRevealAllCB"
    _get_world_builder().revealAll(True)


def WorldBuilderUnRevealAllCB():
    print
    "WorldBuilderUnRevealAllCB"
    _get_world_builder().revealAll(False)


def WorldBuilderGetHighlightPlot(argsList):
    print
    "WorldBuilderGetHighlightPlot"
    if CyInterface().isInAdvancedStart():
        return _get_advanced_start().getHighlightPlot(argsList)
    else:
        return _get_world_builder().getHighlightPlot(argsList)


# Advanced Start functions
def WorldBuilderGetASCityTabID():
    print
    "WorldBuilderGetASCityTabID"
    return _get_advanced_start().getCityTab()


def WorldBuilderGetASCityListID():
    print
    "WorldBuilderGetASCityListID"
    return _get_advanced_start().getCityRow()


def WorldBuilderGetASBuildingsListID():
    print
    "WorldBuilderGetASBuildingsListID"
    return _get_advanced_start().getBuildingsRow()


def WorldBuilderGetASAutomateListID():
    print
    "WorldBuilderGetASAutomateListID"
    return _get_advanced_start().getAutomationRow()


def WorldBuilderGetASUnitTabID():
    print
    "WorldBuilderGetASUnitTabID"
    return _get_advanced_start().getUnitTab()


def WorldBuilderGetASImprovementsTabID():
    print
    "WorldBuilderGetASImprovementsTabID"
    return _get_advanced_start().getImprovementTab()


def WorldBuilderGetASRoutesListID():
    print
    "WorldBuilderGetASRoutesListID"
    return _get_advanced_start().getRoutesRow()


def WorldBuilderGetASImprovementsListID():
    print
    "WorldBuilderGetASImprovementsListID"
    return _get_advanced_start().getImprovementsRow()


def WorldBuilderGetASVisibilityTabID():
    print
    "WorldBuilderGetASVisibilityTabID"
    return _get_advanced_start().getVisibilityTab()


def WorldBuilderGetASTechTabID():
    print
    "WorldBuilderGetASTechTabID"
    return _get_advanced_start().getTechTab()


def WorldBuilderNormalPlayerTabModeCB():
    print
    "WorldBuilderNormalPlayerTabModeCB"
    if CyInterface().isInAdvancedStart():
        getWBToolNormalMapTabCtrl().enable(False)
    else:
        _get_world_builder().normalPlayerTabModeCB()


def WorldBuilderOnAdvancedStartBrushSelected(argsList):
    iList, iIndex, iTab = argsList
    print
    "WorldBuilderOnAdvancedStartBrushSelected, iList=%d, iIndex=%d, type=%d" % (iList, iIndex, iTab)
    advScreen = _get_advanced_start()
    if iTab == advScreen.getTechTab():
        showTechChooser()
    elif iTab == advScreen.getCityTab() and iList == advScreen.getAutomationRow():
        CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_AUTOMATE,
                                                   advScreen.iPlayer, -1, -1, -1, True)

    advScreen.setCurrentSelection(iTab, iIndex, iList)


# Overlay screen - lazy load
overlayScreen = None


def _get_overlay_screen():
    global overlayScreen
    if overlayScreen is None:
        import CvDotMapOverlayScreen
        overlayScreen = CvDotMapOverlayScreen.CvDotMapOverlayScreen(STRATEGY_OVERLAY_SCREEN)
    return overlayScreen


def showOverlayScreen():
    _get_overlay_screen().interfaceScreen()


def hideOverlayScreen():
    _get_overlay_screen().hideScreen()


# Utility Functions
def movieDone(argsList):
    screen_id = argsList[0]
    if screen_id == INTRO_MOVIE_SCREEN:
        screen = _get_screen(INTRO_MOVIE_SCREEN)
        if screen:
            screen.hideScreen()
    elif screen_id == VICTORY_MOVIE_SCREEN:
        screen = _get_screen(VICTORY_MOVIE_SCREEN)
        if screen:
            screen.hideScreen()


def leftMouseDown(argsList):
    screen_id = argsList[0]
    if screen_id == WORLDBUILDER_SCREEN:
        _get_world_builder().leftMouseDown(argsList[1:])
        return 1
    elif screen_id == ADVANCED_START_SCREEN:
        _get_advanced_start().leftMouseDown(argsList[1:])
        return 1
    return 0


def rightMouseDown(argsList):
    screen_id = argsList[0]
    if screen_id == WORLDBUILDER_SCREEN:
        _get_world_builder().rightMouseDown()
        return 1
    elif screen_id == ADVANCED_START_SCREEN:
        _get_advanced_start().rightMouseDown()
        return 1
    return 0


def mouseOverPlot(argsList):
    screen_id = argsList[0]
    if screen_id == STRATEGY_OVERLAY_SCREEN:
        _get_overlay_screen().onMouseOverPlot()
    elif screen_id == WORLDBUILDER_SCREEN:
        _get_world_builder().mouseOverPlot()
    elif screen_id == ADVANCED_START_SCREEN:
        _get_advanced_start().mouseOverPlot()


def handleInput(argsList):
    import ScreenInput as PyScreenInput
    inputClass = PyScreenInput.ScreenInput(argsList)
    iPythonFile = inputClass.ePythonFileEnum

    screen = _get_screen(iPythonFile)
    if screen:
        return screen.handleInput(inputClass)
    return 0


def sendMessage(args):
    import CvUtil
    CvUtil.sendMessage(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9],
                       args[10], args[11])


def update(argsList):
    screen_id = argsList[0]
    if screen_id == STRATEGY_OVERLAY_SCREEN:
        _get_overlay_screen().update(argsList)
    else:
        screen = _get_screen(screen_id)
        if screen:
            screen.update(argsList[1])


def onClose(argsList):
    screen = _get_screen(argsList[0])
    if screen and hasattr(screen, "onClose") and isinstance(screen.onClose, types.MethodType):
        screen.onClose()


def forceScreenUpdate(argsList):
    screen_id = argsList[0]
    if screen_id == TECH_CHOOSER:
        screen = _get_screen(TECH_CHOOSER)
        if screen:
            screen.updateTechRecords(False)
    elif screen_id == MAIN_INTERFACE:
        _get_main_interface().updateScreen()
    elif screen_id == WORLDBUILDER_SCREEN:
        _get_world_builder().updateScreen()
    elif screen_id == ADVANCED_START_SCREEN:
        _get_advanced_start().updateScreen()


def updateWaitingForPlayer(argsList):
    if g_iScreenActive == MAIN_INTERFACE:
        _get_main_interface().updateWaitingForPlayer(argsList[0])


def forceScreenRedraw(argsList):
    screen_id = argsList[0]
    if screen_id == MAIN_INTERFACE:
        _get_main_interface().redraw()
    elif screen_id == TECH_CHOOSER:
        screen = _get_screen(TECH_CHOOSER)
        if screen:
            screen.updateTechRecords(True)
    elif screen_id == ESPIONAGE_ADVISOR:
        screen = _get_screen(ESPIONAGE_ADVISOR)
        if screen:
            screen.redraw(CyGInterfaceScreen("EspionageAdvisor", ESPIONAGE_ADVISOR))


def minimapClicked(argsList):
    if MILITARY_ADVISOR == argsList[0]:
        screen = _get_screen(MILITARY_ADVISOR)
        if screen:
            screen.minimapClicked()


def handleBack(screens):
    if screens:
        for iScreen in screens:
            screen = _get_screen(iScreen)
            if screen and hasattr(screen, "back") and isinstance(screen.back, types.MethodType):
                screen.back()
    else:
        _get_main_interface().back()


def handleForward(screens):
    if screens:
        for iScreen in screens:
            screen = _get_screen(iScreen)
            if screen and hasattr(screen, "forward") and isinstance(screen.forward, types.MethodType):
                screen.forward()
    else:
        _get_main_interface().forward()


def refreshMilitaryAdvisor(argsList):
    screen = _get_screen(MILITARY_ADVISOR)
    if screen:
        if 1 == argsList[0]:
            screen.refreshSelectedGroup(argsList[1])
        elif argsList[0] <= 0:
            screen.refreshSelectedUnit(-argsList[0], argsList[1])


def updateMusicPath(argsList):
    szPathName = argsList[0]
    _get_options_screen().updateMusicPath(szPathName)


def refreshOptionsScreen():
    _get_options_screen().refreshScreen()


# Callback functions
def cityWarningOnClickedCallback(argsList):
    iButtonId = argsList[0]
    iData1 = argsList[1]
    iData2 = argsList[2]
    iData3 = argsList[3]
    iData4 = argsList[4]
    szText = argsList[5]
    bOption1 = argsList[6]
    bOption2 = argsList[7]
    city = CyGlobalContext().getPlayer(_get_active_player()).getCity(iData1)
    if city:
        if iButtonId == 0:
            if city.isProductionProcess():
                CyMessageControl().sendPushOrder(iData1, iData2, iData3, False, False, False)
            else:
                CyMessageControl().sendPushOrder(iData1, iData2, iData3, False, True, False)
        elif iButtonId == 2:
            CyInterface().selectCity(city, False)


def cityWarningOnFocusCallback(argsList):
    CyInterface().playGeneralSound("AS2D_ADVISOR_SUGGEST")
    CyInterface().lookAtCityOffset(argsList[0])
    return 0


def liberateOnClickedCallback(argsList):
    iButtonId = argsList[0]
    iData1 = argsList[1]
    city = CyGlobalContext().getPlayer(_get_active_player()).getCity(iData1)
    if city:
        if iButtonId == 0:
            CyMessageControl().sendDoTask(iData1, TaskTypes.TASK_LIBERATE, 0, -1, False, False, False, False)
        elif iButtonId == 2:
            CyInterface().selectCity(city, False)


def colonyOnClickedCallback(argsList):
    iButtonId = argsList[0]
    iData1 = argsList[1]
    city = CyGlobalContext().getPlayer(_get_active_player()).getCity(iData1)
    if city:
        if iButtonId == 0:
            CyMessageControl().sendEmpireSplit(_get_active_player(), city.area().getID())
        elif iButtonId == 2:
            CyInterface().selectCity(city, False)


def featAccomplishedOnClickedCallback(argsList):
    iButtonId = argsList[0]
    iData1 = argsList[1]
    iData2 = argsList[2]

    if iButtonId == 1:
        if iData1 == FeatTypes.FEAT_TRADE_ROUTE:
            showDomesticAdvisor(())
        elif (iData1 >= FeatTypes.FEAT_UNITCOMBAT_ARCHER) and (iData1 <= FeatTypes.FEAT_UNIT_SPY):
            CyGlobalContext().getGame().doControl(ControlTypes.CONTROL_MILITARY_SCREEN)
        elif (iData1 >= FeatTypes.FEAT_COPPER_CONNECTED) and (iData1 <= FeatTypes.FEAT_FOOD_CONNECTED):
            showForeignAdvisorScreen([0])
        elif iData1 == FeatTypes.FEAT_NATIONAL_WONDER:
            showInfoScreen([2, 0])
        elif (iData1 >= FeatTypes.FEAT_POPULATION_HALF_MILLION) and (iData1 <= FeatTypes.FEAT_POPULATION_2_BILLION):
            showInfoScreen([1, 0])
        elif iData1 == FeatTypes.FEAT_CORPORATION_ENABLED:
            showCorporationScreen()


def featAccomplishedOnFocusCallback(argsList):
    iData1 = argsList[0]
    iData2 = argsList[1]
    CyInterface().playGeneralSound("AS2D_FEAT_ACCOMPLISHED")
    if iData1 >= FeatTypes.FEAT_UNITCOMBAT_ARCHER and iData1 <= FeatTypes.FEAT_FOOD_CONNECTED:
        CyInterface().lookAtCityOffset(iData2)


# Deferred screen definitions - loaded on demand
def _setup_deferred_screens():
    """Setup deferred loading for all screens"""
    global _deferred_screens

    # Core screens
    _deferred_screens[CORPORATION_SCREEN] = ('CvCorporationScreen', 'CvCorporationScreen', ())
    _deferred_screens[ESPIONAGE_ADVISOR] = ('CvEspionageAdvisor', 'CvEspionageAdvisor', ())
    _deferred_screens[MILITARY_ADVISOR] = ('CvMilitaryAdvisor', 'CvMilitaryAdvisor', (MILITARY_ADVISOR,))
    _deferred_screens[DOMESTIC_ADVISOR] = ('CvDomesticAdvisor', 'CvDomesticAdvisor', (DOMESTIC_ADVISOR,))
    _deferred_screens[FOREIGN_ADVISOR] = ('CvForeignAdvisor', 'CvForeignAdvisor', (FOREIGN_ADVISOR,))
    _deferred_screens[FINANCE_ADVISOR] = ('CvFinanceAdvisor', 'CvFinanceAdvisor', (FINANCE_ADVISOR,))
    _deferred_screens[RELIGION_SCREEN] = ('CvReligionScreen', 'CvReligionScreen', ())
    _deferred_screens[ERA_MOVIE_SCREEN] = ('CvEraMovieScreen', 'CvEraMovieScreen', ())
    _deferred_screens[VICTORY_SCREEN] = ('CvVictoryScreen', 'CvVictoryScreen', (VICTORY_SCREEN,))
    _deferred_screens[CIVICS_SCREEN] = ('CvCivicsScreen', 'CvCivicsScreen', (CIVICS_SCREEN,))
    _deferred_screens[HERITAGE_SCREEN] = ('HeritageScreen', 'HeritageScreen', (HERITAGE_SCREEN,))
    _deferred_screens[PARALLEL_MAPS_SCREEN] = ('ParallelMapsScreen', 'ParallelMapsScreen', (PARALLEL_MAPS_SCREEN,))
    _deferred_screens[INFO_SCREEN] = ('CvInfoScreen', 'CvInfoScreen', (INFO_SCREEN,))
    _deferred_screens[DAWN_OF_MAN] = ('CvDawnOfMan', 'CvDawnOfMan', ())
    _deferred_screens[TOP_CIVS] = ('CvTopCivs', 'CvTopCivs', (TOP_CIVS,))
    _deferred_screens[FORGETFUL_SCREEN] = ('Forgetful', 'Forgetful', ())
    _deferred_screens[TECH_CHOOSER] = ('CvTechChooser', 'CvTechChooser', ())
    _deferred_screens[BUILD_LIST_SCREEN] = ('BuildListScreen', 'BuildListScreen', ())
    _deferred_screens[DEBUG_INFO_SCREEN] = ('CvDebugInfoScreen', 'CvDebugInfoScreen', ())
    _deferred_screens[DEBUG_SCREEN] = ('DebugScreen', 'DebugScreen', (DEBUG_SCREEN,))

    # Early loaded screens
    _deferred_screens[INTRO_MOVIE_SCREEN] = ('CvIntroMovieScreen', 'CvIntroMovieScreen', ())
    _deferred_screens[WONDER_MOVIE_SCREEN] = ('CvWonderMovieScreen', 'CvWonderMovieScreen', ())
    _deferred_screens[VICTORY_MOVIE_SCREEN] = ('CvVictoryMovieScreen', 'CvVictoryMovieScreen', ())
    _deferred_screens[HALL_OF_FAME] = ('CvHallOfFameScreen', 'CvHallOfFameScreen', (HALL_OF_FAME,))
    _deferred_screens[DAN_QUAYLE_SCREEN] = ('CvDanQuayle', 'CvDanQuayle', ())
    _deferred_screens[SPACE_SHIP_SCREEN] = ('CvSpaceShipScreen', 'CvSpaceShipScreen', ())
    _deferred_screens[PEDIA] = ('Pedia', 'Pedia', (PEDIA,))


# Worldbuilder deferred screens
def _setup_worldbuilder_screens():
    """Setup worldbuilder screens for lazy loading"""
    if worldBuilderScreen is not None:
        wb = worldBuilderScreen
        # Only load these when worldbuilder is active
        _deferred_screens[WB_PLOT] = ('WBPlotScreen', 'WBPlotScreen', (wb,))
        _deferred_screens[WB_EVENT] = ('WBEventScreen', 'WBEventScreen', (wb,))
        _deferred_screens[WB_BUILDING] = ('WBBuildingScreen', 'WBBuildingScreen', (wb,))
        _deferred_screens[WB_CITYDATA] = ('WBCityDataScreen', 'WBCityDataScreen', (wb,))
        _deferred_screens[WB_CITYEDIT] = ('WBCityEditScreen', 'WBCityEditScreen', (wb,))
        _deferred_screens[WB_PROJECT] = ('WBProjectScreen', 'WBProjectScreen', (wb,))
        _deferred_screens[WB_TEAM] = ('WBTeamScreen', 'WBTeamScreen', (wb,))
        _deferred_screens[WB_PLAYER] = ('WBPlayerScreen', 'WBPlayerScreen', (wb,))
        _deferred_screens[WB_PROMOTION] = ('WBPromotionScreen', 'WBPromotionScreen', (wb,))
        _deferred_screens[WB_DIPLOMACY] = ('WBDiplomacyScreen', 'WBDiplomacyScreen', (wb,))
        _deferred_screens[WB_UNITLIST] = ('WBPlayerUnits', 'WBPlayerUnits', (wb,))
        _deferred_screens[WB_RELIGION] = ('WBReligionScreen', 'WBReligionScreen', (wb,))
        _deferred_screens[WB_CORPORATION] = ('WBCorporationScreen', 'WBCorporationScreen', (wb,))
        _deferred_screens[WB_INFO] = ('WBInfoScreen', 'WBInfoScreen', (wb,))
        _deferred_screens[WB_TRADE] = ('WBTradeScreen', 'WBTradeScreen', (wb,))


def lateInit():
    """Initialize deferred screens and civic data"""
    _setup_deferred_screens()

    # Initialize CivicData
    import CivicData
    CivicData.initCivicData()

    # Create revolution advisor at init
    createRevolutionWatchAdvisor()


def earlyInit():
    """Early initialization - setup deferred screens only"""
    _setup_deferred_screens()


# Initialize on module load
earlyInit()