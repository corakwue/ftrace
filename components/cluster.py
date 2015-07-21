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

log = Logger('Cluster')

IdleInterval = namedtuple('IdleInterval', ['cluster', 'idx', 'state', 'interval'])

class BusyState(ConstantBase):
    BUSY = ()
    IDLE = ()
    UNKNOWN = ()

@register_api('cluster')
class Cluster(FTraceComponent):
    """
    Class with APIs to process all Cluster related events such as:
        - idle intervals
        - active intervals
        - idle/active time

    IMPORTANT: Currently only supports Qualcomm MSM-devices.
    """
    def __init__(self, trace):
        self._trace = trace
        self._events = trace.events

    def _initialize(self):
        """
        """
        self._parse_cluster_idle_events()

    @property
    @requires('cluster_enter', 'cluster_exit')
    def names(self):
        """Returns set of cluster names"""
        return set(self._cluster_idle_events_by_cluster.keys())

    @requires('cluster_enter', 'cluster_exit')
    @memoize
    def idle_time(self, cluster, interval=None):
        """Return Idle time for specified cluster [including in LPM state]"""
        return self._trace.duration - self.active_time(cluster=cluster, interval=interval)

    @requires('cluster_enter', 'cluster_exit')
    @memoize
    def lpm_time(self, cluster, interval=None):
        """Return time for specified cluster when in LPM.
        This is an approximation as we can exit LPM if cluster was in LPM
        for long time after tracing began.
        """
        try:
            lpm_intervals = self.lpm_intervals(cluster=cluster, interval=interval)
            return sum(ti.interval.duration for ti in lpm_intervals)
        except KeyError:
            return 0.0
        except:
            # could be busy or idle entire time.
            return float('nan')

    @requires('cluster_enter', 'cluster_exit')
    @memoize
    def active_time(self, cluster, interval=None):
        """Return Idle time for specified cluster when its not offline.
        todo: filter by task
        """
        try:
            busy_intervals = self.busy_intervals(cluster=cluster, interval=interval)
            return sum(ti.interval.duration for ti in busy_intervals)
        except KeyError:
            return 0.0
        except:
            # could be busy or idle entire time.
            return float('nan')

    @requires('cluster_enter', 'cluster_exit')
    @memoize
    def busy_intervals(self, cluster=None, interval=None):
        """Return Busy interval for specified cluster & interval
        when cluster is not IDLE (in LPM) state
        """
        try:
            return IntervalList(filter(lambda cii: cii.state!=BusyState.IDLE,
                                       self.cluster_intervals(cluster=cluster,
                                                          interval=interval)))
        except:
            return IntervalList()

    @requires('cluster_enter', 'cluster_exit')
    @memoize
    def lpm_intervals(self, cluster=None, interval=None):
        """Return Idle interval for specified cpu & interval
        when cluster is IDLE (in LPM) state
        """
        try:
            return IntervalList(filter(lambda cii: cii.state==BusyState.IDLE,
                                       self.cluster_intervals(cluster=cluster,
                                                          interval=interval)))
        except:
            return IntervalList()


    @requires('cluster_enter', 'cluster_exit')
    @memoize
    def cluster_intervals(self, cluster, interval=None):
        """Return interval for specified cluster & interval
        """
        try:
            self._cluster_idle_intervals_by_cluster
        except AttributeError:
            _ = self._cluster_idle_events_handler()

        if cluster is not None:
            intervals = self._cluster_idle_intervals_by_cluster[cluster]
        else:
            intervals = IntervalList(sorted_items(self._cluster_idle_intervals_by_cluster.values()))

        return intervals.slice(interval=interval)

    def _cluster_idle_events_handler(self):
        """Handler function for Cluster Idle events"""
        self._cluster_idle_intervals_by_cluster = defaultdict(IntervalList)
        for cluster, events in self._cluster_idle_events_by_cluster.iteritems():
            last_event = None
            for cluster_idle in events:
                tp = cluster_idle.tracepoint
                if tp == 'cluster_exit':
                    interval = Interval(last_event.timestamp if last_event else self._trace.interval.start,
                                        cluster_idle.timestamp)
                    idle_interval = IdleInterval(cluster=cluster,
                                                 state=BusyState.IDLE,
                                                 idx=cluster_idle.data.idx,
                                                 interval=interval,
                                                )
                    self._cluster_idle_intervals_by_cluster[cluster].append(idle_interval)
                elif tp == 'cluster_enter':
                    interval = Interval(last_event.timestamp if last_event else self._trace.interval.start,
                                        cluster_idle.timestamp)
                    idle_interval = IdleInterval(cluster=cluster,
                                                 state=BusyState.BUSY,
                                                 idx=-1,
                                                 interval=interval,
                                                )
                    self._cluster_idle_intervals_by_cluster[cluster].append(idle_interval)

                last_event = cluster_idle

            # again, we need some closure.
            if last_event:
                if last_event.tracepoint == 'cluster_exit':
                    state = BusyState.BUSY
                    idx = -1
                else:
                    state = BusyState.IDLE
                    idx = last_event.data.idx
                self._cluster_idle_intervals_by_cluster[cluster].append(IdleInterval(
                                                    cluster=cluster,
                                                    state=state,
                                                    idx=idx,
                                                    interval=Interval(
                                                        last_event.timestamp,
                                                        self._trace.duration
                                                    )
                                                )
                                            )

        return self._cluster_idle_intervals_by_cluster


    def _parse_cluster_idle_events(self):
        """Parse Cluster idle intervals"""
        self._cluster_idle_events_by_cluster = defaultdict(EventList)

        def cluster_idle_events_gen():
            filter_func = lambda event: event.tracepoint in ('cluster_enter',
                            'cluster_exit')
            for event in filter(filter_func, self._events):
                    yield event

        for event in cluster_idle_events_gen():
            self._cluster_idle_events_by_cluster[event.data.name].append(event)