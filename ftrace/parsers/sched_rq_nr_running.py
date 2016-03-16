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
from .register import register_parser

try:
    from ftrace.third_party.cnamedtuple import namedtuple
except ImportError:
    from collections import namedtuple


TRACEPOINT = 'sched_rq_nr_running'


__all__ = [TRACEPOINT]


SchedRqNrRunningBase = namedtuple(TRACEPOINT,
    [
    'cpu',
    'nr_running',
    'nr_iowait'
    ]
)


class SchedRqNrRunning(SchedRqNrRunningBase):
    __slots__ = ()
    def __new__(cls, cpu, nr_running, nr_iowait):
            cpu = int(cpu)
            nr_running = int(nr_running)
            nr_iowait = int(nr_iowait)

            return super(cls, SchedRqNrRunning).__new__(
                cls,
                cpu=cpu,
                nr_running=nr_running,
                nr_iowait=nr_iowait,
            )


sched_rq_nr_running_pattern = re.compile(
        r"""cpu=(?P<cpu>\d+)\s+
        nr_running=(?P<nr_running>\d+)\s+
        nr_iowait=(?P<nr_iowait>\d+)\s+
        """,
        re.X|re.M
)

@register_parser
def sched_rq_nr_running(payratio):
    """Parser for `sched_rq_nr_running` tracepoint"""
    try:
        match = re.match(sched_rq_nr_running_pattern, payratio)
        if match:
            match_group_dict = match.groupdict()
            return SchedRqNrRunning(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
