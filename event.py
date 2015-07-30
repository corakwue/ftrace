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

"""
    Event: Each event written to trace buffer.
    EventList: List with events with timestamps, sorted/sliceable by interval.
"""
from .interval import Interval
from collections import namedtuple
from bisect import bisect_left, bisect

Eventbase = namedtuple("Event",
    [
    'task',
    'cpu', # CPU id which the process was running on.
    'raw_timestamp',
    'timestamp', # Timestamp
    'irqs_off', # IRQs enable/disabled flag, 'd' interrupts are disabled. '.' otherwise.
    'need_resched', # task needs resched flag. 'N' task is set, '.' otherwise.
    'irq_type', # IRQ type (hard or soft)
                # 'H' - hard irq occurred inside a softirq.
                # 'h' - hard irq is running
                # 's' - soft irq is running
                # '.' - normal context.
    'preempt_depth', # preempt depth
    'tracepoint', # Tracepoint
    'data', # payload <can be parsed tuple or string if parser is N/A
    ]
)

class Event(Eventbase):

    __slots__ = ()

    def __new__(cls, task, cpu, timestamp, raw_timestamp, irqs_off, need_resched,
        irq_type, preempt_depth, tracepoint, data, **kwargs):
            cpu = int(cpu)
            raw_timestamp = float(raw_timestamp)
            timestamp = float(timestamp)
            return super(Event, cls).__new__(
                cls, task=task,
                cpu=cpu,
                timestamp=timestamp,
                raw_timestamp=raw_timestamp,
                irqs_off=irqs_off,
                need_resched=need_resched,
                irq_type=irq_type,
                preempt_depth=preempt_depth,
                tracepoint=tracepoint,
                data=data,
            )

    def __repr__(self):
        return "Event(task={}, cpu={}, timestamp={:.4}, data={}".format(
        self.task, self.cpu, self.timestamp, self.data,
        )


class EventList(list):
    """
    List with objects with timestamps, sorted and sliceable by interval.
    """
    def __init__(self, iterable=None):
        self._timestamps = []
        if iterable:
            for item in iterable:
                self.append(item)

    def __repr__(self):
        return '\n'.join([item.__repr__() for item in self])

    @property
    def start(self):
        """First timestamp in list"""
        return self._timestamps[0]

    @property
    def end(self):
        """Last timestamp in list"""
        return self._timestamps[-1]

    @property
    def interval(self):
        """Interval for thie event list"""
        try:
            return Interval(start=self.start, end=self.end)
        except:
            return None

    @property
    def duration(self):
        """Duration of events in seconds"""
        return self.interval.duration if self.interval else None

    def __add_timestamp(self, obj):
        """Insert (sorted) object with timestamp attribute to timestamps list.
        """
        ts = obj.timestamp
        idx = bisect(self._timestamps, ts)
        self._timestamps.insert(idx, ts) # insert items sorted
        return idx

    def append(self, obj):
        """Append new event to list"""
        try:
            obj.timestamp
        except AttributeError:
            raise TypeError("Must have timestamp attribute")
        super(self.__class__, self).insert(self.__add_timestamp(obj), obj)

    def slice(self, interval, closed=None):
        """
        Returns list of objects whose timestamps fall
        between the specified interval.

        Parameters:
        -----------
        closed : string or None, default None
            Make the interval closed with respect to the given interval to
            the 'left', 'right', or both sides (None)

        """
        if interval is None:
            return self
        else:
            start, end = interval.start, interval.end

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

        idx_left = bisect_left(self._timestamps, start)
        idx_right = bisect(self._timestamps, end)

        if start in self._timestamps and not left_closed:
            idx_left = idx_left + 1
        if end in self._timestamps and not right_closed:
            idx_right = idx_right - 1

        left_adjust = idx_left < len(self)

        return EventList(self[idx_left:idx_right]) if left_adjust else EventList()

