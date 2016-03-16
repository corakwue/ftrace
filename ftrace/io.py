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
    DiskIOType: Possible disk I/Os
    DiskCommand: Disk commands
"""
from collections import namedtuple
from .common import ConstantBase


class DiskIOType(ConstantBase):
    DISCARD = ()
    WRITE = ()
    READ = ()
    NONE = ()

class DiskCommand(ConstantBase):
    FUA = () # Forced Unit Access
    AHEAD = ()
    SYNC = ()
    META = ()
    FLUSH = ()

DiskIOTypeMapping = {
    'D': DiskIOType.DISCARD,
    'W': DiskIOType.WRITE,
    'R': DiskIOType.READ,
    'N': DiskIOType.NONE,
}


DiskCommandMapping = {
    'F': DiskCommand.FUA,
    'A': DiskCommand.AHEAD,
    'S': DiskCommand.SYNC,
    'M': DiskCommand.META
}

RWBS = namedtuple('RWBS', ['io_type', 'commands'])