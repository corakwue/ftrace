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
from ftrace.sched_hmp import HMPMigrateMapping
try:
    from ftrace.third_party.cnamedtuple import namedtuple
except ImportError:
    from collections import namedtuple


TRACEPOINT = 'sched_hmp_migrate'

__all__ = [TRACEPOINT]

SchedHMPMigrateBase = namedtuple(TRACEPOINT,
    [
    'comm', # Task name
    'pid', # Process pid
    'dest', # Dest. cpu
    'force'
    ]
)

class SchedHMPMigrate(SchedHMPMigrateBase):
    __slots__ = ()
    def __new__(cls, comm, pid, dest, force):
            pid = int(pid)
            dest = int(dest)
            force = force

            return super(cls, SchedHMPMigrate).__new__(
                cls,
                comm=comm,
                pid=pid,
                dest=dest,
                force=force,
            )

sched_hmp_migrate_pattern = re.compile(
        r"""
        comm=(?P<comm>.+)\s+
        pid=(?P<pid>\d+)\s+
        dest=(?P<dest>\d+)\s+
        force=(?P<force>\d+)
        """,
        re.X|re.M
)

@register_parser
def sched_hmp_migrate(payload):
    """Parser for `sched_hmp_migrate` tracepoint"""
    try:
        match = re.match(sched_hmp_migrate_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            match_group_dict['force'] = HMPMigrateMapping[int(match_group_dict['force'])]
            return SchedHMPMigrate(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
