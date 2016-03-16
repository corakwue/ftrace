#!/usr/bin/python

# Copyright 2015 Huawei Devices USA Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors:
#       Chuk Orakwue <chuk.orakwue@huawei.com>


import sys
import types
import math
import functools
from  .third_party.enum.enum import Enum, unique
from itertools import ifilter
from .utils.decorators import memoize

def is_list_like(arg):
    """Returns True if object is list-like, False otherwise"""
    return (hasattr(arg, '__iter__') and
            not isinstance(arg, str))

@unique
class ConstantBase(Enum):
    """Base class for constants"""

    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.name

    def describe(self):
        return self.name, self.value

    @classmethod
    def universe(cls):
        """Every possible item"""
        return cls.__members__.values()

    @classmethod
    def exclude(cls, items):
        """Everything but item(s) - can be list-like"""
        if is_list_like(items):
            return cls.universe() - items
        universe_list = cls.universe()
        universe_list.remove(items)
        return universe_list

    @classmethod
    @memoize
    def map(cls, name):
        """Return obj from str name"""
        for item in cls.universe():
            if item.name == name:
                return item
        return

def bind_method(cls, name, func):
    """Bind method to class.

    Parameters
    ----------
    cls : object
        Class (object) instance
    name : basestring
        name of method on class instance
    func : function
        function to be bound as method

    Returns
    -------
    None
    """
    # only python 2 has (un)bound method issue
    if not sys.version_info[0] >= 3:
        setattr(cls, name, types.MethodType(func, None, cls))
    else:
        setattr(cls, name, func)


def filter_by_task(iterable, attr, value, how='first'):
    """
    Filter iterable to objects whose `attr` has `value`.

    Parameters
    ----------

    iterable : iterable
        Iterable <list, set> object
    attr : string
        Name of attribute to compare.
    value : object
        Value to filter by.
    how : string
        Which events to return. Valid args: 'any'/'all', 'first', 'last'
    """
    def filter_func(event):
        try:
            return getattr(event.task, attr, None) == value
        except AttributeError:
            return getattr(event.event.task, attr, None) == value
        except:
            return False

    filtered = ifilter(filter_func, iterable)
    rv = None
    try:
        if how in ('any', 'all'):
            rv = iter(filtered)
        elif how == 'first':
            rv = filtered.next()
        elif how == 'last':
            for rv in filtered:
                pass
    except:
        rv = None
    finally:
        return rv

#------------------------------------------------------------------------------
def geomean(iterable):
    return (reduce(lambda x, y: x*y, iterable)) ** (1.0/len(iterable))

## {{{ http://code.activestate.com/recipes/511478/ (r1)
def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

# median is 50th percentile.
median = functools.partial(percentile, percent=0.5)
## end of http://code.activestate.com/recipes/511478/ }}}

#------------------------------------------------------------------------------
def unpack_bitmap(num):
    """
    Unpact bitmap to indicate which cores are set.
    For instance 11d = 1011b = [3,1,0]
    """
    bit_length = num.bit_length()
    return set(idx for idx in range(bit_length) if 2**idx & num)


class FtraceErrorBase(Exception):
    """Base class for exceptions in this module."""
    msg = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.message = str(self)

    def __str__(self):
        msg = self.msg.format(**self.kwargs)
        return msg

    __unicode__ = __str__
    __repr__ = __str__


class FtraceError(FtraceErrorBase):
    """
    Generic error for APIs etc.
    """
    msg = "{msg}"
    
class ParserError(FtraceErrorBase):
    """
    Raised on error with parsing file.
    """

    msg = """Event cannot be parsed. {msg}"""