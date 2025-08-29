# RebelTypes.py
#
# by jdog5000
# Version 1.1 - Memory Optimized

# This file sets up the most likely rebel civ types to appear when a revolution occurs in a particular civ.

from CvPythonExtensions import CyGlobalContext

# Use a single dictionary instead of a list, with tuples for immutable data
# Tuples use less memory than lists for fixed collections
RebelTypeDict = {}


# This function actually sets up the lists of most preferable rebel types for each motherland civ type.
# All rebel types in the list are equally likely.
# No limit on length of rebel list, can be empty.
# If none of these are available, defaults to a similar art style civ.
def setup():
    global RebelTypeDict

    # Clear the dictionary once at start
    RebelTypeDict.clear()

    GC = CyGlobalContext()

    # Use local variable to avoid repeated global lookups (saves memory access overhead)
    g = GC.getInfoTypeForString

    # Store all civ IDs in local variables for single lookup
    # This reduces the number of string operations and lookups
    civs = {
        'ara': g('CIVILIZATION_ARABIA'),
        'ass': g('CIVILIZATION_ASSYRIA'),
        'azt': g('CIVILIZATION_AZTEC'),
        'bab': g('CIVILIZATION_BABYLON'),
        'byz': g('CIVILIZATION_BYZANTIUM'),
        'car': g('CIVILIZATION_CARTHAGE'),
        'cel': g('CIVILIZATION_CELT'),
        'chi': g('CIVILIZATION_CHINA'),
        'egy': g('CIVILIZATION_EGYPT'),
        'eng': g('CIVILIZATION_ENGLAND'),
        'eth': g('CIVILIZATION_ETHIOPIA'),
        'fra': g('CIVILIZATION_FRANCE'),
        'ger': g('CIVILIZATION_GERMANY'),
        'gre': g('CIVILIZATION_GREECE'),
        'hit': g('CIVILIZATION_HITTITES'),
        'hol': g('CIVILIZATION_HOLY_ROMAN'),
        'inc': g('CIVILIZATION_INCA'),
        'ind': g('CIVILIZATION_INDIA'),
        'iro': g('CIVILIZATION_IROQUOIS'),
        'jap': g('CIVILIZATION_JAPAN'),
        'khm': g('CIVILIZATION_KHMER'),
        'kor': g('CIVILIZATION_KOREA'),
        'mal': g('CIVILIZATION_MALI'),
        'may': g('CIVILIZATION_MAYA'),
        'mon': g('CIVILIZATION_MONGOL'),
        'nat': g('CIVILIZATION_SIOUX'),
        'net': g('CIVILIZATION_NETHERLANDS'),
        'ott': g('CIVILIZATION_OTTOMAN'),
        'per': g('CIVILIZATION_PERSIA'),
        'por': g('CIVILIZATION_PORTUGAL'),
        'rom': g('CIVILIZATION_ROME'),
        'rus': g('CIVILIZATION_RUSSIA'),
        'sia': g('CIVILIZATION_SIAM'),
        'spa': g('CIVILIZATION_SPAIN'),
        'sum': g('CIVILIZATION_SUMERIA'),
        'usa': g('CIVILIZATION_AMERICA'),
        'vik': g('CIVILIZATION_SCANDINAVIA'),
        'zul': g('CIVILIZATION_ZULU')
    }

    # Use tuples instead of lists for rebel types (immutable, less memory)
    # Only store entries that have rebel types (no empty lists)
    # Format: RebelTypeDict[iHomeland] = (iRebel1, iRebel2, iRebel3)

    RebelTypeDict[civs['ara']] = (civs['egy'], civs['per'], civs['ott'], civs['bab'], civs['sum'], civs['ass'])
    RebelTypeDict[civs['ass']] = (civs['per'], civs['bab'], civs['sum'], civs['hit'], civs['egy'], civs['ara'])
    RebelTypeDict[civs['azt']] = (civs['inc'], civs['spa'], civs['nat'], civs['may'], civs['iro'])
    RebelTypeDict[civs['bab']] = (civs['sum'], civs['per'], civs['gre'], civs['egy'], civs['ara'], civs['ass'],
                                  civs['hit'])
    RebelTypeDict[civs['byz']] = (civs['gre'], civs['rom'], civs['ott'], civs['hol'], civs['hit'])
    RebelTypeDict[civs['car']] = (civs['rom'], civs['gre'], civs['mal'], civs['spa'])
    RebelTypeDict[civs['cel']] = (civs['fra'], civs['eng'], civs['ger'], civs['spa'])
    RebelTypeDict[civs['chi']] = (civs['kor'], civs['mon'], civs['ind'], civs['jap'], civs['khm'], civs['sia'])
    RebelTypeDict[civs['egy']] = (civs['bab'], civs['ara'], civs['per'], civs['gre'], civs['eth'], civs['ass'],
                                  civs['hit'])
    RebelTypeDict[civs['eng']] = (civs['usa'], civs['ind'], civs['zul'], civs['net'], civs['cel'])
    RebelTypeDict[civs['eth']] = (civs['egy'], civs['mal'], civs['zul'], civs['ara'])
    RebelTypeDict[civs['fra']] = (civs['ger'], civs['cel'], civs['eng'], civs['mal'], civs['hol'])
    RebelTypeDict[civs['ger']] = (civs['fra'], civs['rus'], civs['vik'], civs['hol'], civs['net'])
    RebelTypeDict[civs['gre']] = (civs['rom'], civs['per'], civs['car'], civs['ott'], civs['hit'])
    RebelTypeDict[civs['hit']] = (civs['ass'], civs['egy'], civs['per'], civs['ott'], civs['byz'], civs['gre'],
                                  civs['bab'])
    RebelTypeDict[civs['hol']] = (civs['ger'], civs['fra'], civs['spa'], civs['byz'])
    RebelTypeDict[civs['inc']] = (civs['azt'], civs['spa'], civs['may'], civs['nat'], civs['iro'])
    RebelTypeDict[civs['ind']] = (civs['per'], civs['sia'], civs['chi'], civs['eng'], civs['khm'])
    RebelTypeDict[civs['iro']] = (civs['nat'], civs['azt'], civs['may'], civs['inc'], civs['usa'])
    RebelTypeDict[civs['jap']] = (civs['kor'], civs['chi'], civs['mon'], civs['khm'], civs['sia'])
    RebelTypeDict[civs['khm']] = (civs['sia'], civs['ind'], civs['chi'], civs['mon'], civs['jap'])
    RebelTypeDict[civs['kor']] = (civs['jap'], civs['chi'], civs['mon'], civs['khm'])
    RebelTypeDict[civs['mal']] = (civs['car'], civs['egy'], civs['fra'], civs['zul'], civs['eth'])
    RebelTypeDict[civs['may']] = (civs['azt'], civs['inc'], civs['spa'], civs['nat'], civs['iro'])
    RebelTypeDict[civs['mon']] = (civs['chi'], civs['rus'], civs['per'], civs['kor'], civs['sia'])
    RebelTypeDict[civs['nat']] = (civs['iro'], civs['azt'], civs['may'], civs['usa'], civs['inc'])
    RebelTypeDict[civs['net']] = (civs['por'], civs['ger'], civs['eng'], civs['usa'])
    RebelTypeDict[civs['ott']] = (civs['per'], civs['gre'], civs['ger'], civs['ara'], civs['byz'], civs['hit'])
    RebelTypeDict[civs['per']] = (civs['ott'], civs['ind'], civs['mon'], civs['gre'], civs['sum'], civs['bab'],
                                  civs['ass'], civs['hit'])
    RebelTypeDict[civs['por']] = (civs['spa'], civs['fra'], civs['net'])
    RebelTypeDict[civs['rom']] = (civs['gre'], civs['car'], civs['cel'], civs['egy'], civs['byz'])
    RebelTypeDict[civs['rus']] = (civs['vik'], civs['ger'], civs['mon'], civs['per'])
    RebelTypeDict[civs['sia']] = (civs['khm'], civs['ind'], civs['chi'], civs['mon'], civs['jap'])
    RebelTypeDict[civs['spa']] = (civs['por'], civs['ara'], civs['azt'], civs['inc'], civs['hol'])
    RebelTypeDict[civs['sum']] = (civs['bab'], civs['ott'], civs['gre'], civs['per'], civs['ass'])
    RebelTypeDict[civs['usa']] = (civs['eng'], civs['azt'], civs['nat'], civs['iro'])
    RebelTypeDict[civs['vik']] = (civs['rus'], civs['ger'], civs['eng'], civs['usa'])
    RebelTypeDict[civs['zul']] = (civs['mal'], civs['ara'], civs['egy'], civs['eth'])

    # Clean up the temporary civs dictionary to free memory
    del civs


# Helper function to get rebel types - returns tuple or empty tuple
def getRebelTypes(iCiv):
    """
    Get rebel types for a civilization.
    Returns a tuple of rebel civilization IDs, or empty tuple if none defined.
    More memory efficient than returning None or empty list.
    """
    return RebelTypeDict.get(iCiv, ())


# For backward compatibility with old mod code that might expect RebelTypeList
def getRebelTypeList():
    """
    Legacy function for compatibility.
    Creates a list structure from the dictionary on demand.
    Only use if absolutely necessary for backward compatibility.
    """
    GC = CyGlobalContext()
    result = []
    for iCiv in xrange(GC.getNumCivilizationInfos()):
        # Convert tuple to list for each civ
        rebels = RebelTypeDict.get(iCiv, ())
        if rebels:
            result.append(list(rebels))
        else:
            result.append([])
    return result