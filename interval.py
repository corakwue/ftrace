#!/usr/bin/python

# Copyright 2015 Huawei Devices Inc. All rights reserved.
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

""" Interval:  Represents an interval of time defined by two timestamps.
    IntervalList: List with objects with interval, sorted/sliceable by interval.
"""
from bisect import bisect_left, bisect
from copy import deepcopy

class Interval(object):
    """
    Represents an interval of time defined by two timestamps.

    Parameters:
    -----------

    start: float.
        Starting value.
    end : float
        Ending value. Default is today in UTC, if None
    """

    __slots__ = ("start", "end")

    def __init__(self, start, end):
        if end < start:
            raise ValueError("End date cannot be less than start date")
        self.start, self.end = float(start), float(end)

    def __repr__(self):
        return "Interval(start={:.3f}ms, end={:.3f}ms, duration={:.3f}ms)".format(
            self.start * 1000, self.end * 1000, self.duration * 1000)

    @property
    def duration(self):
        """Returns float"""
        return self.end - self.start
        
    def within(self, timestamp):
        """Returns true if timestamp falls within interval"""
        return True if (timestamp >= self.start) and \
            (timestamp <= self.end) else False


class IntervalList(list):
    """
    List with objects with intervals, sorted and sliceable by interval.
    """
    def __init__(self, iterable=None):
        self._intervals = []
        self._start_timestamps = []
        if iterable:
            for item in iterable:
                self.append(item)

    def __repr__(self):
        return '\n'.join([item.__repr__() for item in self])


    @property
    def _start_times(self):
        return (interval.start for interval in self._intervals)
    
    @property
    def _end_times(self):
        return (interval.end for interval in self._intervals)
        
    @property
    def duration(self):
        """Duration of events in seconds"""
        return max(self._end_times) - min(self._start_times)

    def __add_interval(self, obj):
        """Add interval to (sorted) intervals list"""
        idx = bisect(self._start_timestamps, obj.interval.start)
        self._start_timestamps.insert(idx, obj.interval.start)
        self._intervals.insert(idx, obj.interval)
        return idx

    def append(self, obj):
        """Append new event to list"""
        try:
            obj.interval
        except AttributeError:
            raise TypeError("Must have interval attribute")
        super(self.__class__, self).insert(self.__add_interval(obj), obj)

    def slice(self, interval, trimmed=True):
        """
        Returns list of objects whose interval fall
        between the specified interval.

        Parameters:
        -----------
        trimmed : bool, default True
            Trim interval of returned list of objects to fall within specified
            interval
        """
        if interval is None:
            return self
        
        try:
            idx_left = min(idx for idx, _int in enumerate(self._intervals) 
                if _int.within(interval.start))
        except ValueError:
            idx_left = bisect_left(self._start_timestamps, interval.start)

        try:
            idx_right = max(idx for idx, _int in enumerate(self._intervals) 
                if _int.within(interval.end)) + 1
        except ValueError:
            idx_right = bisect(self._start_timestamps , interval.end)
        
        rv = deepcopy(self[idx_left:idx_right]) if (idx_left or idx_right) else IntervalList()
        
        if trimmed and rv:
            for item in rv:
                if item.interval.start < interval.start:
                    item.interval.start = interval.start
                if item.interval.end > interval.end:
                    item.interval.end = interval.end
        return rv