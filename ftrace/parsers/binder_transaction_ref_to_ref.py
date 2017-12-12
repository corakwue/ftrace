import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_transaction_ref_to_ref'

__all__ = [TRACEPOINT]

#binder_transaction_ref_to_ref: transaction=136308 node=11089 src_ref=11090 src_desc=121 ==> dest_ref=136262 dest_desc=549

BinderTransactionRefToRefBase = namedtuple(TRACEPOINT,
    [
    'transaction',
    'node',
    'src_ref',
    'src_desc',
    'dest_ref',
    'dest_desc'
    ]
)

class BinderTransactionRefToRef(BinderTransactionRefToRefBase):
    __slots__ = ()
    def __new__(cls, transaction, node, src_ref, src_desc, dest_ref, dest_desc):

            return super(cls, BinderTransactionRefToRef).__new__(
                cls,
                transaction=transaction,
                node=node,
                src_ref=src_ref,
                src_desc=src_desc,
                dest_ref=dest_ref,
                dest_desc=dest_desc
            )

binder_transaction_ref_to_ref_pattern = re.compile(
    r"""
    transaction=(\d+)\s+
    node=(\d+)\s+
    src_ref=(\d+)\s+
    src_desc=(\d+)\s+
    ==>\s+
    dest_ref=(\d+)\s+
    dest_desc=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_transaction_ref_to_ref(payload):
    """Parser for `binder_transaction_ref_to_ref`"""
    try:
        match = re.match(binder_transaction_ref_to_ref_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderTransactionRefToRef(int(match.group(1)),
                                             int(match.group(2)),
                                             int(match.group(3)),
                                             int(match.group(4)),
                                             int(match.group(5)),
                                             int(match.group(6)))
    except Exception as e:
        raise ParserError(e.message)
