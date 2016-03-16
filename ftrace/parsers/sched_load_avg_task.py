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
try:
    from ftrace.third_party.cnamedtuple import namedtuple
except ImportError:
    from collections import namedtuple


TRACEPOINT = 'sched_load_avg_task'


__all__ = [TRACEPOINT]


SchedLoadAvgTaskBase = namedtuple(TRACEPOINT,
    [
    'pid',
    'comm',
    'cpu',
    'load_avg',
    'util_avg',
    'load_sum',
    'util_sum',
    'period_contrib',
    ]
)


class SchedLoadAvgTask(SchedLoadAvgTaskBase):
    __slots__ = ()
    def __new__(cls, pid, comm, load_avg,
                util_avg, load_sum, util_sum, period_contrib):
            pid = int(pid)
            load_avg = int(load_avg)
            util_avg = int(util_avg)
            load_sum = int(load_sum)
            util_sum = int(util_sum)
            period_contrib = int(period_contrib)

            return super(cls, SchedLoadAvgTask).__new__(
                cls,
                pid=pid,
                comm=comm,
                load_avg=load_avg,
                util_avg=util_avg,
                load_sum=load_sum,
                util_sum=util_sum,
                period_contrib=period_contrib,
            )

sched_load_avg_task_pattern = re.compile(
        r"""comm=(?P<comm>.*)\s+
        pid=(?P<pid>\d+)\s+
        cpu=(?P<cpu>\d+)\s+
        load_avg=(?P<load_avg>\d+)\s+
        util_avg=(?P<util_avg>\d+)\s+
        load_sum=(?P<load_sum>\d+)\s+
        util_sum=(?P<util_sum>\d+)\s+
        period_contrib=(?P<period_contrib>\d+)\s
        """,
        re.X|re.M
)

@register_parser
def sched_load_avg_task(payload):
    """Parser for `sched_load_avg_task` tracepoint"""
    try:
        match = re.match(sched_load_avg_task_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return SchedLoadAvgTask(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
