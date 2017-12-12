import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_wait_for_work'

__all__ = [TRACEPOINT]

#binder_wait_for_work: proc_work=0 transaction_stack=1 thread_todo=0

BinderWaitForWorkBase = namedtuple(TRACEPOINT,
    [
    'proc_work',
    'transaction_stack',
    'thread_todo'
    ]
)

class BinderWaitForWork(BinderWaitForWorkBase):
    __slots__ = ()
    def __new__(cls, proc_work, transaction_stack, thread_todo):

            return super(cls, BinderWaitForWork).__new__(
                cls,
                proc_work=proc_work,
                transaction_stack=transaction_stack,
                thread_todo=thread_todo
            )

binder_wait_for_work_pattern = re.compile(
    r"""
    proc_work=(\d+)\s+
    transaction_stack=(\d+)\s+
    thread_todo=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_wait_for_work(payload):
    """Parser for `binder_wait_for_work`"""
    try:
        match = re.match(binder_wait_for_work_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderWaitForWork(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except Exception as e:
        raise ParserError(e.message)
