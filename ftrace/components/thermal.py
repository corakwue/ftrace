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

log = Logger('Thermal')

# Track thermal
ThermalInterval = namedtuple('ThermalInterval', ['tsens', 'temp', 'interval', 'mitigated'])

@register_api('thermal')
class Thermal(FTraceComponent):
    """
    Class with APIs to process all Thermal related events such as:
        - temperature for any tsens with `threshold` indicating
          interval threshold hit/clear
    """
    def __init__(self, trace):
        self._trace = trace
        self._events = trace.events

    def _initialize(self):
        self._parse_thermal_events()

    @property
    @requires('tsens_read', 'tsens_threshold_hit', 'tsens_threshold_clear')
    def names(self):
        return set(self._thermal_events_by_tsens.keys())

    @requires('tsens_read', 'tsens_threshold_hit', 'tsens_threshold_clear')
    def temp_intervals(self, tsens, interval=None):
        """Returns temp intervals for specified `tsens`.
        For list of tsens, dump `names`

        IMPORTANT: Since this uses `tsens_read` we do not know what
        temp is prior to starting trace (only change events).
        For such interval, we always set clock rate to -1.
        """
        try:
            return self._thermal_intervals_by_tsens[tsens].slice(interval=interval)
        except AttributeError:
            return self._thermal_events_handler()[tsens].slice(interval=interval)

    def _thermal_events_handler(self):
        """Handler function for thermal events"""
        self._thermal_intervals_by_tsens = defaultdict(IntervalList)
        for tsens, events in self._thermal_events_by_tsens.iteritems():
            last_temp, last_timestamp, last_threshold = -1.0, 0.0, False
            current_threshold = False
            for thermal_event in events:
                current_temp, tracepoint = thermal_event.data.temp, \
                    thermal_event.tracepoint
                if tracepoint == 'tsens_threshold_hit':
                    current_threshold = True
                elif tracepoint == 'tsens_threshold_clear':
                    current_threshold = False
                # update when temperature or threshold state changes.
                if current_temp != last_temp or \
                    current_threshold != last_threshold:
                    interval = Interval(last_timestamp, thermal_event.timestamp)

                    thermal_interval = ThermalInterval(tsens, last_temp,
                                                       interval, last_threshold)
                    self._thermal_intervals_by_tsens[tsens].append(thermal_interval)
                last_temp = current_temp
                last_timestamp = thermal_event.timestamp
                last_threshold = current_threshold
            # again, we need some closure.
            end_interval = ThermalInterval(
                tsens=tsens,
                temp=last_temp,
                interval=Interval(last_timestamp,
                    self._trace.duration
                ),
                mitigated=last_threshold,
            )
            self._thermal_intervals_by_tsens[tsens].append(end_interval)

        return self._thermal_intervals_by_tsens

    def _parse_thermal_events(self):
        """Parse thermal intervals"""
        self._thermal_events_by_tsens = defaultdict(EventList)

        def thermal_events_gen():
            filter_func = lambda event: event.tracepoint in ['tsens_read', 'tsens_threshold_hit', 'tsens_threshold_clear']
            for event in filter(filter_func, self._events):
                yield event

        for event in thermal_events_gen():
            self._thermal_events_by_tsens[event.data.sensor].append(event)