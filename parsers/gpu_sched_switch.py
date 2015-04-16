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

TRACEPOINT = 'gpu_sched_switch'


__all__ = [TRACEPOINT]


GPUSchedSwitchBase = namedtuple(TRACEPOINT,
    [
    'gpu_name', # GPU Hardware block e.g. "2D", "3D", "Compute"
    'timestamp', # Timestamp (not necessarily CPU clock)
    'next_ctx_id', # Next context running on GPU hardware block
    'next_prio', # Priority of next context
    'next_job_id', # Batch of work enqueued
    ]
)


class GPUSchedSwitch(GPUSchedSwitchBase):
    __slots__ = ()
    def __new__(cls, gpu_name, timestamp, next_ctx_id, next_prio, next_job_id):
            timestamp = float(timestamp)
            next_ctx_id = int(next_ctx_id)
            next_prio = int(next_prio)
            next_job_id = int(next_job_id)

            return super(cls, GPUSchedSwitch).__new__(
                cls,
                gpu_name=gpu_name,
                timestamp=timestamp,
                next_ctx_id=next_ctx_id,
                next_prio=next_prio,
                next_job_id=next_job_id,
            )

gpu_sched_switch_pattern = re.compile(
        r"""gpu_name=(?P<gpu_name>.+)\s+
        ts=(?P<ts>\d+)\s+
        next_ctx_id=(?P<next_ctx_id>\d+)\s+
        next_prio=(?P<next_prio>\d+)\s+
        next_job_id=(?P<next_job_id>\d+)
        """,
        re.X|re.M
)

@register_parser
def gpu_sched_switch(payload):
    """Parser for `gpu_sched_switch` tracepoint"""
    try:
        match = re.match(gpu_sched_switch_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return GPUSchedSwitch(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
