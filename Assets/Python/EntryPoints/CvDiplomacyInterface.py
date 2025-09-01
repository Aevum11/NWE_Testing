import CvDiplomacy

# Memory optimization: Create a single module-level instance instead of creating new ones in each function
# This avoids repeated object allocation/deallocation overhead in 32-bit memory-constrained environment
_diploClass = None


def _getDiploClass():
    """
    Lazy initialization of diplomacy class instance.
    Returns cached instance to avoid memory overhead of repeated instantiation.
    """
    global _diploClass
    if _diploClass is None:
        _diploClass = CvDiplomacy.CvDiplomacy()
    return _diploClass


def beginDiplomacy(argsList):
    """
    This is what gets called when you first begin diplomacy
    The first parameter argsList[0] is the 'comment type', or how they feel about you

    Memory optimizations:
    - Direct unpacking of arguments reduces intermediate variable creation
    - Reuses single diplomacy instance instead of creating new one
    """
    # Direct unpacking minimizes temporary variable creation
    eComment = argsList[0]
    commentArgsSize = argsList[1]

    # Efficient argument passing - avoid creating unnecessary list copies
    diploClass = _getDiploClass()
    if commentArgsSize:
        # Direct slice passing without intermediate variable
        # Python 2.4 compatible - no ternary operators
        diploClass.setAIComment(eComment, *argsList[2:])
    else:
        # Pass no additional arguments
        diploClass.setAIComment(eComment)

    # Explicit cleanup of local references in 32-bit environment
    del eComment
    del commentArgsSize
    del diploClass


def handleUserResponse(argsList):
    """
    First parameter of argsList is the comment they clicked on

    Memory optimizations:
    - Direct argument unpacking reduces memory overhead
    - Reuses single diplomacy instance
    """
    # Direct unpacking with minimal temporary variables
    diploClass = _getDiploClass()
    # Pass arguments directly without creating intermediate variables
    diploClass.handleUserResponse(argsList[0], argsList[1], argsList[2])

    # Explicit cleanup
    del diploClass


def dealCanceled():
    """
    Handles deal cancellation

    Memory optimizations:
    - Reuses single diplomacy instance
    - No unnecessary variable creation
    """
    diploClass = _getDiploClass()
    diploClass.dealCanceled()
    del diploClass


def refresh(argsList):
    """
    Refreshes diplomacy responses

    Memory optimizations:
    - Direct argument passing
    - Reuses single diplomacy instance
    """
    diploClass = _getDiploClass()
    # Direct indexing without intermediate variable
    diploClass.determineResponses(argsList[0])
    del diploClass


def toggleDebugLogging():
    """
    Toggles debug logging state

    Memory optimizations:
    - Direct attribute modification without instance creation
    """
    # Direct module attribute access - no instance needed
    CvDiplomacy.DebugLogging = not CvDiplomacy.DebugLogging


def cleanup():
    """
    Cleanup function to explicitly free the cached diplomacy instance.
    Call this when diplomacy module is no longer needed to free memory.
    Useful in 32-bit environments with limited address space.
    """
    global _diploClass
    if _diploClass is not None:
        _diploClass = None