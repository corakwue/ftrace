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


TRACEPOINT = 'cpufreq_sched_update_capacity'

__all__ = [TRACEPOINT]

CpufreqSchedUpdateCapacityBase = namedtuple(TRACEPOINT,
    [
    'cpu'
    'request',
    'cfs', # fair tasks
    'rt', # real-time
    'dl',
    'total',
    'new_total',
    ]
)

class CpufreqSchedUpdateCapacity(CpufreqSchedUpdateCapacityBase):
    __slots__ = ()
    def __new__(cls, cpu, request, cfs, rt, dl, total, new_total):
            cpu = int(cpu)
            request = bool(request)
            cfs = int(cfs)
            rt = int(rt)
            dl = int(dl)
            total = int(total)
            new_total = int(new_total)

            return super(cls, CpufreqSchedUpdateCapacity).__new__(
                cls,
                cpu=cpu,
                request=request,
                cfs=cfs,
                rt=rt,
                dl=dl,
                total=total,
                new_total=new_total
            )

cpufreq_sched_update_capacity_pattern = re.compile(
        r"""
        cpu=(?P<cpu>\d+)\s+
        set_cap=(?P<request>\d+)\s+
        cfs=(?P<cfs>\d+)\s+
        rt=(?P<rt>\d+)\s+
        dl=(?P<dl>\d+)\s+
        old_tot=(?P<total>\d+)\s+
        new_tot=(?P<new_total>\d+)
        """,
        re.X|re.M
)

@register_parser
def cpufreq_sched_update_capacity(payload):
    """Parser for `cpufreq_sched_update_capacity` tracepoint"""
    try:
        match = re.match(cpufreq_sched_update_capacity_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return CpufreqSchedUpdateCapacity(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
