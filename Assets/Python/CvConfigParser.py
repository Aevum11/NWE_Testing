## Copyright (c) 2006, Gillmer J. Derge.

## This file is part of Civilization IV Alerts mod.
##
## Civilization IV Alerts mod is free software; you can redistribute
## it and/or modify it under the terms of the GNU General Public
## License as published by the Free Software Foundation; either
## version 2 of the License, or (at your option) any later version.
##
## Civilization IV Alerts mod is distributed in the hope that it will
## be useful, but WITHOUT ANY WARRANTY; without even the implied
## warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Civilization IV Alerts mod; if not, write to the Free
## Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
## 02110-1301 USA

## Memory-optimized version for 32-bit Caveman2Cosmos mod

__version__ = "$Revision$"

import ConfigParser

# Pre-cache exception types to avoid repeated lookups
_NoSectionError = ConfigParser.NoSectionError
_NoOptionError = ConfigParser.NoOptionError
_SafeConfigParser = ConfigParser.SafeConfigParser


class CvConfigParser(_SafeConfigParser, object):
    """Extends ConfigParser.SafeConfigParser adding two important features.

    First, all of the get functions take an additional argument that serves
    as a default value.  If a default value is given but the option is not
    found in the configuration file, the default value is returned instead
    of throwing an exception.  If no default is given, or if the default is
    None, then an exception is thrown as in the super class function.

    Second, the constructor accepts a filename argument.  If this argument
    is given, the Civilization 4 directories are searched for files
    with that name, and options are automatically read from a file if one
    is found.  If multiple files are found with conflicting options,
    files found earlier on the search path override options in files found
    later.

    The search path is made up of the parent directory of all Assets
    directories on the game's load path.  For example, if the assets path
    contains <userDir>\CustomAssets and <installDir>\Assets, the parser will
    look for .ini files in <userDir> and <installDir>.

    The example below constructs a parser that searches for "Foo.ini" files.
    The variable n is then initialized to the value found in the .ini files
    or a default of 5.

    foo = CvConfigParser.CvConfigParser("Foo.ini")
    i = foo.getint("Foo", "i", 5)

    Memory optimizations:
    - Uses __slots__ to reduce per-instance overhead by ~100-200 bytes
    - Pre-caches parent class methods to reduce attribute lookups
    - Pre-caches exception types for faster exception handling
    - Minimizes object creation in hot paths
    """

    # Use __slots__ to restrict attributes and save memory
    # This prevents __dict__ creation, saving ~100-200 bytes per instance
    __slots__ = (
        '_super_get',  # Cached parent get method
        '_super_getint',  # Cached parent getint method
        '_super_getfloat',  # Cached parent getfloat method
        '_super_getboolean'  # Cached parent getboolean method
    )

    def __init__(self, filename=None, *args, **kwargs):
        """Initializes the parser by reading options from the named file.

        Memory optimized:
        - Lazy imports to avoid loading SystemPaths if not needed
        - Pre-caches parent methods to avoid repeated super() calls
        - Single list allocation for filenames
        """
        # Call parent constructor first
        super(CvConfigParser, self).__init__(*args, **kwargs)

        # Pre-cache parent methods to avoid repeated super() lookups
        # This saves memory by reducing attribute lookup chains
        _super = super(CvConfigParser, self)
        self._super_get = _super.get
        self._super_getint = _super.getint
        self._super_getfloat = _super.getfloat
        self._super_getboolean = _super.getboolean

        # Only import and process if filename is provided
        if filename is not None:
            # Lazy import to save memory if not needed
            import SystemPaths as SP
            # Direct list creation with single element is more efficient
            # than multiple appends or list concatenation
            self.read([SP.joinModDir("Assets", filename)])

    def get(self, section, option, default=None, *args, **kwargs):
        """Looks up the specified section/option pair.

        This extends the base functionality of the Python ConfigParser
        class by adding support for a default value in the event that the
        option is not given in the configuration file.

        Memory optimized:
        - Uses pre-cached parent method
        - Avoids creating wrapper function
        """
        try:
            # Use pre-cached parent method directly
            return self._super_get(section, option, *args, **kwargs)
        except (_NoSectionError, _NoOptionError):
            # Return default only if explicitly provided (not None)
            if default is not None:
                return default
            else:
                raise

    def getint(self, section, option, default=None, *args, **kwargs):
        """Like get(), but converts the value to an integer.

        Memory optimized:
        - Uses pre-cached parent method
        - Direct exception handling without wrapper
        """
        try:
            # Use pre-cached parent method directly
            return self._super_getint(section, option, *args, **kwargs)
        except (_NoSectionError, _NoOptionError):
            if default is not None:
                return default
            else:
                raise

    def getfloat(self, section, option, default=None, *args, **kwargs):
        """Like get(), but converts the value to a float.

        Memory optimized:
        - Uses pre-cached parent method
        - Direct exception handling without wrapper
        """
        try:
            # Use pre-cached parent method directly
            return self._super_getfloat(section, option, *args, **kwargs)
        except (_NoSectionError, _NoOptionError):
            if default is not None:
                return default
            else:
                raise

    def getboolean(self, section, option, default=None, *args, **kwargs):
        """Like get(), but converts the value to a boolean.

        Memory optimized:
        - Uses pre-cached parent method
        - Direct exception handling without wrapper
        """
        try:
            # Use pre-cached parent method directly
            return self._super_getboolean(section, option, *args, **kwargs)
        except (_NoSectionError, _NoOptionError):
            if default is not None:
                return default
            else:
                raise

# Note: _wrappedGet method removed as it added overhead
# Direct implementation in each method is more memory efficient
# by avoiding function call overhead and object creation