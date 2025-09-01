##-------------------------------------------------------------------
## Modified from reminder by eotinb
## by Ruff and EF
##-------------------------------------------------------------------
## Reorganized to work via CvCustomEventManager
## using Civ4lerts as template.
## CvCustomEventManager & Civ4lerts by Gillmer J. Derge
##-------------------------------------------------------------------
## EF: Turned into a real queue, can be disabled
##-------------------------------------------------------------------
## Memory Optimized Version - Python 2.4 Compatible
##-------------------------------------------------------------------

from CvPythonExtensions import *
import CvUtil
import SdToolKit
import ScreenResolution as SR
import gc  # For explicit garbage collection control

STORE_EVENT_ID = CvUtil.getNewEventID()
RECALL_EVENT_ID = CvUtil.getNewEventID()

GC = CyGlobalContext()
GAME = GC.getGame()
TRNSLTR = CyTranslator()

g_reminders = None

# Used to display flashing end-of-turn text - optimized with list for building
g_turnReminderTextsList = []

# Used to receive network messages
g_hasNetMessage = hasattr(CyPlayer, "addReminder")


def hasNetMessage():
    return g_hasNetMessage


def netAddReminder(args):
    playerID, turn, message = args
    g_reminders.push(playerID, Reminder(turn, message))
    del args  # Explicit cleanup


# Shortcut - Create Reminder
def createReminder(argsList):
    g_eventMgr.beginEvent(STORE_EVENT_ID)


class ReminderEventManager:
    __slots__ = ('reminders', 'recall')  # Memory optimization using __slots__

    def __init__(self, eventManager):
        global g_eventMgr, g_autolog, ReminderOpt
        g_eventMgr = eventManager
        import autolog
        g_autolog = autolog.autologInstance()
        import BugCore
        ReminderOpt = BugCore.game.Reminder
        # expose to DLL
        import CvAppInterface
        CvAppInterface.netAddReminder = netAddReminder

        self.setReminders(Reminders())
        self.recall = []

        # Use tuples for event handler data (immutable, less memory)
        handlers = (
            ("BeginActivePlayerTurn", self.onBeginActivePlayerTurn),
            ("GameStart", self.onGameStart),
            ("OnLoad", self.onLoadGame),
            ("PythonReloaded", self.onLoadGame),
            ("OnPreSave", self.onPreSave),
            ("SwitchHotSeatPlayer", self.onSwitchHotSeatPlayer)
        )

        for event, handler in handlers:
            eventManager.addEventHandler(event, handler)

        eventManager.setPopupHandlers(STORE_EVENT_ID, 'Reminder.Store',
                                      self.__eventReminderStoreBegin, self.__eventReminderStoreApply)
        eventManager.setPopupHandlers(RECALL_EVENT_ID, 'Reminder.Recall',
                                      self.__eventReminderRecallBegin, self.__eventReminderRecallApply)

    def __eventReminderStoreBegin(self, argsList):
        # Pre-calculate values to avoid redundant calculations
        x = SR.x
        if x > 2500:
            w, h = 520, 232
        elif x > 1700:
            w, h = 480, 224
        elif x > 1400:
            w, h = 440, 216
        else:
            w, h = 400, 210

        # Build strings once
        prompt_parts = [
            SR.aFontList[2],
            TRNSLTR.getText("TXT_KEY_REMINDER_HEADER", ()),
            "\n",
            SR.aFontList[5],
            TRNSLTR.getText("TXT_KEY_REMINDER_PROMPT", ())
        ]
        prompt = "".join(prompt_parts)
        del prompt_parts  # Clean up temporary list

        ok = TRNSLTR.getText("TXT_KEY_MAIN_MENU_OK", ())
        cancel = TRNSLTR.getText("TXT_KEY_POPUP_CANCEL", ())

        popup = CyPopup(STORE_EVENT_ID, EventContextTypes.EVENTCONTEXT_SELF, True)
        popup.setSize(w, h)
        popup.setPosition(x / 2 - w / 2, SR.y / 2 - h / 2)
        popup.setBodyString(prompt, 1 << 0)
        popup.createSpinBox(0, "", 0, 1, 999, 0)
        popup.createEditBox("", 1)
        popup.addButton(ok)
        popup.addButton(cancel)
        popup.launch(False, PopupStates.POPUPSTATE_IMMEDIATE)

    def __eventReminderStoreApply(self, playerID, userData, popupReturn):
        if popupReturn.getButtonClicked() != 1:
            reminderText = popupReturn.getEditBoxString(1)
            if reminderText:
                global g_turnReminderTextsList

                # Build end turn text efficiently using list
                if g_turnReminderTextsList:
                    # Get last line for width calculation
                    last_parts = []
                    for text in g_turnReminderTextsList:
                        if "\n" in text:
                            idx = text.rfind("\n")
                            last_parts.append(text[idx + 1:])
                        else:
                            last_parts.append(text)

                    last_line = "".join(last_parts)
                    width_limit = SR.x - SR.x / 7

                    if CyInterface().determineWidth(last_line + reminderText) > width_limit:
                        g_turnReminderTextsList.append("\n")
                    else:
                        g_turnReminderTextsList.append("; ")
                    del last_parts, last_line  # Clean up

                g_turnReminderTextsList.append(reminderText)

                turns = popupReturn.getSpinnerWidgetValue(0)
                reminderTurn = turns + GAME.getGameTurn()
                self.addReminder(playerID, Reminder(reminderTurn, reminderText))

                if g_autolog.isLogging() and ReminderOpt.isAutolog():
                    g_autolog.writeLog("Reminder: On Turn %d, %s" % (reminderTurn, reminderText))

    def __eventReminderRecallBegin(self, argsList):
        global g_turnReminderTextsList
        iPlayer = GAME.getActivePlayer()
        queue = self.reminders.get(iPlayer)
        if queue:
            iTurn = GAME.getGameTurn()
            yes = TRNSLTR.getText("TXT_KEY_POPUP_YES", ())
            no = TRNSLTR.getText("TXT_KEY_POPUP_NO", ())
            bLogging = g_autolog.isLogging() and ReminderOpt.isAutolog()
            bShowMsg = ReminderOpt.isShowMessage()
            bShowPop = ReminderOpt.isShowPopup()

            if bShowPop:
                iCount = 0
                prompt = TRNSLTR.getText("TXT_KEY_REMIND_NEXT_TURN_PROMPT", ())

            while not queue.isEmpty():
                nextTurn = queue.nextTurn()
                if nextTurn > iTurn:
                    break
                reminder = queue.pop()

                if nextTurn < iTurn:
                    print
                    "[WARNING] Reminder - skipped turn %d: %s" % (reminder.turn, reminder.message)
                    continue

                if bLogging:
                    g_autolog.writeLog("Reminder: %s" % reminder.message)

                # Build reminder text efficiently
                if g_turnReminderTextsList:
                    # Get last line for width calculation
                    temp_text = "".join(g_turnReminderTextsList)
                    idx = temp_text.rfind("\n")
                    if idx == -1:
                        last_line = temp_text
                    else:
                        last_line = temp_text[idx + 1:]

                    width_limit = SR.x - SR.x / 7
                    if CyInterface().determineWidth(last_line + reminder.message) > width_limit:
                        g_turnReminderTextsList.append("\n")
                    else:
                        g_turnReminderTextsList.append("; ")
                    del temp_text, last_line  # Clean up

                g_turnReminderTextsList.append(reminder.message)

                if bShowMsg:
                    CvUtil.sendMessage(reminder.message, iPlayer, 10, "", ColorTypes(8))

                if bShowPop:
                    body_parts = [
                        SR.aFontList[4],
                        reminder.message,
                        "\n",
                        SR.aFontList[5],
                        prompt
                    ]
                    body = "".join(body_parts)
                    del body_parts  # Clean up

                    popup = CyPopup(RECALL_EVENT_ID, EventContextTypes.EVENTCONTEXT_SELF, True)
                    self.recall.append(reminder)
                    popup.setUserData((iCount,))
                    iCount += 1
                    popup.setPosition(SR.x / 3, SR.y / 3)
                    popup.setBodyString(body, 1 << 0)
                    popup.addButton(yes)
                    popup.addButton(no)
                    popup.launch(False, PopupStates.POPUPSTATE_IMMEDIATE)

    def __eventReminderRecallApply(self, playerID, userData, popupReturn):
        if popupReturn.getButtonClicked() != 1:
            reminder = self.recall[userData[0]]
            reminder.turn += 1
            self.addReminder(playerID, reminder)

        # Clean up recall list periodically
        if len(self.recall) > 100:
            # Keep only last 50 items to prevent unbounded growth
            self.recall = self.recall[-50:]
            gc.collect()  # Force garbage collection

    def setReminders(self, queues):
        self.reminders = queues
        global g_reminders
        g_reminders = queues

    def clearReminders(self):
        self.reminders.clear()
        global g_turnReminderTextsList
        del g_turnReminderTextsList[:]  # Clear list in place

    def addReminder(self, playerID, reminder):
        if hasNetMessage():
            player = GC.getPlayer(playerID)
            player.addReminder(reminder.turn, reminder.message)
        else:
            self.reminders.push(playerID, reminder)

    def onSwitchHotSeatPlayer(self, argsList):
        # Clears the end turn text so hot seat players don't see each other's reminders
        global g_turnReminderTextsList
        del g_turnReminderTextsList[:]  # Clear list in place

    def onBeginActivePlayerTurn(self, argsList):
        global g_turnReminderTextsList
        # Convert list to string for display
        if g_turnReminderTextsList:
            g_turnReminderTexts = "".join(g_turnReminderTextsList)
            # Set the global string variable for compatibility
            import __builtin__
            __builtin__.__dict__['g_turnReminderTexts'] = g_turnReminderTexts
            del g_turnReminderTextsList[:]  # Clear after use

        if ReminderOpt.isEnabled():
            g_eventMgr.beginEvent(RECALL_EVENT_ID)

    def onGameStart(self, argsList):
        self.clearReminders()

    def onLoadGame(self, argsList):
        self.clearReminders()
        queues = SdToolKit.sdGetGlobal("Reminders", "queues")
        if queues:
            self.setReminders(queues)
        else:
            # Ensure clean state
            gc.collect()

    def onPreSave(self, argsList):
        if self.reminders.isEmpty():
            SdToolKit.sdDelGlobal("Reminders", "queues")
        else:
            SdToolKit.sdSetGlobal("Reminders", "queues", self.reminders)


class Reminder(object):
    __slots__ = ('turn', 'message')  # Memory optimization

    def __init__(self, turn, message):
        self.turn = turn
        self.message = message


class ReminderQueue(object):
    __slots__ = ('queue',)  # Memory optimization

    def __init__(self):
        self.clear()

    def clear(self):
        self.queue = []

    def clearBefore(self, turn, log=False):
        while not self.isEmpty() and self.nextTurn() < turn:
            reminder = self.pop()
            if log:
                print
                "Reminder - skipped turn %d: %s" % (reminder.turn, reminder.message)
            del reminder  # Explicit cleanup

    def size(self):
        return len(self.queue)

    def isEmpty(self):
        return self.size() == 0

    def nextTurn(self):
        if not self.size():
            return -1
        return self.queue[0].turn

    def push(self, reminder):
        # Optimized insertion using binary search for better performance
        # with large queues
        queue = self.queue
        low, high = 0, len(queue)
        turn = reminder.turn

        while low < high:
            mid = (low + high) // 2
            if queue[mid].turn < turn:
                low = mid + 1
            else:
                high = mid

        queue.insert(low, reminder)

    def pop(self):
        if self.isEmpty():
            return None
        else:
            return self.queue.pop(0)


class Reminders(object):
    __slots__ = ('queues',)  # Memory optimization

    def __init__(self, queue=None):
        self.clear()
        if queue:
            self.queues[GAME.getActivePlayer()] = queue

    def clear(self):
        self.queues = {}
        gc.collect()  # Force garbage collection after clearing

    def clearBefore(self, turn, log=False):
        for queue in self.queues.itervalues():
            queue.clearBefore(turn, log)

    def exists(self, playerID):
        return playerID in self.queues

    def get(self, playerID):
        if self.exists(playerID):
            return self.queues[playerID]
        return None  # Explicit None return

    def getForUpdate(self, playerID):
        if self.exists(playerID):
            return self.queues[playerID]
        else:
            queue = ReminderQueue()
            self.queues[playerID] = queue
            return queue

    def size(self, playerID=None):
        if playerID is not None:  # Explicit None check
            queue = self.get(playerID)
            if queue:
                return queue.size()
            return 0
        else:
            return len(self.queues)

    def isEmpty(self, playerID=None):
        return self.size(playerID) == 0

    def nextTurn(self, playerID):
        queue = self.get(playerID)
        if queue:
            return queue.nextTurn()
        return -1

    def push(self, playerID, reminder):
        self.getForUpdate(playerID).push(reminder)

    def pop(self, playerID):
        queue = self.get(playerID)
        if queue:
            result = queue.pop()
            # Clean up empty queues to save memory
            if queue.isEmpty():
                del self.queues[playerID]
            return result
        return None