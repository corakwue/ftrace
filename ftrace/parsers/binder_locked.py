import re
from ftrace.common import ParserError
from .register import register_parser
from collections import namedtuple

TRACEPOINT = 'binder_locked'

__all__ = [TRACEPOINT]

#binder_locked: tag=binder_ioctl

BinderLockedBase = namedtuple(TRACEPOINT,
    [
    'tag'
    ]
)

class BinderLocked(BinderLockedBase):
    __slots__ = ()
    def __new__(cls, tag):
            return super(cls, BinderLocked).__new__(
                cls,
                tag=tag
            )

binder_locked_pattern = re.compile(
    r"""
    tag=([^\s]+)
    """,
    re.X|re.M
)

@register_parser
def binder_locked(payload):
    """Parser for `binder_locked`"""
    try:
        match = re.match(binder_locked_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderLocked(match.group(1))
    except Exception as e:
        raise ParserError(e.message)

