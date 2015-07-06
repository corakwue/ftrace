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

TRACEPOINT = 'sched_migrate_task'


__all__ = [TRACEPOINT]

#

SchedMigrateTaskBase = namedtuple(TRACEPOINT,
    [
    'comm', # Task name
    'pid', # Process pid
    'prio', # Process priority
    'load', # load if available
    'orig_cpu', # Orig. cpu
    'dest_cpu', # Dest. cpu
    ]
)

class SchedMigrateTask(SchedMigrateTaskBase):
    __slots__ = ()
    def __new__(cls, comm, pid, prio, orig_cpu, dest_cpu, load=None):
            pid = int(pid)
            prio = int(prio)
            orig_cpu = int(orig_cpu)
            dest_cpu = int(dest_cpu)
            load = int(load) if load else load

            return super(cls, SchedMigrateTask).__new__(
                cls,
                comm=comm,
                pid=pid,
                prio=prio,
                load=load,
                orig_cpu=orig_cpu,
                dest_cpu=dest_cpu,
            )

sched_migrate_pattern = re.compile(
        r"""
        comm=(?P<comm>.+)\s+
        pid=(?P<pid>\d+)\s+
        prio=(?P<prio>\d+)\s+
        \w*\D*(?P<load>\d*)\s*
        orig_cpu=(?P<orig_cpu>\d+)\s+
        dest_cpu=(?P<dest_cpu>\d+)
        """,
        re.X|re.M
)

@register_parser
def sched_migrate_task(payload):
    """Parser for `sched_migrate_task` tracepoint"""
    try:
        match = re.match(sched_migrate_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return SchedMigrateTask(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
