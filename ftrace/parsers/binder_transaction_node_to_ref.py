import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_transaction_node_to_ref'

__all__ = [TRACEPOINT]

#binder_transaction_node_to_ref: transaction=136064 node=135403 src_ptr=0x00000000b2eacc40 ==> dest_ref=135404 dest_desc=525

BinderTransactionNodeToRefBase = namedtuple(TRACEPOINT,
    [
    'transaction',
    'node',
    'src_ptr',
    'dest_ref',
    'dest_desc'
    ]
)

class BinderTransactionNodeToRef(BinderTransactionNodeToRefBase):
    __slots__ = ()
    def __new__(cls, transaction, node, src_ptr, dest_ref, dest_desc):

            return super(cls, BinderTransactionNodeToRef).__new__(
                cls,
                transaction=transaction,
                node=node,
                src_ptr=src_ptr,
                dest_ref=dest_ref,
                dest_desc=dest_desc
            )

binder_transaction_node_to_ref_pattern = re.compile(
    r"""
    transaction=(\d+)\s+
    node=(\d+)\s+
    src_ptr=(0x[0-9a-f]+)\s+
    ==>\s+
    dest_ref=(\d+)\s+
    dest_desc=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_transaction_node_to_ref(payload):
    """Parser for `binder_transaction_node_to_ref`"""
    try:
        match = re.match(binder_transaction_node_to_ref_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderTransactionNodeToRef(int(match.group(1)),
                                              int(match.group(2)),
                                              int(match.group(3), base=16),
                                              int(match.group(4)),
                                              int(match.group(5)))
    except Exception as e:
        raise ParserError(e.message)
