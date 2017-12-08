import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_transaction_buffer_release'

__all__ = [TRACEPOINT]

#binder_transaction_buffer_release: transaction=135918 data_size=28 offsets_size=0

BinderTransactionBufferReleaseBase = namedtuple(TRACEPOINT,
    [
    'transaction',
    'data_size',
    'offsets_size'
    ]
)

class BinderTransactionBufferRelease(BinderTransactionBufferReleaseBase):
    __slots__ = ()
    def __new__(cls, transaction, data_size, offsets_size):

            return super(cls, BinderTransactionBufferRelease).__new__(
                cls,
                transaction=transaction,
                data_size=data_size,
                offsets_size=offsets_size
            )

binder_transaction_buffer_release_pattern = re.compile(
    r"""
    transaction=(\d+)\s+
    data_size=(\d+)\s+
    offsets_size=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_transaction_buffer_release(payload):
    """Parser for `binder_transaction_buffer_release`"""
    try:
        match = re.match(binder_transaction_buffer_release_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderTransactionBufferRelease(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except Exception as e:
        raise ParserError(e.message)
