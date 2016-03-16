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
from collections import namedtuple
#from ftrace.third_party.cnamedtuple import namedtuple

TRACEPOINT = 'cpu_idle'


__all__ = [TRACEPOINT]

# cpu_idle: state=1190400 cpu_id=0

CpuIdleBase = namedtuple(TRACEPOINT,
    [
    'state', # CPU idle state
    'cpu_id', # Target cpu
    ]
)

class CpuIdle(CpuIdleBase):
    __slots__ = ()
    def __new__(cls, state, cpu_id):
            state = int(state)
            cpu_id = int(cpu_id)

            return super(cls, CpuIdle).__new__(
                cls,
                state=state,
                cpu_id=cpu_id,
            )

cpu_idle_pattern = re.compile(
        r"""
        state=(?P<state>\d+)\s+
        cpu_id=(?P<cpu_id>\d+)
        """,
        re.X|re.M
)

@register_parser
def cpu_idle(payload):
    """Parser for `cpu_idle` tracepoint"""
    try:
        match = re.match(cpu_idle_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return CpuIdle(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
