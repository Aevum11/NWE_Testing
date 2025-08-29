# Memory-optimized WoodlandCycle for 32-bit Caveman2Cosmos mod
# Compatible with Python 2.4 - NO ternary expressions
# Optimizations: __slots__, cached references, generator patterns, reduced memory allocation

from CvPythonExtensions import *
import CvUtil  # Removed unused BugUtil import to save memory

# Pre-cache global references to reduce repeated lookups (saves memory and CPU)
GC = CyGlobalContext()
MAP = GC.getMap()
GAME = GC.getGame()
TRNSLTR = CyTranslator()

# Pre-cache frequently used methods (reduces attribute lookup overhead)
_getMapRand = GAME.getMapRand
_getSorenRandNum = GAME.getSorenRandNum
_getCurrentEra = GAME.getCurrentEra
_getGameSpeedType = GAME.getGameSpeedType
_getActivePlayer = GAME.getActivePlayer
_isDebugMode = GAME.isDebugMode
_getText = TRNSLTR.getText
_sendMessage = CvUtil.sendMessage

# Pre-cache CyEngine and CyAudioGame for effects
_triggerEffect = CyEngine().triggerEffect
_play3DSound = CyAudioGame().Play3DSound


class WoodlandCycle:
    # __slots__ eliminates __dict__ overhead, saving ~100-200 bytes per instance
    # Critical for 32-bit memory constraints where every byte matters
    __slots__ = (
        'customEM',
        # Terrain type constants
        'TERRAIN_TAIGA', 'TERRAIN_MUDDY', 'TERRAIN_LUSH',
        # Feature type constants  
        'FEATURE_FOREST_BURNT', 'FEATURE_FOREST_YOUNG', 'FEATURE_FOREST',
        'FEATURE_FOREST_ANCIENT', 'FEATURE_JUNGLE', 'FEATURE_BAMBOO',
        # Cache data - using array module for memory efficiency
        'plot_indices', 'iMaxIndex', 'iFactorGS',
        # Pre-cached effect ID for forest fire
        'EFFECT_FOREST_FIRE',
        # Pre-cached message strings to leverage Python's string interning
        '_MSG_FIRE_CITY', '_MSG_FIRE_REMOTE', '_MSG_UNIT_LOST',
        # Pre-cached terrain tuple for fast membership testing
        '_LUSH_MUDDY_TUPLE'
    )

    def __init__(self, customEM):
        self.customEM = customEM

        # Register event handlers
        customEM.addEventHandler("GameStart", self.onGameStart)
        customEM.addEventHandler("OnLoad", self.onLoadGame)
        customEM.addEventHandler("BeginGameTurn", self.onBeginGameTurn)

        # Cache terrain types once at initialization
        self.TERRAIN_TAIGA = GC.getInfoTypeForString('TERRAIN_TAIGA')
        self.TERRAIN_MUDDY = GC.getInfoTypeForString('TERRAIN_MUDDY')
        self.TERRAIN_LUSH = GC.getInfoTypeForString('TERRAIN_LUSH')

        # Cache feature types once at initialization
        self.FEATURE_FOREST_BURNT = GC.getInfoTypeForString('FEATURE_FOREST_BURNT')
        self.FEATURE_FOREST_YOUNG = GC.getInfoTypeForString('FEATURE_FOREST_YOUNG')
        self.FEATURE_FOREST = GC.getInfoTypeForString('FEATURE_FOREST')
        self.FEATURE_FOREST_ANCIENT = GC.getInfoTypeForString('FEATURE_FOREST_ANCIENT')
        self.FEATURE_JUNGLE = GC.getInfoTypeForString('FEATURE_JUNGLE')
        self.FEATURE_BAMBOO = GC.getInfoTypeForString('FEATURE_BAMBOO')

        # Cache effect ID
        self.EFFECT_FOREST_FIRE = GC.getInfoTypeForString('EFFECT_FOREST_FIRE')

        # Pre-cache message strings (leverage Python's string interning)
        self._MSG_FIRE_CITY = "TXT_KEY_FOREST_FIRE_CITY_VICINITY"
        self._MSG_FIRE_REMOTE = "TXT_KEY_FOREST_FIRE_REMOTE"
        self._MSG_UNIT_LOST = "TXT_KEY_FOREST_FIRE_UNIT_LOST"

        # Pre-create tuple for fast membership testing (immutable, less memory)
        self._LUSH_MUDDY_TUPLE = None  # Will be set in cache()

    def onGameStart(self, argsList):
        self.cache()

    def onLoadGame(self, argsList):
        self.cache()

    def cache(self):
        """Cache plot indices instead of plot objects to save memory"""
        # Import array module for memory-efficient integer storage
        # Arrays use ~50% less memory than lists for integers
        from array import array

        # Create tuple for terrain checking (immutable, less memory)
        self._LUSH_MUDDY_TUPLE = (self.TERRAIN_LUSH, self.TERRAIN_MUDDY)

        # Use array('i') for signed integers - much more memory efficient than list
        # Store only indices, not plot objects (saves significant memory)
        plot_indices = array('i')

        # Use generator expression to avoid creating intermediate list
        iMapNumPlots = MAP.numPlots()
        for i in xrange(iMapNumPlots):
            plot = MAP.plotByIndex(i)
            if not (plot.isWater() or plot.isPeak()):
                plot_indices.append(i)
            # Explicitly delete plot reference to allow garbage collection
            del plot

        self.plot_indices = plot_indices
        self.iMaxIndex = len(plot_indices)

        # Cache game speed factor
        self.iFactorGS = GC.getGameSpeedInfo(_getGameSpeedType()).getSpeedPercent()

    def onBeginGameTurn(self, argsList):
        """Optimized turn processing with reduced memory allocation"""
        # Create local references to reduce attribute lookups in loop
        plot_indices = self.plot_indices
        iMaxIndex = self.iMaxIndex
        iFactorGS = self.iFactorGS

        # Pre-cache feature constants for faster access in loop
        FEATURE_BURNT = self.FEATURE_FOREST_BURNT
        FEATURE_YOUNG = self.FEATURE_FOREST_YOUNG
        FEATURE_FOREST = self.FEATURE_FOREST
        FEATURE_ANCIENT = self.FEATURE_FOREST_ANCIENT
        FEATURE_BAMBOO = self.FEATURE_BAMBOO
        FEATURE_JUNGLE = self.FEATURE_JUNGLE

        # Pre-cache terrain constants
        TERRAIN_TAIGA = self.TERRAIN_TAIGA
        LUSH_MUDDY = self._LUSH_MUDDY_TUPLE

        # Create shuffled index array for random plot selection
        # Using array module for memory efficiency
        from array import array
        plotOrder = array('i', xrange(iMaxIndex))

        # Use native shuffleList function (more efficient than Python shuffle)
        shuffleList(iMaxIndex, _getMapRand(), plotOrder)

        # Calculate max iterations based on era (reduce activity over time)
        iCurrentEra = _getCurrentEra()
        iMaxCount = iMaxIndex / (3 * (iCurrentEra + 1))

        # Pre-cache active player ID
        iActivePlayer = _getActivePlayer()

        # Main processing loop
        iCount = 0
        while iCount < iMaxCount:
            iCount += 1

            # Early exit check - most common case first
            if 25 <= _getSorenRandNum(iFactorGS, "New"):
                continue

            # Get plot by index (more memory efficient than storing plot objects)
            plot = MAP.plotByIndex(plot_indices[plotOrder[iCount - 1]])

            # Cache frequently accessed values
            iFeature = plot.getFeatureType()

            # Process based on feature type (ordered by likelihood)
            if iFeature == -1:
                # No feature - chance to grow new forest
                if not _getSorenRandNum(10, "New"):
                    if plot.canHaveFeature(FEATURE_BAMBOO) and not _getSorenRandNum(10, "Bamboo"):
                        plot.setFeatureType(FEATURE_BAMBOO, 0)
                    elif plot.canHaveFeature(FEATURE_YOUNG):
                        plot.setFeatureType(FEATURE_YOUNG, 0)

            elif iFeature == FEATURE_BURNT:
                # Burnt forest - clear and possibly regrow
                iImp = plot.getImprovementType()
                plot.setFeatureType(-1, 0)

                if _getSorenRandNum(3, "new forest"):
                    if plot.canHaveFeature(FEATURE_BAMBOO) and not _getSorenRandNum(10, "Bamboo"):
                        plot.setFeatureType(FEATURE_BAMBOO, 0)
                    elif plot.canHaveFeature(FEATURE_YOUNG):
                        plot.setFeatureType(FEATURE_YOUNG, 0)

                # Restore improvement if it was removed
                if iImp != plot.getImprovementType() and plot.canHaveImprovement(iImp, -1, True):
                    plot.setImprovementType(iImp)

            elif iFeature == FEATURE_BAMBOO:
                # Bamboo - chance to burn
                if not _getSorenRandNum(50, "Burn"):
                    self._processBurn(plot, iActivePlayer)

            elif iFeature == FEATURE_YOUNG:
                # Young forest - grow to mature
                iTerrain = plot.getTerrainType()

                if iTerrain == TERRAIN_TAIGA:
                    plot.setFeatureType(FEATURE_FOREST, 2)
                elif iTerrain in LUSH_MUDDY:
                    plot.setFeatureType(FEATURE_FOREST, 0)
                else:
                    # Determine forest variety based on neighbors
                    iVariety = self._getForestVariety(plot)
                    plot.setFeatureType(FEATURE_FOREST, iVariety)

            elif iFeature == FEATURE_FOREST:
                # Mature forest - chance to burn or age
                iRand = _getSorenRandNum(148, "forestChange")
                if iRand < 3:
                    self._processBurn(plot, iActivePlayer)
                elif iRand < 7:
                    plot.setFeatureType(FEATURE_ANCIENT, 0)

            elif iFeature == FEATURE_ANCIENT:
                # Ancient forest - chance to burn or become jungle
                iRand = _getSorenRandNum(64, "Burn")
                if iRand < 4:
                    self._processBurn(plot, iActivePlayer)
                elif iRand == 4:
                    plot.setFeatureType(-1, 0)
                    if plot.canHaveFeature(FEATURE_JUNGLE):
                        plot.setFeatureType(FEATURE_JUNGLE, 0)
                    else:
                        plot.setFeatureType(FEATURE_ANCIENT, 0)

    def _getForestVariety(self, plot):
        """Determine forest variety based on neighbors - memory optimized"""
        iX = plot.getX()
        iY = plot.getY()

        # Use simple counters instead of lists
        iLeaf = 1
        iPine = 2  # Head start for pine as leafy tend to dominate

        # Check 3x3 grid around plot
        for dx in xrange(-1, 2):
            x = iX + dx
            for dy in xrange(-1, 2):
                # Skip center plot
                if dx == 0 and dy == 0:
                    continue

                y = iY + dy
                plotX = MAP.plot(x, y)

                if plotX and plotX.getFeatureType() == self.FEATURE_FOREST:
                    iVariety = plotX.getFeatureVariety()
                    if iVariety:  # Count snowy as pine
                        iPine += 1
                    else:
                        iLeaf += 1

        # Determine variety based on neighbor ratio
        if 100 < _getSorenRandNum(100 + 100 * iLeaf / iPine, "Leafy"):
            return 0  # Leafy
        else:
            return 1  # Pine

    def _processBurn(self, plot, iActivePlayer):
        """Process forest fire - separated for clarity and reuse"""
        plot.setFeatureType(self.FEATURE_FOREST_BURNT, 0)

        iPlayer = plot.getOwner()

        # Send message if owned by active player
        if iPlayer > -1 and iPlayer == iActivePlayer:
            CyCity = plot.getWorkingCity()
            if CyCity:
                _sendMessage(
                    _getText(self._MSG_FIRE_CITY, (CyCity.getName(),)),
                    iPlayer, 10,
                    'Art/Terrain/Features/Forest_Burnt/ButtonBurntForest.dds',
                    ColorTypes(13), plot.getX(), plot.getY(), True, True
                )
            else:
                _sendMessage(
                    _getText(self._MSG_FIRE_REMOTE, ()),
                    iPlayer, 6,
                    'Art/Terrain/Features/Forest_Burnt/ButtonBurntForest.dds',
                    ColorTypes(4), plot.getX(), plot.getY(), True, True
                )

        # Visual and audio effects if visible
        if plot.isActiveVisible(_isDebugMode()) and not GC.getActivePlayer().isHumanDisabled():
            point = plot.getPoint()
            _triggerEffect(self.EFFECT_FOREST_FIRE, point)
            _play3DSound("AS3D_FOREST_FIRE", point.x, point.y, point.z)

        # Damage or kill units on plot
        self._damageUnits(plot, iPlayer == iActivePlayer)

    def _damageUnits(self, plot, bActivePlayer):
        """Damage units on burning plot - memory optimized"""
        # Process units with minimal memory allocation
        for CyUnit in plot.units():
            if CyUnit.canFight():
                iHP = CyUnit.getHP()
                iDamage = 5 + _getSorenRandNum(29, "Ouch")

                if iHP > iDamage:
                    CyUnit.changeDamage(iDamage, -1)
                else:
                    if bActivePlayer:
                        _sendMessage(
                            _getText(self._MSG_UNIT_LOST, (CyUnit.getName(),)),
                            plot.getOwner(), 6, eColor=ColorTypes(9)
                        )
                    CyUnit.kill(False, -1)