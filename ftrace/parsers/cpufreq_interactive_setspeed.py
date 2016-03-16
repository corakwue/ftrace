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

TRACEPOINT = 'cpufreq_interactive_setspeed'


__all__ = [TRACEPOINT]

# cpufreq_interactive_setspeed: cpu=0 targ=600000 actual=768000

CPUFreqInteractiveSetSpeedBase = namedtuple(TRACEPOINT,
    [
    'cpu', # CPU
    'targ', # Target Frequency
    'actual', # Actual frequency
    ]
)

class CPUFreqInteractiveSetSpeed(CPUFreqInteractiveSetSpeedBase):
    __slots__ = ()
    def __new__(cls, cpu, targ, actual):
            cpu = int(cpu)
            targ = int(targ)
            actual = int(actual)

            return super(cls, CPUFreqInteractiveSetSpeed).__new__(
                cls,
                cpu=cpu,
                targ=targ,
                actual=actual,
            )

cpufreq_interactive_setspeed_pattern = re.compile(
        r"""
        cpu=(?P<cpu>\d+)\s+
        targ=(?P<targ>\d+)\s+
        actual=(?P<actual>\d+)
        """,
        re.X|re.M
)

@register_parser
def cpufreq_interactive_setspeed(payload):
    """Parser for `cpufreq_interactive_setspeed` tracepoint"""
    try:
        match = re.match(cpufreq_interactive_setspeed_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return CPUFreqInteractiveSetSpeed(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
