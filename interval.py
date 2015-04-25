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
        """Returns relativedelta object"""
        return self.end - self.start


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
    def duration(self):
        """Duration of events in seconds"""
        return sum(interval.duration for interval in self._intervals)

    def __add_interval(self, obj):
        """Add interval to (sorted) intervals list"""
        idx = bisect(self._start_timestamps, obj.interval.start)
        self._start_timestamps.insert(idx, obj.interval.start) # insert items sorted
        self._intervals.insert(idx, obj.interval)
        return idx

    def append(self, obj):
        """Append new event to list"""
        try:
            obj.interval
        except AttributeError:
            raise TypeError("Must have interval attribute")
        super(self.__class__, self).insert(self.__add_interval(obj), obj)

    def slice(self, interval, closed=None, trimmed=True):
        """
        Returns list of objects whose interval fall
        between the specified interval.

        Parameters:
        -----------
        closed : string or None, default None
            Make the interval closed with respect to the given interval to
            the 'left', 'right', or both sides (None)
        trimmed : bool, default True
            Trim interval of returned list of objects to fall within specified
            interval
        """
        if interval is None:
            return self

        left_closed, right_closed = False, False

        if closed is None:
            left_closed = True
            right_closed = True
        elif closed == "left":
            left_closed = True
        elif closed == "right":
            right_closed = True
        else:
            raise ValueError("Closed has to be either 'left', 'right' or None")

        idx_left = bisect_left(self._start_timestamps, interval.start)
        idx_right = bisect(self._start_timestamps, interval.end)

        if interval.start in self._start_timestamps and not left_closed:
            idx_left = idx_left + 1
        if interval.end in self._start_timestamps and not right_closed:
            idx_right = idx_right - 1

        left_adjust = idx_left < len(self)

        rv = self[idx_left:idx_right] if left_adjust else []

#        if trimmed and rv:
#            rv[0].interval.start, rv[-1].interval.end = interval.start, interval.end
#            return rv

        return rv