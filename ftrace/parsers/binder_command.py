import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_command'

__all__ = [TRACEPOINT]

#binder_command: cmd=0x40046303 BC_FREE_BUFFER

BinderCommandBase = namedtuple(TRACEPOINT,
    [
    'cmd',
    'mode',
    'result'
    ]
)

class BinderCommand(BinderCommandBase):
    __slots__ = ()
    def __new__(cls, cmd, result):

            (cmd, mode) = parse_binder_cmd (int (cmd, base=16))

            # Decoded command and text output must be consistent
            if cmd != result:
                return "Invalid command (%s != %s)" % (cmd, result)

            return super(cls, BinderCommand).__new__(
                cls,
                cmd=cmd,
                mode=mode,
                result=result
            )

binder_command_pattern = re.compile(
    r"""
    cmd=(0x[0-9a-f]+)\s+
    BC_([A-Z_]+)
    """,
    re.X|re.M
)

@register_parser
def binder_command(payload):
    """Parser for `binder_command`"""
    try:
        match = re.match(binder_command_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderCommand(match.group(1), match.group(2))
    except Exception as e:
        raise ParserError(e.message)
