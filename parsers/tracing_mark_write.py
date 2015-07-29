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

from .register import register_parser
from collections import namedtuple
#from ftrace.third_party.cnamedtuple import namedtuple
from ftrace.common import ParserError
from ftrace.atrace import AtraceTagMapping, AtraceTag

TRACEPOINT = 'tracing_mark_write'


__all__ = [TRACEPOINT]

# See system/core/include/cutils/trace.h
# For non-async context
#   tracing_mark_write: B|pid|section_name (non-async)
#   tracing_mark_write: E

# For async event tracing start/finish
#   tracing_mark_write: S|pid|section_name|cookie
#   tracing_mark_write: F|pid|section_name|cookie

# For counter event
#   tracing_mark_write: C|pid|counter_name|value (non-async)

ContextEndBase = namedtuple(TRACEPOINT,
    [
    'atrace_tag', # Trace tag [E]
    ]
)

ContextBeginBase = namedtuple(TRACEPOINT,
    [
    'atrace_tag', # Trace tag [B]
    'pid', # Pid
    'section_name', # Section name
    ]
)

AsyncEventBase = namedtuple(TRACEPOINT,
    [
    'atrace_tag', # Trace tag [S|F]
    'pid', # Pid
    'section_name', # Section name
    'cookie', # Cookie
    ]
)

CounterBase = namedtuple(TRACEPOINT,
    [
    'atrace_tag', # Trace tag [C]
    'pid', # Counter value
    'counter_name', # Counter name
    'value', # Counter value
    ]
)

class TracingMarkWriteContextEnd(ContextEndBase):

    __slots__ = ()

    def __new__(cls, atrace_tag):

        return super(cls, TracingMarkWriteContextEnd).__new__(
            cls,
            atrace_tag=atrace_tag,
        )

class TracingMarkWriteContextBegin(ContextBeginBase):

    __slots__ = ()

    def __new__(cls, atrace_tag, pid, section_name):
        pid = int(pid)

        return super(cls, TracingMarkWriteContextBegin).__new__(
            cls,
            atrace_tag=atrace_tag,
            pid=pid,
            section_name=section_name,
        )

class TracingMarkWriteAsyncEvent(AsyncEventBase):

    __slots__ = ()

    def __new__(cls, atrace_tag, pid, section_name, cookie):
        pid = int(pid)
        cookie = int(cookie)

        return super(cls, TracingMarkWriteAsyncEvent).__new__(
            cls,
            atrace_tag=atrace_tag,
            pid=pid,
            section_name=section_name,
            cookie=cookie,
        )

class TracingMarkWriteCounter(CounterBase):

    __slots__ = ()

    def __new__(cls, atrace_tag, pid, counter_name, value):
        pid = int(pid)
        value = int(value)

        return super(cls, TracingMarkWriteCounter).__new__(
            cls,
            atrace_tag=atrace_tag,
            pid=pid,
            counter_name=counter_name,
            value=value,
        )

@register_parser
def tracing_mark_write(payload):
    """Parser for `tracing_mark_write` tracepoint"""
    try:
        split_payload = payload.split('|')
        atrace_tag = AtraceTagMapping[split_payload[0]]
        value_list = [atrace_tag] + split_payload[1:]
        if atrace_tag is AtraceTag.CONTEXT_BEGIN:
            group_dict = dict(zip(ContextBeginBase._fields, value_list))
            return TracingMarkWriteContextBegin(**group_dict)
        elif atrace_tag in [AtraceTag.ASYNC_BEGIN, AtraceTag.ASYNC_END]:
            group_dict = dict(zip(AsyncEventBase._fields, value_list))
            return TracingMarkWriteAsyncEvent(**group_dict)
        elif atrace_tag is  AtraceTag.COUNTER:
            group_dict = dict(zip(CounterBase._fields, value_list))
            return TracingMarkWriteCounter(**group_dict)
        elif atrace_tag is AtraceTag.CONTEXT_END:
            return TracingMarkWriteContextEnd(atrace_tag)
        elif 'trace_event_clock_sync' in payload:
            raise ParserError('Skipping trace_event_clock_sync') 
        else:
            raise ParserError('Unknown tracing_mark_write format')
    except Exception, e:
        raise ParserError(e.message)
