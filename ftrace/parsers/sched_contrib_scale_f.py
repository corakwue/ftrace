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


TRACEPOINT = 'sched_contrib_scale_f'

__all__ = [TRACEPOINT]

SchedContribScaleFBase = namedtuple(TRACEPOINT,
    [
    'cpu'
    'freq_scale_factor',
    'cpu_scale_factor'
    ]
)

class SchedContribScaleF(SchedContribScaleFBase):
    __slots__ = ()
    def __new__(cls, cpu, freq_scale_factor, cpu_scale_factor):
            cpu = int(cpu)
            freq_scale_factor = int(freq_scale_factor)
            cpu_scale_factor = int(cpu_scale_factor)

            return super(cls, SchedContribScaleF).__new__(
                cls,
                cpu=cpu,
                freq_scale_factor=freq_scale_factor,
                cpu_scale_factor=cpu_scale_factor,
            )

sched_contrib_scale_f_pattern = re.compile(
        r"""
        cpu=(?P<cpu>\d+)\s+
        freq_scale_factor=(?P<freq_scale_factor>\d+)\s+
        cpu_scale_factor=(?P<cpu_scale_factor>\d+)
        """,
        re.X|re.M
)

@register_parser
def sched_contrib_scale_f(payload):
    """Parser for `sched_contrib_scale_f` tracepoint"""
    try:
        match = re.match(sched_contrib_scale_f_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return SchedContribScaleF(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
