import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_ioctl'

__all__ = [TRACEPOINT]

#binder_ioctl: cmd=0xc0186201 arg=0xbea7dc28

BinderIoctlBase = namedtuple(TRACEPOINT,
    [
    'cmd',
    'mode',
    'arg',
    ]
)

class BinderIoctl(BinderIoctlBase):
    __slots__ = ()
    def __new__(cls, cmd, arg):

            (cmd, mode) = parse_binder_cmd (int(cmd, base=16))
            arg = int(arg, base=16)

            return super(cls, BinderIoctl).__new__(
                cls,
                cmd=cmd,
                mode=mode,
                arg=hex(arg),
            )

binder_ioctl_pattern = re.compile(
    r"""
    cmd=(0x[0-9a-f]+)\s+
    arg=(0x[0-9a-f]+)
    """,
    re.X|re.M
)

@register_parser
def binder_ioctl(payload):
    """Parser for `binder_ioctl`"""
    try:
        match = re.match(binder_ioctl_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderIoctl(match.group(1), match.group(2))
    except Exception as e:
        raise ParserError(e.message)
