import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_transaction_fd'

__all__ = [TRACEPOINT]

#binder_transaction_fd: transaction=135945 src_fd=63 ==> dest_fd=30

BinderTransactionFdBase = namedtuple(TRACEPOINT,
    [
    'transaction',
    'src_fd',
    'dest_fd'
    ]
)

class BinderTransactionFd(BinderTransactionFdBase):
    __slots__ = ()
    def __new__(cls, transaction, src_fd, dest_fd):

            return super(cls, BinderTransactionFd).__new__(
                cls,
                transaction=transaction,
                src_fd=src_fd,
                dest_fd=dest_fd
            )

binder_transaction_fd_pattern = re.compile(
    r"""
    transaction=(\d+)\s+
    src_fd=(\d+)\s+
    ==>\s+
    dest_fd=(\d+)
    """,
    re.X|re.M
)

@register_parser
def binder_transaction_fd(payload):
    """Parser for `binder_transaction_fd`"""
    try:
        match = re.match(binder_transaction_fd_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderTransactionFd(int(match.group(1)),
                                              int(match.group(2)),
                                              int(match.group(3)))
    except Exception as e:
        raise ParserError(e.message)
