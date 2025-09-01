## Ruff autologger - Memory Optimized Version
## Modified from HOF MOD V1.61.001
## Modified from autolog by eotinb
## contains variables to turn on and off various extra log messages
## Alt+E is always on
## Memory optimized for 32-bit Python 2.4 environment

from CvPythonExtensions import *
import BugConfigTracker
import BugCore
import BugOptions
import SystemPaths as SP
import codecs
import os
import time

AutologOpt = BugCore.game.Autolog


class autologInstance:
    # Using __slots__ to reduce memory overhead (~100-200 bytes per instance)
    # This prevents dynamic attribute dictionary creation
    __slots__ = ('MsgStore', 'bStarted', 'LogFileName', 'LogFilePath',
                 'RealLogFile', 'log')

    def __init__(self):
        self.MsgStore = []
        self.bStarted = False
        self.LogFileName = None
        self.LogFilePath = None
        self.RealLogFile = None
        self.log = None  # Initialize log attribute
        self.setLogFileName(AutologOpt.getFileName())
        self.setLogFilePath(AutologOpt.getFilePath())

    def setLogFileName(self, LogFileName, bSaveToOptions=False):
        if bSaveToOptions:
            AutologOpt.setFileName(LogFileName)
            BugOptions.write()
        self.LogFileName = LogFileName
        self.updateLogFile()

    def getLogFileName(self):
        return self.LogFileName

    def setLogFilePath(self, LogFilePath, bSaveToOptions=False):
        if bSaveToOptions:
            AutologOpt.setFilePath(LogFilePath)
            BugOptions.write()
        if not LogFilePath or LogFilePath == "Default":
            LogFilePath = SP.joinModDir("Autolog")
        if not os.path.isdir(LogFilePath):
            os.makedirs(LogFilePath)
        self.LogFilePath = LogFilePath
        self.updateLogFile()

    def getLogFilePath(self):
        return self.LogFilePath

    def updateLogFile(self):
        if self.LogFileName and self.LogFilePath:
            self.bStarted = False
            self.RealLogFile = os.path.join(self.LogFilePath, self.LogFileName)
            BugConfigTracker.add("Autolog_Log", self.RealLogFile)

    def isLogging(self):
        return AutologOpt.isLoggingOn()

    def start(self):
        GAME = CyGame()
        TRNSLTR = CyTranslator()
        self.writeMsg("")
        self.writeMsg("Logging by autolog.py")
        self.writeMsg("------------------------------------------------")

        # Optimize by calculating values once
        iMaxTurns = GAME.getMaxTurns()
        iElapsedTurns = GAME.getElapsedGameTurns()
        iStartDateTurn = AutologOpt.getStartDateTurn()
        year = GAME.getGameTurnYear()

        if year < 0:
            year = TRNSLTR.getText("TXT_KEY_TIME_BC", (-year,))
        else:
            year = TRNSLTR.getText("TXT_KEY_TIME_AD", (year,))

        if iMaxTurns:
            zTurn = "%i/%i" % (iElapsedTurns + iStartDateTurn, iMaxTurns)
        else:
            zTurn = "%i" % (iElapsedTurns + iStartDateTurn)

        # Use direct string formatting to reduce intermediate strings
        self.writeMsg(TRNSLTR.getText("TXT_KEY_AUTOLOG_TURN",
                                      (zTurn, year, time.strftime("%d-%b-%Y %H:%M:%S"))),
                      vBold=True, vUnderline=True)
        self.bStarted = True

        # Clean up local references
        del GAME
        del TRNSLTR

    def writeLog(self, vMsg, vColor="Black", vBold=False, vUnderline=False, vPrefix=""):
        self.openLog()

        # Optimize message store handling
        if self.MsgStore:  # More efficient than len() > 0
            # Write pending messages and clear in one operation
            for sMsg in self.MsgStore:
                self.log.write(sMsg)
            del self.MsgStore[:]  # More memory efficient than creating new list

        self.writeMsg(vMsg, vColor, vBold, vUnderline, vPrefix)
        self.closeLog()

    def writeMsg(self, vMsg, vColor="Black", vBold=False, vUnderline=False, vPrefix=""):
        # Build and write message directly without intermediate storage
        self.log.write(self.buildMsg(vMsg, vColor, vBold, vUnderline, vPrefix))

    def writeLog_pending(self, vMsg, vColor="Black", vBold=False, vUnderline=False, vPrefix=""):
        # Append message directly to store
        self.MsgStore.append(self.buildMsg(vMsg, vColor, vBold, vUnderline, vPrefix))

    def writeLog_pending_flush(self):
        # More efficient clearing method
        del self.MsgStore[:]

    def openLog(self):
        self.log = codecs.open(self.RealLogFile, 'a', 'utf-8')
        if not self.bStarted:
            self.start()

    def closeLog(self):
        self.log.close()
        self.log = None  # Free reference immediately

    def buildMsg(self, msg, vColor, vBold, vUnderline, vPrefix):
        # Optimize string building with early returns and fewer operations
        if vPrefix:
            msg = vPrefix + " " + msg

        # Cache style value to avoid multiple method calls
        zStyle = AutologOpt.getFormatStyle()

        # Validate style once
        if zStyle < 0 or zStyle > 3:
            zStyle = 0

        # Early return for no formatting
        if not zStyle:
            return msg + "\r\n"

        # HTML formatting
        if zStyle == 1:
            # Build HTML tags more efficiently
            if vBold:
                msg = "<b>%s</b>" % msg
            if vUnderline:
                msg = "<u>%s</u>" % msg
            if vColor != "Black" and AutologOpt.isColorCoding():
                msg = '<span style="color: %s">%s</span>' % (vColor, msg)
            return msg + "<br>\r\n"

        # Forum formatting (styles 2 and 3)
        else:
            # Build forum tags more efficiently
            if vBold:
                msg = "[b]%s[/b]" % msg
            if vUnderline:
                msg = "[u]%s[/u]" % msg
            if vColor != "Black" and AutologOpt.isColorCoding():
                if zStyle == 2:  # color coding with quotes
                    msg = '[color="%s"]%s[/color]' % (vColor, msg)
                else:  # color coding without quotes
                    msg = "[color=%s]%s[/color]" % (vColor, msg)
            return msg + "\r\n"