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

TRACEPOINT = 'ext4_da_write_begin'


__all__ = [TRACEPOINT]

Ext4DAWriteBeginBase = namedtuple(TRACEPOINT,
    [
    'dev_major', 
    'dev_minor', 
    'ino', 
    'pos',
    'len',
    'flags',
    ]
)

class Ext4DAWriteBegin(Ext4DAWriteBeginBase):
    __slots__ = ()
    def __new__(cls, dev_major, dev_minor, ino, pos, _len, flags):
            dev_major = int(dev_major)
            dev_minor = int(dev_minor)
            ino=int(ino)
            pos=int(pos)
            _len=int(_len)
            return super(cls, Ext4DAWriteBegin).__new__(
                cls,
                dev_major=dev_major,
                dev_minor=dev_minor,
                ino=ino,
                pos=pos,
                len=_len,
                flags=flags,
            )

ext4_da_write_begin_pattern = re.compile(
        r"""
        dev\s+(?P<dev_major>\d+),
        (?P<dev_minor>\d+)\s+
        ino\s+(?P<ino>\d+)\s+
        pos\s+(?P<pos>\d+)\s+
        len\s+(?P<len>\d+)\s+
        flags\s+(?P<flags>.+)
        """,
        re.X|re.M
)

@register_parser
def ext4_da_write_begin(payload):
    """Parser for `ext4_da_write_begin` tracepoint"""
    try:
        match = re.match(ext4_da_write_begin_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return Ext4DAWriteBegin(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
