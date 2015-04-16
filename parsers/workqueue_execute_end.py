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

TRACEPOINT = 'workqueue_execute_end'


__all__ = [TRACEPOINT]

WorkqueueQueueExecuteEndBase = namedtuple(TRACEPOINT,
    [
    'work_struct', 
    ]
)

class WorkqueueQueueExecuteEnd(WorkqueueQueueExecuteEndBase):
    __slots__ = ()
    def __new__(cls, work_struct):

            return super(cls, WorkqueueQueueExecuteEnd).__new__(
                cls,
                work_struct=work_struct
            )

workqueue_execute_end_pattern = re.compile(
        r"""
        work struct (?P<work_struct>.+)
        """,
        re.X|re.M
)

@register_parser
def workqueue_execute_end(payload):
    """Parser for `workqueue_execute_end` tracepoint"""
    try:
        match = re.match(workqueue_execute_end_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return WorkqueueQueueExecuteEnd(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
