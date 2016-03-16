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

TRACEPOINT = 'cluster_exit'


__all__ = [TRACEPOINT]

# TODO: Unpsck from bitfield to set/tuple

ClusterExitBase = namedtuple(TRACEPOINT,
    [
    'name',
    'idx',
    'sync', # unpack to tuple or set
    'child', # unpack to tuple or set
    'idle',
    ]
)


class ClusterExit(ClusterExitBase):
    __slots__ = ()
    def __new__(cls, name, idx, sync, child, idle):
            idx=int(idx)
            idle=int(idle)

            return super(cls, ClusterExit).__new__(
                cls,
                name=name,
                idx=idx,
                sync=sync,
                child=child,
                idle=idle,
            )

cluster_exit_pattern = re.compile(
        r"""cluster_name:(?P<name>.+)\s+
        idx:(?P<idx>\d+)\s+
        sync:(?P<sync>\w+)\s+
        child:(?P<child>\w+)\s+
        idle:(?P<idle>\d+)
        """,
        re.X|re.M
)

@register_parser
def cluster_exit(payload):
    """Parser for `cluster_exit` tracepoint"""
    try:
        match = re.match(cluster_exit_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return ClusterExit(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
