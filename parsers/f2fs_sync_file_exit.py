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

TRACEPOINT = 'f2fs_sync_file_exit'


__all__ = [TRACEPOINT]

F2FSSyncFileExitBase = namedtuple(TRACEPOINT,
    [
    'dev_major', 
    'dev_minor', 
    'ino', 
    'need_cp',
    'datasync',
    'ret',
    ]
)

class F2FSSyncFileExit(F2FSSyncFileExitBase):
    __slots__ = ()
    def __new__(cls, dev_major, dev_minor, ino, need_cp, datasync, ret):
            dev_major = int(dev_major)
            dev_minor = int(dev_minor)
            ino=int(ino)
            ret=int(ret)
            
            return super(cls, F2FSSyncFileExit).__new__(
                cls,
                dev_major=dev_major,
                dev_minor=dev_minor,
                ino=ino,
                need_cp=need_cp,
                datasync=datasync,
                ret=ret
            )

f2fs_sync_file_exit_pattern = re.compile(
        r"""
        dev = \((?P<dev_major>\d+),
        (?P<dev_minor>\d+)\),\s+
        ino = (?P<ino>\d+),\s+
        checkpoint is (?P<need_cp>.+),\s+
        datasync = (?P<datasync>\d+),\s+
        ret = (?P<ret>\d+)
        """,
        re.X|re.M
)

@register_parser
def f2fs_sync_file_exit(payload):
    """Parser for `f2fs_sync_file_exit` tracepoint"""
    try:
        match = re.match(f2fs_sync_file_exit_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return F2FSSyncFileExit(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
