import re
from ftrace.common import ParserError
from .register import register_parser
from collections import namedtuple

TRACEPOINT = 'binder_unlock'

__all__ = [TRACEPOINT]

#binder_unlock: tag=binder_ioctl

BinderUnlockBase = namedtuple(TRACEPOINT,
    [
    'tag'
    ]
)

class BinderUnlock(BinderUnlockBase):
    __slots__ = ()
    def __new__(cls, tag):
            return super(cls, BinderUnlock).__new__(
                cls,
                tag=tag
            )

binder_unlock_pattern = re.compile(
    r"""
    tag=([^\s]+)
    """,
    re.X|re.M
)

@register_parser
def binder_unlock(payload):
    """Parser for `binder_unlock`"""
    try:
        match = re.match(binder_unlock_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderUnlock(match.group(1))
    except Exception as e:
        raise ParserError(e.message)

