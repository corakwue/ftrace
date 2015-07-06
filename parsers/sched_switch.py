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
from ftrace.task import TaskStateMapping

TRACEPOINT = 'sched_switch'


__all__ = [TRACEPOINT]

# prev_comm=swapper/7 prev_pid=0 prev_prio=120 prev_state=R ==> next_comm=snapshot-test-2 next_pid=2243 next_prio=120

SchedSwitchBase = namedtuple(TRACEPOINT,
    [
    'prev_comm', # Prev. Task name
    'prev_pid', # Prev. process pid
    'prev_prio', # Prev. process priority
    'prev_state', # Prev. process state
    'next_comm', # Next Task name
    'next_pid', # Next task pid
    'next_prio', # Next task prio
    ]
)


class SchedSwitch(SchedSwitchBase):
    __slots__ = ()
    def __new__(cls, prev_comm, prev_pid, prev_prio,
                prev_state, next_comm, next_pid, next_prio):
            prev_pid = int(prev_pid)
            prev_prio = int(prev_prio)
            next_pid = int(next_pid)
            next_prio = int(next_prio)

            return super(cls, SchedSwitch).__new__(
                cls,
                prev_comm=prev_comm,
                prev_pid=prev_pid,
                prev_prio=prev_prio,
                prev_state=prev_state,
                next_comm=next_comm,
                next_pid=next_pid,
                next_prio=next_prio,
            )

sched_switch_pattern = re.compile(
        r"""prev_comm=(?P<prev_comm>.*)\s+
        prev_pid=(?P<prev_pid>\d+)\s+
        prev_prio=(?P<prev_prio>\d+)\s+
        prev_state=(?P<prev_state>.+)\s+ # todo: handled corner cases e.g. D|W
        ==>\s+
        next_comm=(?P<next_comm>.*)\s+
        next_pid=(?P<next_pid>\d+)\s+
        next_prio=(?P<next_prio>\d+)
        """,
        re.X|re.M
)

@register_parser
def sched_switch(payload):
    """Parser for `sched_switch` tracepoint"""
    try:
        match = re.match(sched_switch_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            match_group_dict['prev_state'] = TaskStateMapping[match_group_dict['prev_state']]
            return SchedSwitch(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
