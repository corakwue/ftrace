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

TRACEPOINT = 'kgsl_pwrlevel'


__all__ = [TRACEPOINT]

#kgsl_pwrlevel: d_name=kgsl-3d0 pwrlevel=1 freq=200000000

KgslPwrlevelBase = namedtuple(TRACEPOINT,
    [
    'd_name',
    'pwrlevel',
    'freq'
    ]
)

class KgslPwrlevel(KgslPwrlevelBase):
    __slots__ = ()
    def __new__(cls, d_name, pwrlevel, freq):
        pwrlevel=int(pwrlevel)
        freq=int(freq)

        return super(cls, KgslPwrlevel).__new__(
            cls,
            d_name=d_name,
            pwrlevel=pwrlevel,
            freq=freq,
        )

kgsl_pwrlevel_pattern = re.compile(
        r"""
        d_name=(?P<d_name>.+)\s+
        pwrlevel=(?P<pwrlevel>\d+)\s+
        freq=(?P<freq>\d+)
        """,
        re.X|re.M
)

@register_parser
def kgsl_pwrlevel(payload):
    """Parser for `kgsl_pwrlevel` tracepoint"""
    try:
        match = re.match(kgsl_pwrlevel_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return KgslPwrlevel(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
