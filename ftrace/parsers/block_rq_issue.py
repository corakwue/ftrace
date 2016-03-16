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
from ftrace.io import DiskCommand, DiskIOTypeMapping, DiskCommandMapping, RWBS
from .register import register_parser
from collections import namedtuple
#from ftrace.third_party.cnamedtuple import namedtuple

TRACEPOINT = 'block_rq_issue'


__all__ = [TRACEPOINT]

#issue pending block IO request operation to device driver
#block_rq_issue: 179,0 WASM () 6455304 + 8 [mmcqd/0]
BlockRQIssueBase = namedtuple(TRACEPOINT,
    [
    'dev_major',
    'dev_minor',
    'sector',
    'nr_sector',
    'cmd',
    'comm',
    'rwbs', #  read burst and write burst bank switching
    ]
)

class BlockRQIssue(BlockRQIssueBase):
    __slots__ = ()
    def __new__(cls, dev_major, dev_minor, sector, nr_sector, cmd, comm, rwbs):
            dev_major = int(dev_major)
            dev_minor = int(dev_minor)
            sector=int(sector)
            nr_sector=int(nr_sector)

            return super(cls, BlockRQIssue).__new__(
                cls,
                dev_major=dev_major,
                dev_minor=dev_minor,
                sector=sector,
                nr_sector=nr_sector,
                comm=comm,
                cmd=cmd,
                rwbs=rwbs,
            )

block_rq_issue_pattern = re.compile(
        r"""
        (?P<dev_major>\d+),
        (?P<dev_minor>\d+)\s+
        (?P<flush>[F]?)
        (?P<rwbs>\w+)\s+\d+\s+
        \((?P<cmd>.*)\)\s+
        (?P<sector>\d+)\s+\+\s+
        (?P<nr_sector>\d+)\s+
        \[(?P<comm>.+)\]
        """,
        re.X|re.M
)

@register_parser
def block_rq_issue(payload):
    """Parser for `block_rq_issue` tracepoint"""
    try:
        match = re.match(block_rq_issue_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            rwbs_command = match_group_dict['rwbs']
            io_type=DiskIOTypeMapping[rwbs_command[0]]
            commands = set(DiskCommandMapping[c] for c in rwbs_command[1:])
            if match_group_dict['flush']:
                commands.add(DiskCommand.FLUSH)
            del match_group_dict['flush']
            match_group_dict['rwbs'] = RWBS(io_type=io_type, commands=commands)
            return BlockRQIssue(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
