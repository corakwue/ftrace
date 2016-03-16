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
from ftrace.common import ConstantBase
from ftrace.utils.decorators import requires, memoize

log = Logger('Bus')

BusRequestInterval = namedtuple('BusRequestInterval',
[
    'device',
    'master_slave', # tuple of (src, dst)
    'state', 
    'average_bw_GBps', 
    'instantaneous_bw_GBps', 
    'interval'
])

AggBusRequestInterval = namedtuple('BusRequestInterval', ['votes', 'interval', 'max_voter'])

class BusState(ConstantBase):
    BUSY = ()
    IDLE = ()
    UNKNOWN = ()

@register_api('bus')
class Bus(FTraceComponent):
    """
    Class with APIs to process all Bus related events.

    IMPORTANT: Currently only supports Qualcomm MSM-devices.
    """
    def __init__(self, trace):
        self._trace = trace
        self._events = trace.events

    def _initialize(self):
        """
        """
        self._parse_bus_update_requests()

    @property
    @requires('bus_update_request')
    def names(self):
        """Returns set of device names"""
        return set(self._bur_events_by_dev.keys())

    @requires('bus_update_request')
    @memoize
    def bus_request_intervals(self, device=None, state=None, interval=None):
        """Return device interval for specified cpu & interval
        """
        try:
            self._bur_intervals_by_dev
        except AttributeError:
            _ = self._bur_events_handler()

        if device is not None:
            try:
                intervals = self._bur_intervals_by_dev[device].slice(interval=interval)
            except KeyError:
                log.warn('No such device: {device} in {devices}'.format(
                    device=device, devices=self.names))
                interval = IntervalList()
        else:
            intervals = IntervalList(sorted_items(self._bur_intervals_by_dev.values())).slice(interval=interval)

        filter_func = (lambda bi: bi.state is state) if state else None
        return IntervalList(filter(filter_func, intervals))
        
        
    @requires('bus_update_request', 'clock_set_rate')
    @memoize
    def bimc_aggregate_requests(self, interval=None):
        """
        Returns alll votes between BIMC clock changes.
        """
        rv = IntervalList()
        votes = {}
        max_voter, max_vote = '', 0
        for bimc_interval in \
            self._trace.clock.frequency_intervals(clock='bimc_clk', 
                                                  interval=interval):
            for bus_requests in self.bus_request_intervals(interval=bimc_interval.interval):
                ib_vote = bus_requests.instantaneous_bw_GBps  
                device = bus_requests.device +  ' ' + repr(bus_requests.master_slave)
                votes[device] = ib_vote
                if ib_vote > max_vote:
                    max_voter = device
                    max_vote = ib_vote
            rv.append(AggBusRequestInterval(votes=votes, max_voter=max_voter,
                                            interval=bimc_interval.interval))
            
        return rv
        
    def _bur_events_handler(self):
        """Handler function for bus update request events"""
        self._bur_intervals_by_dev = defaultdict(IntervalList)
        for device, events in self._bur_events_by_dev.iteritems():
            last_event = None
            for bur_event in events:
                try:
                    interval = \
                        Interval(last_event.timestamp if last_event else self._trace.interval.start, bur_event.timestamp)
                except ValueError, e:
                    raise e
                state = \
                    BusState.BUSY if (bur_event.data.active or \
                        bur_event.data.ib != 0) else BusState.IDLE
                bur_interval = BusRequestInterval(device=device,
                                             state=state,
                                             master_slave=(bur_event.data.src, bur_event.data.dest),
                                             average_bw_GBps=(bur_event.data.ab/1e9),
                                             instantaneous_bw_GBps=(bur_event.data.ib/1e9),
                                             interval=interval,
                                            )
                self._bur_intervals_by_dev[device].append(bur_interval)
                last_event = bur_event

            # again, we need some closure.
            if last_event:
                state=BusState.BUSY if last_event.data.active else BusState.IDLE
                self._bur_intervals_by_dev[device].append(BusRequestInterval(
                                                    device=device,
                                                    state=state,
                                                    master_slave=(last_event.data.src, last_event.data.dest),
                                                    average_bw_GBps=(last_event.data.ib/1e9),
                                                    instantaneous_bw_GBps=(last_event.data.ib/1e9),
                                                    interval=Interval(
                                                        last_event.timestamp,
                                                        self._trace.duration
                                                    )
                                                )
                                            )

        return self._bur_intervals_by_dev

    def _parse_bus_update_requests(self):
        """Parse MSM bus update requests intervals"""
        self._bur_events_by_dev = defaultdict(EventList)

        def bur_events_gen():
            filter_func = lambda event: event.tracepoint =='bus_update_request'
            for event in filter(filter_func, self._events):
                    yield event

        for event in bur_events_gen():
            self._bur_events_by_dev[event.data.name].append(event)