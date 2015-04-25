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
from  .third_party.enum.enum import Enum, unique
from itertools import ifilter

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
    """
    filter_func = lambda event: getattr(event.task, attr, None) == value
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


class FtraceError(Exception):
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


class ParserError(FtraceError):

    msg = """Event cannot be parsed. {msg}"""