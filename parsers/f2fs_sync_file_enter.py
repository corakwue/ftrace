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

# TODO: Validate this!

TRACEPOINT = 'f2fs_sync_file_enter'


__all__ = [TRACEPOINT]

F2FSSyncFileEnterBase = namedtuple(TRACEPOINT,
    [
    'dev_major', 
    'dev_minor', 
    'ino', 
    'parent',
    'datasync',
    ]
)

class F2FSSyncFileEnter(F2FSSyncFileEnterBase):
    __slots__ = ()
    def __new__(cls, dev_major, dev_minor, ino, parent, datasync):
            dev_major = int(dev_major)
            dev_minor = int(dev_minor)
            ino=int(ino)
            parent=int(parent)
            
            return super(cls, F2FSSyncFileEnter).__new__(
                cls,
                dev_major=dev_major,
                dev_minor=dev_minor,
                ino=ino,
                parent=parent,
                datasync=datasync,
            )

f2fs_sync_file_enter_pattern = re.compile(
        r"""
        dev = \((?P<dev_major>\d+),
        (?P<dev_minor>\d+)\),\s+
        ino = (?P<ino>\d+),\s+
        parent = (?P<parent>\d+),\s+
        datasync = (?P<datasync>\d+)
        """,
        re.X|re.M
)

@register_parser
def f2fs_sync_file_enter(payload):
    """Parser for `f2fs_sync_file_enter` tracepoint"""
    try:
        match = re.match(f2fs_sync_file_enter_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return F2FSSyncFileEnter(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
