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
from ftrace.composites import sorted_items
from ftrace.utils.decorators import requires, coroutine, memoize
from ftrace.atrace import AtraceTag

log = Logger('Android')

Context = namedtuple('Context', ['pid', 'name', 'interval', 'event'])
Counter = namedtuple('Counter', ['pid', 'name', 'value', 'interval', 'event'])
# For app  launch latency
LaunchLatency = namedtuple('LaunchLatency', ['task', 'interval', 'latency'])


@register_api('android')
class Android(object):
    """
    Class with APIs to process android trace events
    written to the trace buffer. These are events not
    part of ftrace API but useful for monitoring performance of
    various frameworks in android OS. Some events (as of Lollipop) are:

            gfx - Graphics
           input - Input
            view - View System
         webview - WebView
              wm - Window Manager
              am - Activity Manager
            sync - Sync Manager
           audio - Audio
           video - Video
          camera - Camera
             hal - Hardware Modules
             app - Application
             res - Resource Loading
          dalvik - Dalvik VM
              rs - RenderScript
          bionic - Bionic C Library
           power - Power Management

    See `adb shell atrace --list_categories`.

    """
    def __init__(self, trace):
        self._trace = trace
        self._events = trace.events

        self.__event_handlers = {}
        self._tmw_intervals_by_name = defaultdict(IntervalList)

        self._parse_tmw_events()

    @property
    def names(self):
        return set(self._tmw_intervals_by_name.keys())

    @requires('tracing_mark_write')
    @memoize
    def event_intervals(self, name=None, task=None, interval=None):
        """Returns event intervals for specified `name` and `task`
        Name here implies `section` or `counter` name.
        """
        if name is None:
            intervals = \
                IntervalList(sorted_items(self._tmw_intervals_by_name.values()))
        else:
            intervals = self._tmw_intervals_by_name[name]

        intervals = intervals.slice(interval=interval)
        if task:
            intervals = filter(lambda it: it.event.task == task, intervals)

        return intervals

    #---------------------------------------------------------------------------
    """
    Utility script to estimate application launch latency without instrumenting
    each app. This has been well validated and found effective for over 80 top
    apps on Android Lollipop device. Validation was done by visually comparing
    below markers to screen capture of the launched app.

    IMPORTANT: For complex app with `welcome screen` displayed prior to
    user-interactable window e.g. games, this excludes such intervals and
    only captures up to first displayed window.
    Typically GLSurfaces are used post-welcome screen.

    TODO: Chain this to parse multiple app launch events in one trace.
    """

    @memoize
    def _launched_app_events(self, interval=None):
        """
        Upon launch, applications goes through 3 states:
                -  process creation (fork from zygote)
                -  bind application
                -  launch (as defined in App Lifecycle on Android OS i.e. onCreate/onStart etc.)

        We guestimate which app is launched by on bindApplication logged by Android.
        """
        bindApplications = self.event_intervals(name='bindApplicatio')
        return bindApplications.slice(interval=interval)

    @memoize
    def launched_app_event(self, interval=None):
        """
        First `bindApplication` indicates first (actual) app-launch.
        Note that any single app-launch can initiate launch of other
        processes (hence forks of zygotes and consequent `bindApplication`)
        """
        return self._launched_app_events(interval=interval)[0].event

    @memoize
    def _start_launch_time(self):
        """
        Start time estimated as first time we ever saw (i.e. scheduled on CPU)
        the launched task.
        """
        event = self.launched_app_event()
        if event:
            interval = Interval(0, event.timestamp)
            return self._trace.cpu.task_intervals(task=event.task,
                interval=interval)[0].interval.start

    @requires('tracing_mark_write')
    @memoize
    def _end_launch_time(self):
        """
        End time estimated as last `performTraversals`(screen update) that caused
        a  `setTransactionState`.

        setTransactionState() is invoked to inform SurfaceFlinger state of changes
        of the surface; changes can be layer_state_t and Display_state
        (see native/include/private/gui/LayerState.h).

        layer_state_t indicates changes in position/color/depth/size/alpha/crop etc
        Display_state indicates changes in orientation, etc
        """
        event = self.launched_app_event()
        end_time = None
        # after launch
        pl_interval = Interval(event.timestamp, self._trace.duration)
        performTraversals = self.event_intervals(name='performTraversals', task=event.task, interval=pl_interval)
        for pt_event in performTraversals:
            sts_interval = Interval(pt_event.interval.start, self._trace.duration)
            if not self.event_intervals(name='setTransactionState', interval=sts_interval):
                break
            else:
                end_time = pt_event.interval.end
        return end_time


    @requires('tracing_mark_write', 'sched_switch', 'sched_wakeup')
    @memoize
    def app_launch_latency(self):
        """Return launch latency seen in trace"""
        start_time, end_time = \
            self._start_launch_time(), self._end_launch_time()
        if (start_time and end_time) is not None:
            launch_interval = Interval(start_time, end_time)
            return LaunchLatency(task=self.launched_app_event().task,
                                 interval=launch_interval,
                                 latency=launch_interval.duration)
    #---------------------------------------------------------------------------

    @coroutine
    def _context_handler(self):
        """
        """
        last_timestamp = 0.0
        last_value = -1.0
        last_event = None
        context_events = EventList()

        try:
            while True:
                event = (yield)
                tag = event.data.atrace_tag
                if tag is AtraceTag.CONTEXT_BEGIN:
                    context_events.append(event)
                elif tag is AtraceTag.CONTEXT_END and context_events:
                    last_event = context_events.pop()
                    last_timestamp = last_event.timestamp
                    last_pid, last_name = \
                        last_event.data.pid, last_event.data.section_name
                    interval = Interval(last_timestamp, event.timestamp)
                    context = Context(pid=last_pid, name=last_name,
                                      interval=interval, event=last_event)
                    self._tmw_intervals_by_name[last_name].append(context)
                else:
                    log.warn("Missing start marker {event}".format(event=event))

        except GeneratorExit:
            # close things off
            for event in context_events:
                last_timestamp = event.timestamp
                interval = Interval(last_timestamp, self._trace.duration)
                pid, name = event.data.pid, event.data.section_name
                context = Context(pid=pid, name=name, interval=interval, event=event)
                self._tmw_intervals_by_name[name].append(context)


    @coroutine
    def _async_event_handler(self):
        """
        TODO: Track by cookie. This is rarely used!!!
        """
        last_timestamp = 0.0
        last_value = -1.0
        last_event = None
        # Stack them like Jason (JSON) 'PID', then 'cookie'
        counter_events_by_cookie = defaultdict(EventList)
        counter_events_by_pid = defaultdict(lambda : counter_events_by_cookie)

        try:
            while True:
                event = (yield)
                pid, cookie = event.data.pid, event.data.cookie
                tag = event.data.atrace_tag
                event_list = counter_events_by_pid[pid][cookie]
                if tag is AtraceTag.ASYNC_BEGIN:
                    event_list.append(event)
                elif tag is AtraceTag.ASYNC_END and event_list:
                    last_event = event_list.pop()
                    last_timestamp = last_event.timestamp
                    interval = Interval(last_timestamp, event.timestamp)
                    context = Context(pid=pid, name=last_event.data.section_name,
                                  interval=interval, event=last_event)
                    self._tmw_intervals_by_name[context.name].append(context)
                else:
                    log.warn("Missing start marker {event}".format(event=event))

        except GeneratorExit:
            # close things off
            for pid, by_name in counter_events_by_pid.iteritems():
                for cookie, event_list in by_name.iteritems():
                    for event in event_list:
                        last_timestamp = event.timestamp
                        interval = Interval(last_timestamp, self._trace.duration)
                        context = Context(pid=pid, name=event.data.section_name,
                                          interval=interval, event=event)
                        self._tmw_intervals_by_name[context.name].append(context)

    @coroutine
    def _counter_handler(self):
        """
        """
        last_timestamp = 0.0
        last_value = -1.0
        last_event = None
        # Stack them like Jason (JSON) 'PID', then 'Counter name'
        counter_events_by_name = defaultdict(EventList)
        counter_events_by_pid = defaultdict(lambda : counter_events_by_name)
        try:
            while True:
                event = (yield)
                pid = event.data.pid
                counter_name = event.data.counter_name
                event_list = counter_events_by_pid[pid][counter_name]
                if event_list:
                    last_event = event_list.pop()
                    last_timestamp = last_event.timestamp
                    last_value = last_event.data.value
                event_list.append(event)
                interval = Interval(last_timestamp, event.timestamp)
                counter = Counter(pid=pid, name=counter_name, event=last_event,
                              value=last_value, interval=interval)
                self._tmw_intervals_by_name[counter.name].append(counter)

        except GeneratorExit:
            # close things off
            for pid, by_name in counter_events_by_pid.iteritems():
                for counter_name, event_list in by_name.iteritems():
                    for event in event_list:
                        last_timestamp = event.timestamp
                        last_value = event.data.value
                        interval = Interval(last_timestamp, self._trace.duration)
                        counter = Counter(pid=pid, name=counter_name, event=event,
                                          value=last_value, interval=interval)
                        self._tmw_intervals_by_name[counter.name].append(counter)

    def _parse_tmw_events(self):
        """Parse tracing_mark_write intervals"""
        context_handler = self._context_handler()
        async_event_handler = self._async_event_handler()
        counter_handler = self._counter_handler()

        _ATRACE_TAG_HANDLERS = {
            AtraceTag.CONTEXT_BEGIN : context_handler,
            AtraceTag.CONTEXT_END : context_handler,
            AtraceTag.ASYNC_BEGIN : async_event_handler,
            AtraceTag.ASYNC_END : async_event_handler,
            AtraceTag.COUNTER : counter_handler,
        }

        def tmw_events_gen():
            filter_func = lambda event: event.tracepoint == 'tracing_mark_write'
            for event in filter(filter_func, self._events):
                    yield event

        for event in tmw_events_gen():
            try:
                handler_func = self.__event_handlers[event.data.atrace_tag]
            except KeyError:
                handler_func = \
                    self.__event_handlers[event.data.atrace_tag] = \
                        _ATRACE_TAG_HANDLERS[event.data.atrace_tag]
               # handler_func.next() # prime the coroutine
            handler_func.send(event)

        # shut down the coroutines (..and we are done!)
        for handler_func in self.__event_handlers.itervalues():
            handler_func.close()