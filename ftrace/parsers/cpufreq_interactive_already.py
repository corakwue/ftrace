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

TRACEPOINT = 'cpufreq_interactive_already'


__all__ = [TRACEPOINT]

# cpufreq_interactive_already: cpu=2 load=30 cur=384000 actual=768000 targ=384000

CPUFreqInteractiveAlreadyBase = namedtuple(TRACEPOINT,
    [
    'cpu', # CPU
    'load', # Load
    'cur', # Current Target Frequency
    'targ', # New Target Frequency
    'actual', # Actual frequency
    ]
)

class CPUFreqInteractiveAlready(CPUFreqInteractiveAlreadyBase):
    __slots__ = ()
    def __new__(cls, cpu, load, cur, actual, targ):
            cpu = int(cpu)
            load = int(load)
            cur = int(cur)
            actual = int(actual)
            targ = int(targ)

            return super(cls, CPUFreqInteractiveAlready).__new__(
                cls,
                cpu=cpu,
                load=load,
                cur=cur,
                actual=actual,
                targ=targ,
            )

cpufreq_interactive_already_pattern = re.compile(
        r"""
        cpu=(?P<cpu>\d+)\s+
        load=(?P<load>\d+)\s+
        cur=(?P<cur>\d+)\s+
        actual=(?P<actual>\d+)\s+
        targ=(?P<targ>\d+)
        """,
        re.X|re.M
)

@register_parser
def cpufreq_interactive_already(payload):
    """Parser for `cpufreq_interactive_already` tracepoint"""
    try:
        match = re.match(cpufreq_interactive_already_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return CPUFreqInteractiveAlready(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
