## Sid Meier's Civilization 4
##
## This file is part of the UnitUpgradesPediaMod by Vovan
## Automatic layout algorithm by Progor
## Memory optimized for 32-bit Python 2.4 environment
##
from CvPythonExtensions import *

# globals
GC = CyGlobalContext()

# Intern frequently used strings for memory efficiency
EMPTY_CELL = intern("E")

# Split lists - defined at module level to avoid recreation
unitSplitOutgoing = ["UNIT_SUBDUED_AFRICANELEPHANT", "UNIT_SUBDUED_ELEPHANT", "UNIT_SHAOLINMK",
                     "UNIT_ROGUE", "UNIT_ARSONIST", "UNIT_POST_APOCALYPTIC_GRENADIER", "UNIT_CLUBMAN"]

promotionsSplitIncoming = ["PROMOTION_BLITZ", "PROMOTION_KAMIKAZE", "PROMOTION_CHARGE",
                           "PROMOTION_SPEED", "PROMOTION_MARCH", "PROMOTION_AMBUSH",
                           "PROMOTION_FORMATION", "PROMOTION_COVER", "PROMOTION_PINCH",
                           "PROMOTION_SHOCK", "PROMOTION_SENTRY", "PROMOTION_URBAN_TACTICS1",
                           "PROMOTION_SENSORS", "PROMOTION_NANOIDS"]


class Node:
    "Memory-optimized node with __slots__ to reduce overhead"

    # Using __slots__ saves ~100-200 bytes per instance in 32-bit Python
    __slots__ = ('x', 'y', 'upgradesTo', 'upgradesFrom', 'seen')

    def __init__(self):
        self.x = 999
        self.y = 999
        self.upgradesTo = set()
        self.upgradesFrom = set()
        self.seen = False


class MGraph:
    "Memory-optimized Graph collection"

    __slots__ = ('graph', 'matrix', 'depth', 'width')

    def __init__(self):
        self.graph = {}
        self.matrix = []
        self.depth = 0
        self.width = 0


class UnitUpgradesGraph:

    def __init__(self, pediaScreen, UPGRADES_GRAPH_ID):
        self.mGraphs = []
        self.horizontalMargin = 20
        self.verticalMargin = 20
        self.horizontalSpacing = 40
        self.verticalSpacing = 5
        self.pediaScreen = pediaScreen
        self.upgradesList = UPGRADES_GRAPH_ID
        self.buttonSize = 64
        self.splitIncoming = []
        self.splitOutgoing = unitSplitOutgoing

        self.promotionsSplitIncoming = promotionsSplitIncoming
        self.promotionsSplitOutgoing = []
        self.bUnit = True
        self.bBuilding = False

    def getNumberOfUnits(self):
        return GC.getNumUnitInfos()

    def getPromotionType(self, e):
        return GC.getPromotionInfo(e).getType()

    def getGraphEdges(self, graph):
        for iUnitA in graph:  # More efficient than graph.iterkeys()
            CvUnitInfoA = GC.getUnitInfo(iUnitA)
            for i in xrange(CvUnitInfoA.getNumUnitUpgrades()):
                self.addUpgradePath(graph, iUnitA, CvUnitInfoA.getUnitUpgrade(i))

    def placeOnScreen(self, screen, unit, xPos, yPos):
        screen.setImageButtonAt(self.pediaScreen.getNextWidgetName(), self.upgradesList,
                                GC.getUnitInfo(unit).getButton(), xPos, yPos,
                                self.buttonSize, self.buttonSize,
                                WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, unit, 1)

    def unitToString(self, unit):
        return GC.getUnitInfo(unit).getDescription() + ":%d" % (unit,)

    ################## Unit Upgrade Graph Generation ##################

    def addUpgradePath(self, graph, unitFrom, unitTo):
        # Simplified validation
        if unitFrom >= 0 and unitTo >= 0 and unitFrom in graph and unitTo in graph:
            graph[unitFrom].upgradesTo.add(unitTo)
            graph[unitTo].upgradesFrom.add(unitFrom)

    def getMedianY(self, mGraph, unitSet):
        "Memory-efficient median calculation without creating lists"
        if not unitSet:
            return -1

        total = 0.0
        count = 0
        for unit in unitSet:
            total += mGraph.graph[unit].y
            count += 1
        return total / count if count > 0 else -1

    def swap(self, mGraph, x, yA, yB):
        "Optimized swap operation"
        matrix_row = mGraph.matrix[x]  # Cache row reference
        unitA = matrix_row[yA]
        unitB = matrix_row[yB]

        if unitA != EMPTY_CELL:
            mGraph.graph[unitA].y = yB
        if unitB != EMPTY_CELL:
            mGraph.graph[unitB].y = yA

        matrix_row[yA] = unitB
        matrix_row[yB] = unitA

    def getGraph(self):
        "Memory-optimized graph generation"

        # Initialize first graph
        self.mGraphs.append(MGraph())
        graph = self.mGraphs[0].graph

        # Cache frequently accessed values
        BONUSCLASS_CULTURE = GC.getInfoTypeForString("BONUSCLASS_CULTURE")
        numUnits = self.getNumberOfUnits()

        # Build initial graph
        for iUnit in xrange(numUnits):
            if self.bUnit:
                CvUnitInfo = GC.getUnitInfo(iUnit)
                # Skip corporation units
                if CvUnitInfo.getPrereqCorporation() != -1:
                    continue
                # Skip culture bonus units
                if BONUSCLASS_CULTURE > -1:
                    iPrereq = CvUnitInfo.getPrereqAndBonus()
                    if iPrereq > -1 and GC.getBonusInfo(iPrereq).getBonusClassType() == BONUSCLASS_CULTURE:
                        continue
                graph[iUnit] = Node()
            else:
                graph[iUnit] = Node()

        self.getGraphEdges(graph)

        # Remove isolated units (memory optimization)
        for iUnit in graph.keys():  # keys() creates a list copy for safe iteration
            node = graph[iUnit]
            if not node.upgradesTo and not node.upgradesFrom:
                del graph[iUnit]

        # Split into disconnected graphs
        mGraphIndex = 0
        while mGraphIndex < len(self.mGraphs):
            mGraph = self.mGraphs[mGraphIndex]
            self.mGraphs.append(MGraph())
            newMGraph = self.mGraphs[mGraphIndex + 1]

            # Process connected components
            if mGraph.graph:
                self._processConnectedComponent(mGraph, newMGraph, mGraphIndex)

            # Clean up empty graph
            if not newMGraph.graph:
                del self.mGraphs[mGraphIndex + 1]

            mGraphIndex += 1

        # Process each graph
        for mGraph in self.mGraphs:
            self._finalizeGraph(mGraph)

        # Sort graphs by size (largest first)
        self._sortGraphsBySize()

    def _processConnectedComponent(self, mGraph, newMGraph, mGraphIndex):
        "Memory-efficient connected component processing"
<<<<<<< Updated upstream

=======
        if not mGraph.graph:
            return
>>>>>>> Stashed changes
        # Pick first element
        unit = mGraph.graph.iterkeys().next()
        mGraph.graph[unit].x = 0

        # Use single map to track levels
        level_map = {0: set([unit])}

        # Process nodes
        for _ in xrange(20):  # Iteration limit
            # Forward pass
            for level in xrange(min(level_map), max(level_map) + 1):
                if level not in level_map:
                    continue

                for unit in list(level_map[level]):  # Create copy for iteration
                    node = mGraph.graph[unit]
                    if node.x != level:
                        continue

                    # Check split conditions
                    if self.bUnit:
                        if GC.getUnitInfo(unit).getType() in self.splitOutgoing:
                            continue
                    elif not self.bBuilding and self.getPromotionType(unit) in self.promotionsSplitOutgoing:
                        continue

                    # Process upgrades
                    for u in node.upgradesTo:
                        if u not in mGraph.graph:
                            self._addNodeFromPrevious(mGraph, u, mGraphIndex)

                        nodeB = mGraph.graph[u]
                        nodeB.x = level + 1
                        if level + 1 not in level_map:
                            level_map[level + 1] = set()
                        level_map[level + 1].add(u)

            # Backward pass
            for level in xrange(max(level_map), min(level_map) - 1, -1):
                if level not in level_map:
                    continue

                for unit in list(level_map[level]):
                    node = mGraph.graph[unit]
                    if node.x != level:
                        continue

                    # Check split conditions
                    if self.bUnit:
                        if GC.getUnitInfo(unit).getType() in self.splitIncoming:
                            continue
                    elif not self.bBuilding and self.getPromotionType(unit) in self.promotionsSplitIncoming:
                        continue

                    # Process downgrades
                    for u in node.upgradesFrom:
                        if u not in mGraph.graph:
                            self._addNodeFromPrevious(mGraph, u, mGraphIndex)

                        nodeB = mGraph.graph[u]
                        nodeB.x = level - 1
                        if level - 1 not in level_map:
                            level_map[level - 1] = set()
                        level_map[level - 1].add(u)

        # Normalize positions and move unconnected nodes
        if level_map:
            lowOrder = min(level_map)
            highOrder = max(level_map)
            mGraph.depth = highOrder - lowOrder + 1

            # Move unprocessed nodes to next graph
            for unit in mGraph.graph.keys():
                node = mGraph.graph[unit]
                if node.x == 999:
                    newMGraph.graph[unit] = node
                    del mGraph.graph[unit]
                else:
                    node.x -= lowOrder

        # Clean up
        del level_map

    def _addNodeFromPrevious(self, mGraph, unit, mGraphIndex):
        "Helper to add node from previous graphs"
        for i in xrange(mGraphIndex - 1, -1, -1):
            if unit in self.mGraphs[i].graph:
                src_node = self.mGraphs[i].graph[unit]
                new_node = Node()
                # Copy sets directly (more efficient than copy())
                new_node.upgradesFrom = set(src_node.upgradesFrom)
                new_node.upgradesTo = set(src_node.upgradesTo)
                mGraph.graph[unit] = new_node
                break

    def _finalizeGraph(self, mGraph):
        "Finalize graph structure with memory optimizations"

        # Remove cross-graph links
        for unit in mGraph.graph:
            node = mGraph.graph[unit]
            # Use set comprehension for efficiency
            node.upgradesTo = set(u for u in node.upgradesTo if u in mGraph.graph)
            node.upgradesFrom = set(u for u in node.upgradesFrom if u in mGraph.graph)

        # Add dummy nodes for long paths
        nextDummy = -1
        for unitA in mGraph.graph.keys():
            nodeA = mGraph.graph[unitA]
            for unitB in list(nodeA.upgradesTo):
                nodeB = mGraph.graph[unitB]
                if nodeB.x - nodeA.x > 1:
                    # Insert dummy nodes
                    nodeB.upgradesFrom.discard(unitA)  # More efficient than remove
                    prevDummy = unitA

                    for n in xrange(nodeA.x + 1, nodeB.x):
                        dummy = nextDummy
                        mGraph.graph[dummy] = Node()
                        dummyNode = mGraph.graph[dummy]
                        dummyNode.x = n
                        dummyNode.upgradesFrom.add(prevDummy)
                        mGraph.graph[prevDummy].upgradesTo.add(dummy)
                        prevDummy = dummy
                        nextDummy -= 1

                    mGraph.graph[prevDummy].upgradesTo.add(unitB)
                    nodeB.upgradesFrom.add(prevDummy)

        # Build matrix efficiently
        self._buildMatrix(mGraph)

        # Optimize layout
        self._optimizeLayout(mGraph)

    def _buildMatrix(self, mGraph):
        "Build matrix with memory efficiency"

        # Pre-allocate matrix
        mGraph.matrix = [[] for _ in xrange(mGraph.depth)]

        # Fill matrix
        for unit in mGraph.graph:
            node = mGraph.graph[unit]
            node.y = len(mGraph.matrix[node.x])
            mGraph.matrix[node.x].append(unit)
            if node.y >= mGraph.width:
                mGraph.width = node.y + 1

        # Pad rows efficiently
        for row in mGraph.matrix:
            shortage = mGraph.width - len(row)
            if shortage > 0:
                row.extend([EMPTY_CELL] * shortage)

    def _optimizeLayout(self, mGraph):
        "Sugiyama algorithm with memory optimizations"

        for iteration in xrange(8):  # Limit iterations
            changed = False

            for direction in (1, -1):
                if direction == 1:
                    x_range = xrange(1, mGraph.depth)
                else:
                    x_range = xrange(mGraph.depth - 2, -1, -1)

                for x in x_range:
                    changed |= self._optimizeLayer(mGraph, x, direction)

            if not changed:
                break

    def _optimizeLayer(self, mGraph, x, direction):
        "Optimize single layer - returns True if changed"
        changed = False
        matrix_row = mGraph.matrix[x]  # Cache row

        # Median-based optimization
        for _ in xrange(2):  # Limited passes
            layer_changed = False

            for y in xrange(mGraph.width - 1, 0, -1):
                unitA = matrix_row[y - 1]
                unitB = matrix_row[y]

                if unitA == EMPTY_CELL and unitB == EMPTY_CELL:
                    continue

                medA = -1.0
                medB = -1.0

                if unitA != EMPTY_CELL:
                    nodeA = mGraph.graph[unitA]
                    setA = nodeA.upgradesTo if direction == -1 else nodeA.upgradesFrom
                    medA = self.getMedianY(mGraph, setA)

                if unitB != EMPTY_CELL:
                    nodeB = mGraph.graph[unitB]
                    setB = nodeB.upgradesTo if direction == -1 else nodeB.upgradesFrom
                    medB = self.getMedianY(mGraph, setB)

                # Swap decision
                swap_needed = False
                if medA > -1 and medB > -1 and medA > medB:
                    swap_needed = True
                elif medA == -1 and medB >= 0 and medB < y:
                    swap_needed = True
                elif medB == -1 and medA >= y:
                    swap_needed = True

                if swap_needed:
                    self.swap(mGraph, x, y - 1, y)
                    layer_changed = True
                    changed = True

            if not layer_changed:
                break

        # Cross minimization
        layer_changed = self._minimizeCrosses(mGraph, x, direction)
        changed |= layer_changed

        # Fix median conversions
        if matrix_row[-1] == EMPTY_CELL:
            self._adjustEmptyCell(mGraph, x, direction)

        return changed

    def _minimizeCrosses(self, mGraph, x, direction):
        "Minimize edge crossings in a layer"
        changed = False
        matrix_row = mGraph.matrix[x]

        for y in xrange(1, mGraph.width):
            unitA = matrix_row[y - 1]
            unitB = matrix_row[y]

            if unitA == EMPTY_CELL or unitB == EMPTY_CELL:
                continue

            nodeA = mGraph.graph[unitA]
            nodeB = mGraph.graph[unitB]
            setA = nodeA.upgradesTo if direction == -1 else nodeA.upgradesFrom
            setB = nodeB.upgradesTo if direction == -1 else nodeB.upgradesFrom

            # Count crossings
            crosses = 0
            crossesFlipped = 0

            for a in setA:
                yA = mGraph.graph[a].y
                for b in setB:
                    yB = mGraph.graph[b].y
                    if yB < yA:
                        crosses += 1
                    elif yB > yA:
                        crossesFlipped += 1

            if crossesFlipped < crosses:
                self.swap(mGraph, x, y - 1, y)
                changed = True

        return changed

    def _adjustEmptyCell(self, mGraph, x, direction):
        "Adjust empty cell position based on median"
        matrix_row = mGraph.matrix[x]
        total = 0.0
        count = 0

        for y in xrange(mGraph.width - 1):
            unit = matrix_row[y]
            if unit != EMPTY_CELL:
                node = mGraph.graph[unit]
                seto = node.upgradesTo if direction == -1 else node.upgradesFrom
                median = self.getMedianY(mGraph, seto)
                if median >= 0:
                    total += y - median
                    count += 1

        if count > 0 and total / count < -0.5:
            # Shift everything right
            for y in xrange(mGraph.width - 1, 0, -1):
                unit = matrix_row[y - 1]
                matrix_row[y] = unit
                if unit != EMPTY_CELL:
                    mGraph.graph[unit].y = y
            matrix_row[0] = EMPTY_CELL

    def _sortGraphsBySize(self):
        "Sort graphs by size (bubble sort for simplicity)"
        n = len(self.mGraphs)
        for i in xrange(n - 1):
            for j in xrange(n - 1 - i):
                if len(self.mGraphs[j].graph) < len(self.mGraphs[j + 1].graph):
                    # Swap
                    temp = self.mGraphs[j]
                    self.mGraphs[j] = self.mGraphs[j + 1]
                    self.mGraphs[j + 1] = temp

    ################## Layout and Drawing ###################

    def getPosition(self, x, y, verticalOffset):
        xPos = self.horizontalMargin + x * (self.buttonSize + self.horizontalSpacing)
        yPos = self.verticalMargin + y * (self.buttonSize + self.verticalSpacing) + verticalOffset
        return (xPos, yPos)

    def drawGraph(self):
        screen = self.pediaScreen.getScreen()
        offset = 0

        for mGraph in self.mGraphs:
            # Draw arrows first (under buttons)
            self.drawGraphArrows(mGraph, offset)

            # Draw buttons
            for x in xrange(mGraph.depth):
                for y in xrange(mGraph.width):
                    unit = mGraph.matrix[x][y]
                    if unit != EMPTY_CELL and unit > -1:
                        xPos, yPos = self.getPosition(x, y, offset)
                        self.placeOnScreen(screen, unit, xPos, yPos)

            offset = self.getPosition(0, mGraph.width, offset)[1]

    def drawGraphArrows(self, mGraph, offset):
        # Draw from right to left for proper layering
        for x in xrange(len(mGraph.matrix) - 1, -1, -1):
            row = mGraph.matrix[x]
            for y in xrange(len(row)):
                unit = row[y]
                if unit != EMPTY_CELL:
                    self.drawUnitArrows(mGraph, offset, unit)

    def drawUnitArrows(self, mGraph, offset, unit):
        toNode = mGraph.graph[unit]
        for fromUnit in toNode.upgradesFrom:
            fromNode = mGraph.graph[fromUnit]
            posFrom = self.getPosition(fromNode.x, fromNode.y, offset)
            posTo = self.getPosition(toNode.x, toNode.y, offset)
            self.drawArrow(posFrom, posTo, fromUnit < 0, unit < 0)

    def drawArrow(self, posFrom, posTo, dummyFrom, dummyTo):
        screen = self.pediaScreen.getScreen()

        # Cache art file paths
        AFM = CyArtFileMgr()
        LINE_ARROW = AFM.getInterfaceArtInfo("LINE_ARROW").getPath()
        LINE_TLBR = AFM.getInterfaceArtInfo("LINE_TLBR").getPath()
        LINE_BLTR = AFM.getInterfaceArtInfo("LINE_BLTR").getPath()
        LINE_STRAIT = AFM.getInterfaceArtInfo("LINE_STRAIT").getPath()

        # Calculate positions
        buttonHalf = self.buttonSize / 2
        xFrom = posFrom[0] + (buttonHalf if dummyFrom else self.buttonSize)
        xTo = posTo[0] + (buttonHalf if dummyTo else 0) - (0 if dummyTo else 8)
        yFrom = posFrom[1] + buttonHalf
        yTo = posTo[1] + buttonHalf

        if yFrom == yTo:
            # Straight line
            screen.addDDSGFCAt(self.pediaScreen.getNextWidgetName(), self.upgradesList,
                               LINE_STRAIT, xFrom, yFrom - 3, xTo - xFrom, 8,
                               WidgetTypes.WIDGET_GENERAL, -1, -1, False)
        else:
            # Diagonal line
            xDiff = float(xTo - xFrom)
            yDiff = float(yTo - yFrom)

            # Calculate iterations
            maxDiff = max(xDiff, abs(yDiff))
            iterations = int(maxDiff / 80) + 1
            if abs(xDiff / yDiff) >= 2 or abs(xDiff / yDiff) < 0.5:
                iterations = int(maxDiff / 160) + 1

            line = LINE_BLTR if yDiff < 0 else LINE_TLBR

            # Draw segments
            for i in xrange(iterations):
                factor_start = max(i - 0.1, 0) / iterations
                factor_end = (i + 1.0) / iterations

                xF = int(xDiff * factor_start) + xFrom
                yF = int(yDiff * factor_start) + yFrom
                xT = int(xDiff * factor_end) + xFrom
                yT = int(yDiff * factor_end) + yFrom

                if yT < yF:
                    yF, yT = yT, yF  # Swap

                screen.addDDSGFCAt(self.pediaScreen.getNextWidgetName(), self.upgradesList,
                                   line, xF, yF, xT - xF, yT - yF,
                                   WidgetTypes.WIDGET_GENERAL, -1, -1, False)

        # Draw arrow head
        if not dummyTo:
            screen.addDDSGFCAt(self.pediaScreen.getNextWidgetName(), self.upgradesList,
                               LINE_ARROW, xTo, yTo - 6, 12, 12,
                               WidgetTypes.WIDGET_GENERAL, -1, -1, False)


########################### PROMOTION GRAPH #############################

class PromotionsGraph(UnitUpgradesGraph):

    def __init__(self, pediaScreen, UPGRADES_GRAPH_ID):
        UnitUpgradesGraph.__init__(self, pediaScreen, UPGRADES_GRAPH_ID)
        self.horizontalSpacing = 75
        self.promotionsSplitIncoming = promotionsSplitIncoming
        self.promotionsSplitOutgoing = []
        self.bUnit = False
        self.bBuilding = False

    def getNumberOfUnits(self):
        return GC.getNumPromotionInfos()

    def getPromotionType(self, e):
        return GC.getPromotionInfo(e).getType()

    def getGraphEdges(self, graph):
        for unitA in graph:
            info = GC.getPromotionInfo(unitA)
            # Add all prerequisite promotions
            self.addUpgradePath(graph, info.getPrereqPromotion(), unitA)
            self.addUpgradePath(graph, info.getPrereqOrPromotion1(), unitA)
            self.addUpgradePath(graph, info.getPrereqOrPromotion2(), unitA)

    def unitToString(self, unit):
        return GC.getPromotionInfo(unit).getDescription() + ":%d" % (unit,)

    def placeOnScreen(self, screen, unit, xPos, yPos):
        screen.setImageButtonAt(self.pediaScreen.getNextWidgetName(), self.upgradesList,
                                GC.getPromotionInfo(unit).getButton(), xPos, yPos,
                                self.buttonSize, self.buttonSize,
                                WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, unit, 1)


########################### BUILDINGS GRAPH #############################

class BuildingsGraph(UnitUpgradesGraph):

    def __init__(self, pediaScreen, UPGRADES_GRAPH_ID):
        UnitUpgradesGraph.__init__(self, pediaScreen, UPGRADES_GRAPH_ID)
        self.horizontalSpacing = 75
        self.BuildingSplitIncoming = []
        self.BuildingSplitOutgoing = []
        self.bUnit = False
        self.bBuilding = True

    def getNumberOfUnits(self):
        return GC.getNumBuildingInfos()

    def getGraphEdges(self, graph):
        # Special replacements to ignore
        aSpecialReplacementsList = [
            "BUILDING_POLLUTION_BLACKENED_SKIES",
            "BUILDING_ORDINANCE_GAMBLING_BAN",
            "BUILDING_ORDINANCE_ALCOHOL_PROHIBITION",
            "BUILDING_ORDINANCE_DRUG_PROHIBITION",
            "BUILDING_ORDINANCE_PROSTITUTION_BAN"
        ]

        for buildingA in graph:
            info = GC.getBuildingInfo(buildingA)
            if not info:
                continue

            # Find direct replacements
            buildingReplacesA = []
            for i in xrange(info.getNumReplacementBuilding()):
                replacement = info.getReplacementBuilding(i)
                replacementInfo = GC.getBuildingInfo(replacement)
                if replacementInfo and replacementInfo.getType() not in aSpecialReplacementsList:
                    buildingReplacesA.append(replacement)

            if not buildingReplacesA:
                continue

            # Find secondary replacements
            buildingReplacesAList = []
            for numB in buildingReplacesA:
                infoB = GC.getBuildingInfo(numB)
                if infoB:
                    for i in xrange(infoB.getNumReplacementBuilding()):
                        iReplacement = infoB.getReplacementBuilding(i)
                        if iReplacement not in buildingReplacesAList:
                            buildingReplacesAList.append(iReplacement)

            # Filter out indirect replacements
            finalReplacements = []
            for numB in buildingReplacesA:
                if numB not in buildingReplacesAList:
                    finalReplacements.append(numB)

            # Create upgrade paths
            for numB in finalReplacements:
                self.addUpgradePath(graph, buildingA, numB)

    def unitToString(self, unit):
        return GC.getBuildingInfo(unit).getDescription() + ":%d" % (unit,)

    def placeOnScreen(self, screen, unit, xPos, yPos):
        screen.setImageButtonAt(self.pediaScreen.getNextWidgetName(), self.upgradesList,
                                GC.getBuildingInfo(unit).getButton(), xPos, yPos,
                                self.buttonSize, self.buttonSize,
                                WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, unit, 1)