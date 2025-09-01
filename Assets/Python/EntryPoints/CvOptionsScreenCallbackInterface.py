"""
OPTIONS SCREEN CALLBACK INTERFACE - Memory Optimized Version
Optimized for 32-bit Python 2.4 environment with reduced memory footprint
"""
from CvPythonExtensions import *

# Single global references to reduce memory
UsrPrfl = CyUserProfile()
g_iResChange = 0
_screen = None  # Cached screen reference
_tab = None     # Cached tab control

def saveProfile():
	if UsrPrfl.getProfileName():  # More efficient than != ""
		UsrPrfl.writeToFile(UsrPrfl.getProfileName())

def getOptionsScreen():
	# Cache screen reference to avoid repeated imports
	global _screen
	if _screen is None:
		import CvScreensInterface
		_screen = CvScreensInterface.optionsScreen
	return _screen

def getTabControl():
	# Cache tab control to reduce repeated calls
	global _tab
	if _tab is None:
		_tab = getOptionsScreen().getTabControl()
	return _tab

def refresh():
	getOptionsScreen().refreshScreen()
	global g_iResChange
	if g_iResChange:
		# Lazy import - only when needed
		import ScreenResolution as SR
		szRes = UsrPrfl.getResolutionString(UsrPrfl.getResolution())
		# More efficient split
		iX = szRes.find(" x ")
		SR.x = int(szRes[:iX])
		SR.y = int(szRes[iX+3:])
		SR.calibrate()

		# Lazy import for event manager
		import CvEventInterface
		CvEventInterface.getEventManager().fireEvent("ResolutionChanged", g_iResChange - 100)
		g_iResChange = 0

def restartPopup(bForceShowing=False):
	if CyInterface().isInMainMenu() and not bForceShowing:
		return
	popup = CyPopup(-1, EventContextTypes.NO_EVENTCONTEXT, True)
	popup.setBodyString(CyTranslator().getText("TXT_KEY_OPTIONS_NEED_TO_RESTART", ()), 1<<0)
	popup.launch(True, PopupStates.POPUPSTATE_IMMEDIATE)

# Empty callback - no operation needed
def DummyCallback(argsList): pass

######################### GAME OPTIONS #########################

def handleGameOptionsClicked(argsList):
	bValue, szName = argsList
	# Direct extraction without intermediate variable
	CyMessageControl().sendPlayerOption(int(szName[szName.find("_")+1:]), bValue)
	return 1

def handleLanguagesDropdownBoxInput(argsList):
	iValue = argsList[0]
	CyGame().setCurrentLanguage(iValue)

	popup = CyPopup(-1, EventContextTypes.NO_EVENTCONTEXT, True)
	popup.setBodyString(CyTranslator().getText("TXT_KEY_FEAT_ACCOMPLISHED_OK", ()), 1<<0)
	popup.launch(True, PopupStates.POPUPSTATE_IMMEDIATE)

	# Lazy import
	import CvEventInterface
	CvEventInterface.getEventManager().fireEvent("LanguageChanged", iValue)
	return 1

def handleGameReset(argsList):
	UsrPrfl.resetOptions(TabGroupTypes.TABGROUP_GAME)
	refresh()
	saveProfile()
	return 1

######################### GRAPHIC OPTIONS #########################

# Cache for restart-required options
_RESTART_OPTIONS = frozenset([
	GraphicOptionTypes.GRAPHICOPTION_SINGLE_UNIT_GRAPHICS,
	GraphicOptionTypes.GRAPHICOPTION_FULLSCREEN
])

def handleGraphicOptionsClicked(argsList):
	bValue, szName = argsList
	iGraphicOption = int(szName[szName.find("_")+1:])
	UsrPrfl.setGraphicOption(iGraphicOption, bValue)

	# Use set membership for efficiency
	if iGraphicOption in _RESTART_OPTIONS:
		restartPopup(True)
	elif iGraphicOption == GraphicOptionTypes.GRAPHICOPTION_HIRES_TERRAIN:
		restartPopup(False)
	return 1

def handleGraphicsLevelDropdownBoxInput(argsList):
	UsrPrfl.setGraphicsLevel(argsList[0])
	refresh()
	restartPopup(True)
	return 1

def handleRenderQualityDropdownBoxInput(argsList):
	UsrPrfl.setRenderQualityLevel(argsList[0])
	return 1

def handleGlobeViewDropdownBoxInput(argsList):
	UsrPrfl.setGlobeViewRenderLevel(argsList[0])
	return 1

def handleMovieDropdownBoxInput(argsList):
	UsrPrfl.setMovieQualityLevel(argsList[0])
	return 1

def handleMainMenuDropdownBoxInput(argsList):
	UsrPrfl.setMainMenu(argsList[0])
	refresh()
	saveProfile()
	return 1

def handleResolutionDropdownInput(argsList):
	iValue = argsList[0]
	UsrPrfl.setResolution(iValue)
	global g_iResChange
	g_iResChange = iValue + 100
	return 1

def handleAntiAliasingDropdownInput(argsList):
	UsrPrfl.setAntiAliasing(argsList[0])
	return 1

def handleGraphicsReset(argsList):
	UsrPrfl.resetOptions(TabGroupTypes.TABGROUP_GRAPHICS)
	refresh()
	restartPopup()
	saveProfile()
	return 1

######################### AUDIO OPTIONS #########################

# Volume handler mappings - more efficient than if-elif chains
_VOLUME_SETTERS = (
	UsrPrfl.setMasterVolume,
	UsrPrfl.setMusicVolume,
	UsrPrfl.setSoundEffectsVolume,
	UsrPrfl.setSpeechVolume,
	UsrPrfl.setAmbienceVolume,
	UsrPrfl.setInterfaceVolume
)

_NOSOUND_SETTERS = (
	UsrPrfl.setMasterNoSound,
	UsrPrfl.setMusicNoSound,
	UsrPrfl.setSoundEffectsNoSound,
	UsrPrfl.setSpeechNoSound,
	UsrPrfl.setAmbienceNoSound,
	UsrPrfl.setInterfaceNoSound
)

def handleVolumeSlidersInput(argsList):
	iValue, szName = argsList
	iVolumeType = int(szName[szName.find("_")+1:])

	# Direct function call from tuple - no if-elif chain
	if iVolumeType < len(_VOLUME_SETTERS):
		iMax = UsrPrfl.getVolumeStops()
		_VOLUME_SETTERS[iVolumeType](iMax - iValue)
	return 1

def handleVolumeCheckboxesInput(argsList):
	bValue, szName = argsList
	iVolumeType = int(szName[szName.find("_")+1:])

	# Direct function call from tuple
	if iVolumeType < len(_NOSOUND_SETTERS):
		_NOSOUND_SETTERS[iVolumeType](bValue)
	return 1

def handleCustomMusicPathCheckboxInput(argsList):
	if argsList[0]:
		UsrPrfl.setMusicPath(getOptionsScreen().getMusicPath().encode('latin_1'))
	else:
		UsrPrfl.setMusicPath("")
	return 1

def handleCustomMusicPathButtonInput(argsList):
	UsrPrfl.musicPathDialogBox()
	return 1

def handleSpeakerConfigDropdownInput(argsList):
	szSpeakerConfigName = UsrPrfl.getSpeakerConfigFromList(argsList[0])
	UsrPrfl.setSpeakerConfig(szSpeakerConfigName)
	restartPopup(True)
	return 1

def handleVoiceCheckboxInput(argsList):
	UsrPrfl.setUseVoice(argsList[0])
	return 1

def handleCaptureDeviceDropdownInput(argsList):
	UsrPrfl.setCaptureDevice(argsList[0])
	return 1

def handleCaptureVolumeSliderInput(argsList):
	UsrPrfl.setCaptureVolume(argsList[0])
	return 1

def handlePlaybackDeviceDropdownInput(argsList):
	UsrPrfl.setPlaybackDevice(argsList[0])
	return 1

def handlePlaybackVolumeSliderInput(argsList):
	UsrPrfl.setPlaybackVolume(argsList[0])
	return 1

def handleAudioReset(argsList):
	UsrPrfl.resetOptions(TabGroupTypes.TABGROUP_AUDIO)
	refresh()
	restartPopup(True)
	saveProfile()
	return 1

######################### NETWORK OPTIONS #########################

def handleBroadbandSelected(argsList):
	if argsList[0]:
		CyGame().setModem(False)
	return 1

def handleModemSelected(argsList):
	if argsList[0]:
		CyGame().setModem(True)
	return 1

######################### CLOCK OPTIONS #########################

def handleClockOnCheckboxInput(argsList):
	UsrPrfl.setClockOn(argsList[0])
	return 1

def handle24HourClockCheckboxInput(argsList):
	UsrPrfl.set24Hours(argsList[0])
	return 1

def handleAlarmOnCheckboxInput(argsList):
	if not argsList[0]:
		return 1

	screen = getOptionsScreen()
	hour = screen.getAlarmHour()
	min = screen.getAlarmMin()

	# Optimized validation
	if hour and min and (hour + min).isdigit():
		hour = int(hour)
		min = int(min)
		if hour or min:  # Simplified condition
			toggleAlarm(True, hour, min)
	return 1

def handleOtherReset(argsList):
	UsrPrfl.resetOptions(TabGroupTypes.TABGROUP_CLOCK)
	refresh()
	saveProfile()
	return 1

######################### PROFILES #########################

def handleProfilesDropdownInput(argsList):
	saveProfile()
	szFilename = UsrPrfl.getProfileFileName(argsList[0])
	# More efficient string extraction
	iStart = szFilename.find("PROFILES\\") + 9
	szProfile = szFilename[iStart:-4]
	return loadProfile(szProfile)

def handleNewProfileButtonInput(argsList):
	szNewProfileName = getOptionsScreen().getProfileEditCtrlText()
	szNarrow = szNewProfileName.encode("latin_1")
	UsrPrfl.setProfileName(szNarrow)
	UsrPrfl.writeToFile(szNarrow)
	UsrPrfl.loadProfileFileNames()
	saveProfile()
	refresh()

	popup = CyPopup(-1, EventContextTypes.NO_EVENTCONTEXT, True)
	popup.setBodyString(CyTranslator().getText("TXT_KEY_OPTIONS_SAVED_PROFILE", (szNewProfileName,)), 1<<0)
	popup.launch(True, PopupStates.POPUPSTATE_IMMEDIATE)
	return 1

def handleDeleteProfileButtonInput(argsList):
	szProfileName = getOptionsScreen().getProfileEditCtrlText().encode('latin_1')

	if not UsrPrfl.deleteProfileFile(szProfileName):
		return 0

	UsrPrfl.loadProfileFileNames()

	popup = CyPopup(-1, EventContextTypes.NO_EVENTCONTEXT, True)
	popup.setBodyString(CyTranslator().getText("TXT_KEY_OPTIONS_DELETED_PROFILE", (szProfileName,)), 1<<0)
	popup.launch(True, PopupStates.POPUPSTATE_IMMEDIATE)

	bSuccess = True
	if szProfileName == UsrPrfl.getProfileName():
		UsrPrfl.setProfileName("")
		szFilename = UsrPrfl.getProfileFileName(0)
		iStart = szFilename.find("PROFILES\\") + 9
		szProfile = szFilename[iStart:-4]
		bSuccess = loadProfile(szProfile)

	refresh()
	return bSuccess

def loadProfile(szProfile):
	if not UsrPrfl.readFromFile(szProfile):
		popup = CyPopup(-1, EventContextTypes.NO_EVENTCONTEXT, True)
		popup.setBodyString(CyTranslator().getText("TXT_KEY_OPTIONS_LOAD_PROFILE_FAIL", ()), 1<<0)
		popup.launch(True, PopupStates.POPUPSTATE_IMMEDIATE)
		return 0

	UsrPrfl.recalculateAudioSettings()
	getOptionsScreen().setProfileEditCtrlText(szProfile)

	# Batch operations to reduce function call overhead
	# Game Options
	for i in xrange(PlayerOptionTypes.NUM_PLAYEROPTION_TYPES):
		CyMessageControl().sendPlayerOption(i, UsrPrfl.getPlayerOption(i))

	# Graphics Options
	for i in xrange(GraphicOptionTypes.NUM_GRAPHICOPTION_TYPES):
		bVal = UsrPrfl.getGraphicOption(i)
		UsrPrfl.setGraphicOption(i, bVal)

	# Set remaining options
	UsrPrfl.setAntiAliasing(UsrPrfl.getAntiAliasing())
	UsrPrfl.setResolution(UsrPrfl.getResolution())
	UsrPrfl.setSpeakerConfig(UsrPrfl.getSpeakerConfig())
	UsrPrfl.setMusicPath(UsrPrfl.getMusicPath())
	UsrPrfl.setUseVoice(UsrPrfl.useVoice())
	UsrPrfl.setCaptureDevice(UsrPrfl.getCaptureDeviceIndex())
	UsrPrfl.setPlaybackDevice(UsrPrfl.getPlaybackDeviceIndex())
	UsrPrfl.setCaptureVolume(UsrPrfl.getCaptureVolume())
	UsrPrfl.setPlaybackVolume(UsrPrfl.getPlaybackVolume())
	UsrPrfl.setClockOn(UsrPrfl.isClockOn())

	popup = CyPopup(-1, EventContextTypes.NO_EVENTCONTEXT, True)
	popup.setBodyString(CyTranslator().getText("TXT_KEY_OPTIONS_LOADED_PROFILE", (szProfile,)), 1<<0)
	popup.launch(True, PopupStates.POPUPSTATE_IMMEDIATE)

	refresh()
	return 1

def handleExitButtonInput(argsList):
	saveProfile()
	global _tab, _screen
	if _tab:
		_tab.destroy()
		_tab = None
	_screen = None
	return 1

################
# AND Options  #
################

def handleAutomatedBuildCheckboxClicked(argsList):
	bValue, szName = argsList

	# Lazy imports
	GC = CyGlobalContext()
	iPlayer = CyGame().getActivePlayer()
	CyPlayer = GC.getPlayer(iPlayer)

	# Cache TextUtil import
	import TextUtil

	# Cache build info count
	iNumBuildInfos = GC.getNumBuildInfos()

	# Use generator to avoid creating full list
	for CyCity in CyPlayer.cities():
		cityName = TextUtil.convertToAscii(CyCity.getName())
		if szName.rfind(cityName) == -1:
			continue

		iCityID = CyCity.getID()
		# Check builds for this city
		for k in xrange(iNumBuildInfos):
			if szName.rfind(GC.getBuildInfo(k).getDescription()) > -1:
				# Lazy import
				import AutomatedSettings
				CyMessageControl().sendModNetMessage(
					AutomatedSettings.getCanAutoBuildEventID(),
					iPlayer, iCityID, k, int(bValue)
				)
				return 1
	return 0

def handleNationalAutomatedBuildCheckboxClicked(argsList):
	bValue, szName = argsList

	iPlayer = CyGame().getActivePlayer()
	GC = CyGlobalContext()

	# Direct iteration without intermediate variables
	for i in xrange(GC.getNumBuildInfos()):
		if szName.rfind(GC.getBuildInfo(i).getDescription()) > -1:
			# Lazy import
			import AutomatedSettings
			CyMessageControl().sendModNetMessage(
				AutomatedSettings.getCanPlayerAutoBuildEventID(),
				iPlayer, -1, i, int(bValue)
			)
			return 1
	return 0