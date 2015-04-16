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

TRACEPOINT = 'kgsl_buslevel'


__all__ = [TRACEPOINT]

#kgsl_buslevel: d_name=kgsl-3d0 pwrlevel=1 bus=2

KgslBuslevelBase = namedtuple(TRACEPOINT,
    [
    'd_name',
    'pwrlevel',
    'bus'
    ]
)

class KgslBuslevel(KgslBuslevelBase):
    __slots__ = ()
    def __new__(cls, d_name, pwrlevel, bus):
        pwrlevel=int(pwrlevel)
        bus=int(bus)

        return super(cls, KgslBuslevel).__new__(
            cls,
            d_name=d_name,
            pwrlevel=pwrlevel,
            bus=bus,
        )

kgsl_buslevel_pattern = re.compile(
        r"""
        d_name=(?P<d_name>.+)\s+
        pwrlevel=(?P<pwrlevel>\d+)\s+
        bus=(?P<bus>\d+)
        """,
        re.X|re.M
)

@register_parser
def kgsl_buslevel(payload):
    """Parser for `kgsl_buslevel` tracepoint"""
    try:
        match = re.match(kgsl_buslevel_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return KgslBuslevel(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
