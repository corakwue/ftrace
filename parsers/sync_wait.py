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

TRACEPOINT = 'sync_wait'


__all__ = [TRACEPOINT]

SyncWaitBase = namedtuple(TRACEPOINT,
    [
    'name',
    'status',
    'begin',
    ]
)

class SyncWait(SyncWaitBase):
    __slots__ = ()
    def __new__(cls, name, status, begin):
            status = int(status)
            return super(cls, SyncWait).__new__(
                cls,
                state=state,
                name=name,
                begin=begin,
            )

sync_wait_pattern = re.compile(
        r"""
        (?P<begin>\w+)\s+
        name=(?P<name>.+)\s+
        status=(?P<status>\d+)
        """,
        re.X|re.M
)

@register_parser
def sync_wait(payload):
    """Parser for `sync_wait` tracepoint"""
    try:
        match = re.match(sync_wait_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return SyncWait(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
