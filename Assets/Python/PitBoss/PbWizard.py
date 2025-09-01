## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# Sample PitBoss window/app framework - Memory Optimized Version
# Mustafa Thamer 2-15-05
# Memory optimizations applied for 32-bit compatibility
#
# Pitboss is not yet adapted for C2C as far as we know
#
from CvPythonExtensions import *
import wx
import wx.wizard
import wx.lib.scrolledpanel
import string
import gc  # Added for memory management
import weakref  # Added for weak references

bPublic = True
bSaved = False
bScenario = False
bPatchConfirmed = False
bPatchOK = False
szPatchName = None
msgBox = None
PB = CyPitboss()
gc = CyGlobalContext()
localText = CyTranslator()
curPage = None

# Force initial garbage collection
import gc as garbage_collector

garbage_collector.collect()


#
# Mod Select Page (first page of wizard)
#
class ModSelectPage(wx.wizard.PyWizardPage):
    __slots__ = ('next', 'prev', 'myParent', 'currentMod', 'rbs')

    def __init__(self, parent):
        wx.wizard.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.myParent = weakref.ref(parent)  # Use weak reference to parent

        pageSizer = wx.BoxSizer(wx.VERTICAL)

        modPanel = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(300, 600), style=wx.SUNKEN_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_CHOOSE_MOD", ()))
        pageSizer.Add(header, 0, wx.ALL, 5)

        # Place the radio buttons
        self.currentMod = 0
        self.rbs = []

        # First choice is no mod
        self.rbs.append(
            wx.RadioButton(modPanel, -1, localText.getText("TXT_KEY_MAIN_MENU_NONE", ()), wx.DefaultPosition,
                           wx.DefaultSize, wx.RB_GROUP))
        sizer.Add(self.rbs[0], 0, wx.ALL, 3)

        modName = PB.getModName()
        if modName == "":
            self.rbs[0].SetValue(True)
        del modName  # Explicitly delete temporary variable

        index = 0
        for index in xrange(PB.getNumMods()):
            modText = PB.getModAt(index)
            self.rbs.append(wx.RadioButton(modPanel, -1, modText, wx.DefaultPosition, wx.DefaultSize))
            sizer.Add(self.rbs[index + 1], 0, wx.ALL, 3)

            if PB.isCurrentMod(index):
                self.currentMod = index + 1
                self.rbs[index + 1].SetValue(True)
            del modText  # Clean up temporary

        modPanel.SetSizer(sizer)
        modPanel.SetAutoLayout(1)
        modPanel.SetupScrolling()

        pageSizer.Add(modPanel, 0, wx.ALL, 5)
        self.SetSizer(pageSizer)

        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.OnPageChanging)

    def enableButtons(self):
        parent = self.myParent()
        if parent:
            parent.FindWindowById(wx.ID_FORWARD).Enable(True)
            parent.FindWindowById(wx.ID_BACKWARD).Enable(False)

    def OnPageChanged(self, event):
        global curPage
        global bPatchConfirmed
        global bPatchOK

        bPatchConfirmed = False
        bPatchOK = False
        self.enableButtons()
        curPage = self

    def OnPageChanging(self, event):
        if event.GetDirection():
            iSelection = 0
            while not self.rbs[iSelection].GetValue() and iSelection < PB.getNumMods():
                iSelection += 1

            if iSelection != self.currentMod:
                PB.loadMod(iSelection - 1)
                PB.quit()

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        next = self.next
        iSelection = 0
        while not self.rbs[iSelection].GetValue() and iSelection < PB.getNumMods():
            iSelection += 1

        if iSelection != self.currentMod:
            next = None
        return next

    def GetPrev(self):
        return self.prev


#
# SMTP Login Page
#
class SMTPLoginPage(wx.wizard.WizardPageSimple):
    __slots__ = ('myParent', 'host', 'username', 'password', 'email')

    def __init__(self, parent):
        wx.wizard.WizardPageSimple.__init__(self, parent)
        self.myParent = weakref.ref(parent)

        header = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_SMTP_HEADER", ()))

        hostLbl = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_SMTP_HOST", ()))
        self.host = wx.TextCtrl(self, -1, PB.getSMTPHost(), size=(125, -1))
        self.host.SetHelpText(localText.getText("TXT_KEY_PITBOSS_SMTP_HOST_HELP", ()))
        self.host.SetInsertionPoint(0)

        usernameLbl = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_SMTP_LOGIN", ()))
        self.username = wx.TextCtrl(self, -1, PB.getSMTPLogin(), size=(125, -1))
        self.username.SetHelpText(localText.getText("TXT_KEY_PITBOSS_SMTP_LOGIN_HELP", ()))

        passwordLbl = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_SMTP_PASSWORD", ()))
        self.password = wx.TextCtrl(self, -1, "", size=(125, -1), style=wx.TE_PASSWORD)
        self.password.SetHelpText(localText.getText("TXT_KEY_PITBOSS_SMTP_PASSWORD_HELP", ()))

        emailLbl = wx.StaticText(self, -1, localText.getText("TXT_KEY_POPUP_DETAILS_EMAIL", ()))
        self.email = wx.TextCtrl(self, -1, PB.getEmail(), size=(125, -1))
        self.email.SetHelpText(localText.getText("TXT_KEY_POPUP_DETAILS_EMAIL", ()))

        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)

        sizer = wx.FlexGridSizer(cols=2, hgap=4, vgap=4)
        # Use tuple for immutable data
        controls = (hostLbl, self.host, usernameLbl, self.username, passwordLbl, self.password, emailLbl, self.email)
        sizer.AddMany(controls)
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(sizer, 0, wx.ALL, 25)
        self.SetSizer(border)
        self.SetAutoLayout(True)

    def enableButtons(self):
        parent = self.myParent()
        if parent:
            parent.FindWindowById(wx.ID_FORWARD).Enable(True)
            parent.FindWindowById(wx.ID_BACKWARD).Enable(True)

    def OnPageChanged(self, event):
        global curPage
        self.enableButtons()
        curPage = self

    def OnPageChanging(self, event):
        if event.GetDirection():
            PB.setSMTPValues(self.host.GetValue(), self.username.GetValue(),
                             self.password.GetValue(), self.email.GetValue())


#
# Network Selection Page
#
class NetSelectPage(wx.wizard.PyWizardPage):
    __slots__ = ('next', 'prev', 'myParent', 'rb')

    def __init__(self, parent):
        wx.wizard.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.myParent = weakref.ref(parent)

        # Use tuple for immutable selections
        selections = (localText.getText("TXT_KEY_PITBOSS_DIRECTIP", ()),
                      localText.getText("TXT_KEY_PITBOSS_LAN", ()),
                      localText.getText("TXT_KEY_PITBOSS_INTERNET", ()))

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.rb = wx.RadioBox(self, -1, localText.getText("TXT_KEY_PITBOSS_SELECT_NETWORK", ()),
                              wx.DefaultPosition, wx.DefaultSize, selections, 1, wx.RA_SPECIFY_COLS)

        self.rb.SetToolTip(wx.ToolTip(localText.getText("TXT_KEY_PITBOSS_SELECT_NETWORK_HELP", ())))
        sizer.Add(self.rb, 0, wx.ALL, 5)
        self.SetSizer(sizer)
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)

    def enableButtons(self):
        parent = self.myParent()
        if parent:
            parent.FindWindowById(wx.ID_FORWARD).Enable(True)
            parent.FindWindowById(wx.ID_BACKWARD).Enable(True)

    def OnPageChanged(self, event):
        global curPage
        self.enableButtons()
        curPage = self

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        global bPublic
        next = self.next
        selection = self.rb.GetSelection()

        if selection == 0:
            bPublic = True
            next = next.GetNext()
        elif selection == 1:
            bPublic = False
            next = next.GetNext()
        else:
            bPublic = True
        return next

    def GetPrev(self):
        return self.prev


#
# Login page (optional 2nd page)
#
class LoginPage(wx.wizard.WizardPageSimple):
    __slots__ = ('myParent', 'username', 'password')

    def __init__(self, parent):
        wx.wizard.WizardPageSimple.__init__(self, parent)
        self.myParent = weakref.ref(parent)

        header = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_LOGIN", ()))

        usernameLbl = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_USERNAME", ()))
        self.username = wx.TextCtrl(self, -1, "", size=(125, -1))
        self.username.SetHelpText(localText.getText("TXT_KEY_PITBOSS_USERNAME_HELP", ()))
        self.username.SetInsertionPoint(0)
        self.Bind(wx.EVT_TEXT, self.OnTextEntered, self.username)

        passwordLbl = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_PASSWORD", ()))
        self.password = wx.TextCtrl(self, -1, "", size=(125, -1), style=wx.TE_PASSWORD)
        self.password.SetHelpText(localText.getText("TXT_KEY_PITBOSS_PASSWORD_HELP", ()))
        self.Bind(wx.EVT_TEXT, self.OnTextEntered, self.password)

        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)

        sizer = wx.FlexGridSizer(cols=2, hgap=4, vgap=4)
        sizer.AddMany((usernameLbl, self.username, passwordLbl, self.password))
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(sizer, 0, wx.ALL, 25)
        self.SetSizer(border)
        self.SetAutoLayout(True)

    def enableButtons(self):
        global bPatchConfirmed
        global bPatchOK

        parent = self.myParent()
        if not parent:
            return

        if not bPatchConfirmed:
            parent.FindWindowById(wx.ID_FORWARD).Disable()
            parent.FindWindowById(wx.ID_BACKWARD).Disable()
        elif self.username.GetValue() == "" or self.password.GetValue() == "" or not bPatchOK:
            parent.FindWindowById(wx.ID_FORWARD).Disable()
            parent.FindWindowById(wx.ID_BACKWARD).Enable(True)
        else:
            parent.FindWindowById(wx.ID_FORWARD).Enable(True)
            parent.FindWindowById(wx.ID_BACKWARD).Enable(True)

    def patchAvailable(self, patchName, patchUrl):
        global bPatchConfirmed
        global szPatchName

        dlg = wx.MessageDialog(self, localText.getText("TXT_KEY_PITBOSS_PATCH_REQUIRED_DESC", ()),
                               localText.getText("TXT_KEY_PITBOSS_PATCH_REQUIRED_TITLE", ()),
                               wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)

        if dlg.ShowModal() == wx.ID_OK:
            if not PB.downloadPatch(patchName, patchUrl):
                msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_PATCH_DOWNLOAD_ERROR_DESC", ()),
                                    localText.getText("TXT_KEY_PITBOSS_PATCH_DOWNLOAD_ERROR_TITLE", ()),
                                    wx.ICON_ERROR)
                bPatchConfirmed = True
                szPatchName = patchName
                self.enableButtons()
        else:
            bPatchConfirmed = True
            self.enableButtons()

        dlg.Destroy()  # Clean up dialog

    def patchComplete(self):
        global bPatchConfirmed
        global bPatchOK
        global szPatchName

        dlg = wx.MessageDialog(self, localText.getText("TXT_KEY_PITBOSS_PATCH_COMPLETE_DESC", ()),
                               localText.getText("TXT_KEY_PITBOSS_PATCH_COMPLETE_TITLE", ()),
                               wx.OK | wx.ICON_EXCLAMATION)

        if dlg.ShowModal() == wx.ID_OK:
            PB.installPatch(szPatchName)
        else:
            bPatchConfirmed = True
            bPatchOK = False

        dlg.Destroy()  # Clean up dialog

    def OnTextEntered(self, event):
        self.enableButtons()

    def OnPageChanging(self, event):
        if event.GetDirection():
            if not PB.login(self.username.GetValue(), self.password.GetValue()):
                msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_LOGIN_FAILED", ()),
                                    localText.getText("TXT_KEY_PITBOSS_LOGIN_ERROR", ()),
                                    wx.ICON_ERROR)
                event.Veto()

    def OnPageChanged(self, event):
        global bPatchConfirmed
        global curPage

        if not bPatchConfirmed:
            if not PB.checkPatch():
                msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_PATCH_CHECK_ERROR_DESC", ()),
                                    localText.getText("TXT_KEY_PITBOSS_PATCH_DOWNLOAD_ERROR_TITLE", ()),
                                    wx.ICON_ERROR)
                bPatchConfirmed = True

        self.enableButtons()
        curPage = self


#
# Load Select Page
#
class LoadSelectPage(wx.wizard.PyWizardPage):
    __slots__ = ('next', 'prev', 'myParent', 'rb')

    def __init__(self, parent):
        wx.wizard.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.myParent = weakref.ref(parent)

        # Use tuple for immutable selections
        selections = (localText.getText("TXT_KEY_PITBOSS_NEWGAME", ()),
                      localText.getText("TXT_KEY_PITBOSS_SCENARIO", ()),
                      localText.getText("TXT_KEY_PITBOSS_LOADGAME", ()))

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.rb = wx.RadioBox(self, -1, localText.getText("TXT_KEY_PITBOSS_SELECT_INIT", ()),
                              wx.DefaultPosition, wx.DefaultSize, selections, 1, wx.RA_SPECIFY_COLS)

        self.rb.SetToolTip(wx.ToolTip(localText.getText("TXT_KEY_PITBOSS_SELECT_INIT_HELP", ())))
        sizer.Add(self.rb, 0, wx.ALL, 5)
        self.SetSizer(sizer)

        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.OnPageChanging)

    def enableButtons(self):
        global bPatchConfirmed
        parent = self.myParent()
        if parent:
            parent.FindWindowById(wx.ID_FORWARD).Enable(bPatchConfirmed)
            parent.FindWindowById(wx.ID_BACKWARD).Enable(bPatchConfirmed)

    def patchAvailable(self, patchName, patchUrl):
        global bPatchConfirmed

        dlg = wx.MessageDialog(self, localText.getText("TXT_KEY_PITBOSS_PATCH_AVAILABLE_DESC", ()),
                               localText.getText("TXT_KEY_PITBOSS_PATCH_AVAILABLE_TITLE", ()),
                               wx.YES_NO | wx.ICON_QUESTION)

        if dlg.ShowModal() == wx.ID_YES:
            if not PB.downloadPatch(patchName, patchUrl):
                msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_PATCH_DOWNLOAD_ERROR_DESC", ()),
                                    localText.getText("TXT_KEY_PITBOSS_PATCH_DOWNLOAD_ERROR_TITLE", ()),
                                    wx.ICON_ERROR)
                bPatchConfirmed = True
                self.enableButtons()
        else:
            bPatchConfirmed = True
            self.enableButtons()

        dlg.Destroy()  # Clean up dialog

    def patchComplete(self):
        global bPatchConfirmed
        global bPatchOK
        global szPatchName

        dlg = wx.MessageDialog(self, localText.getText("TXT_KEY_PITBOSS_PATCH_COMPLETE_DESC", ()),
                               localText.getText("TXT_KEY_PITBOSS_PATCH_COMPLETE_TITLE", ()),
                               wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)

        if dlg.ShowModal() == wx.ID_OK:
            PB.installPatch(szPatchName)
        else:
            bPatchConfirmed = True
            bPatchOK = False

        dlg.Destroy()  # Clean up dialog

    def OnPageChanged(self, event):
        global curPage
        global bPatchConfirmed

        if not bPatchConfirmed and not PB.checkPatch():
            msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_PATCH_CHECK_ERROR_DESC", ()),
                                localText.getText("TXT_KEY_PITBOSS_PATCH_CHECK_ERROR_TITLE", ()),
                                wx.ICON_ERROR)
            bPatchConfirmed = True

        self.enableButtons()
        curPage = self

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        next = self.next
        selection = self.rb.GetSelection()

        if selection == 0:
            next = next.GetNext()
        elif selection == 2:
            next = None
        return next

    def GetPrev(self):
        return self.prev

    def OnPageChanging(self, event):
        global bSaved
        global bScenario

        if event.GetDirection():
            selection = self.rb.GetSelection()

            if selection == 2:  # Loading a game
                bScenario = False
                dlg = wx.FileDialog(
                    self, message=localText.getText("TXT_KEY_PITBOSS_CHOOSE_SAVE", ()),
                    defaultDir=".\saves\multi",
                    defaultFile="",
                    wildcard=localText.getText("TXT_KEY_PITBOSS_SAVE_FILES",
                                               ("(*.CivBeyondSwordSave)|*.CivBeyondSwordSave",)),
                    style=wx.OPEN
                )

                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    if path:
                        pwdDlg = wx.TextEntryDialog(
                            self, localText.getText("TXT_KEY_MAIN_MENU_CIV_ADMINPWD_DESC", ()),
                            localText.getText("TXT_MAIN_MENU_CIV_PASSWORD_TITLEBAR", ()))

                        if pwdDlg.ShowModal() == wx.ID_OK:
                            adminPwd = pwdDlg.GetValue()
                            iResult = PB.load(path, adminPwd)

                            if iResult != 0:
                                if iResult == 1:
                                    msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_ERROR_LOADING", ()),
                                                        localText.getText("TXT_KEY_PITBOSS_LOAD_ERROR", ()),
                                                        wx.ICON_ERROR)
                                elif iResult == -1:
                                    msg = wx.MessageBox(localText.getText("TXT_MAIN_MENU_CIV_PASSWORD_RETRY_DESC", ()),
                                                        localText.getText("TXT_KEY_BAD_PASSWORD_TITLE", ()),
                                                        wx.ICON_ERROR)
                                PB.reset()
                                event.Veto()
                            else:
                                PB.setLoadFileName(path)
                                if not PB.host(bPublic, bScenario):
                                    msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_ERROR_HOSTING", ()),
                                                        localText.getText("TXT_KEY_PITBOSS_HOST_ERROR", ()),
                                                        wx.ICON_ERROR)
                                    PB.reset()
                                    event.Veto()
                                else:
                                    bSaved = True
                            del adminPwd  # Clean up password
                        else:
                            PB.reset()
                            event.Veto()

                        pwdDlg.Destroy()  # Clean up dialog
                    else:
                        event.Veto()
                else:
                    event.Veto()

                dlg.Destroy()  # Clean up dialog

            else:
                bSaved = False

                if selection == 0 and PB.getNumMapScripts() == 0:
                    msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_NO_MAPS_DESC", ()),
                                        localText.getText("TXT_KEY_PITBOSS_NO_MAPS_TITLE", ()),
                                        wx.ICON_EXCLAMATION)
                    event.Veto()
                    return

                if selection == 1 and PB.getNumScenarios() == 0:
                    msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_NO_SCENARIOS_DESC", ()),
                                        localText.getText("TXT_KEY_PITBOSS_NO_SCENARIOS_TITLE", ()),
                                        wx.ICON_EXCLAMATION)
                    event.Veto()
                    return

                nameDlg = wx.TextEntryDialog(self, localText.getText("TXT_KEY_PITBOSS_NAME_GAME_DESC", ()),
                                             localText.getText("TXT_KEY_PITBOSS_NAME_GAME_TITLE", ()))

                if nameDlg.ShowModal() == wx.ID_OK:
                    gamename = nameDlg.GetValue()
                    if gamename:
                        PB.setGamename(gamename)

                        bOK = not bPublic
                        if bPublic:
                            pwdDlg = wx.TextEntryDialog(self, localText.getText("TXT_KEY_PITBOSS_PWD_GAME_DESC", ()),
                                                        localText.getText("TXT_KEY_PITBOSS_PWD_GAME_TITLE", ()))

                            if pwdDlg.ShowModal() == wx.ID_OK:
                                bOK = True
                                PB.setGamePassword(pwdDlg.GetValue())

                            pwdDlg.Destroy()  # Clean up dialog

                        if bOK:
                            if selection == 0:
                                bScenario = False
                                if not PB.host(bPublic, bScenario):
                                    msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_ERROR_HOSTING", ()),
                                                        localText.getText("TXT_KEY_PITBOSS_HOST_ERROR", ()),
                                                        wx.ICON_ERROR)
                                    PB.reset()
                                    event.Veto()
                        else:
                            event.Veto()
                    else:
                        event.Veto()
                else:
                    event.Veto()

                nameDlg.Destroy()  # Clean up dialog
        else:
            PB.reset()
            PB.logout()


#
# Scenario Selection page (optional 4th page)
#
class ScenarioSelectPage(wx.wizard.WizardPageSimple):
    __slots__ = ('myParent', 'rbs')

    def __init__(self, parent):
        wx.wizard.WizardPageSimple.__init__(self, parent)
        self.myParent = weakref.ref(parent)

        pageSizer = wx.BoxSizer(wx.VERTICAL)

        scenarioPanel = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(300, 600), style=wx.SUNKEN_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_CHOOSE_SCENARIO", ()))
        pageSizer.Add(header, 0, wx.ALL, 5)

        self.rbs = []
        for index in xrange(PB.getNumScenarios()):
            scenarioName = PB.getScenarioAt(index)
            if not index:
                rb = wx.RadioButton(scenarioPanel, -1, scenarioName, wx.DefaultPosition, wx.DefaultSize, wx.RB_GROUP)
            else:
                rb = wx.RadioButton(scenarioPanel, -1, scenarioName, wx.DefaultPosition, wx.DefaultSize)

            self.rbs.append(rb)
            sizer.Add(rb, 0, wx.ALL, 3)
            del scenarioName  # Clean up temporary

        scenarioPanel.SetSizer(sizer)
        scenarioPanel.SetAutoLayout(1)
        scenarioPanel.SetupScrolling()

        pageSizer.Add(scenarioPanel, 0, wx.ALL, 5)
        self.SetSizer(pageSizer)

        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.OnPageChanging)

    def enableButtons(self):
        parent = self.myParent()
        if parent:
            parent.FindWindowById(wx.ID_FORWARD).Enable(True)
            parent.FindWindowById(wx.ID_BACKWARD).Enable(True)

    def OnPageChanged(self, event):
        global curPage
        self.enableButtons()
        curPage = self

    def OnPageChanging(self, event):
        global bPublic
        global bScenario

        if event.GetDirection():
            iSelection = 0
            while not self.rbs[iSelection].GetValue() and iSelection < PB.getNumScenarios():
                iSelection += 1

            scenarioName = PB.getScenarioAt(iSelection)
            if PB.loadScenarioInfo(scenarioName):
                bScenario = True
                if not PB.host(bPublic, bScenario):
                    msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_ERROR_HOSTING", ()),
                                        localText.getText("TXT_KEY_PITBOSS_HOST_ERROR", ()),
                                        wx.ICON_ERROR)
                    PB.reset()
                    event.Veto()
            else:
                msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_SCENARIO_ERROR", ()),
                                    localText.getText("TXT_KEY_PITBOSS_SCENARIO_ERROR_TITLE", ()),
                                    wx.ICON_ERROR)
                PB.reset()
                event.Veto()
            del scenarioName  # Clean up temporary
        else:
            PB.reset()


#
# Staging room (last page before launch) - Memory optimized version
#
class StagingPage(wx.wizard.WizardPageSimple):
    __slots__ = ('myParent', 'optionArray', 'mpOptionArray', 'victoriesArray',
                 'whoArray', 'civArray', 'leaderArray', 'teamArray', 'diffArray',
                 'statusArray', 'customItemSizerArray', 'customMapTextArray',
                 'customMapOptionArray', 'mapChoice', 'sizeChoice', 'climateChoice',
                 'seaLevelChoice', 'eraChoice', 'speedChoice', 'turnTimerEdit',
                 'maxTurnsEdit', 'cityEliminationEdit', 'advancedStartPointsEdit',
                 'adminPasswordEdit', 'leaderRefresh', 'pageSizer', 'optionsSizer',
                 'dropDownSizer')

    def __init__(self, parent):
        wx.wizard.WizardPageSimple.__init__(self, parent)
        self.myParent = weakref.ref(parent)

        # Get the game info struct
        gameData = PB.getGameSetupData()

        # Initialize arrays
        self.optionArray = []
        self.mpOptionArray = []
        self.victoriesArray = []
        self.whoArray = []
        self.civArray = []
        self.leaderArray = []
        self.teamArray = []
        self.diffArray = []
        self.statusArray = []
        self.customItemSizerArray = []
        self.customMapTextArray = []
        self.customMapOptionArray = []

        # Build selection lists as tuples (immutable)
        mapNameList = tuple(PB.getMapNameAt(i) for i in xrange(PB.getNumMapScripts()))
        sizeList = tuple(PB.getSizeAt(i) for i in xrange(PB.getNumSizes()))
        climateList = tuple(PB.getClimateAt(i) for i in xrange(PB.getNumClimates()))
        seaLevelList = tuple(PB.getSeaLevelAt(i) for i in xrange(PB.getNumSeaLevels()))
        eraList = tuple(PB.getEraAt(i) for i in xrange(PB.getNumEras()))
        speedList = tuple(PB.getSpeedAt(i) for i in xrange(PB.getNumSpeeds()))

        # Create the master page sizer
        self.pageSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the game options area
        masterBorder = wx.StaticBox(self, -1, localText.getText("TXT_KEY_PITBOSS_GAME_SETUP", ()))
        self.optionsSizer = wx.StaticBoxSizer(masterBorder, wx.HORIZONTAL)

        # Create the drop down side
        settingsBorder = wx.StaticBox(self, -1, localText.getText("TXT_KEY_PITBOSS_GAME_SETTINGS", ()))
        self.dropDownSizer = wx.StaticBoxSizer(settingsBorder, wx.VERTICAL)

        # Create map dropdown
        itemSizer = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_MAP", ()))
        self.mapChoice = wx.Choice(self, -1, (-1, -1), choices=list(mapNameList))
        self.mapChoice.SetStringSelection(gameData.getMapName())
        itemSizer.Add(txt)
        itemSizer.Add(self.mapChoice)
        self.dropDownSizer.Add(itemSizer, 0, wx.TOP, 3)
        self.Bind(wx.EVT_CHOICE, self.OnGameChoice, self.mapChoice)

        # Create size dropdown
        itemSizer = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_SIZE", ()))
        self.sizeChoice = wx.Choice(self, -1, (-1, -1), choices=list(sizeList))
        self.sizeChoice.SetSelection(gameData.iSize)
        itemSizer.Add(txt)
        itemSizer.Add(self.sizeChoice)
        self.dropDownSizer.Add(itemSizer, 0, wx.TOP, 3)
        self.Bind(wx.EVT_CHOICE, self.OnGameChoice, self.sizeChoice)

        # Create climate dropdown
        itemSizer = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_CLIMATE", ()))
        self.climateChoice = wx.Choice(self, -1, (-1, -1), choices=list(climateList))
        self.climateChoice.SetSelection(gameData.iClimate)
        itemSizer.Add(txt)
        itemSizer.Add(self.climateChoice)
        self.dropDownSizer.Add(itemSizer, 0, wx.TOP, 3)
        self.Bind(wx.EVT_CHOICE, self.OnGameChoice, self.climateChoice)

        # Create sealevel dropdown
        itemSizer = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_SEALEVEL", ()))
        self.seaLevelChoice = wx.Choice(self, -1, (-1, -1), choices=list(seaLevelList))
        self.seaLevelChoice.SetSelection(gameData.iSeaLevel)
        itemSizer.Add(txt)
        itemSizer.Add(self.seaLevelChoice)
        self.dropDownSizer.Add(itemSizer, 0, wx.TOP, 3)
        self.Bind(wx.EVT_CHOICE, self.OnGameChoice, self.seaLevelChoice)

        # Create era dropdown
        itemSizer = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_ERA", ()))
        self.eraChoice = wx.Choice(self, -1, (-1, -1), choices=list(eraList))
        self.eraChoice.SetSelection(gameData.iEra)
        itemSizer.Add(txt)
        itemSizer.Add(self.eraChoice)
        self.dropDownSizer.Add(itemSizer, 0, wx.TOP, 3)
        self.Bind(wx.EVT_CHOICE, self.OnGameChoice, self.eraChoice)

        # Create speed dropdown
        itemSizer = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_SPEED", ()))
        self.speedChoice = wx.Choice(self, -1, (-1, -1), choices=list(speedList))
        self.speedChoice.SetSelection(gameData.iSpeed)
        itemSizer.Add(txt)
        itemSizer.Add(self.speedChoice)
        self.dropDownSizer.Add(itemSizer, 0, wx.TOP, 3)
        self.Bind(wx.EVT_CHOICE, self.OnGameChoice, self.speedChoice)

        # Build custom map options
        self.buildCustomMapOptions(gameData.getMapName())

        self.optionsSizer.Add(self.dropDownSizer, 0, wx.RIGHT, 10)

        # Create the multiplayer option column
        centerSizer = wx.BoxSizer(wx.VERTICAL)

        mpOptionsBorder = wx.StaticBox(self, -1, localText.getText("TXT_KEY_PITBOSS_GAME_MPOPTIONS", ()))
        mpOptionsSizer = wx.StaticBoxSizer(mpOptionsBorder, wx.VERTICAL)

        # Create MP option checkboxes
        for rowNum in xrange(PB.getNumMPOptions()):
            mpCheckBox = wx.CheckBox(self, (rowNum + 1000), PB.getMPOptionDescAt(rowNum))
            mpCheckBox.SetValue(gameData.getMPOptionAt(rowNum))
            mpOptionsSizer.Add(mpCheckBox, 0, wx.TOP, 5)
            self.mpOptionArray.append(mpCheckBox)
            self.Bind(wx.EVT_CHECKBOX, self.OnOptionChoice, mpCheckBox)

        # Turn timer
        timerOutputSizer = wx.BoxSizer(wx.HORIZONTAL)
        timerPreText = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_TURNTIMER_A", ()))
        self.turnTimerEdit = wx.TextCtrl(self, -1, str(gameData.iTurnTime), size=(30, -1))
        timerPostText = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_TURNTIMER_B", ()))
        timerOutputSizer.Add(timerPreText, 0, wx.TOP, 5)
        timerOutputSizer.Add(self.turnTimerEdit, 0, wx.TOP, 5)
        timerOutputSizer.Add(timerPostText, 0, wx.TOP, 5)
        self.Bind(wx.EVT_TEXT, self.OnTurnTimeEntered, self.turnTimerEdit)
        mpOptionsSizer.Add(timerOutputSizer, 0, wx.ALL, 5)

        # Max turns
        maxTurnsSizer = wx.BoxSizer(wx.HORIZONTAL)
        maxTurnsText = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_MAX_TURN", ()))
        self.maxTurnsEdit = wx.TextCtrl(self, -1, str(gameData.iMaxTurns), size=(30, -1))
        maxTurnsSizer.Add(maxTurnsText, 0, wx.TOP, 5)
        maxTurnsSizer.Add(self.maxTurnsEdit, 0, wx.TOP, 5)
        self.Bind(wx.EVT_TEXT, self.OnMaxTurnsEntered, self.maxTurnsEdit)
        mpOptionsSizer.Add(maxTurnsSizer, 0, wx.ALL, 5)

        # City elimination
        cityEliminationSizer = wx.BoxSizer(wx.HORIZONTAL)
        cityEliminationText = wx.StaticText(self, -1, localText.getText("TXT_KEY_PITBOSS_CITY_ELIMINATION", ()))
        self.cityEliminationEdit = wx.TextCtrl(self, -1, str(gameData.iCityElimination), size=(30, -1))
        cityEliminationSizer.Add(cityEliminationText, 0, wx.TOP, 5)
        cityEliminationSizer.Add(self.cityEliminationEdit, 0, wx.TOP, 5)
        self.Bind(wx.EVT_TEXT, self.OnCityEliminationEntered, self.cityEliminationEdit)
        mpOptionsSizer.Add(cityEliminationSizer, 0, wx.ALL, 5)

        centerSizer.Add(mpOptionsSizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Victories
        victoriesBorder = wx.StaticBox(self, -1, localText.getText("TXT_KEY_PITBOSS_GAME_VICTORIES", ()))
        victoriesSizer = wx.StaticBoxSizer(victoriesBorder, wx.VERTICAL)

        for rowNum in xrange(PB.getNumVictories()):
            victoryCheckBox = wx.CheckBox(self, (rowNum + 2000), PB.getVictoryDescAt(rowNum))
            victoryCheckBox.SetValue(gameData.getVictory(rowNum))
            victoriesSizer.Add(victoryCheckBox, 0, wx.TOP, 5)
            self.victoriesArray.append(victoryCheckBox)
            self.Bind(wx.EVT_CHECKBOX, self.OnOptionChoice, victoryCheckBox)

        centerSizer.Add(victoriesSizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Admin password
        itemSizer = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(self, -1, localText.getText("TXT_KEY_POPUP_ADMIN_PASSWORD", ()))
        self.adminPasswordEdit = wx.TextCtrl(self, -1, "", size=(100, -1))
        itemSizer.Add(txt)
        itemSizer.Add(self.adminPasswordEdit)
        mpOptionsSizer.Add(itemSizer, 0, wx.TOP, 5)
        self.Bind(wx.EVT_TEXT, self.OnAdminPasswordEntered, self.adminPasswordEdit)

        self.optionsSizer.Add(centerSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # Game options
        optionsBorder = wx.StaticBox(self, -1, localText.getText("TXT_KEY_PITBOSS_GAME_OPTIONS", ()))
        checkBoxSizer = wx.StaticBoxSizer(optionsBorder, wx.VERTICAL)

        for rowNum in xrange(PB.getNumOptions()):
            checkBox = wx.CheckBox(self, rowNum, PB.getOptionDescAt(rowNum))
            checkBox.SetValue(gameData.getOptionAt(rowNum))
            checkBoxSizer.Add(checkBox, 0, wx.TOP, 5)
            self.optionArray.append(checkBox)
            self.Bind(wx.EVT_CHECKBOX, self.OnOptionChoice, checkBox)

        self.optionsSizer.Add(checkBoxSizer, 0, wx.LEFT, 10)

        # Advanced start points
        advancedStartPointsSizer = wx.BoxSizer(wx.HORIZONTAL)
        advancedStartPointsText = wx.StaticText(self, -1, localText.getText("TXT_KEY_ADVANCED_START_POINTS", ()))
        self.advancedStartPointsEdit = wx.TextCtrl(self, -1, str(gameData.iAdvancedStartPoints), size=(50, -1))
        advancedStartPointsSizer.Add(advancedStartPointsText, 0, wx.TOP, 5)
        advancedStartPointsSizer.Add(self.advancedStartPointsEdit, 0, wx.TOP, 5)
        self.Bind(wx.EVT_TEXT, self.OnAdvancedStartPointsEntered, self.advancedStartPointsEdit)
        mpOptionsSizer.Add(advancedStartPointsSizer, 0, wx.ALL, 5)

        self.pageSizer.Add(self.optionsSizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Build static lists as tuples
        slotStatusList = (localText.getText("TXT_KEY_PITBOSS_HUMAN", ()),
                          localText.getText("TXT_KEY_PITBOSS_COMPUTER", ()),
                          localText.getText("TXT_KEY_PITBOSS_CLOSED", ()))

        # Build civ list
        civList = [localText.getText("TXT_KEY_PITBOSS_RANDOM", ())]
        civList.extend(PB.getCivAt(i) for i in xrange(PB.getNumCivs()))

        leaderList = [localText.getText("TXT_KEY_PITBOSS_RANDOM", ())]
        teamList = tuple(str(i + 1) for i in xrange(gc.getMAX_PC_PLAYERS()))
        diffList = tuple(PB.getHandicapAt(i) for i in xrange(PB.getNumHandicaps()))

        # Player panel
        playerPanel = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(425, 300), style=wx.SUNKEN_BORDER)
        panelSizer = wx.BoxSizer(wx.VERTICAL)

        # Create player rows
        for rowNum in xrange(gc.getMAX_PC_PLAYERS()):
            border = wx.StaticBox(playerPanel, -1, localText.getText("TXT_KEY_PITBOSS_PLAYER", (rowNum + 1,)),
                                  (0, (rowNum * 30)))
            rowSizer = wx.StaticBoxSizer(border, wx.HORIZONTAL)

            playerData = PB.getPlayerSetupData(rowNum)

            # Slot status
            itemSizer = wx.BoxSizer(wx.VERTICAL)
            txt = wx.StaticText(playerPanel, -1, localText.getText("TXT_KEY_PITBOSS_WHO", ()))
            dropDown = wx.Choice(playerPanel, rowNum, (-1, -1), choices=list(slotStatusList))
            dropDown.SetSelection(playerData.iWho)
            itemSizer.Add(txt)
            itemSizer.Add(dropDown)
            rowSizer.Add(itemSizer, 0, wx.TOP, 3)
            self.whoArray.append(dropDown)
            self.Bind(wx.EVT_CHOICE, self.OnPlayerChoice, dropDown)

            # Civ dropdown
            itemSizer = wx.BoxSizer(wx.VERTICAL)
            txt = wx.StaticText(playerPanel, -1, localText.getText("TXT_KEY_PITBOSS_CIV", ()))
            dropDown = wx.Choice(playerPanel, rowNum, (-1, -1), choices=civList)
            dropDown.SetSelection(playerData.iCiv + 1)
            itemSizer.Add(txt)
            itemSizer.Add(dropDown)
            rowSizer.Add(itemSizer, 0, wx.TOP, 3)
            self.civArray.append(dropDown)
            self.Bind(wx.EVT_CHOICE, self.OnPlayerChoice, dropDown)

            # Leader dropdown
            itemSizer = wx.BoxSizer(wx.VERTICAL)
            txt = wx.StaticText(playerPanel, -1, localText.getText("TXT_KEY_PITBOSS_LEADER", ()))
            dropDown = wx.Choice(playerPanel, rowNum, (-1, -1), choices=leaderList)
            dropDown.SetSelection(playerData.iLeader + 1)
            itemSizer.Add(txt)
            itemSizer.Add(dropDown)
            rowSizer.Add(itemSizer, 0, wx.TOP, 3)
            self.leaderArray.append(dropDown)
            self.Bind(wx.EVT_CHOICE, self.OnPlayerChoice, dropDown)

            # Team dropdown
            itemSizer = wx.BoxSizer(wx.VERTICAL)
            txt = wx.StaticText(playerPanel, -1, localText.getText("TXT_KEY_PITBOSS_TEAM", ()))
            dropDown = wx.Choice(playerPanel, rowNum, (-1, -1), choices=list(teamList))
            dropDown.SetSelection(playerData.iTeam)
            itemSizer.Add(txt)
            itemSizer.Add(dropDown)
            rowSizer.Add(itemSizer, 0, wx.TOP, 3)
            self.teamArray.append(dropDown)
            self.Bind(wx.EVT_CHOICE, self.OnPlayerChoice, dropDown)

            # Difficulty dropdown
            itemSizer = wx.BoxSizer(wx.VERTICAL)
            txt = wx.StaticText(playerPanel, -1, localText.getText("TXT_KEY_PITBOSS_DIFFICULTY", ()))
            dropDown = wx.Choice(playerPanel, rowNum, (-1, -1), choices=list(diffList))
            dropDown.SetSelection(playerData.iDifficulty)
            itemSizer.Add(txt)
            itemSizer.Add(dropDown)
            rowSizer.Add(itemSizer, 0, wx.TOP, 3)
            self.diffArray.append(dropDown)
            self.Bind(wx.EVT_CHOICE, self.OnPlayerChoice, dropDown)

            # Status
            itemSizer = wx.BoxSizer(wx.VERTICAL)
            txt = wx.StaticText(playerPanel, -1, localText.getText("TXT_KEY_PITBOSS_STATUS", ()))
            statusTxt = wx.StaticText(playerPanel, rowNum, playerData.getStatusText())
            itemSizer.Add(txt)
            itemSizer.Add(statusTxt)
            rowSizer.Add(itemSizer, 0, wx.ALL, 5)
            self.statusArray.append(statusTxt)

            panelSizer.Add(rowSizer, 0, wx.ALL, 5)

        playerPanel.SetSizer(panelSizer)
        playerPanel.SetAutoLayout(1)
        playerPanel.SetupScrolling()

        self.pageSizer.Add(playerPanel, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.leaderRefresh = False

        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.OnPageChanging)

        self.SetSizer(self.pageSizer)

        # Force garbage collection after setup
        garbage_collector.collect()

    def enableButtons(self):
        parent = self.myParent()
        if parent:
            parent.FindWindowById(wx.ID_FORWARD).Enable(True)
            parent.FindWindowById(wx.ID_BACKWARD).Enable(True)

    def OnGameChoice(self, event):
        self.ChangeGameParam()

    def ChangeGameParam(self):
        maxTurnsValue = 0
        cityEliminationValue = 0
        advancedStartPointsValue = 0
        turnTimerValue = 0

        strValue = self.maxTurnsEdit.GetValue()
        if strValue:
            maxTurnsValue = int(strValue)

        strValue = self.cityEliminationEdit.GetValue()
        if strValue:
            cityEliminationValue = int(strValue)

        strValue = self.advancedStartPointsEdit.GetValue()
        if strValue:
            advancedStartPointsValue = int(strValue)

        strValue = self.turnTimerEdit.GetValue()
        if strValue:
            turnTimerValue = int(strValue)

        PB.gameParamChanged(
            self.mapChoice.GetStringSelection(), self.sizeChoice.GetSelection(),
            self.climateChoice.GetSelection(), self.seaLevelChoice.GetSelection(),
            self.eraChoice.GetSelection(), self.speedChoice.GetSelection(), maxTurnsValue, cityEliminationValue,
            advancedStartPointsValue, turnTimerValue, self.adminPasswordEdit.GetValue()
        )

    def OnCustomMapOptionChoice(self, event):
        optionID = event.GetId() / 100 - 1
        PB.customMapOptionChanged(optionID, self.customMapOptionArray[optionID].GetSelection())

    def IsNumericString(self, myStr):
        for myChar in myStr:
            if myChar not in string.digits:
                return False
        return True

    def OnMaxTurnsEntered(self, event):
        if self.maxTurnsEdit.GetValue():
            if not self.IsNumericString(self.maxTurnsEdit.GetValue()):
                dlg = wx.MessageDialog(self, localText.getText("TXT_KEY_PITBOSS_MAXTURN_ERROR_DESC", ()),
                                       localText.getText("TXT_KEY_PITBOSS_MAXTURN_ERROR_TITLE", ()),
                                       wx.OK | wx.ICON_EXCLAMATION)
                if dlg.ShowModal() == wx.ID_OK:
                    self.maxTurnsEdit.SetValue("")
                dlg.Destroy()
            else:
                self.ChangeGameParam()
        else:
            self.ChangeGameParam()

    def OnCityEliminationEntered(self, event):
        if self.cityEliminationEdit.GetValue():
            if not self.IsNumericString(self.cityEliminationEdit.GetValue()):
                dlg = wx.MessageDialog(self, localText.getText("TXT_KEY_PITBOSS_CITYELIMINATION_ERROR_DESC", ()),
                                       localText.getText("TXT_KEY_PITBOSS_CITYELIMINATION_ERROR_TITLE", ()),
                                       wx.OK | wx.ICON_EXCLAMATION)
                if dlg.ShowModal() == wx.ID_OK:
                    self.cityEliminationEdit.SetValue("")
                dlg.Destroy()
            else:
                self.ChangeGameParam()
        else:
            self.ChangeGameParam()

    def OnAdvancedStartPointsEntered(self, event):
        if self.advancedStartPointsEdit.GetValue():
            if not self.IsNumericString(self.advancedStartPointsEdit.GetValue()):
                dlg = wx.MessageDialog(self, localText.getText("TXT_KEY_PITBOSS_CITYELIMINATION_ERROR_DESC", ()),
                                       localText.getText("TXT_KEY_PITBOSS_CITYELIMINATION_ERROR_TITLE", ()),
                                       wx.OK | wx.ICON_EXCLAMATION)
                if dlg.ShowModal() == wx.ID_OK:
                    self.advancedStartPointsEdit.SetValue("")
                dlg.Destroy()
            else:
                self.ChangeGameParam()
        else:
            self.ChangeGameParam()

    def OnTurnTimeEntered(self, event):
        if self.turnTimerEdit.GetValue():
            if not self.IsNumericString(self.turnTimerEdit.GetValue()):
                dlg = wx.MessageDialog(self, localText.getText("TXT_KEY_PITBOSS_TURNTIMER_ERROR_DESC", ()),
                                       localText.getText("TXT_KEY_PITBOSS_TURNTIMER_ERROR_TITLE", ()),
                                       wx.OK | wx.ICON_EXCLAMATION)
                if dlg.ShowModal() == wx.ID_OK:
                    self.turnTimerEdit.SetValue("")
                dlg.Destroy()
            else:
                self.ChangeGameParam()
        else:
            self.ChangeGameParam()

    def OnAdminPasswordEntered(self, event):
        self.ChangeGameParam()

    def OnOptionChoice(self, event):
        optionID = event.GetId()

        if optionID >= 2000:  # Victory Options
            PB.victoriesChanged((optionID - 2000), self.victoriesArray[(optionID - 2000)].GetValue())
        elif optionID >= 1000:  # MP options
            PB.mpOptionChanged((optionID - 1000), self.mpOptionArray[(optionID - 1000)].GetValue())
        else:
            PB.gameOptionChanged(optionID, self.optionArray[optionID].GetValue())

        bEnable = PB.getTurnTimer()
        self.turnTimerEdit.Enable(bEnable)

    def OnPlayerChoice(self, event):
        iRow = event.GetId()
        iValue = self.whoArray[iRow].GetSelection()

        if bScenario and iValue == 2 and not PB.getNoPlayersScenario() and PB.getWho(iRow) != iValue:
            self.whoArray[iRow].SetSelection(1)
            iValue = 1

        if not self.leaderRefresh:
            self.leaderRefresh = PB.getCiv(iRow) != self.civArray[iRow].GetSelection() - 1

        PB.playerParamChanged(
            iRow, iValue, self.civArray[iRow].GetSelection() - 1, self.teamArray[iRow].GetSelection(),
            self.diffArray[iRow].GetSelection(),
            PB.getGlobalLeaderIndex(self.civArray[iRow].GetSelection() - 1, self.leaderArray[iRow].GetSelection() - 1)
        )

    def OnPageChanging(self, event):
        if not event.GetDirection():
            PB.reset()

    def OnPageChanged(self, event):
        global curPage
        self.enableButtons()
        self.setDefaults()
        curPage = self

    def setDefaults(self):
        global bSaved
        global bScenario

        PB.resetAdvancedStartPoints()
        gameData = PB.getGameSetupData()

        self.refreshCustomMapOptions(gameData.getMapName())

        mapName = gameData.getMapName()
        if self.mapChoice.FindString(mapName) == wx.NOT_FOUND:
            self.mapChoice.Append(mapName)
        self.mapChoice.SetStringSelection(mapName)
        self.mapChoice.Enable(not bSaved and not bScenario)
        del mapName  # Clean up

        self.sizeChoice.SetSelection(gameData.iSize)
        self.sizeChoice.Enable(not bSaved and not bScenario)

        self.climateChoice.SetSelection(gameData.iClimate)
        self.climateChoice.Enable(not bSaved and not bScenario)

        self.seaLevelChoice.SetSelection(gameData.iSeaLevel)
        self.seaLevelChoice.Enable(not bSaved and not bScenario)

        self.eraChoice.SetSelection(gameData.iEra)
        self.eraChoice.Enable(not bSaved and not bScenario)

        self.speedChoice.SetSelection(gameData.iSpeed)
        self.speedChoice.Enable(not bSaved and not PB.forceSpeed())

        self.maxTurnsEdit.SetValue(str(gameData.iMaxTurns))
        self.maxTurnsEdit.Enable(not bSaved and not PB.forceMaxTurns())

        self.cityEliminationEdit.SetValue(str(gameData.iCityElimination))
        self.cityEliminationEdit.Enable(not bSaved and not PB.forceCityElimination())

        self.advancedStartPointsEdit.SetValue(str(gameData.iAdvancedStartPoints))
        self.advancedStartPointsEdit.Enable(not bSaved and not PB.forceAdvancedStart())

        self.turnTimerEdit.SetValue(str(gameData.iTurnTime))
        if not bSaved:
            bEnable = PB.getTurnTimer()
            self.turnTimerEdit.Enable(bEnable)
        else:
            self.turnTimerEdit.Disable()

        # Set custom map options
        for optionNum in xrange(PB.getNumCustomMapOptions(gameData.getMapName())):
            self.customMapOptionArray[optionNum].SetSelection(gameData.getCustomMapOption(optionNum))
            self.customMapOptionArray[optionNum].Enable(not bSaved and not bScenario)

        # Set MP options
        for i in xrange(PB.getNumMPOptions()):
            self.mpOptionArray[i].SetValue(gameData.getMPOptionAt(i))
            self.mpOptionArray[i].Enable(not bSaved)

        # Set victories
        for i in xrange(PB.getNumVictories()):
            self.victoriesArray[i].SetValue(gameData.getVictory(i))
            self.victoriesArray[i].Enable(not bSaved and not PB.forceVictories() and not PB.isPermanentVictory(i))

        # Set options
        for i in xrange(PB.getNumOptions()):
            self.optionArray[i].SetValue(gameData.getOptionAt(i))
            self.optionArray[i].Enable(not bSaved and not PB.forceOptions() and PB.isOptionValid(i))

        PB.suggestPlayerSetup()

        # Set player data
        for i in xrange(gc.getMAX_PC_PLAYERS()):
            playerData = PB.getPlayerSetupData(i)

            self.refreshWhoBox(i, playerData.iWho)
            self.whoArray[i].SetSelection(playerData.iWho)
            if playerData.iWho == 1:  # AI
                self.whoArray[i].Enable(not bSaved and PB.isPlayableCiv(i))

            civChoice = playerData.iCiv + 1
            self.civArray[i].SetSelection(civChoice)
            self.civArray[i].Enable(not bSaved and (not bScenario or PB.getNoPlayersScenario()))

            self.refreshLeaderBox(i, playerData.iCiv)
            self.leaderRefresh = False
            self.leaderArray[i].SetSelection(PB.getCivLeaderIndex(civChoice - 1, playerData.iLeader) + 1)
            self.leaderArray[i].Enable(not bSaved and (not bScenario or PB.getNoPlayersScenario()))

            self.teamArray[i].SetSelection(playerData.iTeam)
            self.teamArray[i].Enable(not bSaved and (not bScenario or PB.getNoPlayersScenario()))

            self.diffArray[i].SetSelection(playerData.iDifficulty)
            self.diffArray[i].Enable(not bSaved and not PB.forceDifficulty())

            self.statusArray[i].SetLabel(playerData.getStatusText())

        # Clean up
        del gameData
        garbage_collector.collect()

    def refreshRow(self, iRow):
        global bSaved

        bAllReady = not PB.isPendingInit()

        if not bSaved and bAllReady:
            for i in xrange(gc.getMAX_PC_PLAYERS()):
                if PB.getWho(i) == 3 and not PB.getReady(i):
                    bAllReady = False
                    break

        parent = self.myParent()
        if parent:
            parent.FindWindowById(wx.ID_FORWARD).Enable(bAllReady)

        playerData = PB.getPlayerSetupData(iRow)

        self.refreshWhoBox(iRow, playerData.iWho)
        self.whoArray[iRow].SetSelection(playerData.iWho)

        dropDown = self.civArray[iRow]
        civChoice = playerData.iCiv + 1
        if not self.leaderRefresh:
            self.leaderRefresh = (civChoice != dropDown.GetSelection())
        dropDown.SetSelection(civChoice)

        if self.leaderRefresh:
            self.refreshLeaderBox(iRow, playerData.iCiv)
            self.leaderRefresh = False

        dropDown = self.leaderArray[iRow]
        dropDown.SetSelection(PB.getCivLeaderIndex(civChoice - 1, playerData.iLeader) + 1)

        dropDown = self.teamArray[iRow]
        dropDown.SetSelection(playerData.iTeam)

        dropDown = self.diffArray[iRow]
        dropDown.SetSelection(playerData.iDifficulty)

        self.statusArray[iRow].SetLabel(playerData.getStatusText())

    def refreshWhoBox(self, iRow, iWho):
        dropDown = self.whoArray[iRow]

        if iWho < 3:
            if dropDown.GetCount() > 3:
                dropDown.Delete(3)
        elif dropDown.GetCount() == 3:
            dropDown.Append(PB.getName(iRow))
        else:
            dropDown.SetString(3, PB.getName(iRow))

    def refreshLeaderBox(self, iRow, iCiv):
        dropDown = self.leaderArray[iRow]
        dropDown.Clear()

        dropDown.Append(localText.getText("TXT_KEY_PITBOSS_RANDOM", ()))

        if iCiv > -1:
            for i in xrange(PB.getNumLeaders(iCiv)):
                dropDown.Append(PB.getCivLeaderAt(iCiv, i))

        dropDown.SetSelection(0)

    def refreshCustomMapOptions(self, szMapName):
        # Clean up old controls
        for i in xrange(len(self.customItemSizerArray)):
            self.Unbind(wx.EVT_CHOICE, self.customMapOptionArray[i])
            currentSizer = self.customItemSizerArray[i]
            currentSizer.Remove(1)
            currentSizer.Remove(0)
            self.dropDownSizer.Remove(currentSizer)
            self.customMapOptionArray[i].Destroy()
            self.customMapTextArray[i].Destroy()

        # Clear arrays
        del self.customItemSizerArray[:]
        del self.customMapTextArray[:]
        del self.customMapOptionArray[:]

        self.buildCustomMapOptions(szMapName)

        self.dropDownSizer.Layout()
        self.optionsSizer.Layout()
        self.pageSizer.Layout()
        self.Layout()

        # Clean up
        garbage_collector.collect()

    def refreshAdvancedStartPoints(self, iPoints):
        self.advancedStartPointsEdit.SetValue(str(iPoints))

    def buildCustomMapOptions(self, szMapName):
        gameData = PB.getGameSetupData()

        # Clear arrays first
        del self.customItemSizerArray[:]
        del self.customMapTextArray[:]
        del self.customMapOptionArray[:]

        szMap = gameData.getMapName()

        for i in xrange(PB.getNumCustomMapOptions(szMapName)):
            values = []
            for j in xrange(PB.getNumCustomMapOptionValues(i, szMap)):
                values.append(PB.getCustomMapOptionDescAt(i, j, szMap))

            itemSizer = wx.BoxSizer(wx.VERTICAL)
            txt = wx.StaticText(self, -1, PB.getCustomMapOptionName(i, szMapName))
            optionDropDown = wx.Choice(self, 100 * (i + 1), (-1, -1), choices=values)
            optionDropDown.SetSelection(gameData.getCustomMapOption(i))
            itemSizer.Add(txt)
            itemSizer.Add(optionDropDown)
            self.customItemSizerArray.append(itemSizer)
            self.customMapTextArray.append(txt)
            self.customMapOptionArray.append(optionDropDown)
            self.dropDownSizer.Add(itemSizer, 0, wx.TOP, 3)
            self.Bind(wx.EVT_CHOICE, self.OnCustomMapOptionChoice, self.customMapOptionArray[i])

            del values  # Clean up


#
# Progress bar dialog
#
class ProgressDialog(wx.Dialog):
    __slots__ = ('myParent', 'iValue', 'iTotal', 'sizer', 'progress')

    def __init__(self, parent):
        global curPage
        wx.Dialog.__init__(self, curPage, -1, localText.getText("TXT_KEY_PITBOSS_PATCH_PROGRESS_TITLE", ()),
                           wx.DefaultPosition, wx.DefaultSize, wx.STAY_ON_TOP)

        self.myParent = weakref.ref(parent)
        self.iValue = 0
        self.iTotal = 100

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.progress = None

        progressSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(progressSizer, 0, wx.ALL, 5)

        cancelButton = wx.Button(self, -1, localText.getText("TXT_KEY_SCREEN_CANCEL", ()))
        cancelButton.SetHelpText(localText.getText("TXT_KEY_CANCEL_PATCH_DOWNLOAD", ()))
        self.Bind(wx.EVT_BUTTON, self.OnCancelDownload, cancelButton)
        self.sizer.Add(cancelButton, 0, wx.ALL, 5)

        self.SetSizer(self.sizer)

    def setValue(self, iValue):
        if iValue > 0:
            self.iValue = iValue
            if self.progress != None:
                self.progress.SetValue(self.iValue)

    def setTotal(self, iTotal):
        if iTotal != self.iTotal and iTotal > 0:
            self.iTotal = iTotal
            if self.progress == None:
                self.progress = wx.Gauge(self, self.iValue, self.iTotal)
                self.sizer.Add(self.progress, 0, wx.ALL, 5)

    def OnCancelDownload(self, event):
        parent = self.myParent()
        if parent:
            parent.cancelDownload()

        if self.IsModal():
            self.EndModal(wx.ID_CANCEL)
        else:
            self.Show(False)
            return wx.ID_CANCEL


#
# main app class
#
class StartupIFace(wx.App):
    __slots__ = ('wizard', 'modSelect', 'smtpLogin', 'netSelect', 'login',
                 'loadSelect', 'scenarioSelect', 'staging', 'progressDlg', 'updateTimer')

    def OnInit(self):
        global curPage

        "Create the Pitboss Setup Wizard"
        self.wizard = wx.wizard.Wizard(None, -1, localText.getText("TXT_KEY_PITBOSS_TITLE", ()))

        # Create wizard pages
        self.modSelect = ModSelectPage(self.wizard)
        self.smtpLogin = SMTPLoginPage(self.wizard)
        self.netSelect = NetSelectPage(self.wizard)
        self.login = LoginPage(self.wizard)
        self.loadSelect = LoadSelectPage(self.wizard)
        self.scenarioSelect = ScenarioSelectPage(self.wizard)
        self.staging = StagingPage(self.wizard)

        # Set page connections
        self.modSelect.SetNext(self.smtpLogin)
        self.smtpLogin.SetPrev(self.modSelect)
        self.smtpLogin.SetNext(self.netSelect)
        self.netSelect.SetPrev(self.smtpLogin)
        self.netSelect.SetNext(self.login)
        self.login.SetPrev(self.netSelect)
        self.login.SetNext(self.loadSelect)
        self.loadSelect.SetPrev(self.netSelect)
        self.loadSelect.SetNext(self.scenarioSelect)
        self.scenarioSelect.SetPrev(self.loadSelect)
        self.scenarioSelect.SetNext(self.staging)
        self.staging.SetPrev(self.loadSelect)

        self.progressDlg = None
        curPage = self.modSelect

        self.wizard.FitToPage(curPage)

        # Create timer for updates
        timerID = wx.NewId()
        self.updateTimer = wx.Timer(self, timerID)
        self.Bind(wx.EVT_TIMER, self.OnTimedUpdate, id=timerID)
        self.updateTimer.Start(250)

        return True

    def startWizard(self):
        global curPage

        if self.wizard.RunWizard(curPage) and not PB.getDone():
            self.updateTimer.Stop()
            PB.launch()
            return True

        self.updateTimer.Stop()
        PB.quit()
        return False

    def OnTimedUpdate(self, event):
        PB.handleMessages()

    def displayMessageBox(self, title, desc):
        outMsg = title + ":\n" + desc
        PB.consoleOut(outMsg)

    def patchAvailable(self, patchName, patchUrl):
        global curPage

        if curPage == self.login or curPage == self.loadSelect:
            curPage.patchAvailable(patchName, patchUrl)

    def patchProgress(self, bytesRecvd, bytesTotal):
        global bPatchConfirmed

        if not bPatchConfirmed:
            if self.progressDlg == None:
                self.progressDlg = ProgressDialog(self)
                self.progressDlg.Show(True)

            self.progressDlg.setTotal(bytesTotal)
            self.progressDlg.setValue(bytesRecvd)

    def cancelDownload(self):
        global bPatchConfirmed
        bPatchConfirmed = True

        if self.progressDlg != None:
            self.progressDlg.Show(False)
            self.progressDlg = None

        PB.cancelPatchDownload()

    def patchDownloadComplete(self, bSuccess):
        global curPage
        global bPatchConfirmed
        global bPatchOK

        if self.progressDlg != None:
            self.progressDlg.Show(False)
            self.progressDlg = None

        if bSuccess:
            curPage.patchComplete()
        else:
            bPatchOK = False
            msg = wx.MessageBox(localText.getText("TXT_KEY_PITBOSS_PATCH_DOWNLOAD_ERROR_DESC", ()),
                                localText.getText("TXT_KEY_PITBOSS_PATCH_DOWNLOAD_ERROR_TITLE", ()),
                                wx.ICON_ERROR)

        bPatchConfirmed = True
        curPage.enableButtons()

    def upToDate(self):
        global curPage
        global bPatchConfirmed
        global bPatchOK

        bPatchConfirmed = True
        bPatchOK = True

        if curPage == self.login or curPage == self.loadSelect:
            curPage.enableButtons()

    def refreshRow(self, iRow):
        global curPage

        if curPage == self.staging:
            curPage.refreshRow(iRow)

    def refreshCustomMapOptions(self, szMapName):
        global curPage

        if curPage == self.staging:
            curPage.refreshCustomMapOptions(szMapName)

    def refreshAdvancedStartPoints(self, iPoints):
        global curPage

        if curPage == self.staging:
            curPage.refreshAdvancedStartPoints(iPoints)