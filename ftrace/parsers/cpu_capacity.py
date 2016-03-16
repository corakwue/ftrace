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
try:
    from ftrace.third_party.cnamedtuple import namedtuple
except ImportError:
    from collections import namedtuple

TRACEPOINT = 'cpu_capacity'


__all__ = [TRACEPOINT]


CpuCapacityBase = namedtuple(TRACEPOINT,
    [
    'capacity', # CPU frequency
    'cpu_id', # Target cpu
    ]
)

class CpuCapacity(CpuCapacityBase):
    __slots__ = ()
    def __new__(cls, capacity, cpu_id):
            capacity = int(capacity)
            cpu_id = int(cpu_id)

            return super(cls, CpuCapacity).__new__(
                cls,
                capacity=capacity,
                cpu_id=cpu_id,
            )

cpu_capacity_pattern = re.compile(
        r"""
        capacity=(?P<capacity>\d+)\s+
        cpu_id=(?P<cpu_id>\d+)
        """,
        re.X|re.M
)

@register_parser
def cpu_capacity(payload):
    """Parser for `cpu_capacity` tracepoint"""
    try:
        match = re.match(cpu_capacity_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return CpuCapacity(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
