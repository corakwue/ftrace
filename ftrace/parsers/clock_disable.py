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

TRACEPOINT = 'clock_disable'


__all__ = [TRACEPOINT]


ClockDisableBase = namedtuple(TRACEPOINT,
    [
    'clk', # Clock name
    'state', # Frequency
    'cpu_id', # Target cpu
    ]
)

class ClockDisable(ClockDisableBase):
    __slots__ = ()
    def __new__(cls, clk, state, cpu_id):
            state = int(state)
            cpu_id = int(cpu_id)

            return super(cls, ClockDisable).__new__(
                cls,
                clk=clk,
                state=state,
                cpu_id=cpu_id,
            )

clock_disable_pattern = re.compile(
        r"""
        (?P<clk>.+)\s+
        state=(?P<state>\d+)\s+
        cpu_id=(?P<cpu_id>\d+)
        """,
        re.X|re.M
)

@register_parser
def clock_disable(payload):
    """Parser for `clock_disable` tracepoint"""
    try:
        match = re.match(clock_disable_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return ClockDisable(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
