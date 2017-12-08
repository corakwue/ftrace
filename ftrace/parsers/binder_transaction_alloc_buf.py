import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_transaction_alloc_buf'

__all__ = [TRACEPOINT]

#binder_transaction_alloc_buf: transaction=135931 data_size=96 offsets_size=0

BinderTransactionAllocBufBase = namedtuple(TRACEPOINT,
    [
    'transaction',
    'data_size',
    'offsets_size'
    ]
)

class BinderTransactionAllocBuf(BinderTransactionAllocBufBase):
    __slots__ = ()
    def __new__(cls, transaction, data_size, offsets_size):

            return super(cls, BinderTransactionAllocBuf).__new__(
                cls,
                transaction=transaction,
                data_size=data_size,
                offsets_size=offsets_size
            )

binder_transaction_alloc_buf_pattern = re.compile(
    r"""
    transaction=(\d+)\s+
    data_size=(\d+)\s+
    offsets_size=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_transaction_alloc_buf(payload):
    """Parser for `binder_transaction_alloc_buf`"""
    try:
        match = re.match(binder_transaction_alloc_buf_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderTransactionAllocBuf(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except Exception as e:
        raise ParserError(e.message)
