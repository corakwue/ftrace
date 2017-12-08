import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_transaction_received'

__all__ = [TRACEPOINT]

#binder_transaction_received: transaction=135934

BinderTransactionReceivedBase = namedtuple(TRACEPOINT,
    [
    'transaction',
    ]
)

class BinderTransactionReceived(BinderTransactionReceivedBase):
    __slots__ = ()
    def __new__(cls, transaction):

            return super(cls, BinderTransactionReceived).__new__(
                cls,
                transaction=transaction
            )

binder_transaction_received_pattern = re.compile(
    r"""
    transaction=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_transaction_received(payload):
    """Parser for `binder_transaction_received`"""
    try:
        match = re.match(binder_transaction_received_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderTransactionReceived(int(match.group(1)))
    except Exception as e:
        raise ParserError(e.message)
