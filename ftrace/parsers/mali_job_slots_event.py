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
from .register import register_parser
from collections import namedtuple
from ftrace.common import ParserError
#from ftrace.third_party.cnamedtuple import namedtuple

TRACEPOINT = 'mali_job_slots_event'

__all__ = [TRACEPOINT]

MaliJobSlotsEventBase = namedtuple(TRACEPOINT,
    [
    'event',
    'tgid',
    'pid',
    'job_id'
    
    ]
)

class MaliJobSlotsEvent(MaliJobSlotsEventBase):
    __slots__ = ()
    def __new__(cls, event, tgid, pid, job_id):

            tgid=int(tgid)
            pid=int(pid)
            job_id=int(job_id)
            
            return super(cls, MaliJobSlotsEvent).__new__(
                cls,
                event=event,
                tgid=tgid,
                pid=pid,
                job_id=job_id
            )

mali_job_slots_event_pattern = re.compile(
        r"""
        event=(?P<event>\d+)\s+
        tgid=(?P<tgid>\d+)\s+
        pid=(?P<pid>\d+)\s+
        job_id=(?P<job_id>\d+)
        """,
        re.X|re.M
)

@register_parser
def mali_job_slots_event(payload):
    """Parser for `mali_job_slots_event` tracepoint"""
    try:
        match = re.match(mali_job_slots_event_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return MaliJobSlotsEvent(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
