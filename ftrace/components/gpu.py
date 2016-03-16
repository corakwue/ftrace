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
    from logging import Logger
from collections import defaultdict, namedtuple
from ftrace.interval import Interval, IntervalList
from ftrace.event import EventList
from ftrace.ftrace import register_api, FTraceComponent
from ftrace.composites import sorted_items
from ftrace.common import ConstantBase, is_list_like
from ftrace.utils.decorators import requires, memoize

log = Logger('CPU')

# Used to track interval when task is in/out of run-queue & its state.
#TaskInterval = namedtuple('TaskInterval', ['task', 'device', 'interval', 'state'])
# Used to track intervals when N cpus are concurrently active
BusyInterval = namedtuple('BusyInterval', ['device', 'utilization', 'interval', 'power_constraint'])
# Track CPU frequency
FreqInterval = namedtuple('FreqInterval', ['device', 'frequency', 'pwrlevel', 'interval'])
# Track Idle state
IdleInterval = namedtuple('IdleInterval', ['device', 'state', 'interval'])
# Bus level Interval
BusLevelInterval = namedtuple('BusLevelInterval', ['device', 'pwrlevel', 'bus', 'interval'])

class BusyState(ConstantBase):
    ACTIVE = ()
    AWARE = ()
    NAP = ()
    SLUMBER = ()
    UNKNOWN = ()

    @classmethod
    def BUSY(cls):
        return [cls.ACTIVE, cls.AWARE]

    @classmethod
    def IDLE(cls):
        return [cls.NAP, cls.SLUMBER]

class PowerConstraintType(ConstantBase):
    PWRLEVEL = ()
    NONE = ()
    UNKNOWN = ()

class PowerConstraintSubType(ConstantBase):
    MIN = ()
    MAX = ()
    UNKNOWN = ()

class PowerStatus(ConstantBase):
    ON = ()
    OFF = ()
    UNKNOWN = ()

class ContextFlag(ConstantBase):
    NO_GMEM_ALLOC = ()
    PREAMBLE = ()
    TRASH_STATE = ()
    PER_CONTEXT_TS = ()
    UNKNOWN = ()

# Map src/dst
BUS_DCVS_SRC_DEST = {
    (89, 604) : 'OCMEM',
    (26, 512) : 'GFX3D',
    }

@register_api('gpu')
class GPU(FTraceComponent):
    """
    Utilities to dump:
        - GPU clock frequency and GPU Bus Frequency Intervals
        - GPU Power States (i.e. INIT (AWARE), BUSY, NAP, SLUMBER) per device.

    """
    def __init__(self, trace):
        self._trace = trace
        self._events = trace.events

    def _initialize(self):
        """
        """
        self._parse_freq_events()
        self._parse_bus_events()
        self._parse_pwr_state_events()

    @requires('kgsl_pwr_set_state')
    @memoize
    def idle_time(self, device=None, interval=None):
        """Return Idle time for specified device [including in LPM & INIT/AWARE state]"""
        duration = interval.duration if interval else self._trace.duration 
        return duration - self.busy_time(device=device, interval=interval)

    @requires('kgsl_pwr_set_state')
    @memoize
    def lpm_time(self, device=None, state=None, interval=None):
        """Return time for specified cpu when in LPM.
        This is an approximation as we can exit LPM if GPU was in LPM
        for long time after tracing began.
        """
        try:
            lpm_intervals = self.idle_intervals(device=device, state=state, interval=interval)
            return sum(ti.interval.duration for ti in lpm_intervals)
        except KeyError:
            return 0.0
        except:
            # could be busy or idle entire time.
            return float('nan')

    @requires('kgsl_pwr_set_state')
    @memoize
    def busy_time(self, device=None, interval=None):
        """
        Return Busy (ACTIVE) time for specified gpu device.
        """
        try:
            busy_intervals = self.busy_intervals(device=device, state=BusyState.ACTIVE, interval=interval)
            return sum(ti.interval.duration for ti in busy_intervals)
        except KeyError:
            return 0.0
        except:
            # could be busy or idle entire time.
            return float('nan')
            
    @requires('kgsl_pwr_set_state')
    @memoize
    def idle_intervals(self, device=None, state=None, interval=None):
        """
        Returns busy (pwr state) intervals for specified state (if any)
        on device (if any) over the specified interval (if any).
        """
        return self.pwrstate_intervals(device=device,
            state=state or BusyState.IDLE(), interval=interval)

    @requires('kgsl_pwr_set_state')
    @memoize
    def busy_intervals(self, device=None, state=None, interval=None):
        """
        Returns pwr state intervals for specified state (if any)
        on device (if any) over the specified interval (if any).
        """
        return self.pwrstate_intervals(device=device,
            state=state or BusyState.BUSY(), interval=interval)

    @requires('kgsl_pwr_set_state')
    @memoize
    def pwrstate_intervals(self, device=None, state=None, interval=None):
        """
        Returns pwr state intervals for specified state (if any)
        on device (if any) over the specified interval (if any).
        """
        try:
            self._pwrstate_intervals_by_device.keys()
        except AttributeError:
            self._pwrstate_events_handler()

        try:
            if device is not None:
                intervals = self._pwrstate_intervals_by_device[device]
            else:
                intervals = IntervalList(
                                sorted_items(
                                    self._pwrstate_intervals_by_device.values()))
            if is_list_like(state):
                filter_func = (lambda ti: ti.state in state) if state else None
            else:
                filter_func = (lambda ti: ti.state == state) if state else None
            return IntervalList(filter(filter_func,
                                       intervals.slice(interval=interval)))
        except:
            return IntervalList()

    @requires('kgsl_buslevel')
    @memoize
    def buslevel_intervals(self, device=None, interval=None):
        """
        """
        try:
            self._buslevel_intervals_by_device.keys()
        except AttributeError:
            self._buslevel_events_handler()

        try:
            if device is not None:
                intervals = self._buslevel_intervals_by_device[device]
            else:
                intervals = IntervalList(
                                sorted_items(
                                    self._buslevel_intervals_by_device.values()))

            return intervals.slice(interval=interval)
        except:
            return IntervalList()

    @requires('kgsl_pwrlevel')
    @memoize
    def frequency_intervals(self, device=None, interval=None):
        """Returns freq intervals for specified interval on device"""
        try:
            self._pwrlevel_intervals_by_device.keys()
        except AttributeError:
            self._pwrlevel_events_handler()

        try:
            if device is not None:
                intervals = self._pwrlevel_intervals_by_device[device]
            else:
                intervals = IntervalList(
                                sorted_items(
                                    self._pwrlevel_intervals_by_device.values()))

            return intervals.slice(interval=interval)
        except:
            return IntervalList()

    def _pwrlevel_events_handler(self):
        """Handler function for GPU Pwr Level events"""
        self._pwrlevel_intervals_by_device = defaultdict(IntervalList)
        for device, events in self._pwrlevel_events_by_device.iteritems():
            for pwr_a, pwr_b in zip(events, events[1:]):
                interval = Interval(pwr_a.timestamp, pwr_b.timestamp)
                freq_interval = FreqInterval(device=device,
                   frequency=pwr_a.data.freq,
                   pwrlevel=pwr_a.data.pwrlevel,
                   interval=interval,
                   )
                self._pwrlevel_intervals_by_device[device].append(freq_interval)
            # again, we need some closure.
            if events:
                self._pwrlevel_intervals_by_device[device].append(FreqInterval(
                                                        device=device,
                                                        frequency=pwr_b.data.freq,
                                                        pwrlevel=pwr_b.data.pwrlevel,
                                                        interval=Interval(
                                                            pwr_b.timestamp,
                                                            self._trace.duration
                                                        )
                                                    )
                                                )
            return self._pwrlevel_intervals_by_device

    def _pwrstate_events_handler(self):
        """Handler function for GPU Pwr State events"""
        self._pwrstate_intervals_by_device = defaultdict(IntervalList)
        for device, events in self._pwrstate_events_by_device.iteritems():
            for pwr_a, pwr_b in zip(events, events[1:]):
                interval = Interval(pwr_a.timestamp, pwr_b.timestamp)
                state = BusyState.map(pwr_a.data.state) or BusyState.UNKNOWN
                idle_interval = IdleInterval(device=device,
                   state=state,
                   interval=interval,
                   )
                self._pwrstate_intervals_by_device[device].append(idle_interval)
            # again, we need some closure.
            if events:
                state = BusyState.map(pwr_b.data.state) or BusyState.UNKNOWN
                self._pwrstate_intervals_by_device[device].append(IdleInterval(
                                                        device=device,
                                                        state=state,
                                                        interval=Interval(
                                                            pwr_b.timestamp,
                                                            self._trace.duration
                                                        )
                                                    )
                                                )
            return self._pwrstate_intervals_by_device


    def _buslevel_events_handler(self):
        """Handler function for GPU Bus Level events"""
        self._buslevel_intervals_by_device = defaultdict(IntervalList)
        for device, events in self._buslevel_events_by_device.iteritems():
            for bus_a, bus_b in zip(events, events[1:]):
                interval = Interval(bus_a.timestamp, bus_b.timestamp)
                bus_interval = BusLevelInterval(device=device,
                   pwrlevel=bus_a.data.pwrlevel,
                   bus=bus_a.data.bus,
                   interval=interval,
                   )
                self._buslevel_intervals_by_device[device].append(bus_interval)
            # again, we need some closure.
            if events:
                self._buslevel_intervals_by_device[device].append(BusLevelInterval(
                                                        device=device,
                                                        pwrlevel=bus_b.data.pwrlevel,
                                                        bus=bus_b.data.bus,
                                                        interval=Interval(
                                                            bus_b.timestamp,
                                                            self._trace.duration
                                                        )
                                                    )
                                                )
            return self._buslevel_intervals_by_device

    def _parse_bus_events(self):
        """
        Parses GPU bus level events
        """
        self._buslevel_events_by_device = defaultdict(EventList)

        def buslevel_events_gen():
            filter_func = lambda event: event.tracepoint == 'kgsl_buslevel'
            for event in filter(filter_func, self._events):
                    yield event

        for event in buslevel_events_gen():
            self._buslevel_events_by_device[event.data.d_name].append(event)

    def _parse_pwr_state_events(self):
        """
        Parses GPU pwr state events
        """
        self._pwrstate_events_by_device = defaultdict(EventList)

        def pwrstate_events_gen():
            filter_func = lambda event: event.tracepoint in 'kgsl_pwr_set_state'
            for event in filter(filter_func, self._events):
                    yield event

        for event in pwrstate_events_gen():
            self._pwrstate_events_by_device[event.data.d_name].append(event)


    def _parse_freq_events(self):
        """
        Parses GPU pwr level (freq + pwrlevel) events
        """
        self._pwrlevel_events_by_device = defaultdict(EventList)

        def pwrlevel_events_gen():
            filter_func = lambda event: event.tracepoint in 'kgsl_pwrlevel'
            for event in filter(filter_func, self._events):
                    yield event

        for event in pwrlevel_events_gen():
            self._pwrlevel_events_by_device[event.data.d_name].append(event)