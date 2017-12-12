import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_write_done'

__all__ = [TRACEPOINT]

#binder_write_done: ret=0

BinderWriteDoneBase = namedtuple(TRACEPOINT,
    [
    'ret'
    ]
)

class BinderWriteDone(BinderWriteDoneBase):
    __slots__ = ()
    def __new__(cls, ret):

            return super(cls, BinderWriteDone).__new__(
                cls,
                ret=ret
            )

binder_write_done_pattern = re.compile(
    r"""
    ret=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_write_done(payload):
    """Parser for `binder_write_done`"""
    try:
        match = re.match(binder_write_done_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderWriteDone(int(match.group(1)))
    except Exception as e:
        raise ParserError(e.message)
