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

import os
import sys
import re
import abc
from six import with_metaclass

try:
    from logbook import Logger
except ImportError:
    import logging
    logging.basicConfig()
    from logging import getLogger as Logger

from .parsers import PARSERS
from .task import Task
from .event import Event, EventList
from .common import (
    ConstantBase,
    is_list_like,
    ParserError,
)

__all__ = ['Ftrace']

log = Logger('Ftrace')

class Filetype(ConstantBase):
    UNKNOWN = ()
    FTRACE = ()
    SYSTRACE = ()

#------------------------------------------------------------------------------
# FTraceComponent

class FTraceComponent(with_metaclass(abc.ABCMeta)):
    """Abstract Base Class for FTrace Components APIs"""

    _initialized = False

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

    def _initialize(self):
        raise NotImplementedError

#------------------------------------------------------------------------------
# FTrace

class Ftrace(object):

    _APIS = {}
    _TRACER_PATTERN = re.compile(r"""#\s+tracer:\s+(?P<tracer>.+)""")
    _BUFFER_PATTERN = re.compile(
        r"""
        #\s+entries-in-buffer/entries-written:\s+
        (?P<entries_in>\d+)/(?P<entries_written>\d+)\s+.+
        """,
        re.X)

    _LINE_PATTERN = re.compile(
        r"""
        (?P<name>.+) # task name
        \D
        (?P<pid>\d+) # pid
        \s+
        \D*(?P<tgid>\d*)\D* # tgid
        \s*
        \[(?P<cpu>\d+)\] # cpu#
        \s+
        (?P<irqs_off>[d|X|\.]) # irqs-off
        (?P<need_resched>[N|n|p|\.]) # need-resched
        (?P<irq_type>[H|h|s|.]) # hardirq/softirq
        (?P<preempt_depth>[0-9|.]) # preempt-depth
        \s+
        (?P<timestamp>\d+\W{1}\d+)
        \W{1}\s+
        (?P<tracepoint>\w+) # tracepoint
        \W{1}\s+
        (?P<data>.+) # payload
        """,
        re.X|re.M
    )

    def __init__(self, filepath, tracepoints=None):
        """
        Parser for ftrace output.

        Params:
        -------
        filepath : str
            Path of file to parse
        tracepoints : str or list-like (optional)
            List of tracepoints to parse - nothing more!
        """
        self.filepath = filepath

        self._initial_tps = tracepoints if (is_list_like(tracepoints) or tracepoints is None) else [tracepoints]
        self.filetype = self._check_filetype()

        self.duration = 0.0
        self._raw_start_timestamp = None
        self.events = None
        self.interval = None
        self.tracepoints = set()
        self.seen_cpus = set()

        # tracer metadata
        self.tracer = None
        self.entries_in = 0
        self.entries_written = 0
        self.filedir, self.filename = os.path.split(self.filepath)

        success = self._parse_file()
        if success:
            self.interval = self.events.interval
            self._initiate_apis()

    def __repr__(self):
        return "Trace(filepath={}, tracer={}, lost_entries={})".format(
            self.filepath, self.tracer, self.num_lost_events
            )

    @property
    def buffer_overflowed(self):
        """
        Returns True/False if buffer overflow occurred .
        """
        return self.entries_in == self.entries_written

    @property
    def num_lost_events(self):
        """
        Returns number of lost events
        """
        return self.entries_written - self.entries_in

    def _parse_file(self):
        """
        Parse input file (lazily), return True if successful, False otherwise.
        """
        try:
            self.events = EventList(self._parse_lines())
            return True
        except Exception, e:
            log.exception(e)
            return False

    def _parse_lines(self):
        """
        Parse systrace lines in file.
        """
        num_events = 0
        log.info("Parsing {filename}.".format(filename=self.filename))
        for line in self._line_gen():
            match = re.match(self._LINE_PATTERN, line)
            if match:
                match_dict = match.groupdict()
                match_dict['raw_timestamp'] = float(match_dict['timestamp'])
                match_dict['timestamp'] = float(match_dict['timestamp'])
                if self._raw_start_timestamp is None:
                    self._raw_start_timestamp = match_dict['raw_timestamp']
                # Normalize timestamp
                match_dict['timestamp'] -= self._raw_start_timestamp
                match_dict['task'] = Task(**match_dict)

                parsed_data = self._parse_data(
                    match_dict['tracepoint'],
                    match_dict['data'],
                )
                match_dict['data']= parsed_data
                event = Event(**match_dict)
                # Special treatment, adjust timestamp
                if event.tracepoint in ('bus_update_request'):
                    event = event._replace(data=event.data._replace(timestamp=event.data.timestamp - self._raw_start_timestamp))
                    event = event._replace(timestamp=event.data.timestamp)
                # add to seen cpus
                self.seen_cpus.add(event.cpu)
                if self._initial_tps is None or event.tracepoint in self._initial_tps:
                    self.tracepoints.add(event.tracepoint)
                    yield event
                    num_events +=1
                if num_events % 10000 == 0: # Every 10000 lines, dump
                    sys.stdout.write('.')
                    
        # Properly calculate duration (even if _initial_tps is used)
        self.duration = event.timestamp

    def _line_gen(self):
        """
        Generator that yields ftrace lines in file.
        """
        yield_trace = False
        with open(self.filepath, 'rU') as f:
            num_lines = os.fstat(f.fileno()).st_size
            while True:
                line = f.readline().strip()
                if self.filetype is Filetype.SYSTRACE:
                    line = line.rstrip() # line[:-3]
                if self.tracer is None and 'tracer:' in line:
                    self.tracer = self._check_tracer(line)
                if not (self.entries_in or self.entries_written) and \
                    'entries-in-buffer' in line:
                    self.entries_in, self.entries_written = \
                        self._check_buffer_entries(line)
                if not yield_trace and 'TASK-PID' in line:
                    yield_trace = True
                    _ = f.readline()
                    continue
                if yield_trace:
                    yield line
                if not line and f.tell() == num_lines:
                    break

    def _parse_data(self, tracepoint, data):
        """
        Parse payload(data) for tracepoint - if we have it.
        """
        rv = data
        try:
            rv = PARSERS[tracepoint](data)
        except Exception, e:
            rv = PARSERS[tracepoint](data)
        except ParserError, e:
            log.exception(e)
            log.warn('Error parsing {tp} with {data}'.format(tp=tracepoint, data=data))
        finally:
            return rv if rv else data

    def _check_tracer(self, line):
        """
        Return tracer (typically 'nop')
        """
        match = re.match(self._TRACER_PATTERN, line.strip())
        if match:
            return match.groupdict()['tracer']
        return None

    def _check_buffer_entries(self, line):
        """
        Return tuple of (entries-in-buffer, entries-written)
        """
        match = re.match(self._BUFFER_PATTERN, line)
        if match:
            mgd = match.groupdict()
            return int(mgd['entries_in']), int(mgd['entries_written'])
        return 0, 0

    def _check_filetype(self):
        """
        Return file type.
        """
        if self.filepath.endswith('.html'):
            return Filetype.SYSTRACE
        elif self.filepath.endswith('.txt'):
            return Filetype.FTRACE
        return Filetype.UNKNOWN

    def _initiate_apis(self):
        """Start initialized all registered apis after parsing events in file"""
        for name, cls in self._APIS.iteritems():
            setattr(self, name, cls(self))

def register_api(name):
    """Decorator for registering api methods"""
    def wrapped(cls):
        Ftrace._APIS[name] = cls
        log.info("Registering {name} api to trace".format(name=name))
        return cls
    return wrapped
