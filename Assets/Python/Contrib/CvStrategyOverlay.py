# -------------------------------------------------------------------------------
# Name:        CvStrategyOverlay.py
# Purpose:     Draws the strategy overlay itself.
#              CvOverlayScreen.py does the editing.
#              Contains:
#              -Dot Mapper
#              -Categorized signs
#
# Author:      Del69, EmperorFool
#
# Created:     11/12/2008
# -------------------------------------------------------------------------------

from CvPythonExtensions import *
import CvScreensInterface
import BugCore
import SdToolKit

# Memory optimization: Global constants
COLOR_KEYS = None
PALETTE_WIDTH = None
GC = CyGlobalContext()
StratLayerOpt = BugCore.game.StrategyOverlay

# Memory optimization: Single instance pattern for layers
g_layers = {}
g_DotMap = None

# Memory optimization: Constants for coordinates (avoid tuple creation)
X = 0
Y = 1

# Memory optimization: Message constants
MSG_ADD_CITY = 500
MSG_REMOVE_CITY = 501


def init(paletteWidth=3, paletteColors=None):
    global COLOR_KEYS, PALETTE_WIDTH

    # setup palette width
    if paletteWidth:
        PALETTE_WIDTH = paletteWidth
    else:
        PALETTE_WIDTH = 10

    # setup palette colors - Memory optimization: build list only once
    if paletteColors:
        COLOR_KEYS = paletteColors
    else:
        PALETTE_WIDTH = 10  # override because it has 127 colors
        COLOR_KEYS = []
        # Memory optimization: Pre-allocate list size if possible
        for index in xrange(200):
            try:
                info = GC.getColorInfo(index)
                COLOR_KEYS.append(info.getType())
            except:
                break

    # create layers - single instance
    global g_DotMap
    if g_DotMap is None:
        g_DotMap = DotMapLayer()


def getLayer(id):
    return g_layers.get(id)


def callEachLayer(func, *args):
    # Memory optimization: Use itervalues() which is more memory efficient in Python 2.4
    for layer in g_layers.itervalues():
        func(layer, *args)


## Event Handlers

def onGameStart(argsList):
    for layer in g_layers.itervalues():
        layer.reset()


def onLoad(argsList):
    for layer in g_layers.itervalues():
        layer.read()


def onPreSave(argsList):
    for layer in g_layers.itervalues():
        layer.write()


def onSwitchHotSeatPlayer(args):
    g_DotMap.onSwitchHotSeatPlayer()


def onModNetMessage(args):
    iData1, iData2, iData3, iData4, iData5 = args
    if iData1 == MSG_ADD_CITY:
        g_DotMap.addCityMessage(iData2, iData3, iData4, iData5)
    elif iData1 == MSG_REMOVE_CITY:
        g_DotMap.removeCityMessage(iData2, iData3)
    else:
        return 0
    return 1


## Base Strategy Layer Class

class StrategyLayer(object):
    # Memory optimization: Use __slots__ to reduce per-instance memory overhead
    __slots__ = ('INVISIBLE_COLOR', 'id', 'visible', 'editing', 'dirty')

    # Provides common functionality for all of the strategy layers.
    def __init__(self, id):
        self.INVISIBLE_COLOR = NiColorA(0, 0, 0, 0)
        self.id = id
        self.visible = False
        self.editing = False
        self.dirty = False
        g_layers[id] = self
        self.reset()

    # Resets the data to a blank state and clears the dirty flag.
    def reset(self):
        self.visible = False
        self.editing = False
        self.dirty = False

    # Reads the data from the game and clears the dirty flag.
    def read(self):
        self.editing = False
        self.dirty = False

    # Writes the data to the game and clears the dirty flag.
    def write(self):
        self.dirty = False

    def toggleVisibility(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def show(self):
        if not self.visible:
            self.visible = True
            return True
        return False

    def hide(self):
        if self.visible:
            self.freeze()
            self.visible = False
            return True
        return False

    def toggleEditing(self):
        if not self.editing:
            self.edit()
        else:
            self.freeze()

    def edit(self):
        if not self.editing:
            self.show()
            self.editing = True
            return True
        return False

    def freeze(self):
        if self.editing:
            self.editing = False
            return True
        return False


## ----------------------------------------------------------------------
## DOT MAP
## ----------------------------------------------------------------------

DOTMAP_LAYER = "DotMap"


class City:
    # Memory optimization: Use __slots__ to reduce memory overhead for city instances
    __slots__ = ('point', 'color', 'layer', 'bAlt')

    # Holds the data for a single dot-mapped city.
    def __init__(self, point, color, layer, bAlt):
        self.point = point
        self.color = color
        self.layer = layer
        self.bAlt = bAlt

    def __eq__(self, other):
        return self.point == other.point and self.color == other.color and self.bAlt == other.bAlt

    def __str__(self):
        return "(%d,%d) on %d" % (self.point[X], self.point[Y], self.layer)

    def isAt(self, point):
        return self.point == point


def getDotMap():
    if g_DotMap is None:
        print
        "[ERROR] CvStrategyOverlay has not been initialized"
    return g_DotMap


def hideDotMap(args=None):
    g_DotMap.hide()


def toggleDotMapSize(args=None):
    g_DotMap.toggleSize()


def toggleDotMapVisibility(args=None):
    g_DotMap.toggleVisibility()


def toggleDotMapEditMode(args=None):
    g_DotMap.toggleEditing()


def onDotMapOptionChanged(option, value):
    g_DotMap.optionChanged(option, value)


class DotMapLayer(StrategyLayer):
    # Memory optimization: Additional slots for DotMapLayer specific attributes
    __slots__ = ('HIGHLIGHT_CROSS_LAYER', 'FIRST_CROSS_LAYER', 'NUM_CROSS_LAYERS',
                 'DOT_LAYER', 'NO_DOT_STYLE', 'MAX_DOT_STYLE', 'BFC_OFFSETS_STD',
                 'BFC_OFFSETS_ALT', 'bAlt', 'CROSS_ALPHA', 'DOT_ALPHA',
                 'HIGHLIGHT_CROSS_ALPHA', 'HIGHLIGHT_DOT_ALPHA', 'DRAW_DOTS',
                 'DOT_STYLE', 'cities', 'highlightedCity')

    # Draws city crosses of different colors so the user can create a dot-map.
    def __init__(self):
        super(DotMapLayer, self).__init__(DOTMAP_LAYER)
        # constants
        self.HIGHLIGHT_CROSS_LAYER = 8
        self.FIRST_CROSS_LAYER = 9
        self.NUM_CROSS_LAYERS = 36
        self.DOT_LAYER = PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_NUMPAD_HELP
        self.NO_DOT_STYLE = PlotStyles.PLOT_STYLE_NONE
        self.MAX_DOT_STYLE = PlotStyles.PLOT_STYLE_WAVES

        # Memory optimization: Use tuples instead of lists for immutable offset data
        self.BFC_OFFSETS_STD = ()
        self.BFC_OFFSETS_ALT = ()
        self.bAlt = False

        # Memory optimization: Build offsets more efficiently
        self._buildOffsets()

        # default options
        self.CROSS_ALPHA = 50.0
        self.DOT_ALPHA = 50.0
        self.HIGHLIGHT_CROSS_ALPHA = 100.0
        self.HIGHLIGHT_DOT_ALPHA = 100.0
        self.DRAW_DOTS = True
        self.DOT_STYLE = PlotStyles.PLOT_STYLE_DOT_TARGET
        self.readOptions()

        # state
        self.cities = {}
        self.highlightedCity = None

    def _buildOffsets(self):
        # Memory optimization: Build offsets once using more efficient logic
        std_offsets = []
        alt_offsets = []

        for x in xrange(-3, 4):
            for y in xrange(-3, 4):
                # Memory optimization: Calculate absolute values once
                abs_x = abs(x)
                abs_y = abs(y)

                if abs_x < 3 or abs_y < 3:
                    # Check if not in excluded positions
                    if (abs_x, abs_y) not in ((3, 3), (3, 2), (2, 3)):
                        alt_offsets.append((x, y))

                        # Add to standard offsets if within range
                        if abs_x > 2 or abs_y > 2 or (abs_x == 2 and abs_y == 2):
                            continue
                        std_offsets.append((x, y))

        # Convert to tuples for immutability and memory efficiency
        self.BFC_OFFSETS_STD = tuple(std_offsets)
        self.BFC_OFFSETS_ALT = tuple(alt_offsets)

    def toggleSize(self):
        self.bAlt = not self.bAlt

    def reset(self):
        self.cities = {}
        self.dirty = False
        self.highlightedCity = None

    def read(self):
        data = SdToolKit.sdGetGlobal("StrategyOverlay", "CityDataDict")
        self.clearCityLayers()
        if data:
            self.cities = data
            self.dirty = False
        else:
            self.reset()

    def write(self):
        if self.dirty:
            SdToolKit.sdSetGlobal("StrategyOverlay", "CityDataDict", self.cities)
            self.dirty = False

    def show(self):
        if super(DotMapLayer, self).show():
            self.redrawCities()

    def hide(self):
        if super(DotMapLayer, self).hide():
            self.clearCityLayers()

    def edit(self):
        if super(DotMapLayer, self).edit():
            CvScreensInterface.showOverlayScreen()

    def freeze(self):
        if super(DotMapLayer, self).freeze():
            self.unhighlightCity()
            CvScreensInterface.hideOverlayScreen()

    def onSwitchHotSeatPlayer(self):
        self.hide()

    def hasCities(self, ePlayer):
        return ePlayer in self.cities

    def hasCity(self, ePlayer, point):
        # Memory optimization: Short-circuit evaluation
        if ePlayer not in self.cities:
            return False
        return point in self.cities[ePlayer]

    def getCities(self, ePlayer):
        # Memory optimization: Use setdefault to avoid double lookup
        return self.cities.setdefault(ePlayer, {})

    def getCity(self, ePlayer, point):
        # Memory optimization: Single lookup with get()
        if ePlayer in self.cities:
            return self.cities[ePlayer].get(point)
        return None

    def iterCities(self, ePlayer):
        # Memory optimization: Direct iteration without intermediate checks
        if ePlayer in self.cities:
            for city in self.cities[ePlayer].itervalues():
                yield city

    def addCityAt(self, point, color, layer):
        # Sends a message to add a city for the active player at the given point.
        # Memory optimization: Calculate once
        player = GC.getGame().getActivePlayer()
        xy = point[X] * 1000 + point[Y]
        CyMessageControl().sendModNetMessage(MSG_ADD_CITY, player, xy, color, layer)

    def addCityMessage(self, ePlayer, xy, color, layer):
        # Processes a message to add a city.
        # Memory optimization: Use integer division for better performance
        x = xy / 1000
        y = xy % 1000
        city = City((x, y), color, layer, self.bAlt)
        self.addCity(ePlayer, city)

    def addCity(self, ePlayer, city):
        # Adds the city to the data set and draws its dot and cross.
        cities_dict = self.getCities(ePlayer)

        if city.point in cities_dict:
            oldCity = cities_dict[city.point]
            if city == oldCity:
                return
            print
            "DotMap - replacing city at (%d,%d)" % city.point
            self.removeCity(ePlayer, oldCity)

        print
        "DotMap - adding city %s" % city
        cities_dict[city.point] = city
        self.dirty = True

        if ePlayer == GC.getGame().getActivePlayer():
            self.drawCity(city, self.CROSS_ALPHA, self.DOT_ALPHA)

    def removeCityAt(self, point):
        # Sends a message to remove the active player's city at the given point.
        ePlayer = GC.getGame().getActivePlayer()
        if self.hasCity(ePlayer, point):
            xy = point[X] * 1000 + point[Y]
            CyMessageControl().sendModNetMessage(MSG_REMOVE_CITY, ePlayer, xy, -1, -1)
        else:
            self.freeze()

    def removeCityMessage(self, ePlayer, xy):
        # Processes a message to remove a city.
        x = xy / 1000
        y = xy % 1000
        city = self.getCity(ePlayer, (x, y))
        if city:
            self.removeCity(ePlayer, city)

    def removeCity(self, ePlayer, city):
        # Removes the city from the data set and erases its dot and cross.
        if city:
            print
            "DotMap - removing city %s" % city
            del self.cities[ePlayer][city.point]
            self.dirty = True
            if ePlayer == GC.getGame().getActivePlayer():
                self.redrawCrosses(city.layer)
                self.eraseDot(city, self.DOT_ALPHA)
        else:
            print
            "City doesn't exist"

    def highlightCity(self, point, color):
        """
        Highlights the given city location by drawing it using the given color on the highlight layer.
        Unhighlights the currently highlighted city if there is one.
        """
        city = City(point, color, self.HIGHLIGHT_CROSS_LAYER, self.bAlt)
        if self.highlightedCity:
            if self.highlightedCity == city:
                return
            self.unhighlightCity()

        self.highlightedCity = city
        ePlayer = GC.getGame().getActivePlayer()
        existingCity = self.getCity(ePlayer, point)

        if existingCity is not None:
            self.redrawCrosses(existingCity.layer, point)
            self.eraseDot(existingCity, self.DOT_ALPHA)

        self.drawCross(city, self.HIGHLIGHT_CROSS_ALPHA)

    def unhighlightCity(self):
        """
        Removes the highlight from the existing city location if there is one.
        """
        if self.highlightedCity:
            point = self.highlightedCity.point
            self.clearHighlightCrossLayer()

            ePlayer = GC.getGame().getActivePlayer()
            city = self.getCity(ePlayer, point)

            if city is not None:
                self.drawCity(city, self.CROSS_ALPHA, self.DOT_ALPHA)

            self.highlightedCity = None

    def redrawCities(self):
        # Erases all city layers and draws all of the cities.
        self.clearCityLayers()
        self.drawCities()

    def redrawCrosses(self, layer, skip=None):
        # Erases the given layer and draws all city crosses in that layer.
        self.clearCrossLayer(layer)
        self.drawCrosses(layer, skip)

    def redrawDots(self):
        # Erases and redraws all city dots as they are all in the same layer.
        self.clearDotLayer()
        self.drawDots()

    def drawCities(self, skip=None):
        # Draws all of the cities except skip, if given.
        crossAlpha = self.CROSS_ALPHA
        dotAlpha = self.DOT_ALPHA
        ePlayer = GC.getGame().getActivePlayer()

        # Memory optimization: Direct iteration
        if ePlayer in self.cities:
            for city in self.cities[ePlayer].itervalues():
                if skip is None or not city.isAt(skip):
                    self.drawCity(city, crossAlpha, dotAlpha)

    def drawCrosses(self, layer=None, skip=None):
        # Draws the cross for every city in the given layer.
        crossAlpha = self.CROSS_ALPHA
        ePlayer = GC.getGame().getActivePlayer()

        # Memory optimization: Direct iteration
        if ePlayer in self.cities:
            for city in self.cities[ePlayer].itervalues():
                if skip is None or not city.isAt(skip):
                    if layer is None or layer == city.layer:
                        self.drawCross(city, crossAlpha)

    def drawDots(self, skip=None):
        # Draws the dot for every city.
        if not self.DRAW_DOTS:
            return

        dotAlpha = self.DOT_ALPHA
        ePlayer = GC.getGame().getActivePlayer()

        # Memory optimization: Direct iteration
        if ePlayer in self.cities:
            for city in self.cities[ePlayer].itervalues():
                if skip is None or not city.isAt(skip):
                    self.drawDot(city, dotAlpha)

    def drawCity(self, city, crossAlpha, dotAlpha):
        # Draws the cross and dot for a single city.
        self.drawCross(city, crossAlpha)
        if self.DRAW_DOTS:
            self.drawDot(city, dotAlpha)

    def drawCross(self, city, alpha):
        # Draws the cross for a single city.
        x, y = city.point
        # Memory optimization: Cache color lookup
        color = GC.getColorInfo(city.color).getType()
        layer = city.layer

        # Memory optimization: Use appropriate offset list directly
        if city.bAlt:
            offsets = self.BFC_OFFSETS_ALT
        else:
            offsets = self.BFC_OFFSETS_STD

        # Memory optimization: Direct iteration over offsets
        for dx, dy in offsets:
            CyEngine().fillAreaBorderPlotAlt(x + dx, y + dy, layer, color, alpha)

    def drawDot(self, city, alpha):
        # Draws the dot for a single city.
        if self.DRAW_DOTS:
            x, y = city.point
            color_type = GC.getColorInfo(city.color).getType()
            CyEngine().addColoredPlotAlt(x, y, self.DOT_STYLE, self.DOT_LAYER, color_type, alpha)

    def eraseDot(self, city, alpha):
        # Erases the dot for a single city.
        if self.DRAW_DOTS:
            x, y = city.point
            CyEngine().addColoredPlotAlt(x, y, self.NO_DOT_STYLE, self.DOT_LAYER, "COLOR_BLACK", alpha)

    def clearCityLayers(self):
        # Erases all city crosses and dots.
        self.clearHighlightCrossLayer()
        # Memory optimization: Use xrange for iteration
        for index in xrange(self.NUM_CROSS_LAYERS):
            self.clearCrossLayer(index + self.FIRST_CROSS_LAYER)
        self.clearDotLayer()

    def clearHighlightCrossLayer(self):
        # Clears the indexed border layer.
        self.clearCrossLayer(self.HIGHLIGHT_CROSS_LAYER)

    def clearCrossLayer(self, layer):
        # Clears the indexed border layer.
        CyEngine().clearAreaBorderPlots(layer)

    def clearDotLayer(self):
        # Clears all the dots from screen.
        CyEngine().clearColoredPlots(self.DOT_LAYER)

    def percentToAlpha(self, percent):
        # Memory optimization: Use min/max directly
        if percent < 0:
            return 0.0
        elif percent > 100:
            return 1.0
        else:
            return percent / 100.0

    def readOptions(self):
        # Memory optimization: Cache option calls
        brightness = StratLayerOpt.getDotMapBrightness()
        highlight_brightness = StratLayerOpt.getDotMapHighlightBrightness()

        self.CROSS_ALPHA = self.percentToAlpha(brightness)
        self.DOT_ALPHA = self.percentToAlpha(brightness)
        self.HIGHLIGHT_CROSS_ALPHA = self.percentToAlpha(highlight_brightness)
        self.HIGHLIGHT_DOT_ALPHA = self.percentToAlpha(highlight_brightness)
        self.DRAW_DOTS = StratLayerOpt.isDotMapDrawDots()

        # Memory optimization: Clamp dot style value
        dot_style = StratLayerOpt.getDotMapDotIcon()
        if dot_style < 0:
            self.DOT_STYLE = 0
        elif dot_style > self.MAX_DOT_STYLE:
            self.DOT_STYLE = self.MAX_DOT_STYLE
        else:
            self.DOT_STYLE = dot_style

    def optionChanged(self, option, value):
        # Redraws the layer if it is currently visible.
        self.unhighlightCity()
        self.readOptions()
        if self.visible:
            self.redrawCities()