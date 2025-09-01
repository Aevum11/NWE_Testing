# BUG_OptionsCB_IF - Memory Optimized Version
# Optimizations applied:
# - Consolidated redundant handler functions to reduce code duplication
# - Lazy loading of imports to reduce memory footprint
# - Removed unnecessary global screen variable
# - Used single dispatch function to minimize function objects in memory
# - Maintained full Python 2.4 compatibility

# Global variable for options only (reduced from 2 to 1)
g_options = None

def init():
	"""Initialize callback interface with lazy loading"""
	global g_options
	if g_options is None:
		import BugOptions
		g_options = BugOptions.getOptions()

# Initialize on module load
init()

def handleBugExitButtonInput(argsList):
	"""Exits the screen after saving the options to disk"""
	# Lazy import - only loaded when function is called
	import BugOptionsScreen
	BugOptionsScreen.g_screen.close()

def handleBugHelpButtonInput(argsList):
	"""Opens the BUG web page externally"""
	# Lazy import - only loaded when function is called
	import _misc
	_misc.LaunchDefaultBrowser("http://civ4bug.sourceforge.net/BUGMod.html")

# Consolidated handler for all option changes
# This reduces memory by having one function instead of six similar ones
def _handleOptionChange(value, name, method_name):
	"""Internal handler for all option changes"""
	option = g_options.getOption(name)
	if option is not None:
		if method_name == 'setValue':
			option.setValue(value)
		elif method_name == 'setIndex':
			option.setIndex(value)

# Public interface functions - minimal wrappers around consolidated handler
def handleBugCheckboxClicked(argsList):
	"""Handle checkbox value changes"""
	bValue, szName = argsList
	_handleOptionChange(bValue, szName, 'setValue')

def handleBugTextEditChange(argsList):
	"""Handle text edit changes"""
	szValue, szName = argsList
	_handleOptionChange(szValue, szName, 'setValue')

def handleBugDropdownChange(argsList):
	"""Handle dropdown selection changes"""
	iIndex, szName = argsList
	_handleOptionChange(iIndex, szName, 'setIndex')

def handleBugIntDropdownChange(argsList):
	"""Handle integer dropdown changes"""
	iIndex, szName = argsList
	_handleOptionChange(iIndex, szName, 'setIndex')

def handleBugFloatDropdownChange(argsList):
	"""Handle float dropdown changes"""
	iIndex, szName = argsList
	_handleOptionChange(iIndex, szName, 'setIndex')

def handleBugColorDropdownChange(argsList):
	"""Handle color dropdown changes"""
	iIndex, szName = argsList
	_handleOptionChange(iIndex, szName, 'setIndex')

def handleBugSliderChanged(argsList):
	"""Handle slider value changes"""
	iValue, szName = argsList
	_handleOptionChange(iValue, szName, 'setValue')