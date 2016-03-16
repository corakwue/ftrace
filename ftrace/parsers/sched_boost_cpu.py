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


TRACEPOINT = 'sched_boost_cpu'

__all__ = [TRACEPOINT]

SchedBoostCpuBase = namedtuple(TRACEPOINT,
    [
    'cpu'
    'util',
    'margin'
    ]
)

class SchedBoostCpu(SchedBoostCpuBase):
    __slots__ = ()
    def __new__(cls, cpu, util, margin):
            cpu = int(cpu)
            util = int(util)
            margin = int(margin)

            return super(cls, SchedBoostCpu).__new__(
                cls,
                cpu=cpu,
                util=util,
                margin=margin,
            )

sched_boost_cpu_pattern = re.compile(
        r"""
        cpu=(?P<cpu>\d+)\s+
        util=(?P<util>\d+)\s+
        margin=(?P<margin>\d+)
        """,
        re.X|re.M
)

@register_parser
def sched_boost_cpu(payload):
    """Parser for `sched_boost_cpu` tracepoint"""
    try:
        match = re.match(sched_boost_cpu_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return SchedBoostCpu(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
