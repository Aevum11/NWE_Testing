## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## Memory-optimized version for 32-bit Caveman2Cosmos mod

# Class to decipher and make screen input easy to read...
class ScreenInput:
    # __slots__ eliminates __dict__ overhead, saving ~100-200 bytes per instance
    # Critical optimization for 32-bit memory constraints in games
    __slots__ = (
        'eNotifyCode', 'iData', 'uiFlags', 'iItemID', 'ePythonFileEnum',
        'szFunctionName', 'bShift', 'bCtrl', 'bAlt', 'iMouseX', 'iMouseY',
        'iButtonType', 'iData1', 'iData2', 'bOption'
    )

    # Init call - optimized for memory efficiency
    def __init__(self, argsList):
        # Efficient length validation
        args_len = len(argsList)
        if args_len < 15:
            raise ValueError("argsList must contain at least 15 elements")

        # Direct tuple unpacking is more memory-efficient than individual assignments
        # Reduces temporary variable creation and assignment overhead
        (self.eNotifyCode, self.iData, self.uiFlags, self.iItemID,
         self.ePythonFileEnum, self.szFunctionName, self.bShift, self.bCtrl,
         self.bAlt, self.iMouseX, self.iMouseY, self.iButtonType,
         self.iData1, self.iData2, self.bOption) = argsList[:15]

    # NotifyCode
    def getNotifyCode(self):
        return self.eNotifyCode

    # Data
    def getData(self):
        return self.iData

    # Flags
    def getFlags(self):
        return self.uiFlags

    # Item ID
    def getID(self):
        return self.iItemID

    # Python File
    def getPythonFile(self):
        return self.ePythonFileEnum

    # Function Name...
    def getFunctionName(self):
        return self.szFunctionName

    # Shift Key Down
    def isShiftKeyDown(self):
        return self.bShift

    # Ctrl Key Down
    def isCtrlKeyDown(self):
        return self.bCtrl

    # Alt Key Down
    def isAltKeyDown(self):
        return self.bAlt

    # X location of the mouse cursor
    def getMouseX(self):
        return self.iMouseX

    # Y location of the mouse cursor
    def getMouseY(self):
        return self.iMouseY

    # WidgetType
    def getButtonType(self):
        return self.iButtonType

    # Widget Data 1
    def getData1(self):
        return self.iData1

    # Widget Data 2
    def getData2(self):
        return self.iData2

    # Widget Option
    def getOption(self):
        return self.bOption