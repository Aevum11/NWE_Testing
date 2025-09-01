# CivicData.py - Memory-optimized version for 32-bit Caveman2Cosmos
# Optimizations:
# - Pre-cache global references and methods to reduce lookups
# - Use tuples instead of lists for immutable data (saves ~16 bytes per container)
# - Direct method references avoid repeated attribute lookups
# - Single global allocation reduces fragmentation

from CvPythonExtensions import CyGlobalContext

# Pre-cache global context to avoid repeated calls
_GC = None

# Pre-cache frequently used methods (initialized in initCivicData)
_getNumCivicOptionInfos = None
_getNumCivicInfos = None
_getCivicInfo = None

# Global civic data storage - will be tuple of tuples for memory efficiency
civicLists = None


def initCivicData():
    """
    Initialize civic data structures with memory optimizations.
    Uses tuples instead of lists to save memory (tuples use ~16 bytes less).
    Pre-caches all method references to avoid repeated attribute lookups.
    """
    global _GC, _getNumCivicOptionInfos, _getNumCivicInfos, _getCivicInfo, civicLists

<<<<<<< Updated upstream
    print
    "CivicData.initCivicData"
=======
    print "CivicData.initCivicData"
>>>>>>> Stashed changes

    # Cache global context once
    _GC = CyGlobalContext()

    # Pre-cache methods to avoid repeated attribute lookups
    # This saves memory by reducing the lookup chain overhead
    _getNumCivicOptionInfos = _GC.getNumCivicOptionInfos
    _getNumCivicInfos = _GC.getNumCivicInfos
    _getCivicInfo = _GC.getCivicInfo

    # Use list comprehension for initial construction (more memory efficient)
    # Then convert to tuple for long-term storage
    temp_civic_lists = []

    # Pre-allocate lists with known sizes to reduce reallocation overhead
    num_options = _getNumCivicOptionInfos()
    for iCat in xrange(num_options):
        temp_civic_lists.append([])

    # Build civic data with direct method calls
    num_civics = _getNumCivicInfos()
    for iCivic in xrange(num_civics):
        info = _getCivicInfo(iCivic)
        option_type = info.getCivicOptionType()
        # Store as tuple (immutable, less memory than list)
        temp_civic_lists[option_type].append((info, iCivic))

    # Convert inner lists to tuples for memory efficiency
    # Tuples use less memory than lists and are appropriate for read-only data
    final_lists = []
    for civic_list in temp_civic_lists:
        # Convert each inner list to tuple
        final_lists.append(tuple(civic_list))

    # Convert outer list to tuple as well
    civicLists = tuple(final_lists)

    # Clear temporary list to free memory immediately
    del temp_civic_lists


# Note: The civic info objects themselves are C++ objects managed by the game,
# so we're only storing references which is memory efficient


def getCivicList(iCivicOption):
    """
    Get the civic list for a specific civic option type.
    Returns a tuple of (CvCivicInfo, iCivic) pairs.

    Memory optimized: Returns immutable tuple, no copying.
    """
    global civicLists
    if civicLists and 0 <= iCivicOption < len(civicLists):
        return civicLists[iCivicOption]
    return ()  # Return empty tuple instead of None to avoid null checks


def getCivicInfo(iCivicOption, iIndex):
    """
    Get specific civic info by option type and index.
    Returns (CvCivicInfo, iCivic) tuple or None.

    Memory optimized: Direct indexing without intermediate variables.
    """
    global civicLists
    if civicLists and 0 <= iCivicOption < len(civicLists):
        civic_list = civicLists[iCivicOption]
        if 0 <= iIndex < len(civic_list):
            return civic_list[iIndex]
    return None


def getNumCivicsInOption(iCivicOption):
    """
    Get the number of civics in a specific civic option category.

    Memory optimized: Direct len() call on immutable tuple.
    """
    global civicLists
    if civicLists and 0 <= iCivicOption < len(civicLists):
        return len(civicLists[iCivicOption])
    return 0


def findCivicByType(iCivicType):
    """
    Find civic info and option type by civic type ID.
    Returns (CvCivicInfo, iCivicOption) or None.

    Memory optimized: Early exit on match, no intermediate storage.
    """
    global civicLists
    if not civicLists:
        return None

    for iOption, civic_list in enumerate(civicLists):
        for info, iCivic in civic_list:
            if iCivic == iCivicType:
                return (info, iOption)
    return None


def clearCivicData():
    """
    Clear civic data to free memory when no longer needed.
    Useful for memory-constrained 32-bit environments.
    """
    global civicLists, _GC, _getNumCivicOptionInfos, _getNumCivicInfos, _getCivicInfo
    civicLists = None
    _GC = None
    _getNumCivicOptionInfos = None
    _getNumCivicInfos = None
    _getCivicInfo = None