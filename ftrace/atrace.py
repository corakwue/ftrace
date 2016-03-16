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

"""
    AtraceTag: Atrace tags
"""
from .common import ConstantBase

# See system/core/include/cutils/trace.h
# For non-async context
#   tracing_mark_write: B|pid|section_name (non-async)
#   tracing_mark_write: E

# For async event tracing start/finish
#   tracing_mark_write: S|pid|section_name|cookie
#   tracing_mark_write: F|pid|section_name|cookie

# For counter event
#   tracing_mark_write: C|pid|counter_name|value (non-async)

class AtraceTag(ConstantBase):
    CONTEXT_BEGIN = ()
    CONTEXT_END = ()
    ASYNC_BEGIN = ()
    ASYNC_END = ()
    COUNTER = ()

AtraceTagMapping = {
    'B': AtraceTag.CONTEXT_BEGIN,
    'S': AtraceTag.ASYNC_BEGIN,
    'E': AtraceTag.CONTEXT_END,
    'F': AtraceTag.ASYNC_END,
    'C': AtraceTag.COUNTER
}
