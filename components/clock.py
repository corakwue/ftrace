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

try:
    from logbook import Logger
except ImportError:
    import logging
    logging.basicConfig()
    from logging import getLogger as Logger
from collections import defaultdict, namedtuple
from ftrace.interval import Interval, IntervalList
from ftrace.event import EventList
from ftrace.ftrace import register_api
from ftrace.utils.decorators import requires

log = Logger('Clock')

# Track clock frequency
FreqInterval = namedtuple('FreqInterval', ['clock', 'frequency', 'interval'])

@register_api('clock')
class Clock(object):
    """
    Class with APIs to process all Clock related events such as:
        - frequency residencies for any clock

    For CPU, see `trace.cpu.frequency_intervals`
    """
    def __init__(self, trace):
        self._trace = trace
        self._events = trace.events

        self._parse_clock_events()

    @property
    def names(self):
        return set(self._freq_events_by_clock.keys())

    @requires('clock_set_rate')
    def frequency_intervals(self, clock, interval=None):
        """Returns clock intervals for specified `clock`.
        For list of clocks, dump `names`

        IMPORTANT: Since this uses `clock_set_rate` we do not know what
        clock rate is prior to starting trace (only change events).
        For such interval, we always set clock rate to -1.

        Similarly, clock_disable/enable events are not currently accounted for.
        """
        try:
            return self._freq_intervals_by_clock[clock].slice(interval=interval)
        except AttributeError:
            return self._freq_events_handler()[clock].slice(interval=interval)

    def _freq_events_handler(self):
        """Handler function for clock frequency events"""
        self._freq_intervals_by_clock = defaultdict(IntervalList)
        for clock, events in self._freq_events_by_clock.iteritems():
            last_rate, last_timestamp = -1.0, 0.0
            for freq_event in events:
                interval = Interval(last_timestamp, freq_event.timestamp)
                freq_interval = FreqInterval(clock, last_rate, interval)
                self._freq_intervals_by_clock[clock].append(freq_interval)
                last_rate = freq_event.data.state
                last_timestamp = freq_event.timestamp
            # again, we need some closure.
            end_interval = FreqInterval(
                clock=clock,
                    frequency=last_rate,
                    interval=Interval(last_timestamp,
                        self._trace.duration
                    )
            )
            self._freq_intervals_by_clock[clock].append(end_interval)

        return self._freq_intervals_by_clock

    def _parse_clock_events(self):
        """Parse clock frequency intervals"""
        self._freq_events_by_clock = defaultdict(EventList)

        def clock_events_gen():
            filter_func = lambda event: event.tracepoint == 'clock_set_rate'
            for event in filter(filter_func, self._events):
                    yield event

        for event in clock_events_gen():
            self._freq_events_by_clock[event.data.clk].append(event)