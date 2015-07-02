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

TRACEPOINT = 'cpu_frequency_switch_end'


__all__ = [TRACEPOINT]

# cpu_frequency_switch_end: cpu_id=0

CpuFrequencySwitchEndBase = namedtuple(TRACEPOINT,
    [
    'cpu_id', # Target cpu
    ]
)

class CpuFrequencySwitchEnd(CpuFrequencySwitchEndBase):
    __slots__ = ()
    def __new__(cls, cpu_id):
            cpu_id = int(cpu_id)

            return super(cls, CpuFrequencySwitchEnd).__new__(
                cls,
                cpu_id=cpu_id,
            )

cpu_frequency_switch_end_pattern = re.compile(
        r"""
        cpu_id=(?P<cpu_id>\d+)
        """,
        re.X|re.M
)

@register_parser
def cpu_frequency_switch_end(payload):
    """Parser for `cpu_frequency_switch_end` tracepoint"""
    try:
        match = re.match(cpu_frequency_switch_end_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return CpuFrequencySwitchEnd(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
