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

import re
from ftrace.common import ParserError
from ftrace.globals import SCHED_RAVG_WINDOW
from .register import register_parser
from collections import namedtuple
#from ftrace.third_party.cnamedtuple import namedtuple

TRACEPOINT = 'sched_task_load'


__all__ = [TRACEPOINT]

# sched_task_load: 563 (EventThread): sum=986, sum_scaled=245, period=47165 demand=111446 small=1 boost=0 reason=0 sync=0 prefer_idle=0\n\

SchedTaskLoadBase = namedtuple(TRACEPOINT,
    [
    'pid',
    'comm',
    'sum',
    'sum_scaled',
    'period',
    'demand',
    'small',
    'boost',
    'reason',
    'sync',
    'prefer_idle',
    ]
)


class SchedTaskLoad(SchedTaskLoadBase):
    __slots__ = ()
    def __new__(cls, pid, comm, _sum, sum_scaled,
                period, demand, small, boost, reason,
                sync, prefer_idle):
            pid = int(pid)
            _sum = int(_sum)
            sum_scaled = int(sum_scaled)
            period = int(period)
            demand = int(demand)
            small = int(small)
            boost = int(boost)
            reason = int(reason)

            return super(cls, SchedTaskLoad).__new__(
                cls,
                pid=pid,
                comm=comm,
                sum=_sum,
                sum_scaled=sum_scaled,
                period=period,
                demand=demand,
                small=small,
                boost=boost,
                reason=reason,
                sync=sync,
                prefer_idle=prefer_idle,
            )

    @property
    def wb_load(self):
        """Returns Task Load as seen by Qualcomm's Window Based Task Demand"""
        return self.demand/float(SCHED_RAVG_WINDOW)


sched_task_load_pattern = re.compile(
        r"""(?P<pid>\d+)\s+
        \((?P<comm>.*)\):\s+
        sum=(?P<_sum>\d+),\s+
        sum_scaled=(?P<sum_scaled>\d+),\s+
        period=(?P<period>\d+)\s+
        demand=(?P<demand>\d+)\s+
        small=(?P<small>\d+)\s+
        boost=(?P<boost>\d+)\s+
        reason=(?P<reason>\d+)\s+
        sync=(?P<sync>\d+)\s+
        prefer_idle=(?P<prefer_idle>\d+)
        """,
        re.X|re.M
)

@register_parser
def sched_task_load(payload):
    """Parser for `sched_task_load` tracepoint"""
    try:
        match = re.match(sched_task_load_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return SchedTaskLoad(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
