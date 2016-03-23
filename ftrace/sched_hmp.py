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


from .common import ConstantBase
from collections import defaultdict

class HMPMigrate(ConstantBase):

##    When a task that was previously idle becomes ready to run,
##    the scheduler needs to decide which processor will execute the task.
##    To choose between big and LITTLE cores, the ARM MP solution uses the
##    tracked load history of a task.

    WAKEUP = ()

##    Fork migration operates when the fork system call is used to ceate a new
##    software thread. At this point, clearly no historical load
##    information is available ? the thread is new.
##    The system defaults to a big core for new threads on the assumption that
##    a ?light? thread will quickly migrate down to a LITTLE core as a result
##    of wake migration
    FORCE = ()

##    The big.LITTLE MP solution requires that normal scheduler
##    load balancing be disabled. The downside of this is that long-running
##    threads can concentrate on the big cores, leaving the LITTLE cores
##    idle and under-utilized. Overal system performance, in this situation,
##    can clearly be improved by utilizing all the cores.
##    Offload migration works to peridically migrate threads downwards
##    to LITTLE cores to make use of unused compute capacity.
##    Threads which are migrated downwards in this way remain candidates for
##    up migration if they exceed the threshold at next scheduling opportunity

    OFFLOAD = ()

##    Idle Pull Migration is designed to make best use of active big cores.
##    When a big core has no task to run, a check is made on
##    all LITTLE cores to see if a currently running task on a
##    LITTLE core has a higher load metric that the up migration threshold.
##    Such a task can then be immediately migrated to the idle big core.
##    If no suitable task is found, then the big core can be powered down.

    IDLE_PULL = ()

## What is this?
    UNKNOWN = ()

# linux/sched.h
# /trace/events/sched.h
HMPMigrateMapping = defaultdict(lambda: HMPMigrate.UNKNOWN)
state_dict = {
    0 : HMPMigrate.WAKEUP,
    1 : HMPMigrate.FORCE,
    2 : HMPMigrate.OFFLOAD,
    3 : HMPMigrate.IDLE_PULL,
}

HMPMigrateMapping.update(state_dict)