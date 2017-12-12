import re
from ftrace.common import ParserError
from .register import register_parser
from .binder import parse_binder_cmd
from collections import namedtuple

TRACEPOINT = 'binder_transaction'

__all__ = [TRACEPOINT]

#binder_transaction: transaction=135931 dest_node=133235 dest_proc=280 dest_thread=0 reply=0 flags=0x10 code=0x2

BinderTransactionBase = namedtuple(TRACEPOINT,
    [
    'transaction',
    'dest_node',
    'dest_proc',
    'dest_thread',
    'reply',
    'flags',
    'code'
    ]
)

def decode_transaction_flags (flags):

    result = set()

    # this is a one-way call: async, no return
    if flags & 0x01: result.add ('TF_ONE_WAY')

    # contents are the component's root object
    if flags & 0x04: result.add ('TF_ROOT_OBJECT')

    # contents are a 32-bit status code
    if flags & 0x08: result.add ('TF_STATUS_CODE')

    # allow replies with file descriptors
    if flags & 0x10: result.add ('TF_ACCEPT_FDS')

    # Check for missing flags
    remain = flags & 0xffffffe2
    if remain: result.add ('UNKNOWN_FLAGS_%x' % remain)

    return result


class BinderTransaction(BinderTransactionBase):
    __slots__ = ()
    def __new__(cls, transaction, dest_node, dest_proc, dest_thread, reply, flags, code):

            return super(cls, BinderTransaction).__new__(
                cls,
                transaction=transaction,
                dest_node=dest_node,
                dest_proc=dest_proc,
                dest_thread=dest_thread,
                reply=reply,
                flags=flags,
                code=code
            )

binder_transaction_pattern = re.compile(
    r"""
    transaction=(\d+)\s+
    dest_node=(\d+)\s+
    dest_proc=(\d+)\s+
    dest_thread=(\d+)\s+
    reply=(\d+)\s+
    flags=(0x[0-9a-f]+)\s+
    code=(0x[0-9a-f]+)
    """,
    re.X|re.M
)

@register_parser
def binder_transaction(payload):
    """Parser for `binder_transaction`"""
    try:
        match = re.match(binder_transaction_pattern, payload)
        if match:
            match_group_dict = match.groupdict()
            return BinderTransaction(int(match.group(1)),
                                     int(match.group(2)),
                                     int(match.group(3)),
                                     int(match.group(4)),
                                     int(match.group(5)),
                                     decode_transaction_flags (int(match.group(6), base=16)),
                                     int(match.group(7), base=16))
    except Exception as e:
        raise ParserError(e.message)
