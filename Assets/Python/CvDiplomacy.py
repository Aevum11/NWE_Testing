## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## Memory-optimized version for 32-bit Caveman2Cosmos mod
from CvPythonExtensions import *

DebugLogging = False  # Adjusted from CvDiplomacyInterface

# Pre-cache global references to save repeated lookups
GC = CyGlobalContext()
GAME = GC.getGame()
ASYNC_RAND = GC.getASyncRand()

# Pre-cache frequently used methods
_getPlayer = GC.getPlayer
_getActivePlayer = GAME.getActivePlayer
_getTeam = GC.getTeam
_getActiveTeam = GAME.getActiveTeam
_getDiplomacyInfo = GC.getDiplomacyInfo
_getInfoTypeForString = GC.getInfoTypeForString
_getTechInfo = GC.getTechInfo
_getNumCivilizationInfos = GC.getNumCivilizationInfos
_getNumLeaderHeadInfos = GC.getNumLeaderHeadInfos
_getMAX_PC_PLAYERS = GC.getMAX_PC_PLAYERS

# Pre-cache all AI comment type strings as constants
_AI_DECLARE_WAR = _getInfoTypeForString("AI_DIPLOCOMMENT_DECLARE_WAR")
_AI_FIRST_CONTACT = _getInfoTypeForString("AI_DIPLOCOMMENT_FIRST_CONTACT")
_AI_NO_VASSAL = _getInfoTypeForString("AI_DIPLOCOMMENT_NO_VASSAL")
_AI_REFUSE_TO_TALK = _getInfoTypeForString("AI_DIPLOCOMMENT_REFUSE_TO_TALK")
_AI_OFFER_CITY = _getInfoTypeForString("AI_DIPLOCOMMENT_OFFER_CITY")
_AI_GIVE_HELP = _getInfoTypeForString("AI_DIPLOCOMMENT_GIVE_HELP")
_AI_OFFER_PEACE = _getInfoTypeForString("AI_DIPLOCOMMENT_OFFER_PEACE")
_AI_OFFER_DEAL = _getInfoTypeForString("AI_DIPLOCOMMENT_OFFER_DEAL")
_AI_OFFER_VASSAL = _getInfoTypeForString("AI_DIPLOCOMMENT_OFFER_VASSAL")
_AI_CANCEL_DEAL = _getInfoTypeForString("AI_DIPLOCOMMENT_CANCEL_DEAL")
_AI_ASK_FOR_HELP = _getInfoTypeForString("AI_DIPLOCOMMENT_ASK_FOR_HELP")
_AI_DEMAND_TRIBUTE = _getInfoTypeForString("AI_DIPLOCOMMENT_DEMAND_TRIBUTE")
_AI_RELIGION_PRESSURE = _getInfoTypeForString("AI_DIPLOCOMMENT_RELIGION_PRESSURE")
_AI_CIVIC_PRESSURE = _getInfoTypeForString("AI_DIPLOCOMMENT_CIVIC_PRESSURE")
_AI_JOIN_WAR = _getInfoTypeForString("AI_DIPLOCOMMENT_JOIN_WAR")
_AI_STOP_TRADING = _getInfoTypeForString("AI_DIPLOCOMMENT_STOP_TRADING")
_AI_MAKE_PEACE_WITH = _getInfoTypeForString("AI_DIPLOCOMMENT_MAKE_PEACE_WITH")
_AI_CURRENT_DEALS = _getInfoTypeForString("AI_DIPLOCOMMENT_CURRENT_DEALS")
_AI_TRADING = _getInfoTypeForString("AI_DIPLOCOMMENT_TRADING")
_AI_TRY_THIS_DEAL = _getInfoTypeForString("AI_DIPLOCOMMENT_TRY_THIS_DEAL")
_AI_NO_DEAL = _getInfoTypeForString("AI_DIPLOCOMMENT_NO_DEAL")
_AI_REJECT = _getInfoTypeForString("AI_DIPLOCOMMENT_REJECT")
_AI_REJECT_ASK = _getInfoTypeForString("AI_DIPLOCOMMENT_REJECT_ASK")
_AI_REJECT_DEMAND = _getInfoTypeForString("AI_DIPLOCOMMENT_REJECT_DEMAND")
_AI_SORRY = _getInfoTypeForString("AI_DIPLOCOMMENT_SORRY")
_AI_SOMETHING_ELSE = _getInfoTypeForString("AI_DIPLOCOMMENT_SOMETHING_ELSE")
_AI_RESEARCH = _getInfoTypeForString("AI_DIPLOCOMMENT_RESEARCH")
_AI_ATTITUDE = _getInfoTypeForString("AI_DIPLOCOMMENT_ATTITUDE")
_AI_ATTITUDE_FURIOUS = _getInfoTypeForString("AI_DIPLOCOMMENT_ATTITUDE_PLAYER_FURIOUS")
_AI_ATTITUDE_ANNOYED = _getInfoTypeForString("AI_DIPLOCOMMENT_ATTITUDE_PLAYER_ANNOYED")
_AI_ATTITUDE_CAUTIOUS = _getInfoTypeForString("AI_DIPLOCOMMENT_ATTITUDE_PLAYER_CAUTIOUS")
_AI_ATTITUDE_PLEASED = _getInfoTypeForString("AI_DIPLOCOMMENT_ATTITUDE_PLAYER_PLEASED")
_AI_ATTITUDE_FRIENDLY = _getInfoTypeForString("AI_DIPLOCOMMENT_ATTITUDE_PLAYER_FRIENDLY")
_AI_TARGET = _getInfoTypeForString("AI_DIPLOCOMMENT_TARGET")
_AI_GREETINGS = _getInfoTypeForString("AI_DIPLOCOMMENT_GREETINGS")
_AI_UNIT_BRAG = _getInfoTypeForString("AI_DIPLOCOMMENT_UNIT_BRAG")
_AI_WORST_ENEMY = _getInfoTypeForString("AI_DIPLOCOMMENT_WORST_ENEMY")
_AI_WORST_ENEMY_TRADING = _getInfoTypeForString("AI_DIPLOCOMMENT_WORST_ENEMY_TRADING")
_AI_NUKES = _getInfoTypeForString("AI_DIPLOCOMMENT_NUKES")
_AI_PEACE = _getInfoTypeForString("AI_DIPLOCOMMENT_PEACE")
_AI_ACCEPT = _getInfoTypeForString("AI_DIPLOCOMMENT_ACCEPT")
_AI_NO_PEACE = _getInfoTypeForString("AI_DIPLOCOMMENT_NO_PEACE")
_AI_GLAD = _getInfoTypeForString("AI_DIPLOCOMMENT_GLAD")
_AI_ACCEPT_ASK = _getInfoTypeForString("AI_DIPLOCOMMENT_ACCEPT_ASK")
_AI_ACCEPT_DEMAND = _getInfoTypeForString("AI_DIPLOCOMMENT_ACCEPT_DEMAND")
_AI_ACCEPT_DEMAND_TEAM = _getInfoTypeForString("AI_DIPLOCOMMENT_ACCEPT_DEMAND_TEAM")
_AI_THANKS = _getInfoTypeForString("AI_DIPLOCOMMENT_THANKS")
_AI_HELP_REFUSED = _getInfoTypeForString("AI_DIPLOCOMMENT_HELP_REFUSED")
_AI_DEMAND_REJECTED = _getInfoTypeForString("AI_DIPLOCOMMENT_DEMAND_REJECTED")
_AI_RELIGION_DENIED = _getInfoTypeForString("AI_DIPLOCOMMENT_RELIGION_DENIED")
_AI_CIVIC_DENIED = _getInfoTypeForString("AI_DIPLOCOMMENT_CIVIC_DENIED")
_AI_JOIN_DENIED = _getInfoTypeForString("AI_DIPLOCOMMENT_JOIN_DENIED")
_AI_STOP_DENIED = _getInfoTypeForString("AI_DIPLOCOMMENT_STOP_DENIED")
_AI_MAKE_PEACE_DENIED = _getInfoTypeForString("AI_DIPLOCOMMENT_MAKE_PEACE_DENIED")
_AI_WELL = _getInfoTypeForString("AI_DIPLOCOMMENT_WELL")
_AI_RESEARCH_TECH = _getInfoTypeForString("AI_DIPLOCOMMENT_RESEARCH_TECH")
_AI_TARGET_CITY = _getInfoTypeForString("AI_DIPLOCOMMENT_TARGET_CITY")
_AI_ASSUME_REALLY_SNUFFED = _getInfoTypeForString("AI_ASSUME_REALLY_SNUFFED")
_AI_ASSUME_SNUFFED = _getInfoTypeForString("AI_ASSUME_SNUFFED")
_AI_ASSUME_NOT_SNUFFED = _getInfoTypeForString("AI_ASSUME_NOT_SNUFFED")
_AI_RESUME_TALKS_RELUCTANT = _getInfoTypeForString("AI_RESUME_TALKS_RELUCTANT")
_AI_RESUME_TALKS = _getInfoTypeForString("AI_RESUME_TALKS")
_AI_RESUME_TALKS_GLADLY = _getInfoTypeForString("AI_RESUME_TALKS_GLADLY")

# Pre-cache user comment strings
_USER_WAR_RESPONSE = "USER_DIPLOCOMMENT_WAR_RESPONSE"
_USER_WAR = "USER_DIPLOCOMMENT_WAR"
_USER_PEACE = "USER_DIPLOCOMMENT_PEACE"
_USER_EXIT = "USER_DIPLOCOMMENT_EXIT"
_USER_ACCEPT_OFFER = "USER_DIPLOCOMMENT_ACCEPT_OFFER"
_USER_REJECT_OFFER = "USER_DIPLOCOMMENT_REJECT_OFFER"
_USER_RENEGOTIATE = "USER_DIPLOCOMMENT_RENEGOTIATE"
_USER_NO_RENEGOTIATE = "USER_DIPLOCOMMENT_NO_RENEGOTIATE"
_USER_GIVE_HELP = "USER_DIPLOCOMMENT_GIVE_HELP"
_USER_REFUSE_HELP = "USER_DIPLOCOMMENT_REFUSE_HELP"
_USER_ACCEPT_DEMAND = "USER_DIPLOCOMMENT_ACCEPT_DEMAND"
_USER_REJECT_DEMAND = "USER_DIPLOCOMMENT_REJECT_DEMAND"
_USER_CONVERT = "USER_DIPLOCOMMENT_CONVERT"
_USER_NO_CONVERT = "USER_DIPLOCOMMENT_NO_CONVERT"
_USER_REVOLUTION = "USER_DIPLOCOMMENT_REVOLUTION"
_USER_NO_REVOLUTION = "USER_DIPLOCOMMENT_NO_REVOLUTION"
_USER_JOIN_WAR = "USER_DIPLOCOMMENT_JOIN_WAR"
_USER_NO_JOIN_WAR = "USER_DIPLOCOMMENT_NO_JOIN_WAR"
_USER_STOP_TRADING = "USER_DIPLOCOMMENT_STOP_TRADING"
_USER_NO_STOP_TRADING = "USER_DIPLOCOMMENT_NO_STOP_TRADING"
_USER_MAKE_PEACE_WITH = "USER_DIPLOCOMMENT_MAKE_PEACE_WITH"
_USER_NO_MAKE_PEACE_WITH = "USER_DIPLOCOMMENT_NO_MAKE_PEACE_WITH"
_USER_NEVERMIND = "USER_DIPLOCOMMENT_NEVERMIND"
_USER_PROPOSE = "USER_DIPLOCOMMENT_PROPOSE"
_USER_OFFER_PEACE = "USER_DIPLOCOMMENT_OFFER_PEACE"
_USER_ACCEPT = "USER_DIPLOCOMMENT_ACCEPT"
_USER_REJECT = "USER_DIPLOCOMMENT_REJECT"
_USER_COMPLETE_DEAL = "USER_DIPLOCOMMENT_COMPLETE_DEAL"
_USER_DEMAND_TEAM = "USER_DIPLOCOMMENT_DEMAND_TEAM"
_USER_OFFER = "USER_DIPLOCOMMENT_OFFER"
_USER_VASSAL_TRIBUTE = "USER_DIPLOCOMMENT_VASSAL_TRIBUTE"
_USER_ASK = "USER_DIPLOCOMMENT_ASK"
_USER_DEMAND = "USER_DIPLOCOMMENT_DEMAND"
_USER_FISH_FOR_DEAL = "USER_DIPLOCOMMENT_FISH_FOR_DEAL"
_USER_GIFT = "USER_DIPLOCOMMENT_GIFT"
_USER_SUGGEST_PEACE = "USER_DIPLOCOMMENT_SUGGEST_PEACE"
_USER_CURRENT_DEALS = "USER_DIPLOCOMMENT_CURRENT_DEALS"
_USER_PROPOSAL = "USER_DIPLOCOMMENT_PROPOSAL"
_USER_ATTITUDE = "USER_DIPLOCOMMENT_ATTITUDE"
_USER_RESEARCH = "USER_DIPLOCOMMENT_RESEARCH"
_USER_TARGET = "USER_DIPLOCOMMENT_TARGET"
_USER_RESUME_TALKS = "USER_RESUME_TALKS"
_USER_DO_NOT_BOTHER_US = "USER_DO_NOT_BOTHER_US"
_USER_SOMETHING_ELSE = "USER_DIPLOCOMMENT_SOMETHING_ELSE"
_USER_RESEARCH_TECH = "USER_DIPLOCOMMENT_RESEARCH_TECH"
_USER_ATTITUDE_PLAYER = "USER_DIPLOCOMMENT_ATTITUDE_PLAYER"
_USER_TARGET_CITY = "USER_DIPLOCOMMENT_TARGET_CITY"

# Pre-build sets for fast membership testing
_AI_OFFER_TYPES = frozenset((_AI_OFFER_PEACE, _AI_OFFER_DEAL, _AI_OFFER_VASSAL))
_AI_TRADING_TYPES = frozenset((_AI_TRADING, _AI_REJECT, _AI_TRY_THIS_DEAL, _AI_SORRY,
                               _AI_NO_DEAL, _AI_REJECT_ASK, _AI_REJECT_DEMAND))
_AI_DEFAULT_TYPES = frozenset((_AI_GREETINGS, _AI_UNIT_BRAG, _AI_WORST_ENEMY_TRADING,
                               _AI_WORST_ENEMY, _AI_NUKES))
_AI_ATTITUDE_TYPES = frozenset((_AI_ATTITUDE_FURIOUS, _AI_ATTITUDE_ANNOYED, _AI_ATTITUDE,
                                _AI_ATTITUDE_CAUTIOUS, _AI_ATTITUDE_FRIENDLY, _AI_ATTITUDE_PLEASED))
_AI_ASSUME_TYPES = frozenset((_AI_ASSUME_REALLY_SNUFFED, _AI_ASSUME_SNUFFED, _AI_ASSUME_NOT_SNUFFED))
_AI_RESUME_TYPES = frozenset((_AI_RESUME_TALKS_RELUCTANT, _AI_RESUME_TALKS, _AI_RESUME_TALKS_GLADLY))


class CvDiplomacy:
    "Code used by Civ Diplomacy interface - memory optimized"

    # Use __slots__ to reduce memory overhead by ~100-200 bytes per instance
<<<<<<< Updated upstream
    __slots__ = ('iLastResponseID', 'diploScreen', '_comment_handlers')
=======
    __slots__ = ('iLastResponseID', 'diploScreen', '_comment_handlers', '_lastAIComment')
>>>>>>> Stashed changes

    def __init__(self):
        "constructor - set up class vars, AI and User strings"
        if DebugLogging:
            print "Launching Diplomacy"
        self.iLastResponseID = -1
        self.diploScreen = CyDiplomacy()
<<<<<<< Updated upstream
=======
        self._lastAIComment = None
>>>>>>> Stashed changes

        # Pre-build handler dispatch dictionary for determineResponses
        # This replaces long if-elif chains with O(1) dictionary lookup
        self._comment_handlers = {
            _AI_DECLARE_WAR: self._handleDeclareWar,
            _AI_FIRST_CONTACT: self._handleFirstContact,
            _AI_NO_VASSAL: self._handleFirstContact,
            _AI_REFUSE_TO_TALK: self._handleRefuseToTalk,
            _AI_OFFER_CITY: self._handleOffer,
            _AI_GIVE_HELP: self._handleOffer,
            _AI_CANCEL_DEAL: self._handleCancelDeal,
            _AI_ASK_FOR_HELP: self._handleDemand,
            _AI_DEMAND_TRIBUTE: self._handleDemandTribute,
            _AI_RELIGION_PRESSURE: self._handleReligionPressure,
            _AI_CIVIC_PRESSURE: self._handleCivicPressure,
            _AI_JOIN_WAR: self._handleJoinWar,
            _AI_STOP_TRADING: self._handleStopTrading,
            _AI_MAKE_PEACE_WITH: self._handleMakePeace,
            _AI_CURRENT_DEALS: self._handleCurrentDeals,
            _AI_SOMETHING_ELSE: self._handleSomethingElse,
            _AI_RESEARCH: self._handleResearch,
            _AI_TARGET: self._handleTarget
        }

    def determineResponses(self, eComment):
        "Will determine the user responses given an AI comment"
        if DebugLogging:
            szType = _getDiplomacyInfo(eComment).getType()
            print "CvDiplomacy.determineResponses: \n\t%s\n\t%s" % (eComment, szType)

        # Eliminate previous comments
        self.diploScreen.clearUserComments()

        # Use dispatch dictionary for O(1) lookup instead of long if-elif chain
        handler = self._comment_handlers.get(eComment)
        if handler:
            handler()
        elif eComment in _AI_OFFER_TYPES:
            self._handleOfferDeal()
        elif eComment in _AI_TRADING_TYPES:
            self._handleTrading()
        elif eComment in _AI_ATTITUDE_TYPES:
            self._handleAttitude()
        else:
            self._handleDefault()

    # Handler methods for different comment types - reduces code duplication
    def _handleDeclareWar(self):
        self.addUserComment(_USER_WAR_RESPONSE)
        self.diploScreen.endTrade()

    def _handleFirstContact(self):
        if _getTeam(_getActiveTeam()).canDeclareWar(_getPlayer(self.diploScreen.getWhoTradingWith()).getTeam()):
            self.addUserComment(_USER_WAR)
        self.addUserComment(_USER_PEACE)
        self.diploScreen.endTrade()

    def _handleRefuseToTalk(self):
        self.addUserComment(_USER_EXIT)
        self.diploScreen.endTrade()

    def _handleOffer(self):
        self.addUserComment(_USER_ACCEPT_OFFER)
        self.addUserComment(_USER_REJECT_OFFER)

    def _handleOfferDeal(self):
        self.addUserComment(_USER_ACCEPT_OFFER)
        self.addUserComment(_USER_RENEGOTIATE)
        self.addUserComment(_USER_REJECT_OFFER)

    def _handleCancelDeal(self):
        self.addUserComment(_USER_RENEGOTIATE)
        self.addUserComment(_USER_NO_RENEGOTIATE)

    def _handleDemand(self):
        self.addUserComment(_USER_GIVE_HELP)
        self.addUserComment(_USER_REFUSE_HELP)

    def _handleDemandTribute(self):
        self.addUserComment(_USER_ACCEPT_DEMAND)
        self.addUserComment(_USER_REJECT_DEMAND)

    def _handleReligionPressure(self):
        self.addUserComment(_USER_CONVERT)
        self.addUserComment(_USER_NO_CONVERT)

    def _handleCivicPressure(self):
        self.addUserComment(_USER_REVOLUTION)
        self.addUserComment(_USER_NO_REVOLUTION)

    def _handleJoinWar(self):
        self.addUserComment(_USER_JOIN_WAR)
        self.addUserComment(_USER_NO_JOIN_WAR)

    def _handleStopTrading(self):
        self.addUserComment(_USER_STOP_TRADING)
        self.addUserComment(_USER_NO_STOP_TRADING)

    def _handleMakePeace(self):
        self.addUserComment(_USER_MAKE_PEACE_WITH)
        self.addUserComment(_USER_NO_MAKE_PEACE_WITH)

    def _handleCurrentDeals(self):
        self.addUserComment(_USER_NEVERMIND)
        self.addUserComment(_USER_EXIT)
        self.diploScreen.startTrade(_AI_CURRENT_DEALS, True)

    def _handleTrading(self):
        # Cache these checks to avoid repeated method calls
        bOurOfferEmpty = self.diploScreen.ourOfferEmpty()
        bTheirOfferEmpty = self.diploScreen.theirOfferEmpty()

        if bOurOfferEmpty and bTheirOfferEmpty:
            if self.diploScreen.atWar():
                self.addUserComment(_USER_PROPOSE)
                self.addUserComment(_USER_OFFER_PEACE)

        if not (bOurOfferEmpty and bTheirOfferEmpty):
            if self.diploScreen.isAIOffer():
                self.addUserComment(_USER_ACCEPT)
                self.addUserComment(_USER_REJECT)
            else:
                if not bOurOfferEmpty and not bTheirOfferEmpty:
                    self.addUserComment(_USER_PROPOSE)
                    if not self.diploScreen.atWar():
                        if _getActiveTeam() != _getPlayer(self.diploScreen.getWhoTradingWith()).getTeam():
                            self.addUserComment(_USER_COMPLETE_DEAL)
                elif not bTheirOfferEmpty:
                    if self.diploScreen.atWar():
                        self.addUserComment(_USER_PROPOSE)
                    else:
                        CyPlayer = _getPlayer(self.diploScreen.getWhoTradingWith())
                        iTeam = CyPlayer.getTeam()
                        iTeamAct = _getActiveTeam()

                        if iTeamAct == iTeam:
                            self.addUserComment(_USER_DEMAND_TEAM)
                        else:
                            CyTeam = _getTeam(iTeam)
                            self.addUserComment(_USER_OFFER)
                            bVassal = CyTeam.isVassal(iTeamAct)
                            if bVassal and self.diploScreen.theirVassalTribute():
                                self.addUserComment(_USER_VASSAL_TRIBUTE)
                            elif CyPlayer.AI_getAttitude(_getActivePlayer()) >= AttitudeTypes.ATTITUDE_PLEASED:
                                self.addUserComment(_USER_ASK)
                            elif bVassal or _getTeam(iTeamAct).canDeclareWar(iTeam):
                                self.addUserComment(_USER_DEMAND)
                else:
                    if self.diploScreen.atWar():
                        self.addUserComment(_USER_PROPOSE)
                    else:
                        if _getActiveTeam() != _getPlayer(self.diploScreen.getWhoTradingWith()).getTeam():
                            self.addUserComment(_USER_FISH_FOR_DEAL)
                        self.addUserComment(_USER_GIFT)

        self.addUserComment(_USER_NEVERMIND)
        self.addUserComment(_USER_EXIT)
        self.diploScreen.startTrade(_AI_TRADING, False)

    def _handleSomethingElse(self):
        iTeamAct = _getActiveTeam()
        CyTeamAct = _getTeam(iTeamAct)
        iTeam = _getPlayer(self.diploScreen.getWhoTradingWith()).getTeam()

        if CyTeamAct.canDeclareWar(iTeam):
            self.addUserComment(_USER_WAR)

        self.addUserComment(_USER_ATTITUDE)

        if iTeamAct == iTeam or _getTeam(iTeam).isVassal(iTeamAct):
            self.addUserComment(_USER_RESEARCH)

        if CyTeamAct.AI_shareWar(iTeam):
            self.addUserComment(_USER_TARGET)

        self.addUserComment(_USER_NEVERMIND)
        self.addUserComment(_USER_EXIT)

    def _handleResearch(self):
        player = _getPlayer(self.diploScreen.getWhoTradingWith())
        team = _getTeam(player.getTeam())
        for i in xrange(team.getNumAdjacentResearch()):
            iTechX = team.getAdjacentResearch(i)
            if player.canResearch(iTechX, True, True):
                self.addUserComment(_USER_RESEARCH_TECH, iTechX, -1, _getTechInfo(iTechX).getTextKey())

        self.addUserComment(_USER_SOMETHING_ELSE)
        self.addUserComment(_USER_EXIT)

    def _handleAttitude(self):
        iPlayerAct = _getActivePlayer()
        CyTeamAct = _getTeam(_getActiveTeam())
        iPlayer = self.diploScreen.getWhoTradingWith()
        CyTeam = _getTeam(_getPlayer(iPlayer).getTeam())

        for iPlayerX in xrange(_getMAX_PC_PLAYERS()):
            if iPlayerX in (iPlayerAct, iPlayer):
                continue
            CyPlayerX = _getPlayer(iPlayerX)
            if CyPlayerX.isAlive():
                iTeamX = CyPlayerX.getTeam()
                if CyTeamAct.isHasMet(iTeamX) and CyTeam.isHasMet(iTeamX):
                    self.addUserComment(_USER_ATTITUDE_PLAYER, iPlayerX, -1, CyPlayerX.getNameKey())

        self.addUserComment(_USER_SOMETHING_ELSE)
        self.addUserComment(_USER_EXIT)

    def _handleTarget(self):
        iTeamAct = _getActiveTeam()
        CyTeamAct = _getTeam(iTeamAct)
        for iPlayerX in xrange(_getMAX_PC_PLAYERS()):
            CyPlayerX = _getPlayer(iPlayerX)
            if CyPlayerX.isAlive() and CyTeamAct.isAtWarWith(CyPlayerX.getTeam()):
                for CyCity in CyPlayerX.cities():
                    if CyCity.isRevealed(iTeamAct, False):
                        self.addUserComment(_USER_TARGET_CITY, iPlayerX, CyCity.getID(), CyCity.getNameKey())

        self.addUserComment(_USER_SOMETHING_ELSE)
        self.addUserComment(_USER_EXIT)

    def _handleDefault(self):
        iPlayerAct = _getActivePlayer()
        iPlayer = self.diploScreen.getWhoTradingWith()
        CyPlayer = _getPlayer(iPlayer)

        if _getPlayer(iPlayerAct).canTradeWith(iPlayer):
            self.addUserComment(_USER_PROPOSAL)

        if self.diploScreen.atWar():
            self.addUserComment(_USER_SUGGEST_PEACE)

        if self.diploScreen.hasAnnualDeal():
            self.addUserComment(_USER_CURRENT_DEALS)

        self.addUserComment(_USER_SOMETHING_ELSE)

        if CyPlayer and not GAME.isNetworkMultiPlayer():
<<<<<<< Updated upstream
            eComment = self.iLastResponseID # Corrected line: use the instance variable
=======
            eComment = self._lastAIComment
>>>>>>> Stashed changes
            if eComment in _AI_ASSUME_TYPES:
                self.addUserComment(_USER_RESUME_TALKS)
            elif eComment in _AI_RESUME_TYPES:
                self.addUserComment(_USER_DO_NOT_BOTHER_US, iPlayerAct)
            elif CyPlayer.isDoNotBotherStatus(iPlayerAct):
                self.addUserComment(_USER_RESUME_TALKS)
            else:
                self.addUserComment(_USER_DO_NOT_BOTHER_US, iPlayerAct)

        self.addUserComment(_USER_EXIT)
        self.diploScreen.endTrade()

    def addUserComment(self, szType, iData1=-1, iData2=-1, *args):
        "Helper for adding User Comments"
        iComment = _getInfoTypeForString(szType)
        self.diploScreen.addUserComment(iComment, iData1, iData2, self.getDiplomacyComment(iComment), args)

    def setAIComment(self, eComment, *args):
        "Handles the determining the AI comments"
        AIString = self.getDiplomacyComment(eComment)

        if DebugLogging:
            print "CvDiplomacy.setAIComment: %s" % (eComment,)
            if args:
                print "args", args
            AIString = "(%d) - %s" % (self.iLastResponseID, AIString)

        self.diploScreen.setAIString(AIString, args)
        self.diploScreen.setAIComment(eComment)
<<<<<<< Updated upstream
=======
        self._lastAIComment = eComment
>>>>>>> Stashed changes
        self.determineResponses(eComment)

    def getDiplomacyComment(self, eComment):
        "Function to get the user String"
        eComment = int(eComment)
        if DebugLogging:
            print "CvDiplomacy.getDiplomacyComment:", eComment

        CvDiplomacyInfo = _getDiplomacyInfo(eComment)
        if CvDiplomacyInfo:
            return self.filterUserResponse(CvDiplomacyInfo)
        else:
            print "CvDiplomacy.getDiplomacyComment: %s does not exist!" % (eComment,)
            return "Error***: No string found for eComment: %s" % eComment

    def isUsed(self, var, i, num):
        "returns True if any element in the var list is True"
        for j in xrange(num):
            if var(i, j):
                return True
        return False

    def filterUserResponse(self, diploInfo):
        "pick the user's response from a CvDiplomacyTextInfo, based on response conditions"
        iPlayer = self.diploScreen.getWhoTradingWith()
        if iPlayer == -1:
            return ""

        # Pre-cache commonly used values
        CyPlayer = _getPlayer(iPlayer)
        iCiv = CyPlayer.getCivilizationType()
        iLeader = CyPlayer.getLeaderType()
        CyPlayerAct = _getPlayer(_getActivePlayer())
        iPlayerAct = CyPlayerAct.getID()
        iAttitude = CyPlayer.AI_getAttitude(iPlayerAct)

        # Power comparison - calculate once
        iTheirPower = CyPlayer.getPower()
        iOurPower = CyPlayerAct.getPower()
        bUsSuperior = iOurPower > iTheirPower * 2
        bUsInferior = iOurPower < iTheirPower / 2

        responses = []
        for i in xrange(diploInfo.getNumResponses()):
            # Early exit checks
            if self.isUsed(diploInfo.getAttitudeTypes, i, AttitudeTypes.NUM_ATTITUDE_TYPES):
                if not diploInfo.getAttitudeTypes(i, iAttitude):
                    continue

            if self.isUsed(diploInfo.getCivilizationTypes, i, _getNumCivilizationInfos()):
                if not diploInfo.getCivilizationTypes(i, iCiv):
                    continue

            if self.isUsed(diploInfo.getLeaderHeadTypes, i, _getNumLeaderHeadInfos()):
                if not diploInfo.getLeaderHeadTypes(i, iLeader):
                    continue

            if self.isUsed(diploInfo.getDiplomacyPowerTypes, i, DiplomacyPowerTypes.NUM_DIPLOMACYPOWER_TYPES):
<<<<<<< Updated upstream
                if bUsInferior and not diploInfo.getDiplomacyPowerTypes(i, DiplomacyPowerTypes.DIPLOMACYPOWER_STRONGER):
                    continue
                elif bUsSuperior and not diploInfo.getDiplomacyPowerTypes(i, DiplomacyPowerTypes.DIPLOMACYPOWER_WEAKER):
                    continue
                elif diploInfo.getDiplomacyPowerTypes(i, DiplomacyPowerTypes.DIPLOMACYPOWER_EQUAL):
=======
                bEqual = not bUsInferior and not bUsSuperior
                if bUsInferior and not diploInfo.getDiplomacyPowerTypes(i, DiplomacyPowerTypes.DIPLOMACYPOWER_STRONGER):
                    continue
                if bUsSuperior and not diploInfo.getDiplomacyPowerTypes(i, DiplomacyPowerTypes.DIPLOMACYPOWER_WEAKER):
                    continue
                if bEqual and not diploInfo.getDiplomacyPowerTypes(i, DiplomacyPowerTypes.DIPLOMACYPOWER_EQUAL):
>>>>>>> Stashed changes
                    continue

            # Passed all tests, extend responses list efficiently
            responses.extend([diploInfo.getDiplomacyText(i, j) for j in xrange(diploInfo.getNumDiplomacyText(i))])

        # Pick a random response
        if responses:
            iResponse = ASYNC_RAND.get(len(responses), "Python Diplomacy ASYNC")
            self.iLastResponseID = iResponse
            return responses[iResponse]

        return ""  # no responses matched

    def handleUserResponse(self, eComment, iData1, iData2):
        if DebugLogging:
            print "CvDiplomacy.handleUserResponse: %s" % (eComment,)

        diploScreen = self.diploScreen  # Cache reference
        szType = _getDiplomacyInfo(eComment).getType()

        # Build dispatch dictionary for user responses
        # Using a static method dispatch would save memory but Python 2.4 doesn't support it well
        # So we use direct conditionals with early exits

        if szType == "USER_DIPLOCOMMENT_PEACE":
            self.setAIComment(_AI_PEACE)
        elif szType == "USER_DIPLOCOMMENT_WAR":
            diploScreen.declareWar()
        elif szType in ("USER_DIPLOCOMMENT_PROPOSAL", "USER_DIPLOCOMMENT_RENEGOTIATE"):
            self.setAIComment(_AI_TRADING)
            diploScreen.showAllTrade(True)
        elif szType == "USER_DIPLOCOMMENT_PROPOSE":
            if diploScreen.offerDeal():
                self.setAIComment(_AI_ACCEPT)
            else:
                self.setAIComment(_AI_REJECT)
        elif szType == "USER_DIPLOCOMMENT_SUGGEST_PEACE":
            if diploScreen.offerDeal():
                self.setAIComment(_AI_PEACE)
            else:
                self.setAIComment(_AI_NO_PEACE)
        elif szType == "USER_DIPLOCOMMENT_ACCEPT":
            diploScreen.implementDeal()
            diploScreen.setAIOffer(0)
            self.setAIComment(_AI_GLAD)
        elif szType == "USER_DIPLOCOMMENT_REJECT":
            diploScreen.setAIOffer(0)
            self.setAIComment(_AI_SORRY)
        elif szType in ("USER_DIPLOCOMMENT_OFFER", "USER_DIPLOCOMMENT_COMPLETE_DEAL",
                        "USER_DIPLOCOMMENT_FISH_FOR_DEAL", "USER_DIPLOCOMMENT_OFFER_PEACE"):
            if diploScreen.counterPropose():
                self.setAIComment(_AI_TRY_THIS_DEAL)
            else:
                self.setAIComment(_AI_NO_DEAL)
        elif szType == "USER_DIPLOCOMMENT_ASK":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_ASK_HELP, -1, -1)
            if diploScreen.offerDeal():
                self.setAIComment(_AI_ACCEPT_ASK)
            else:
                self.setAIComment(_AI_REJECT_ASK)
        elif szType == "USER_DIPLOCOMMENT_DEMAND":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_MADE_DEMAND, -1, -1)
            if diploScreen.offerDeal():
                self.setAIComment(_AI_ACCEPT_DEMAND)
            else:
                self.setAIComment(_AI_REJECT_DEMAND)
        elif szType == "USER_DIPLOCOMMENT_VASSAL_TRIBUTE":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_MADE_DEMAND_VASSAL, -1, -1)
            if diploScreen.offerDeal():
                self.setAIComment(_AI_ACCEPT_DEMAND)
            else:
                self.setAIComment(_AI_DECLARE_WAR)
                diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_DEMAND_WAR, -1, -1)
        elif szType == "USER_DIPLOCOMMENT_DEMAND_TEAM":
            diploScreen.offerDeal()
            self.setAIComment(_AI_ACCEPT_DEMAND_TEAM)
        elif szType == "USER_DIPLOCOMMENT_GIFT":
            diploScreen.offerDeal()
            self.setAIComment(_AI_THANKS)
        elif szType == "USER_DIPLOCOMMENT_CURRENT_DEALS":
            self.setAIComment(_AI_CURRENT_DEALS)
            diploScreen.showAllTrade(False)
        elif szType == "USER_DIPLOCOMMENT_GIVE_HELP":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_GIVE_HELP, -1, -1)
            diploScreen.implementDeal()
            diploScreen.setAIOffer(0)
            self.setAIComment(_AI_THANKS)
        elif szType == "USER_DIPLOCOMMENT_ACCEPT_DEMAND":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_ACCEPT_DEMAND, -1, -1)
            diploScreen.implementDeal()
            diploScreen.setAIOffer(0)
            self.setAIComment(_AI_THANKS)
        elif szType == "USER_DIPLOCOMMENT_ACCEPT_OFFER":
            diploScreen.implementDeal()
            diploScreen.setAIOffer(0)
            self.setAIComment(_AI_THANKS)
        elif szType == "USER_DIPLOCOMMENT_REFUSE_HELP":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_REFUSED_HELP, -1, -1)
            self.setAIComment(_AI_HELP_REFUSED)
        elif szType == "USER_DIPLOCOMMENT_REJECT_DEMAND":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_REJECTED_DEMAND, -1, -1)
            CyPlayer = _getPlayer(self.diploScreen.getWhoTradingWith())
            if CyPlayer.AI_demandRebukedWar(_getActivePlayer()):
                self.setAIComment(_AI_DECLARE_WAR)
                diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_DEMAND_WAR, -1, -1)
            else:
                self.setAIComment(_AI_DEMAND_REJECTED)
        elif szType == "USER_DIPLOCOMMENT_CONVERT":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_CONVERT, -1, -1)
            self.setAIComment(_AI_THANKS)
        elif szType == "USER_DIPLOCOMMENT_NO_CONVERT":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_NO_CONVERT, -1, -1)
            self.setAIComment(_AI_RELIGION_DENIED)
        elif szType == "USER_DIPLOCOMMENT_REVOLUTION":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_REVOLUTION, -1, -1)
            self.setAIComment(_AI_THANKS)
        elif szType == "USER_DIPLOCOMMENT_NO_REVOLUTION":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_NO_REVOLUTION, -1, -1)
            self.setAIComment(_AI_CIVIC_DENIED)
        elif szType == "USER_DIPLOCOMMENT_JOIN_WAR":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_JOIN_WAR, diploScreen.getData(), -1)
            self.setAIComment(_AI_THANKS)
        elif szType == "USER_DIPLOCOMMENT_NO_JOIN_WAR":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_NO_JOIN_WAR, -1, -1)
            self.setAIComment(_AI_JOIN_DENIED)
        elif szType == "USER_DIPLOCOMMENT_STOP_TRADING":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_STOP_TRADING, diploScreen.getData(), -1)
            self.setAIComment(_AI_THANKS)
        elif szType == "USER_DIPLOCOMMENT_NO_STOP_TRADING":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_NO_STOP_TRADING, -1, -1)
            self.setAIComment(_AI_STOP_DENIED)
        elif szType == "USER_DIPLOCOMMENT_MAKE_PEACE_WITH":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_MAKE_PEACE_WITH, diploScreen.getData(), -1)
            self.setAIComment(_AI_THANKS)
        elif szType == "USER_DIPLOCOMMENT_NO_MAKE_PEACE_WITH":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_NO_MAKE_PEACE_WITH, diploScreen.getData(), -1)
            self.setAIComment(_AI_MAKE_PEACE_DENIED)
        elif szType == "USER_DIPLOCOMMENT_NEVERMIND":
            self.setAIComment(_AI_WELL)
        elif szType == "USER_DIPLOCOMMENT_SOMETHING_ELSE":
            self.setAIComment(_AI_SOMETHING_ELSE)
        elif szType == "USER_DIPLOCOMMENT_RESEARCH":
            self.setAIComment(_AI_RESEARCH)
        elif szType == "USER_DIPLOCOMMENT_RESEARCH_TECH":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_RESEARCH_TECH, iData1, -1)
            self.setAIComment(_AI_RESEARCH_TECH)
        elif szType == "USER_DIPLOCOMMENT_ATTITUDE":
            self.setAIComment(_AI_ATTITUDE)
        elif szType == "USER_DIPLOCOMMENT_ATTITUDE_PLAYER":
            CyPlayer = _getPlayer(self.diploScreen.getWhoTradingWith())
            eAttitude = CyPlayer.AI_getAttitude(iData1)
            nameKey = _getPlayer(iData1).getNameKey()

            # Use tuple for attitude mapping
            attitude_map = (
                (AttitudeTypes.ATTITUDE_FURIOUS, _AI_ATTITUDE_FURIOUS),
                (AttitudeTypes.ATTITUDE_ANNOYED, _AI_ATTITUDE_ANNOYED),
                (AttitudeTypes.ATTITUDE_CAUTIOUS, _AI_ATTITUDE_CAUTIOUS),
                (AttitudeTypes.ATTITUDE_PLEASED, _AI_ATTITUDE_PLEASED)
            )

            for att_type, ai_comment in attitude_map:
                if eAttitude == att_type:
                    self.setAIComment(ai_comment, nameKey)
                    break
            else:
                self.setAIComment(_AI_ATTITUDE_FRIENDLY, nameKey)
        elif szType == "USER_DIPLOCOMMENT_TARGET":
            self.setAIComment(_AI_TARGET)
        elif szType == "USER_DIPLOCOMMENT_TARGET_CITY":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_TARGET_CITY, iData1, iData2)
            self.setAIComment(_AI_TARGET_CITY)
        elif szType == "USER_DO_NOT_BOTHER_US":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_DO_NOT_BOTHER, iData1, -1)
            CyPlayer = _getPlayer(self.diploScreen.getWhoTradingWith())
            eAttitude = CyPlayer.AI_getAttitude(_getActivePlayer())

            if eAttitude in (AttitudeTypes.ATTITUDE_FURIOUS, AttitudeTypes.ATTITUDE_ANNOYED):
                self.setAIComment(_AI_ASSUME_REALLY_SNUFFED)
            elif eAttitude == AttitudeTypes.ATTITUDE_CAUTIOUS:
                self.setAIComment(_AI_ASSUME_SNUFFED)
            else:
                self.setAIComment(_AI_ASSUME_NOT_SNUFFED)
        elif szType == "USER_RESUME_TALKS":
            diploScreen.diploEvent(DiploEventTypes.DIPLOEVENT_RESUME_BOTHER, -1, -1)
            CyPlayer = _getPlayer(self.diploScreen.getWhoTradingWith())
            eAttitude = CyPlayer.AI_getAttitude(_getActivePlayer())

            if eAttitude in (AttitudeTypes.ATTITUDE_FURIOUS, AttitudeTypes.ATTITUDE_ANNOYED):
                self.setAIComment(_AI_RESUME_TALKS_RELUCTANT)
            elif eAttitude == AttitudeTypes.ATTITUDE_CAUTIOUS:
                self.setAIComment(_AI_RESUME_TALKS)
            else:
                self.setAIComment(_AI_RESUME_TALKS_GLADLY)
        else:
            diploScreen.closeScreen()

    def dealCanceled(self):  # Called by CvDiplomacyInterface
        self.setAIComment(_AI_TRADING)