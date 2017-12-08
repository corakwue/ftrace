import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_transaction_ref_to_node'

__all__ = [TRACEPOINT]

#binder_transaction_ref_to_node: transaction=135943 node=135186 src_ref=135187 src_desc=27 ==> dest_ptr=0x00000000941a4840

BinderTransactionRefToNodeBase = namedtuple(TRACEPOINT,
    [
    'transaction',
    'node',
    'src_ref',
    'src_desc',
    'dest_ptr'
    ]
)

class BinderTransactionRefToNode(BinderTransactionRefToNodeBase):
    __slots__ = ()
    def __new__(cls, transaction, node, src_ref, src_desc, dest_ptr):

            return super(cls, BinderTransactionRefToNode).__new__(
                cls,
                transaction=transaction,
                node=node,
                src_ref=src_ref,
                src_desc=src_desc,
                dest_ptr=dest_ptr
            )

binder_transaction_ref_to_node_pattern = re.compile(
    r"""
    transaction=(\d+)\s+
    node=(\d+)\s+
    src_ref=(\d+)\s+
    src_desc=(\d+)\s+
    ==>\s+
    dest_ptr=(0x[0-9a-f]+)
    """,
    re.X|re.M
)

@register_parser
def binder_transaction_ref_to_node(payload):
    """Parser for `binder_transaction_ref_to_node`"""
    try:
        match = re.match(binder_transaction_ref_to_node_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderTransactionRefToNode(int(match.group(1)),
                                              int(match.group(2)),
                                              int(match.group(3)),
                                              int(match.group(4)),
                                              int(match.group(5), base=16))
    except Exception as e:
        raise ParserError(e.message)
