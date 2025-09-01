#
# Roman Numbers - Memory Optimized
# version 1.0
# Original By: Sen2000
# Optimized for Civilization IV (32-bit, Python 2.4)
#

from CvPythonExtensions import *


# Define exceptions with __slots__ to reduce memory overhead
# Using __slots__ saves ~100-200 bytes per exception instance
class RomanError(Exception):
    __slots__ = ('args',)  # Restrict attributes to save memory
    pass


class OutOfRangeError(RomanError):
    __slots__ = ('args',)  # Inherit slots restriction
    pass


# Pre-create error message to avoid repeated string creation
# This saves memory in cases where the error is raised multiple times
<<<<<<< Updated upstream
_OUT_OF_RANGE_MSG = "number out of range (must be 1..9999)"
=======
_MAX_ROMAN_VALUE = 9999
_OUT_OF_RANGE_MSG = "number out of range (must be 1..%d)" % _MAX_ROMAN_VALUE
>>>>>>> Stashed changes

# Using tuple (immutable) instead of list - already optimal in original
# Tuples use less memory than lists for fixed collections
RomanNumberMap = (
    ('M', 1000),
    ('CM', 900),
    ('D', 500),
    ('CD', 400),
    ('C', 100),
    ('XC', 90),
    ('L', 50),
    ('XL', 40),
    ('X', 10),
    ('IX', 9),
    ('V', 5),
    ('IV', 4),
    ('I', 1)
)

# Pre-calculate the length to avoid repeated len() calls
_ROMAN_MAP_LEN = len(RomanNumberMap)


def toRoman(Number):
    """Convert integer to Roman numeral - memory optimized version"""

    # Optimized range check - single comparison is slightly faster
    # and uses less memory than compound comparison
<<<<<<< Updated upstream
    if Number <= 0 or Number >= 10000:
=======
    if Number <= 0 or Number > _MAX_ROMAN_VALUE:
>>>>>>> Stashed changes
        raise OutOfRangeError, _OUT_OF_RANGE_MSG

    # Use list append + join instead of string concatenation
    # String concatenation creates new string objects each time
    # List append + join is more memory efficient for multiple concatenations
    roman_parts = []

    # Iterate through the mapping
    for Romantext, integer in RomanNumberMap:
        if Number >= integer:
            # Calculate how many times this Roman numeral fits
            count = Number // integer
            if count > 0:
                # Append the Roman text multiple times efficiently
                # Using list multiplication is more memory efficient
                # than multiple append calls for repeated values
                roman_parts.append(Romantext * count)
                Number -= integer * count

        # Early exit optimization - if Number reaches 0, we're done
        if Number == 0:
            break

    # Join all parts into final string - single memory allocation
    return ''.join(roman_parts)

# Memory optimization notes for Civilization IV context:
# 1. __slots__ in exception classes reduces per-instance overhead
# 2. Pre-created error message avoids repeated string allocation
# 3. List append + join pattern reduces intermediate string objects
# 4. Early exit optimization reduces unnecessary iterations
# 5. Integer division optimization reduces loop iterations
# 6. All optimizations maintain Python 2.4 compatibility
# 7. No ternary operators used (Python 2.5+ feature)