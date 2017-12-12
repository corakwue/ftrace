# see Documentation/ioctl/ioctl-decoding.txt for decoding ioctls()
param_types = {
    0: 'no params',
    1: 'read',
    2: 'write',
    3: 'read-write'
}

def binder_ioctl (fun):

    # From include/uapi/linux/android/binder.h
    if fun == 1:
        return "READ_WRITE"
    elif fun == 3:
        return "SET_IDLE_TIMEOUT"
    elif fun == 5:
        return "SET_MAX_THREADS"
    elif fun == 6:
        return "SET_IDLE_PRIORITY"
    elif fun == 7:
        return "SET_CONTEXT_MGR"
    elif fun == 8:
        return "THREAD_EXIT"
    elif fun == 9:
        return "VERSION"
    elif fun == 11:
        return "GET_NODE_DEBUG_INFO"
    else:
        return "INVALID_BINDER_IOCTL:%d" % (int(fun))

def binder_command (fun):

    # From include/uapi/linux/android/binder.h
    if fun == 0:
        return "TRANSACTION"
    elif fun == 1:
        return "REPLY"
    elif fun == 2:
        return "ACQUIRE_RESULT"
    elif fun == 3:
        return "FREE_BUFFER"
    elif fun == 4:
        return "INCREFS"
    elif fun == 5:
        return "ACQUIRE"
    elif fun == 6:
        return "RELEASE"
    elif fun == 7:
        return "DECREFS"
    elif fun == 8:
        return "INCREFS_DONE"
    elif fun == 9:
        return "ACQUIRE_DONE"
    elif fun == 10:
        return "ATTEMPT_ACQUIRE"
    elif fun == 11:
        return "REGISTER_LOOPER"
    elif fun == 12:
        return "ENTER_LOOPER"
    elif fun == 13:
        return "EXIT_LOOPER"
    elif fun == 14:
        return "REQUEST_DEATH_NOTIFICATION"
    elif fun == 15:
        return "CLEAR_DEATH_NOTIFICATION"
    elif fun == 16:
        return "DEAD_BINDER_DONE"
    elif fun == 17:
        return "TRANSACTION_SG"
    elif fun == 18:
        return "REPLY_SG"
    else:
        return "INVALID_BINDER_COMMAND:%d" % (int(fun))

def binder_return (fun):

    # From include/uapi/linux/android/binder.h
    if fun == 0:
        return "ERROR"
    elif fun == 1:
        return "OK"
    elif fun == 2:
        return "TRANSACTION"
    elif fun == 3:
        return "REPLY"
    elif fun == 4:
        return "ACQUIRE_RESULT"
    elif fun == 5:
        return "DEAD_REPLY"
    elif fun == 6:
        return "TRANSACTION_COMPLETE"
    elif fun == 7:
        return "INCREFS"
    elif fun == 8:
        return "ACQUIRE"
    elif fun == 9:
        return "RELEASE"
    elif fun == 10:
        return "DECREFS"
    elif fun == 11:
        return "ATTEMPT_ACQUIRE"
    elif fun == 12:
        return "NOOP"
    elif fun == 13:
        return "SPAWN_LOOPER"
    elif fun == 14:
        return "FINISHED"
    elif fun == 15:
        return "DEAD_BINDER"
    elif fun == 16:
        return "CLEAR_DEATH_NOTIFICATION_DONE"
    elif fun == 17:
        return "FAILED_REPLY"
    else:
        return "INVALID_BINDER_RETURN:%d" % (int(fun))

def parse_binder_cmd (cmd):

    cmd_type = (cmd & 0xc0000000) >> 30
    cmd_size = (cmd & 0x3fff0000) >> 16
    cmd_id   = (cmd & 0x0000ff00) >>  8
    cmd_fun  = (cmd & 0x000000ff) >>  0

    cmd_type = param_types[cmd_type]

    if chr(cmd_id) == 'b':
        return (binder_ioctl (cmd_fun), cmd_type)

    if chr(cmd_id) == 'c':
        return (binder_command (cmd_fun), cmd_type)

    if chr(cmd_id) == 'r':
        return (binder_return (cmd_fun), cmd_type)

    return ("INV_ID:%c[size=%d,fun=%d]" % (cmd_id, cmd_size, cmd_fun), cmd_type)
