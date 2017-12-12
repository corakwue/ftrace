import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_ioctl_done'

__all__ = [TRACEPOINT]

#binder_ioctl_done: ret=0

BinderIoctlDoneBase = namedtuple(TRACEPOINT,
    [
    'ret'
    ]
)

class BinderIoctlDone(BinderIoctlDoneBase):
    __slots__ = ()
    def __new__(cls, ret):

            return super(cls, BinderIoctlDone).__new__(
                cls,
                ret=ret
            )

binder_ioctl_done_pattern = re.compile(
    r"""
    ret=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_ioctl_done(payload):
    """Parser for `binder_ioctl_done`"""
    try:
        match = re.match(binder_ioctl_done_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderIoctlDone(int(match.group(1)))
    except Exception as e:
        raise ParserError(e.message)
