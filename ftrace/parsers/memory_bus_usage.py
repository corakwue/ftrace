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
from .register import register_parser
from collections import namedtuple, defaultdict
#from ftrace.third_party.cnamedtuple import namedtuple
from ftrace.common import ConstantBase, ParserError

TRACEPOINT = 'memory_bus_usage'


__all__ = [TRACEPOINT]


MemoryBusUsageBase = namedtuple(TRACEPOINT,
    [
    'bus', # Bus name
    'rw_bytes', # Bytes written/read
    'r_bytes', # Bytes read
    'w_bytes', # Bytes written
    'cycles', # Bus cycles
    'ns', # nanoseconds
    'r_MBps', # Read throughput (MB/s)
    'w_MBps', # Write throughput (MB/s)
    ]
)


class MemoryBusUsage(MemoryBusUsageBase):
    __slots__ = ()
    def __new__(cls, bus, rw_bytes, r_bytes, w_bytes, cycles, ns):
            rw_bytes = int(rw_bytes)
            r_bytes = int(r_bytes)
            w_bytes = int(w_bytes)
            cycles = int(cycles)
            ns = int(ns)

            r_MBps = (1E9 * (r_bytes / ns))/ 1048576.0
            w_MBps = (1E9 * (w_bytes / ns))/ 1048576.0

            return super(cls, MemoryBusUsage).__new__(
                cls,
                bus=bus,
                rw_bytes=rw_bytes,
                r_bytes=r_bytes,
                w_bytes=w_bytes,
                cycles=cycles,
                ns=ns,
                r_MBps=r_MBps,
                w_MBps=w_MBps,
            )

memory_bus_usage_pattern = re.compile(
        r"""bus=(?P<bus>.+)\s+
        rw_bytes=(?P<rw_bytes>\d+)\s+
        r_bytes=(?P<next_ctx_id>\d+)\s+
        w_bytes=(?P<w_bytes>\d+)\s+
        cycles=(?P<cycles>\d+)\s+
        ns=(?P<ns>\d+)
        """,
        re.X|re.M
)

@register_parser
def memory_bus_usage(payload):
    """Parser for `memory_bus_usage` tracepoint"""
    try:
        match = re.match(memory_bus_usage_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return MemoryBusUsage(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
