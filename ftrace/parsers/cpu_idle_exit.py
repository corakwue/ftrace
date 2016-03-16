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

TRACEPOINT = 'cpu_idle_exit'


__all__ = [TRACEPOINT]


CpuIdleExitBase = namedtuple(TRACEPOINT,
    [
    'idx',
    'success'
    ]
)


class CpuIdleExit(CpuIdleExitBase):
    __slots__ = ()
    def __new__(cls, idx, success):
            idx = int(idx)
            success = int(success)

            return super(cls, CpuIdleExit).__new__(
                cls,
                idx=idx,
                success=success,
            )

cpu_idle_exit_pattern = re.compile(
        r"""idx:(?P<idx>\d+)\s+
        success:(?P<success>\d+)
        """,
        re.X|re.M
)

@register_parser
def cpu_idle_exit(payload):
    """Parser for `cpu_idle_exit` tracepoint"""
    try:
        match = re.match(cpu_idle_exit_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return CpuIdleExit(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
