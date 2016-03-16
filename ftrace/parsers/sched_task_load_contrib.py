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

try:
    from ftrace.third_party.cnamedtuple import namedtuple
except ImportError:
    from collections import namedtuple


TRACEPOINT = 'sched_task_load_contrib'


__all__ = [TRACEPOINT]


SchedTaskLoadContribBase = namedtuple(TRACEPOINT,
    [
    'comm',
    'pid',
    'load_contrib'
    ]
)


class SchedTaskLoadContrib(SchedTaskLoadContribBase):
    __slots__ = ()
    def __new__(cls, comm, pid, load_contrib):
            pid = int(pid)
            load_contrib = float(load_contrib)

            return super(cls, SchedTaskLoadContrib).__new__(
                cls,
                comm=comm,
                pid=pid,
                load_contrib=load_contrib,
            )

sched_task_load_contrib_pattern = re.compile(
        r"""comm=(?P<comm>.*)\s+
        pid=(?P<pid>\d+)\s+
        load_contrib=(?P<load_contrib>\d+)\s+
        """,
        re.X|re.M
)

@register_parser
def sched_task_load_contrib(payload):
    """Parser for `sched_task_load_contrib` tracepoint"""
    try:
        match = re.match(sched_task_load_contrib_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return SchedTaskLoadContrib(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
