import re
from ftrace.common import ParserError
from .register import register_parser
from collections import namedtuple

TRACEPOINT = 'binder_lock'

__all__ = [TRACEPOINT]

#binder_lock: tag=binder_ioctl

BinderLockBase = namedtuple(TRACEPOINT,
    [
    'tag'
    ]
)

class BinderLock(BinderLockBase):
    __slots__ = ()
    def __new__(cls, tag):
            return super(cls, BinderLock).__new__(
                cls,
                tag=tag
            )

binder_lock_pattern = re.compile(
    r"""
    tag=([^\s]+)
    """,
    re.X|re.M
)

@register_parser
def binder_lock(payload):
    """Parser for `binder_lock`"""
    try:
        match = re.match(binder_lock_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderLock(match.group(1))
    except Exception as e:
        raise ParserError(e.message)

