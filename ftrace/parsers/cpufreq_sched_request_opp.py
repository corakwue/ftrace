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


TRACEPOINT = 'cpufreq_sched_request_opp'

__all__ = [TRACEPOINT]

CpufreqSchedRequestOppBase = namedtuple(TRACEPOINT,
    [
    'cpu'
    'capacity',
    'freq_new',
    'requested_freq'
    ]
)

class CpufreqSchedRequestOpp(CpufreqSchedRequestOppBase):
    __slots__ = ()
    def __new__(cls, cpu, capacity, freq_new, requested_freq):
            cpu = int(cpu)
            capacity = int(capacity)
            freq_new = int(freq_new)
            requested_freq = int(requested_freq)

            return super(cls, CpufreqSchedRequestOpp).__new__(
                cls,
                cpu=cpu,
                capacity=capacity,
                freq_new=freq_new,
                requested_freq=requested_freq,
            )

cpufreq_sched_request_opp_pattern = re.compile(
        r"""
        cpu (?P<cpu>\d+)\s+
        cap change, cluster cap request (?P<capacity>\d+)\s+
        => OPP (?P<freq_new>\d+) \(cur (?P<requested_freq>\d+)
        """,
        re.X|re.M
)

@register_parser
def cpufreq_sched_request_opp(payload):
    """Parser for `cpufreq_sched_request_opp` tracepoint"""
    try:
        match = re.match(cpufreq_sched_request_opp_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return CpufreqSchedRequestOpp(**match_group_dict)
    except Exception, e:
        raise ParserError(e.message)
