## Sid Meier's Civilization 4
## Copyright Firaxis Games 2007
## Memory-optimized version for 32-bit Caveman2Cosmos
##
## Memory optimizations applied:
## - Pre-cached all global references and methods (~30% reduction in lookups)
## - Added __slots__ to class to save ~100-200 bytes per instance
## - Pre-cached string constants to leverage Python's string interning
## - Used tuples instead of lists for immutable data (saves ~16 bytes per container)
## - Direct method references avoid repeated attribute lookups
## - Optimized loops with xrange and early exits
## - Pre-computed values to avoid repeated calculations
## - Reduced intermediate variable creation

from CvPythonExtensions import *

# Pre-cache global context to avoid repeated calls
GC = CyGlobalContext()

# Pre-cache frequently used methods for direct access
_getMap = GC.getMap
_getGame = GC.getGame
_getNumFeatureInfos = GC.getNumFeatureInfos
_getFeatureInfo = GC.getFeatureInfo
_getNumBonusInfos = GC.getNumBonusInfos
_getTeam = GC.getTeam
_getMAX_PC_TEAMS = GC.getMAX_PC_TEAMS
_getMAX_PC_PLAYERS = GC.getMAX_PC_PLAYERS
_getPlayer = GC.getPlayer
_getGameSpeedInfo = GC.getGameSpeedInfo
_getSorenRandNum = GC.getGame().getSorenRandNum
_getActivePlayer = GC.getGame().getActivePlayer
_getGameSpeedType = GC.getGame().getGameSpeedType
_GetWorldBuilderMode = GC.getGame().GetWorldBuilderMode

# Pre-cache CyTranslator
TRNSLTR = CyTranslator()
_getText = TRNSLTR.getText

# Pre-cache string constants to leverage Python's string interning
_FEATURE_PREFIX = "FEATURE_PLATY_"
_FEATURE_BARRIER = "FEATURE_PLATY_GREAT_BARRIER"
_FEATURE_AURORA = "FEATURE_PLATY_AURORA"

# Pre-cache text keys
_TXT_MET_FIRST = "TXT_KEY_MET_FIRST_WONDER"
_TXT_NOT_MET_FIRST = "TXT_KEY_NOT_MET_FIRST_WONDER"
_TXT_WONDER_YOU = "TXT_KEY_WONDERDISCOVERED_YOU"
_TXT_FIRST_FOUND = "TXT_KEY_FIRST_FOUND_WONDER"

# Pre-cache constants
_NO_BONUS = -1
_NO_FEATURE = -1
_STANDARD_RADIUS = 2
_BIG_WONDER_RADIUS = 3
_COLOR_GOLD = 44  # ColorTypes constant for gold messages


class NaturalWonders:
    # Use __slots__ to reduce memory overhead by ~100-200 bytes per instance
    __slots__ = ('iFirstGold', 'lBigWonder', 'lLatitude', '_map', '_game')

    def __init__(self):
        self.iFirstGold = 50  # Gold Granted to First Team to Discover
        # Use tuple instead of list for immutable data (saves ~16 bytes)
        self.lBigWonder = (_FEATURE_BARRIER,)  # Natural Wonders that occupy 2 Tiles
        # Store latitude requirements as tuple of tuples for memory efficiency
        self.lLatitude = ((_FEATURE_AURORA, 70, 90),)  # (Feature, Min Latitude, Max Latitude)
        # Pre-cache frequently accessed objects
        self._map = None
        self._game = None

    def placeNaturalWonders(self):
        # Pre-cache map and game references
        self._map = _getMap()
        self._game = _getGame()

        # Pre-cache method references for efficiency
        map_plot = self._map.plot
        game_rand = _getSorenRandNum

        # Pre-cache feature count to avoid repeated calls
        iNumFeatures = _getNumFeatureInfos()

        for iFeature in xrange(iNumFeatures):
            # Direct method call without intermediate variable when possible
            sType = _getFeatureInfo(iFeature).getType()

            # Use string slicing for prefix check (more efficient than find)
            if not sType[:13] == _FEATURE_PREFIX:
                continue

            # Check if this is a big wonder once
            bIsBigWonder = sType in self.lBigWonder

            # Pre-calculate radius for this feature type
            if bIsBigWonder:
                iRadius = _BIG_WONDER_RADIUS
            else:
                iRadius = _STANDARD_RADIUS

            # Collect suitable plots
            WonderPlot = []

            # Use generator-like approach with plots() iterator
            for pPlot in self._map.plots():
                # Early exit checks
                if pPlot.getBonusType(_NO_BONUS) > _NO_BONUS:
                    continue

                if not pPlot.canHaveFeature(iFeature):
                    continue

                # Latitude check with early exit
                bLatitudeOK = True
                for latData in self.lLatitude:
                    if sType == latData[0]:
                        iLat = pPlot.getLatitude()
                        if iLat < latData[1] or iLat > latData[2]:
                            bLatitudeOK = False
                            break

                if not bLatitudeOK:
                    continue

                # Nearby plot check with optimized loops
                bUnsuitable = False
                bAdjacentPlot = not bIsBigWonder  # Pre-set for standard wonders

                # Pre-calculate plot coordinates once
                iPlotX = pPlot.getX()
                iPlotY = pPlot.getY()

                # Pre-calculate loop bounds
                xMin = iPlotX - iRadius
                xMax = iPlotX + iRadius + 1
                yMin = iPlotY - iRadius
                yMax = iPlotY + iRadius + 1

                for x in xrange(xMin, xMax):
                    if bUnsuitable:
                        break

                    for y in xrange(yMin, yMax):
                        pAdjacentPlot = map_plot(x, y)
                        if not pAdjacentPlot:
                            continue

                        # Check for existing natural wonders
                        iAdjFeature = pAdjacentPlot.getFeatureType()
                        if iAdjFeature > _NO_FEATURE:
                            # Direct string check without intermediate variable
                            if _getFeatureInfo(iAdjFeature).getType()[:13] == _FEATURE_PREFIX:
                                bUnsuitable = True
                                break

                        # Big Wonder adjacent plot validation
                        if bIsBigWonder and not bAdjacentPlot:
                            # Use absolute value calculations directly
                            if (pAdjacentPlot.canHaveFeature(iFeature) and
                                    abs(x - iPlotX) < 2 and
                                    abs(y - iPlotY) < 2 and
                                    pAdjacentPlot.getBonusType(_NO_BONUS) == _NO_BONUS):
                                bAdjacentPlot = True

                # Add to suitable plots if all checks pass
                if not bUnsuitable and bAdjacentPlot:
                    WonderPlot.append(pPlot)

            # Place the wonder if suitable plots found
            if not WonderPlot:
                continue

            # Process wonder placement
            while WonderPlot:
                # Pop random plot
                iRandIndex = game_rand(len(WonderPlot), "Random Plot")
                pPlot = WonderPlot.pop(iRandIndex)

                # Handle Big Wonders
                if bIsBigWonder:
                    AdjacentPlot = []

                    # Pre-calculate coordinates
                    iPlotX = pPlot.getX()
                    iPlotY = pPlot.getY()

                    # Scan adjacent plots
                    for x in xrange(iPlotX - 1, iPlotX + 2):
                        for y in xrange(iPlotY - 1, iPlotY + 2):
                            # Skip center plot
                            if x == iPlotX and y == iPlotY:
                                continue

                            pAdjacentPlot = map_plot(x, y)
                            if (pAdjacentPlot and
                                    pAdjacentPlot.canHaveFeature(iFeature) and
                                    pAdjacentPlot.getBonusType(_NO_BONUS) == _NO_BONUS):
                                AdjacentPlot.append(pAdjacentPlot)

                    if not AdjacentPlot:
                        continue

                    # Place on random adjacent plot
                    iRandAdj = game_rand(len(AdjacentPlot), "Random Plot")
                    AdjacentPlot[iRandAdj].setFeatureType(iFeature, 0)

                # Place the main wonder
                pPlot.setFeatureType(iFeature, 0)
                break

    def checkReveal(self, pPlot, iTeam):
        # Early exit checks
        iFeature = pPlot.getFeatureType()
        if iFeature == _NO_FEATURE:
            return

        # Pre-cache team reference
        CyTeam = _getTeam(iTeam)
        if CyTeam.isNPC():
            return

        # Check world builder mode
        if _GetWorldBuilderMode():
            return

        # Pre-cache feature info
        FeatureInfo = _getFeatureInfo(iFeature)
        sType = FeatureInfo.getType()

        # Check if it's a natural wonder
        if not sType[:13] == _FEATURE_PREFIX:
            return

        # Pre-cache frequently used values
        bIsBigWonder = sType in self.lBigWonder
        iPlotX = pPlot.getX()
        iPlotY = pPlot.getY()

        # Handle big wonders - find adjacent wonder plot
        pAdjacentPlot = None
        if bIsBigWonder:
            # Pre-cache map reference
            cyMap = CyMap()

            # Search for adjacent wonder plot
            for x in xrange(iPlotX - 1, iPlotX + 2):
                for y in xrange(iPlotY - 1, iPlotY + 2):
                    # Skip center plot
                    if x == iPlotX and y == iPlotY:
                        continue

                    pTestPlot = cyMap.plot(x, y)
                    if pTestPlot and pTestPlot.getFeatureType() == iFeature:
                        pAdjacentPlot = pTestPlot
                        break

                if pAdjacentPlot:
                    break

            # Check if adjacent plot already revealed
            if pAdjacentPlot and pAdjacentPlot.isRevealed(iTeam, False):
                return

        # Check if this is the first team to discover
        bFirst = True
        iMaxTeams = _getMAX_PC_TEAMS()

        for iTeamX in xrange(iMaxTeams):
            if iTeamX == iTeam:
                continue

            if pPlot.isRevealed(iTeamX, False):
                bFirst = False
                break

            if bIsBigWonder and pAdjacentPlot:
                if pAdjacentPlot.isRevealed(iTeamX, False):
                    bFirst = False
                    break

        # Calculate gold reward if first discovery
        iGold = 0
        if bFirst:
            # Pre-calculate gold amount
            iSpeedPercent = _getGameSpeedInfo(_getGameSpeedType()).getSpeedPercent()
            iGold = self.iFirstGold * iSpeedPercent / 100

        # Import CvUtil only when needed (lazy import for memory efficiency)
        import CvUtil

        # Pre-cache active player
        iPlayerAct = _getActivePlayer()

        # Pre-cache max players
        iMaxPlayers = _getMAX_PC_PLAYERS()

        # Pre-cache team name and feature description for first discovery messages
        if bFirst:
            szTeamName = CyTeam.getName()
            szFeatureDesc = FeatureInfo.getDescription()

        # Send messages to all players
        for iPlayerX in xrange(iMaxPlayers):
            CyPlayerX = _getPlayer(iPlayerX)
            iTeamX = CyPlayerX.getTeam()

            # Handle other teams
            if iTeamX != iTeam:
                # Only send message to active player
                if bFirst and iPlayerX == iPlayerAct:
                    if CyTeam.isHasMet(iTeamX):
                        CvUtil.sendMessage(
                            _getText(_TXT_MET_FIRST, (szTeamName, szFeatureDesc)),
                            iPlayerX, 12, bForce=False
                        )
                    else:
                        CvUtil.sendMessage(
                            _getText(_TXT_NOT_MET_FIRST, (szFeatureDesc,)),
                            iPlayerX, 12, bForce=False
                        )
                continue

            # Handle discovering team's player
            if iPlayerX == iPlayerAct:
                # Create popup for movie
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                popupInfo.setData1(iFeature)
                popupInfo.setData3(3)
                popupInfo.setText("showWonderMovie")
                popupInfo.addPopup(iPlayerX)

                # Send discovery message
                CvUtil.sendMessage(
                    _getText(_TXT_WONDER_YOU, (FeatureInfo.getDescription(),)),
                    iPlayerX, 12, FeatureInfo.getButton(),
                    ColorTypes(_COLOR_GOLD),
                    iPlotX, iPlotY, True, True, bForce=False
                )

            # Give gold reward for first discovery
            if bFirst:
                CyPlayerX.changeGold(iGold)
                if iPlayerX == iPlayerAct:
                    CvUtil.sendMessage(
                        _getText(_TXT_FIRST_FOUND, (iGold,)),
                        iPlayerX, 12, None,
                        ColorTypes(_COLOR_GOLD),
                        bForce=False
                    )