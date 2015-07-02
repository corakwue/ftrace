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

TRACEPOINT = 'bus_update_request'


__all__ = [TRACEPOINT]

#bus_update_request: time= 15618.608339249 name=sdhc1 index=6 src=78 dest=512 ab=400000000 ib=800000000

BusUpdateRequestBase = namedtuple(TRACEPOINT,
    [
    'timestamp',
    'name',
    'src',
    'dest',
    'ab', # average bw
    'ib', # instantenous bw
    'active',
    ]
)

class BusUpdateRequest(BusUpdateRequestBase):
    __slots__ = ()
    def __new__(cls, timestamp, name, src, dest, ab, ib, active):
            timestamp = float(timestamp)
            src = int(src)
            dest = int(dest)
            ab = float(ab)
            ib = float(ib)
            active = int(active)

            return super(cls, BusUpdateRequest).__new__(
                cls,
                timestamp=timestamp,
                name=name,
                src=src,
                dest=dest,
                ab=ab,
                ib=ib,
                active=active,
            )

bus_update_request_pattern = re.compile(
        r"""
        time[=|:](?P<timestamp>.+)\s+
        name[=|:](?P<name>.+)\s+
        src[=|:](?P<src>\d+)\s+
        dest[=|:](?P<dest>\d+)\s+
        ab[=|:](?P<ab>\d+)\s+
        ib[=|:](?P<ib>\d+)\s+
        active[=|:](?P<active>\d+)
        """,
        re.X|re.M
)

@register_parser
def bus_update_request(payload):
    """Parser for `bus_update_request` tracepoint"""
    try:
        match = re.match(bus_update_request_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BusUpdateRequest(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
