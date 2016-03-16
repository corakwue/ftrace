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

import heapq
from .event import EventList
from .interval import IntervalList
from .common import FtraceError

def _decorate_items(iterable):

    if isinstance(iterable, EventList):
        for item in iterable:
            yield (item.timestamp, item)
    elif isinstance(iterable, IntervalList):
        for item in iterable:
            yield (item.interval.start, item)
    else:
        raise FtraceError(msg='Unsupported iterable: {}'.format(type(iterable)))

def sorted_items(iterables):
    sorted_iterable = heapq.merge(*(_decorate_items(s) for s in iterables))

    for _, item in sorted_iterable:
        yield item