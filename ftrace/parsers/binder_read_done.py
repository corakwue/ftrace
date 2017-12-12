import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_read_done'

__all__ = [TRACEPOINT]

#binder_read_done: ret=0

BinderReadDoneBase = namedtuple(TRACEPOINT,
    [
    'ret'
    ]
)

class BinderReadDone(BinderReadDoneBase):
    __slots__ = ()
    def __new__(cls, ret):

            return super(cls, BinderReadDone).__new__(
                cls,
                ret=ret
            )

binder_read_done_pattern = re.compile(
    r"""
    ret=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_read_done(payload):
    """Parser for `binder_read_done`"""
    try:
        match = re.match(binder_read_done_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderReadDone(int(match.group(1)))
    except Exception as e:
        raise ParserError(e.message)
