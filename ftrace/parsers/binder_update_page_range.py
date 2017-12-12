import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_update_page_range'

__all__ = [TRACEPOINT]

#binder_update_page_range: proc=3624 allocate=1 offset=4096 size=8192

BinderUpdatePageRangeBase = namedtuple(TRACEPOINT,
    [
    'proc',
    'allocate',
    'offset',
    'size'
    ]
)

class BinderUpdatePageRange(BinderUpdatePageRangeBase):
    __slots__ = ()
    def __new__(cls, proc, allocate, offset, size):

            return super(cls, BinderUpdatePageRange).__new__(
                cls,
                proc=proc,
                allocate=allocate,
                offset=offset,
                size=size
            )

binder_update_page_range_pattern = re.compile(
    r"""
    proc=(\d+)\s+
    allocate=(\d+)\s+
    offset=(\d+)\s+
    size=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_update_page_range(payload):
    """Parser for `binder_update_page_range`"""
    try:
        match = re.match(binder_update_page_range_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderUpdatePageRange(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)))
    except Exception as e:
        raise ParserError(e.message)
