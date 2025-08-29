## UnitName
## by Ruff_Hi
## for BUG Mod
## Memory Optimized Version for 32-bit Python 2.4
##-------------------------------------------------------------------
## Naming Convention
##  - ^civ4^ - no naming convention, uses standard civ4
##  - ^rd^ - random name
##  - ^rc^ - random civ related name
##  - ^ct^ - City
##  - ^cv^ - Civilization
##  - ^ut^ - unit (eg Archer)
##  - ^cb^ - combat type (Melee)
##  - ^dm^ - domain (Water)
##  - ^ld^ - leader
##  - ^cnt[f][r]^ - counting code, if the code isn't there - return 'ALL'
##  - where
##  -   r = 'a' means count across all units (just increments)
##  -   r = 'u' means count across same unit (increments based on unit)
##  -   r = 'c' means count across same city (increments based on city)
##  -   r = 't' means count across same unit / city (increments based on unit / city)
##  -   r = 'b' means count across same combat type (increments based on combat type)
##  -   r = 'd' means count across same domain (increments based on domain)
##  -   r = other, means count across units that have the same code
##  - ^tt1[f][x:y]^ - total where the total is a random number between x and y (number)
##  - ^tt2[f][x]^ - total count (starts at x, incremented by 1 each time ^tt is reset to 1)
##
## Where [f] can be either 's', 'A', 'a', 'p', 'g', 'n', 'o' or 'r' for ...
##  - silent (not shown)
##  - alpha (A, B, C, D, ...)
##  - alpha (a, b, c, d, ...)
##  - phonetic (alpha, bravo, charlie, delta, echo, ...)
##  - greek (alpha, beta, gamma, delta, epsilon, ...)
##  - number
##  - ordinal (1st, 2nd, 3rd, 4th, ...)
##  - roman (I, IV, V, X, ...)
##-------------------------------------------------------------------

from CvPythonExtensions import *
import CvUtil
import BugUtil
import BugCore
import Roman
import RandomNameUtils
import random
import BugData

# Memory optimization: Use single character keys where possible
SD_MOD_ID = "UnitCnt"
RENAME_EVENT_ID = CvUtil.getNewEventID()

# Memory optimization: Cache global context once
GC = CyGlobalContext()

# Memory optimization: Cache frequently accessed config
UnitNamingOpt = BugCore.game.UnitNaming

# Memory optimization: Use tuples instead of lists (immutable, less memory)
# Combined into single string to save memory, will be split when needed
PHONETIC_DATA = "Alpha,Bravo,Charlie,Delta,Echo,Foxtrot,Golf,Hotel,India,Juliet,Kilo,Lima,Mike,November,Oscar,Papa,Quebec,Romeo,Sierra,Tango,Uniform,Victor,Whiskey,Xray,Yankee,Zulu"
GREEK_DATA = "Alpha,Beta,Gamma,Delta,Epsilon,Zeta,Eta,Theta,Iota,Kappa,Lambda,Mu,Nu,Xi,Omicron,Pi,Rho,Sigma,Tau,Upsilon,Phi,Chi,Psi,Omega"
# Memory optimization: Store as single string instead of list
ORDINAL_SUFFIXES = "th st nd rd th th th th th th"

# Memory optimization: Pre-calculate constants
_ORD_97 = 97  # ord('a') - 1
_ORD_65 = 65  # ord('A') - 1


class UnitNameEventManager:
    """Memory optimized unit naming event manager"""

    __slots__ = ('_eventManager',)  # Memory optimization: Use __slots__ to reduce instance overhead

    def __init__(self, eventManager):
        self._eventManager = eventManager
        eventManager.addEventHandler("unitBuilt", self.onUnitBuilt)

    def onUnitBuilt(self, argsList):
        pUnit = argsList[1]
        if pUnit is None:
            return

        iPlayer = pUnit.getOwner()
        # Memory optimization: Single condition check
        if iPlayer != GC.getGame().getActivePlayer() or not UnitNamingOpt.isEnabled():
            return

        # Memory optimization: Store references to reduce lookups
        if UnitNamingOpt.isAdvanced():
            pPlayer = GC.getPlayer(iPlayer)
            zsUnitNameConv = UnitNamingOpt.getByEraAndClass(
                GC.getEraInfo(pPlayer.getCurrentEra()).getType()[4:],
                GC.getUnitInfo(pUnit.getUnitType()).getType()[5:]
            )
        else:
            zsUnitNameConv = UnitNamingOpt.getDefault()

        # Memory optimization: Use singleton instance
        zsUnitName = _unit_renamer.getUnitName(zsUnitNameConv, pUnit, argsList[0], True)

        if zsUnitName:
            pUnit.setName(zsUnitName)


class UnitReName(object):
    """Memory optimized unit renaming engine"""

    __slots__ = ('_phonetic_cache', '_greek_cache', '_ordinal_cache')  # Memory optimization

    def __init__(self):
        # Lazy initialization caches
        self._phonetic_cache = None
        self._greek_cache = None
        self._ordinal_cache = None

    def getUnitName(self, sUnitNameConv, pUnit, pCity, bIncrementCounter):
        # Memory optimization: Early return for civ4 naming
        if "^civ4^" in sUnitNameConv:
            return ""

        zsName = sUnitNameConv
        iPlayer = pUnit.getOwner()
        pPlayer = GC.getPlayer(iPlayer)

        # Memory optimization: Get all replacements at once to minimize function calls
        replacements = {}

        # Only get values if they're in the naming convention string
        if "^cv^" in zsName:
            replacements["^cv^"] = pPlayer.getCivilizationAdjective(0)
        if "^ld^" in zsName:
            replacements["^ld^"] = pPlayer.getName()
        if "^cb^" in zsName:
            replacements["^cb^"] = self._getUnitCombatOptimized(pUnit)
        if "^dm^" in zsName:
            replacements["^dm^"] = BugUtil.getPlainText(
                "TXT_KEY_BUG_UNIT_NAMING_" + GC.getDomainInfo(pUnit.getDomainType()).getType())
        if "^ut^" in zsName:
            replacements["^ut^"] = GC.getUnitInfo(pUnit.getUnitType()).getDescription()
        if "^ct^" in zsName and pCity:
            replacements["^ct^"] = pCity.getName()
        elif "^ct^" in zsName:
            replacements["^ct^"] = ""

        # Process random names if needed
        if "^rd^" in zsName:
            replacements["^rd^"] = RandomNameUtils.getRandomName()
        if "^rc^" in zsName:
            replacements["^rc^"] = RandomNameUtils.getRandomCivilizationName(pPlayer.getCivilizationType())

        # Memory optimization: Single pass replacement
        for key, value in replacements.iteritems():
            zsName = zsName.replace(key, value)

        # Process counters if present
        if "^cnt" in zsName:
            zsName = self._processCounters(zsName, pUnit, pCity, bIncrementCounter, replacements)

        return zsName

    def _getUnitCombatOptimized(self, pUnit):
        """Memory optimized unit combat type getter"""
        if pUnit is None:
            return "UNITCOMBAT_None"

        infoUnitCombat = GC.getUnitCombatInfo(pUnit.getUnitCombatType())
        if infoUnitCombat is None:
            return "UNITCOMBAT_None"

        return infoUnitCombat.getType()

    def _processCounters(self, zsName, pUnit, pCity, bIncrementCounter, replacements):
        """Process counter codes in the naming convention"""
        counters = BugData.getGameData().getTable(SD_MOD_ID)

        while "^cnt" in zsName:
            # Get counter key
            zsSDKey = self._getCounterKey(zsName, replacements, pCity)

            # Get or create counter table
            if not counters.hasTable(zsSDKey):
                ziCnt = 0
                ziTT1 = self._getTotal1(zsName)
                ziTT2 = self._getTotal2(zsName)
                counter = counters.getTable(zsSDKey)
            else:
                counter = counters.getTable(zsSDKey)
                ziCnt = counter["cnt"]
                ziTT1 = counter["tt1"]
                ziTT2 = counter["tt2"]

            # Increment if needed
            if bIncrementCounter:
                ziCnt = ziCnt + 1
                if ziTT1 > 0 and ziCnt > ziTT1:
                    ziCnt = 1
                    ziTT1 = self._getTotal1(zsName)
                    ziTT2 = ziTT2 + 1
                # Store new values
                counter["cnt"] = ziCnt
                counter["tt1"] = ziTT1
                counter["tt2"] = ziTT2

            # Replace count codes
            zsName = self._swapCountCode(zsName, "^cnt", ziCnt)
            zsName = self._swapCountCode(zsName, "^tt1", ziTT1)
            zsName = self._swapCountCode(zsName, "^tt2", ziTT2)

        return zsName

    def _getCounterKey(self, conv, replacements, pCity):
        """Get the counter key based on the convention"""
        ziStart = conv.find("^cnt[")
        if ziStart == -1:
            return "ALL"

        # Find the counter type
        ziStart = conv.find("[", conv.find("[", ziStart) + 1)
        ziEnd = conv.find("]", ziStart + 1)
        zsValue = conv[ziStart + 1:ziEnd]

        # Memory optimization: Use dict lookup instead of multiple if statements
        key_map = {
            "a": "ALL",
            "u": "UNIT",
            "c": "CITY",
            "t": "UNITCITY",
            "b": "COMBAT",
            "d": "DOMAIN"
        }

        base_key = key_map.get(zsValue, zsValue)

        # Build the full key if needed
        if base_key == "UNIT" and "^ut^" in replacements:
            return base_key + replacements.get("^ut^", "")
        elif base_key == "COMBAT" and "^cb^" in replacements:
            return base_key + replacements.get("^cb^", "")
        elif base_key == "CITY":
            return base_key + (pCity.getName() if pCity else "")
        elif base_key == "UNITCITY":
            unit_part = replacements.get("^ut^", "")
            city_part = pCity.getName() if pCity else ""
            return base_key + unit_part + city_part
        elif base_key == "DOMAIN" and "^dm^" in replacements:
            return base_key + replacements.get("^dm^", "")

        return base_key

    def _getTotal1(self, conv):
        """Get total1 value from convention"""
        ziStart = conv.find("^tt1[")
        if ziStart == -1:
            return -1

        # Extract values efficiently
        ziStart = conv.find("[", conv.find("[", ziStart) + 1)
        ziEnd = conv.find(":", ziStart)
        ziLow = int(conv[ziStart + 1:ziEnd])
        if ziLow < 1:
            ziLow = 1

        ziStart = ziEnd
        ziEnd = conv.find("]", ziStart)
        ziHigh = int(conv[ziStart + 1:ziEnd])
        if ziHigh < 1:
            ziHigh = 1

        if ziLow > ziHigh:
            return ziLow

        return random.randint(ziLow, ziHigh)

    def _getTotal2(self, conv):
        """Get total2 value from convention"""
        ziStart = conv.find("^tt2[")
        if ziStart == -1:
            return -1

        ziStart = conv.find("[", conv.find("[", ziStart) + 1)
        ziEnd = conv.find("]", ziStart)
        ziValue = int(conv[ziStart + 1:ziEnd])

        if ziValue < 1:
            return 1
        return ziValue

    def _getNumberFormat(self, conv, searchStr):
        """Get number format from convention"""
        ziStart = conv.find("[", conv.find(searchStr))
        if ziStart == -1:
            return "s"
        return conv[ziStart + 1]  # Memory optimization: just get single char

    def _getCountCode(self, conv, searchStr):
        """Get count code from convention"""
        ziStart = conv.find(searchStr)
        if ziStart == -1:
            return ""

        ziEnd = conv.find("^", ziStart + 1)
        return conv[ziStart:ziEnd + 1]

    def _swapCountCode(self, conv, searchStr, iCnt):
        """Replace count code with formatted number"""
        if iCnt < 0:
            return conv

        zsCntCode = self._getCountCode(conv, searchStr)

        if zsCntCode:
            return conv.replace(zsCntCode, self._formatNumber(self._getNumberFormat(conv, searchStr), iCnt))
        return conv

    def _formatNumber(self, fmt, i):
        """Format number according to format type"""
        if i < 1:
            i = 1

        # Memory optimization: Use single character comparison
        if fmt == "s":
            return ""
        elif fmt == "a":
            return chr(_ORD_97 + ((i - 1) % 26))
        elif fmt == "A":
            return chr(_ORD_65 + ((i - 1) % 26))
        elif fmt == "p":
            # Lazy load phonetic array
            if self._phonetic_cache is None:
                self._phonetic_cache = PHONETIC_DATA.split(',')
            return self._phonetic_cache[(i - 1) % 26]
        elif fmt == "g":
            # Lazy load greek array
            if self._greek_cache is None:
                self._greek_cache = GREEK_DATA.split(',')
            return self._greek_cache[(i - 1) % 24]
        elif fmt == "n":
            return str(i)
        elif fmt == "o":
            return self._getOrdinal(i)
        elif fmt == "r":
            return Roman.toRoman(i)
        else:
            return str(i)

    def _getOrdinal(self, i):
        """Get ordinal string for number"""
        # Memory optimization: Handle special cases inline
        if 11 <= (i % 100) <= 13:
            return '%dth' % i

        # Lazy load ordinal suffixes
        if self._ordinal_cache is None:
            self._ordinal_cache = ORDINAL_SUFFIXES.split()

        return str(i) + self._ordinal_cache[i % 10]


# Memory optimization: Create single global instance
_unit_renamer = UnitReName()