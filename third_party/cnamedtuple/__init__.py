from collections import OrderedDict

from cnamedtuple._namedtuple import namedtuple, _register_asdict

__all__ = [
    'namedtuple'
]

__version__ = '0.1.5'

# Register `OrderedDict` as the constructor to use when calling `_asdict`.
# This step exists because there is currently work being done to move this into
# Python 3.5, and this works to solve a circular dependency between
# 'cnamedtuple/_namedtuple.c' ('Modules/_collectionsmodule.c' in cpyton)
# and 'Lib/collections.py'.
_register_asdict(OrderedDict)

# Clean up the namespace for this module, the only public api should be
# `namedtuple`.
del _register_asdict
del OrderedDict
