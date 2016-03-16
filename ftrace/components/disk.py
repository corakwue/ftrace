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
from ftrace.ftrace import register_api, FTraceComponent
from ftrace.composites import sorted_items
from ftrace.utils.decorators import requires, coroutine, memoize
from ftrace.io import DiskCommand

log = Logger('Disk')

BLOCK_TRACEPOINTS = ['block_rq_complete', 'block_rq_insert', 'block_rq_issue']

IOInterval = namedtuple('IOLatency', ['io_type', 'task', 'device', 'sector', 'numSectors', 'interval', 'commands', 'errors'])

@register_api('disk')
class Disk(FTraceComponent):
    """
    Class with APIs to process disk/block trace events

    """
    def __init__(self, trace):
        self._trace = trace
        self._events = trace.events

        self.__event_handlers = {}
        self._io_insert_intervals_by_op = defaultdict(IntervalList)
        self._io_issue_intervals_by_op = defaultdict(IntervalList)

    def _initialize(self):
        self._parse_io_events()

    @property
    @requires('clock_set_rate')
    def ops(self):
        return set(self._io_issue_intervals_by_op.keys())

##    @requires("block_rq_issue", "block_rq_complete")
##    @memoize
##    def io_time(self, op=None, interval=None):
##        """
##        Time for specified `op` over specified interval.
##        # TODO: This isn't entirely correct -- FIX ME!
##        """
##        try:
##            request_intervals = self.io_request_intervals(op=op, interval=interval)
##            return sum(ri.interval.duration for ri in request_intervals)
##        except KeyError:
##            return 0.0
##        except:
##            return -1.

    @requires(*BLOCK_TRACEPOINTS)
    @memoize
    def total_io_requests(self, op=None, interval=None, by='issue'):
        try:
            request_intervals = self.io_request_intervals(op=op, interval=interval)
            return len(request_intervals)
        except KeyError:
            return 0.0
        except:
            return float('nan')

    @requires(*BLOCK_TRACEPOINTS)
    @memoize
    def io_request_intervals(self, op=None, interval=None, by='issue'):
        """Returns event intervals for specified `op`

        If by ='issue' (default):
            returns intervals from block issue ==> complete
        Elif by = 'insert':
            returns intervals from insert to queue ==> complete

        For list of io_types (aka ops) see `trace.disk.ops`
        # TODO: Filter by # of sectors & devices.

        See `DiskIOType` in `ftrace.io` for op.
        """
        if by == 'insert':
            interval_dict = self._io_insert_intervals_by_op
        else:
            interval_dict = self._io_issue_intervals_by_op
        if op is None:
            intervals = \
                IntervalList(sorted_items(interval_dict.values()))
        else:
            intervals = interval_dict[op]

        intervals = intervals.slice(interval=interval)
        return intervals

    @coroutine
    def _block_handler(self):
        """
        """
        last_timestamp = self._trace.interval.start
        last_event = None
        block_issue_events_by_sector = defaultdict(list)
        block_insert_events_by_sector = defaultdict(list)

        try:
            while True:
                event = (yield)
                tracepoint = event.tracepoint
                sector = event.data.sector
                if tracepoint == 'block_rq_issue':
                    block_issue_events_by_sector[sector].append(event)
                elif tracepoint == 'block_rq_insert':
                    block_insert_events_by_sector[sector].append(event)
                elif tracepoint == 'block_rq_complete':
                    # TODO: [CHUK] validate this, currently assuming
                    # each block i/o request per sector is serially queued.
                    # This is true for simple trace I have but maynot always hold.
                    if block_issue_events_by_sector[sector]:
                        last_event = block_issue_events_by_sector[sector].pop()
                        last_timestamp = last_event.timestamp
                        io_type=event.data.rwbs.io_type
                        device = (event.data.dev_major, event.data.dev_minor)
                        interval = Interval(last_timestamp, event.timestamp)
                        block_io = IOInterval(io_type=io_type,
                                             task=last_event.task,
                                             device=device,
                                             sector=sector,
                                             errors=event.data.errors,
                                             numSectors=event.data.nr_sector,
                                             interval=interval,
                                             commands=event.data.rwbs.commands)
                        self._io_issue_intervals_by_op[io_type].append(block_io)

                    if block_insert_events_by_sector[sector]:
                        last_event = block_insert_events_by_sector[sector].pop()
                        last_timestamp = last_event.timestamp
                        io_type=event.data.rwbs.io_type
                        device = (event.data.dev_major, event.data.dev_minor)
                        interval = Interval(last_timestamp, event.timestamp)
                        block_io = IOInterval(io_type=io_type,
                                             task=last_event.task,
                                             device=device,
                                             sector=sector,
                                             errors=event.data.errors,
                                             numSectors=event.data.nr_sector,
                                             interval=interval,
                                             commands=event.data.rwbs.commands)
                        self._io_insert_intervals_by_op[io_type].append(block_io)
                else:
                    log.warn("Missing issue marker {event}".format(event=event))

        except GeneratorExit:
            # close things off
            def closure(dict_to_use, dest_dict):
                for sector, event_list in dict_to_use.iteritems():
                    for event in event_list:
                        last_timestamp = event.timestamp
                        io_type=event.data.rwbs.io_type
                        device = (event.data.dev_major, event.data.dev_minor)
                        interval = Interval(last_timestamp, self._trace.duration)
                        block_io = IOInterval(io_type=io_type,
                                             task=event.task,
                                             device=device,
                                             sector=sector,
                                             errors=event.data.errors,
                                             numSectors=event.data.nr_sector,
                                             interval=interval,
                                             commands=event.data.rwbs.commands)
                        dest_dict[io_type].append(block_io)

            closure(block_issue_events_by_sector, self._io_issue_intervals_by_op)
            closure(block_insert_events_by_sector, self._io_insert_intervals_by_op)

    def _parse_io_events(self):
        """Parse block i/o intervals"""
        block_handler = self._block_handler()

        _IO_HANDLERS = {
            'block_rq_complete' : block_handler,
            'block_rq_issue' : block_handler,
        }

        def io_events_gen():
            filter_func = lambda event: event.tracepoint in BLOCK_TRACEPOINTS
            for event in filter(filter_func, self._events):
                    yield event

        for event in io_events_gen():
            try:
                handler_func = self.__event_handlers[event.tracepoint]
            except KeyError:
                handler_func = \
                    self.__event_handlers[event.tracepoint] = \
                        _IO_HANDLERS[event.tracepoint]
            if isinstance(event.data, str):
                pass
            if DiskCommand.FLUSH not in event.data.rwbs.commands:
                # CHUK: for now, discard FLUSH commands.
                handler_func.send(event)

        # shut down the coroutines (..and we are done!)
        for handler_func in self.__event_handlers.itervalues():
            handler_func.close()