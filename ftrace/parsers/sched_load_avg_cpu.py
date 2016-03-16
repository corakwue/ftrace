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


TRACEPOINT = 'sched_load_avg_cpu'

__all__ = [TRACEPOINT]

SchedLoadAvgCpuCpuBase = namedtuple(TRACEPOINT,
    [
    'cpu'
    'load_avg',
    'util_avg'
    ]
)

class SchedLoadAvgCpuCpu(SchedLoadAvgCpuCpuBase):
    __slots__ = ()
    def __new__(cls, cpu, load_avg, util_avg):
            cpu = int(cpu)
            load_avg = int(load_avg)
            util_avg = int(util_avg)

            return super(cls, SchedLoadAvgCpuCpu).__new__(
                cls,
                cpu=cpu,
                load_avg=load_avg,
                util_avg=util_avg,
            )

sched_load_avg_cpu_pattern = re.compile(
        r"""
        cpu=(?P<cpu>\d+)\s+
        load_avg=(?P<load_avg>\d+)\s+
        util_avg=(?P<util_avg>\d+)
        """,
        re.X|re.M
)

@register_parser
def sched_load_avg_cpu(payload):
    """Parser for `sched_load_avg_cpu` tracepoint"""
    try:
        match = re.match(sched_load_avg_cpu_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return SchedLoadAvgCpuCpu(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
