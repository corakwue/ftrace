#!/usr/bin/python

# Copyright 2015 Huawei Devices USA Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors:
#       Chuk Orakwue <chuk.orakwue@huawei.com>

"""
    TaskState: Possible task states from linux/sched.h
    Task: Runnable thread (process) executed on CPU.
"""
from six import integer_types
from collections import namedtuple, defaultdict
from .common import ConstantBase

TaskBase = namedtuple("Task",
    [
    'name', # Task name
    'pid', # Process pid
    'prio', # Task priority
    'tgid', # Thread group ID
    'ppid', # Parent process ID
    ]
)

class TaskState(ConstantBase):
    RUNNING = ()
    SLEEPING = ()
    UNINTERRUPTIBLE = ()
    STOPPED = ()

    EXIT_DEAD = ()
    EXIT_ZOMBIE = ()

    TASK_DEAD = ()
    TASK_WAKEKILL = ()
    TASK_WAKING = ()
    TASK_PARKED = ()

    TRACED = ()
    UNKNOWN = ()

    # based on sched_wakeup
    RUNNABLE = ()

# linux/sched.h
# /trace/events/sched.h
TaskStateMapping = defaultdict(lambda: TaskState.UNKNOWN)
state_dict = {
    'S' : TaskState.SLEEPING,
    'D' : TaskState.UNINTERRUPTIBLE,
    'T' : TaskState.STOPPED,
    't' : TaskState.TRACED,
    'Z' : TaskState.EXIT_ZOMBIE,
    'X' : TaskState.EXIT_DEAD,
    'x' : TaskState.TASK_DEAD,
    'K' : TaskState.TASK_WAKEKILL,
    'W' : TaskState.TASK_WAKING,
    'P' : TaskState.TASK_PARKED,
    'R+': TaskState.RUNNABLE,
    'R' : TaskState.RUNNING,
}

TaskStateMapping.update(state_dict)

class Task(TaskBase):

    __slots__ = ()

    def __new__(cls, name, pid, prio=None, tgid=None, ppid=None, **kwargs):
        pid = int(pid) if pid else pid
        prio = int(prio) if prio else prio
        try:
            tgid = int(tgid)
        except:
            tgid = tgid

        return super(Task, cls).__new__(
            cls,
            name=name,
            pid=pid,
            prio=prio,
            tgid=tgid,
            ppid=ppid,
        )

    def __repr__(self):
        return "Task(name={}, pid={}, prio={})".format(
        self.name, self.pid, self.prio,
        )

    def __eq__(self, other):
        """
        Compare by PID only. Prority is subject to change (dynamically)
        as is task name (post-fork).
        """
        if isinstance(other, Task):
            return True if other.pid == self.pid else False
        elif isinstance(other, integer_types):
            return True if other == self.pid else False

        raise ValueError('{type} not supported'.format(type(other)))

    def __hash__(self):
        # IMPORTANT: Don't hash by name or priority
        # as those are subject to change in runtime
       return hash((self.pid))

    def affinity(self):
        """Return affinity if any, None otherwise"""
        try:
            return int(self.name.split('/')[-1][0])
        except:
            return

##normal scheduling policies
##    range: 0
##    (SCHED_OTHER, SCHED_IDLE, SCHED_BATCH)
##
##real-time policies
##    range: 1(low) to 99(high)
##    (SCHED_FIFO, SCHED_RR)
##
##PRIORITY = 20 + NICE
##NICE : -20 (high) to (20)
