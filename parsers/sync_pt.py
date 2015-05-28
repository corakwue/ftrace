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

TRACEPOINT = 'sync_pt'


__all__ = [TRACEPOINT]

SyncPTBase = namedtuple(TRACEPOINT,
    [
    'name',
    'value',
    ]
)

class SyncPT(SyncPTBase):
    __slots__ = ()
    def __new__(cls, name, value):
            return super(cls, SyncPT).__new__(
                cls,
                name=name,
                value=value,
            )

sync_pt_pattern = re.compile(
        r"""
        name=(?P<name>.+)\s+
        value=(?P<value>.+)
        """,
        re.X|re.M
)

@register_parser
def sync_pt(payload):
    """Parser for `sync_pt` tracepoint"""
    try:
        match = re.match(sync_pt_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return SyncPT(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
