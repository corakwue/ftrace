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

TRACEPOINT = 'kgsl_gpubusy'


__all__ = [TRACEPOINT]

#kgsl_gpubusy: d_name=kgsl-3d0 busy=0 elapsed=-1258611171

KgslGpuBusyBase = namedtuple(TRACEPOINT,
    [
    'd_name',
    'busy',
    'elapsed',
    ]
)

class KgslGpuBusy(KgslGpuBusyBase):
    __slots__ = ()
    def __new__(cls, d_name, busy, elapsed):
            busy=int(busy)
            elapsed=int(elapsed)

            return super(cls, KgslGpuBusy).__new__(
                cls,
                d_name=d_name,
                busy=busy,
                elapsed=elapsed,
            )

kgsl_gpubusy_pattern = re.compile(
        r"""
        d_name=(?P<d_name>.+)\s+
        busy=(?P<busy>\d+)\s+
        elapsed=(?P<elapsed>.+)
        """,
        re.X|re.M
)

@register_parser
def kgsl_gpubusy(payload):
    """Parser for `kgsl_gpubusy` tracepoint"""
    try:
        match = re.match(kgsl_gpubusy_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return KgslGpuBusy(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
