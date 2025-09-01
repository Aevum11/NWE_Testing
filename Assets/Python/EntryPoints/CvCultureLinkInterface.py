from __future__ import division
from CvPythonExtensions import *
from array import array
from math import sin, cos, atan, sqrt, pi

# Constants moved to module level to avoid repeated allocation
DMAX_EARTH = 20038  # max possible distance between two points on earth (WGS-84)
SEMI_MAJOR_AXIS = 6378.137
INVERSE_FLATTENING = 1 / 298.257223563
PI_DIV_360 = pi / 360
PI_DIV_180 = pi / 180

# Global coordinate cache - initialized once
_coord_cache = None
_coord_initialized = False


def _get_coord_cache():
    """Lazy initialization of coordinate cache to save memory until needed"""
    global _coord_cache, _coord_initialized
    if not _coord_initialized:
        _init_coord_cache()
        _coord_initialized = True
    return _coord_cache


def _init_coord_cache():
    """Initialize coordinate cache only with existing civilizations"""
    global _coord_cache
    _coord_cache = {}
    GC = CyGlobalContext()

    # Civilization coordinate data stored as tuples (more memory efficient than objects)
    # Format: (civ_key, lat, lon)
    coord_data = [
        ("CIVILIZATION_ARABIA", 21.423, 39.826),
        ("CIVILIZATION_ABORIGINES", -25.215, 130.282),
        ("CIVILIZATION_AUSTRALIA", -25.585, 134.504),
        ("CIVILIZATION_NEWZEALAND", -44.056, 70.354),
        ("CIVILIZATION_MAORI", -35.442, 173.820),
        ("CIVILIZATION_POLYNESIA", -14.209, -169.553),
        ("CIVILIZATION_DENE", 39.898, 5.040),
        ("CIVILIZATION_UPAAJUT", 63.747, -68.522),
        ("CIVILIZATION_CANADA", 45.389, -75.681),
        ("CIVILIZATION_TILLIKUM", 53.265, -131.990),
        ("CIVILIZATION_AMERICA", 38.895, -77.037),
        ("CIVILIZATION_CUBA", 23.132, -82.367),
        ("CIVILIZATION_HAITI", 39.893, 5.035),
        ("CIVILIZATION_MEXICO", 19.431, -99.133),
        ("CIVILIZATION_OLMEC", 37.680, -122.127),
        ("CIVILIZATION_PALEO", 33.425, -111.937),
        ("CIVILIZATION_WESTINDIES", 14.525, -75.818),
        ("CIVILIZATION_CHILE", -35.786, -71.674),
        ("CIVILIZATION_VENEZUELA", 7.665, -66.145),
        ("CIVILIZATION_BRAZIL", -22.908, -43.196),
        ("CIVILIZATION_HONDURAS", 14.975, -86.264),
        ("CIVILIZATION_BOLIVARIAN", 10.487, -66.886),
        ("CIVILIZATION_ARGENTINA", -34.608, -58.373),
        ("CIVILIZATION_AZTEC", 19.808, -96.917),
        ("CIVILIZATION_TUPI", -7.833, -36.366),
        ("CIVILIZATION_NAZCA", -14.880, -74.994),
        ("CIVILIZATION_ZAPOTEC", 17.036, -96.784),
        ("CIVILIZATION_SIOUX", 43.75, -102.5),
        ("CIVILIZATION_LOWER_SIOUX", 44.550, -94.987),
        ("CIVILIZATION_AMERICAN_CONFEDERACY", 37.540, -77.433),
        ("CIVILIZATION_CHIPPEWA", 46.759, -92.613),
        ("CIVILIZATION_GREAT_PLAINS", 47.086, -109.282),
        ("CIVILIZATION_MIDWEST", 41.884, -87.632),
        ("CIVILIZATION_IROQUOIS", 43.080, -79.071),
        ("CIVILIZATION_INCA", -13.508, -71.972),
        ("CIVILIZATION_MAYA", 14.632, -90.549),
        ("CIVILIZATION_JIVARO", 20.468, -89.213),
        ("CIVILIZATION_APACHE", 32.769, -108.275),
        ("CIVILIZATION_CHEROKEE", 34.679, -83.325),
        ("CIVILIZATION_NAVAJO", 35.399, -110.321),
        ("CIVILIZATION_ANASAZI", 36.060, -107.970),
        ("CIVILIZATION_COMANCHE", 34.605, -98.389),
        ("CIVILIZATION_PIRATES", 17.938, -76.840),
        ("CIVILIZATION_NAZI_GERMANY", 52.516, 13.376),
        ("CIVILIZATION_FINLAND", 60.186, 24.931),
        ("CIVILIZATION_GERMANY", 50.112, 8.683),
        ("CIVILIZATION_AUSTRIA", 48.243, 16.375),
        ("CIVILIZATION_POLAND", 52.228, 21.006),
        ("CIVILIZATION_GOTHS", 58.361, 15.780),
        ("CIVILIZATION_NORWAY", 59.924, 10.752),
        ("CIVILIZATION_DENMARK", 55.690, 12.571),
        ("CIVILIZATION_NETHERLANDS", 52.330, 4.864),
        ("CIVILIZATION_ICELAND", 49.554, 20.125),
        ("CIVILIZATION_IRELAND", 49.553, 20.126),
        ("CIVILIZATION_WALES", 49.552, 20.127),
        ("CIVILIZATION_SCOTLAND", 49.551, 20.128),
        ("CIVILIZATION_ENGLAND", 51.508, -0.128),
        ("CIVILIZATION_BELGIUM", 49.549, 20.130),
        ("CIVILIZATION_BULGARIA", 49.548, 20.131),
        ("CIVILIZATION_SWEDEN", 49.547, 20.132),
        ("CIVILIZATION_SWISS_CONFEDERACY", 49.546, 20.133),
        ("CIVILIZATION_LITHUANIA", 49.545, 20.134),
        ("CIVILIZATION_LATVIA", 49.544, 20.135),
        ("CIVILIZATION_MAGYAR", 49.543, 20.136),
        ("CIVILIZATION_FRANCE", 48.856, 2.341),
        ("CIVILIZATION_SPAIN", 40.413, -3.704),
        ("CIVILIZATION_PORTUGAL", 38.717, -9.167),
        ("CIVILIZATION_ITALY", 41.895, 12.476),
        ("CIVILIZATION_PAPAL", 49.538, 20.145),
        ("CIVILIZATION_GREECE", 37.731, 22.756),
        ("CIVILIZATION_MINOANS", 35.299, 25.170),
        ("CIVILIZATION_MICROSTATESEUR", 49.536, 20.146),
        ("CIVILIZATION_ROMANIA", 49.535, 20.147),
        ("CIVILIZATION_CROATIA", 49.534, 20.148),
        ("CIVILIZATION_SLOVENIA", 49.533, 20.149),
        ("CIVILIZATION_CZECH", 49.532, 20.150),
        ("CIVILIZATION_SLOVAKIA", 48.149, 17.106),
        ("CIVILIZATION_BIH", 49.563, 20.151),
        ("CIVILIZATION_SERBIA", 49.564, 20.152),
        ("CIVILIZATION_ARMENIA", 40.207, 44.556),
        ("CIVILIZATION_KOSOVO", 49.565, 20.153),
        ("CIVILIZATION_UKRAINE", 49.566, 20.154),
        ("CIVILIZATION_RUSSIA", 55.756, 37.615),
        ("CIVILIZATION_GEORGIA", 49.568, 20.156),
        ("CIVILIZATION_CHECHNYA", 49.569, 20.157),
        ("CIVILIZATION_ROME", 41.883, 12.483),
        ("CIVILIZATION_BAKTRIA", 49.529, 20.159),
        ("CIVILIZATION_KAZAKH", 45.046, 45.752),
        ("CIVILIZATION_UZBEK", 41.320, 69.306),
        ("CIVILIZATION_XIONGNU", 41.775, 84.244),
        ("CIVILIZATION_YANGSHAO", 36.042, 114.983),
        ("CIVILIZATION_MANCHURIA", 41.787, 123.404),
        ("CIVILIZATION_AFGHANISTAN", 45.044, 45.754),
        ("CIVILIZATION_CENTRALASUN", 45.043, 45.755),
        ("CIVILIZATION_UYGHUR", 45.042, 45.756),
        ("CIVILIZATION_MONGOL", 47.198, 102.821),
        ("CIVILIZATION_HUNS", 45.041, 45.758),
        ("CIVILIZATION_JAPAN", 35.017, 135.767),
        ("CIVILIZATION_AINU", 45.040, 45.771),
        ("CIVILIZATION_KOREA", 39.019, 125.738),
        ("CIVILIZATION_CHINA", 34.455, 113.025),
        ("CIVILIZATION_TIBET", 29.650, 91.100),
        ("CIVILIZATION_VIETNAM", 21.033, 105.850),
        ("CIVILIZATION_KHMER", 13.433, 103.833),
        ("CIVILIZATION_BURMA", 45.034, 45.761),
        ("CIVILIZATION_BANGLADESH", 45.033, 45.760),
        ("CIVILIZATION_INDIA", 25.611, 85.144),
        ("CIVILIZATION_PAKISTAN", 45.031, 45.758),
        ("CIVILIZATION_SIAM", 17.021, 99.704),
        ("CIVILIZATION_MALAYSIA", 45.029, 45.768),
        ("CIVILIZATION_MICROSTATESA", 45.028, 45.769),
        ("CIVILIZATION_INDONESIA", 45.027, 45.770),
        ("CIVILIZATION_PHILIPPINES", 45.026, 45.771),
        ("CIVILIZATION_ASSYRIA", 35.457, 43.263),
        ("CIVILIZATION_ALBANIA", 21.432, 39.836),
        ("CIVILIZATION_OTTOMAN", 21.431, 39.835),
        ("CIVILIZATION_LEBANON", 21.430, 39.834),
        ("CIVILIZATION_ISRAEL", 31.783, 35.216),
        ("CIVILIZATION_PALMYRA", 21.428, 39.832),
        ("CIVILIZATION_IRAQ", 21.427, 39.831),
        ("CIVILIZATION_IRAN", 21.426, 39.830),
        ("CIVILIZATION_SOMALIA", 2.033, 45.333),
        ("CIVILIZATION_YEMEN", 21.424, 39.828),
        ("CIVILIZATION_ETHIOPIA", 14.117, 38.733),
        ("CIVILIZATION_EGYPT", 26.333, 31.900),
        ("CIVILIZATION_PHOENICIA", 35.602, 35.782),
        ("CIVILIZATION_SUDAN", 21.420, 39.824),
        ("CIVILIZATION_GARAMANTES", 21.419, 39.823),
        ("CIVILIZATION_ABYSSINIANS", 21.418, 39.822),
        ("CIVILIZATION_MORROCO", 21.417, 39.821),
        ("CIVILIZATION_KANEMBORNU", 10.418, 29.825),
        ("CIVILIZATION_MALI", 13.890, -4.540),
        ("CIVILIZATION_BENIN", 10.416, 29.823),
        ("CIVILIZATION_NIGERIA", 10.415, 29.822),
        ("CIVILIZATION_MANDE", 10.414, 29.821),
        ("CIVILIZATION_GHANA", 10.413, 29.820),
        ("CIVILIZATION_CONGO", -6.267, 14.250),
        ("CIVILIZATION_TOGO", 10.411, 29.818),
        ("CIVILIZATION_KITARA", 10.410, 29.817),
        ("CIVILIZATION_MAASAI", 10.409, 29.816),
        ("CIVILIZATION_MUTAPA", 10.408, 29.815),
        ("CIVILIZATION_SOUTH_AFRICA", 10.407, 29.814),
        ("CIVILIZATION_KHOISAN", 10.406, 29.813),
        ("CIVILIZATION_MALAGASY", 10.405, 29.812),
        ("CIVILIZATION_ZULU", -28.317, 31.417),
        ("CIVILIZATION_BABYLON", 32.536, 44.421),
        ("CIVILIZATION_BYZANTIUM", 41.009, 28.976),
        ("CIVILIZATION_CARTHAGE", 36.887, 10.315),
        ("CIVILIZATION_CELT", 46.923, 4.038),
        ("CIVILIZATION_PICTS", 46.923, 4.037),
        ("CIVILIZATION_HITTITES", 41.016, 28.966),
        ("CIVILIZATION_HOLY_ROMAN", 50.775, 6.084),
        ("CIVILIZATION_PERSIA", 30.012, 52.408),
        ("CIVILIZATION_SUMERIA", 31.322, 45.636),
        ("CIVILIZATION_SCANDINAVIA", 63.420, 10.393),
        ("CIVILIZATION_NEANDERTHAL", 51.227, 6.951),
        ("CIVILIZATION_ARAWAK", 14.53, -75.82)
    ]

    # Only add civilizations that actually exist in the game
    for civ_key, lat, lon in coord_data:
        civ_id = GC.getInfoTypeForString(civ_key, True)
        if civ_id > -1:
            _coord_cache[civ_id] = (lat, lon)


def assignCulturallyLinkedStarts():
    """Main entry point for culturally linked starts"""
    print
    "Culturally Linked Starts Enabled."
    CultureLink().assignStartingPlots()
    # Clear cache after use to free memory
    global _coord_cache, _coord_initialized
    _coord_cache = None
    _coord_initialized = False


class CultureLink:
    """Optimized culture link implementation using memory-efficient techniques"""

    # Use __slots__ to reduce memory overhead per instance
    __slots__ = ('starting_plots', 'rw_coords', 'num_players', 'player_indices')

    def __init__(self):
        GC = CyGlobalContext()
        self.num_players = GC.getGame().countCivPlayersEverAlive()
        # Use array for player indices
        self.player_indices = array('i', range(self.num_players))

        # Initialize starting plots
        self.starting_plots = []
        for i in xrange(self.num_players):
            self.starting_plots.append(GC.getPlayer(i).getStartingPlot())

        # Initialize real world coordinates
        coord_cache = _get_coord_cache()
        self.rw_coords = []
        for i in xrange(self.num_players):
            pPlayer = GC.getPlayer(i)
            civ_type = pPlayer.getCivilizationType()
            if civ_type in coord_cache:
                self.rw_coords.append(coord_cache[civ_type])
            else:
                print
                "[ERROR] Culturally Linked Starts: civilization %d not defined" % civ_type
                # Default fallback coordinates
                self.rw_coords.append((0.0, 0.0))

    def assignStartingPlots(self):
        """Assign starting plots using optimized distance calculations"""

        # Compute distance matrices
        sp_distances = self._compute_sp_distances()
        rw_distances = self._compute_rw_distances()

        # Print debug info
        print
        FormatMatrix(sp_distances, "Starting Plots Distance Matrix:")
        print
        FormatMatrix(rw_distances, "Real World Distance Matrix:")

        # Find best permutation
        if self.num_players <= 9:
            best_perm = self._brute_force_search(sp_distances, rw_distances)
        else:
            best_perm = self._ant_colony_optimization(sp_distances, rw_distances)

        # Apply the best permutation
        GC = CyGlobalContext()
        for player_id, plot_id in enumerate(best_perm):
            GC.getPlayer(player_id).setStartingPlot(self.starting_plots[plot_id], True)

    def _compute_sp_distances(self):
        """Compute starting plot distances efficiently"""
        n = self.num_players
        # Pre-calculate max distance once
        max_dist = _get_max_step_distance()

        # Use list of lists for matrix (more memory efficient than nested arrays)
        distances = []
        for i in xrange(n):
            row = [0.0] * n
            distances.append(row)

        # Fill upper triangle and mirror
        for i in xrange(n):
            plot_a = self.starting_plots[i]
            xa, ya = plot_a.getX(), plot_a.getY()
            area_a = plot_a.getArea()

            for j in xrange(i + 1, n):
                plot_b = self.starting_plots[j]
                xb, yb = plot_b.getX(), plot_b.getY()

                # Calculate step distance
                dist = stepDistance(xa, ya, xb, yb) / max_dist

                # Double distance for different areas
                if area_a != plot_b.getArea():
                    dist *= 2

                distances[i][j] = dist
                distances[j][i] = dist

        return distances

    def _compute_rw_distances(self):
        """Compute real world distances efficiently"""
        n = self.num_players

        # Use list of lists for matrix
        distances = []
        for i in xrange(n):
            row = [0.0] * n
            distances.append(row)

        # Fill upper triangle and mirror
        for i in xrange(n):
            lat_a, lon_a = self.rw_coords[i]

            for j in xrange(i + 1, n):
                lat_b, lon_b = self.rw_coords[j]

                # Calculate real world distance
                dist = _calc_rw_distance(lat_a, lon_a, lat_b, lon_b) / DMAX_EARTH

                distances[i][j] = dist
                distances[j][i] = dist

        return distances

    def _brute_force_search(self, sp_dists, rw_dists):
        """Brute force search for small player counts"""
        best_perm = None
        best_error = 1e10  # Large initial value

        # Generate permutations recursively
        def search(perm, used, depth):
            if depth == self.num_players:
                error = self._evaluate_permutation(perm, sp_dists, rw_dists)
                return (list(perm), error)

            min_result = (None, 1e10)
            for i in xrange(self.num_players):
                if not used[i]:
                    perm[depth] = i
                    used[i] = True
                    result = search(perm, used, depth + 1)
                    if result[1] < min_result[1]:
                        min_result = result
                    used[i] = False

            return min_result

        perm = [0] * self.num_players
        used = [False] * self.num_players
        best_perm, best_error = search(perm, used, 0)
        print
        "%s %.4f" % (best_perm, best_error)

        return best_perm

    def _ant_colony_optimization(self, sp_dists, rw_dists):
        """ACO for larger player counts - optimized version"""
        n = self.num_players

        # Adjusted parameters for memory efficiency
        num_ants = n
        num_best = max(1, n // 10)
        num_runs = n * 25
        pheromone_update = 0.34 / n

        # Initialize pheromone matrix
        pheromones = []
        init_val = 1.0 / n
        for i in xrange(n):
            row = [init_val] * n
            pheromones.append(row)

        best_ant = None
        best_error = 1e10

        for run in xrange(num_runs):
            ants = []

            # Generate ants
            for _ in xrange(num_ants):
                perm = self._random_permutation(pheromones)
                error = self._evaluate_permutation(perm, sp_dists, rw_dists)
                ants.append((perm, error))

            # Sort and get best ants
            ants.sort(key=lambda x: x[1])
            best_ants = ants[:num_best]

            # Check for new best
            if best_ants[0][1] < best_error:
                best_ant = best_ants[0][0]
                best_error = best_ants[0][1]
                print
                "%s %.8f (%d)" % (best_ant, best_error, run)

            # Update pheromones
            for i in xrange(n):
                for ant_perm, _ in best_ants:
                    j = ant_perm[i]
                    pheromones[i][j] += pheromone_update

                # Normalize row
                row_sum = sum(pheromones[i])
                if row_sum > 0:
                    for j in xrange(n):
                        pheromones[i][j] /= row_sum

        return best_ant

    def _evaluate_permutation(self, perm, sp_dists, rw_dists):
        """Evaluate permutation error efficiently"""
        error = 0.0
        n = self.num_players

        # Only check upper triangle
        for i in xrange(n):
            pi = perm[i]
            for j in xrange(i + 1, n):
                pj = perm[j]
                diff = abs(sp_dists[i][j] - rw_dists[pi][pj])
                error += diff ** 1.3

        return error

    def _random_permutation(self, pheromones):
        """Generate random permutation based on pheromone matrix"""
        n = self.num_players
        perm = []
        available = range(n)

        for i in xrange(n):
            # Calculate probabilities for available positions
            probs = []
            for j in available:
                probs.append(pheromones[i][j])

            # Normalize
            total = sum(probs)
            if total > 0:
                for k in xrange(len(probs)):
                    probs[k] /= total

            # Select random element
            r = CyGame().getSorenRand().get(65535, "CultureLink") / 65535.0
            cumulative = 0.0
            selected = available[-1]

            for k, prob in enumerate(probs):
                cumulative += prob
                if r < cumulative:
                    selected = available[k]
                    break

            perm.append(selected)
            available.remove(selected)

        return perm


# Optimized distance calculation functions
def _calc_rw_distance(lat_a, lon_a, lat_b, lon_b):
    """Calculate real world distance with optimized trigonometry"""
    # Pre-calculate frequently used values
    lat_sum = lat_a + lat_b
    lat_diff = lat_a - lat_b
    lon_diff = lon_a - lon_b

    F = PI_DIV_360 * lat_sum
    G = PI_DIV_360 * lat_diff
    l = PI_DIV_360 * lon_diff

    # Cache sin/cos values
    sin_G = sin(G)
    cos_G = cos(G)
    sin_F = sin(F)
    cos_F = cos(F)
    sin_l = sin(l)
    cos_l = cos(l)

    sin_G_sq = sin_G * sin_G
    cos_G_sq = cos_G * cos_G
    sin_F_sq = sin_F * sin_F
    cos_F_sq = cos_F * cos_F
    sin_l_sq = sin_l * sin_l
    cos_l_sq = cos_l * cos_l

    S = sin_G_sq * cos_l_sq + cos_F_sq * sin_l_sq
    C = cos_G_sq * cos_l_sq + sin_F_sq * sin_l_sq

    if C == 0:
        return 0.0

    w = atan(sqrt(S / C))
    if w == 0:
        return 0.0

    D = 2 * w * SEMI_MAJOR_AXIS

    # Flattening correction
    R = sqrt(S * C) / w
    H1 = INVERSE_FLATTENING * (3 * R - 1) / (2 * C)
    H2 = INVERSE_FLATTENING * (3 * R + 1) / (2 * S)

    return D * (1 + H1 * sin_F_sq * cos_G_sq - H2 * cos_F_sq * sin_G_sq)


def _get_max_step_distance():
    """Calculate maximum possible step distance once"""
    map_w = CyMap().getGridWidth()
    map_h = CyMap().getGridHeight()

    if map_w > map_h:
        if CyMap().isWrapX():
            return (map_w + 1) // 2
        return map_w
    else:
        if CyMap().isWrapY():
            return (map_h + 1) // 2
        return map_h


def FormatMatrix(matrix, description=None):
    """Format matrix for printing - memory efficient version"""
    if not matrix:
        return "Error: Empty matrix"

    # Use string list and join at end (more efficient than concatenation)
    lines = []

    if description:
        lines.append(description)
        lines.append("")

    lines.append("[")

    n = len(matrix)
    for i in xrange(n):
        if i > 0:
            line = " ["
        else:
            line = "["

        row = matrix[i]
        m = len(row)
        for j in xrange(m):
            val = row[j]
            if val is not None:
                line += "%8.4f" % val
            else:
                line += "    None"

            if j < m - 1:
                line += ","

        if i == n - 1:
            line += "]]"
        else:
            line += "],"

        lines.append(line)

    return "\n".join(lines)