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
from ftrace.ftrace import register_api, FTraceComponent
from ftrace.utils.decorators import requires
from ftrace.common import ConstantBase

log = Logger('Clock')

# Track clock frequency
FreqInterval = namedtuple('FreqInterval', ['clock', 'frequency', 'interval'])
ClkInterval = namedtuple('ClkInterval', ['clock', 'state', 'interval'])

class ClockState(ConstantBase):
    ENABLED = ()
    DISABLED = ()
    
@register_api('clock')
class Clock(FTraceComponent):
    """
    Class with APIs to process all Clock related events such as:
        - frequency residencies for any clock

    For CPU, see `trace.cpu.frequency_intervals`
    """
    def __init__(self, trace):
        self._trace = trace
        self._events = trace.events

    def _initialize(self):
        self._parse_clock_events()
        self._parse_clock_enable_disable_events()

    @property
    @requires('clock_set_rate')
    def names(self):
        return set(self._freq_events_by_clock.keys())

    @requires('clock_set_rate')
    def frequency_intervals(self, clock, interval=None):
        """Returns frequency intervals for specified `clock`.
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


    @requires('clock_disable', 'clock_enable')
    def clock_intervals(self, clock, state=None, interval=None):
        """Returns clock (enabled/disabled) intervals for specified `clock`.
        For list of clocks, dump `names`
        """
        try:
            clk_intervals = \
                self._clk_intervals_by_clock[clock].slice(interval=interval)
        except AttributeError:
            clk_intervals = \
                self._clk_events_handler()[clock].slice(interval=interval)
        except KeyError:
            log.warn('No such clock: {clock} in {clocks}'.format(
                    clock=clock, clocks=self.names))
            return IntervalList()
            
        # Hack in case clock was always ON:
        if not clk_intervals and self.frequency_intervals(clock=clock, interval=interval):
            clk_intervals = IntervalList([ClkInterval(clock, ClockState.ENABLED, self._trace.interval)])
                
        filter_func = lambda ci: ci.state is state if state else None
        return IntervalList(filter(filter_func, clk_intervals)).slice(interval=interval)


    def _clk_events_handler(self):
        """Handler function for clock enable/disable events"""
        self._clk_intervals_by_clock = defaultdict(IntervalList)
        for clock, events in self._clk_events_by_clock.iteritems():
            last_timestamp = self._trace.interval.start
            for clk_event in events:
                # Yes, keep inverted as we track when change occurs
                state = ClockState.DISABLED if  \
                    clk_event.data.state \
                    else ClockState.ENABLED
                interval = Interval(last_timestamp, clk_event.timestamp)
                clk_interval = ClkInterval(clock, state, interval)
                self._clk_intervals_by_clock[clock].append(clk_interval)
                last_timestamp = clk_event.timestamp
            # again, we need some closure.
            if events:
                # not a change, so leave as is.
                state = ClockState.ENABLED if  \
                    clk_event.data.state \
                    else ClockState.DISABLED
                end_interval = ClkInterval(
                    clock=clock,
                    state=state,
                    interval=Interval(clk_event.timestamp,
                        self._trace.duration
                    )
                )
            self._clk_intervals_by_clock[clock].append(end_interval)

        return self._clk_intervals_by_clock
        
    def _freq_events_handler(self):
        """Handler function for clock frequency events"""
        self._freq_intervals_by_clock = defaultdict(IntervalList)
        for clock, events in self._freq_events_by_clock.iteritems():
            last_rate, last_timestamp = -1.0, self._trace.interval.start
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


    def _parse_clock_enable_disable_events(self):
        """Parse clock frequency intervals"""
        self._clk_events_by_clock = defaultdict(EventList)
        self._clock_enable_disable_tracepoints = set(['clock_disable', 'clock_enable'])
        def clock_enable_disable_events_gen():
            filter_func = lambda event: event.tracepoint in self._clock_enable_disable_tracepoints
            for event in filter(filter_func, self._events):
                    yield event

        for event in clock_enable_disable_events_gen():
            self._clk_events_by_clock[event.data.clk].append(event)

    def _parse_clock_events(self):
        """Parse clock frequency intervals"""
        self._freq_events_by_clock = defaultdict(EventList)

        def clock_events_gen():
            filter_func = lambda event: event.tracepoint == 'clock_set_rate'
            for event in filter(filter_func, self._events):
                    yield event

        for event in clock_events_gen():
            self._freq_events_by_clock[event.data.clk].append(event)