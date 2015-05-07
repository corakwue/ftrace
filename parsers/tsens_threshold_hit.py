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

TRACEPOINT = 'tsens_threshold_hit'


__all__ = [TRACEPOINT]


TsensThresholdHitBase = namedtuple(TRACEPOINT,
    [
    'temp', 
    'sensor'
    ]
)

class TsensThresholdHit(TsensThresholdHitBase):
    __slots__ = ()
    def __new__(cls, temp, sensor):
        temp = int(temp)

        return super(cls, TsensThresholdHit).__new__(
            cls,
            temp=temp,
            sensor=sensor,
        )

tsens_threshold_hit_pattern = re.compile(
        r"""
        temp=(?P<temp>\d+)\s+
        sensor=(?P<sensor>.+)
        """,
        re.X|re.M
)

@register_parser
def tsens_threshold_hit(payload):
    """Parser for `tsens_threshold_hit` tracepoint"""
    try:
        match = re.match(tsens_threshold_hit_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return TsensThresholdHit(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
