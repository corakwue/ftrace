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
# Purpose:     Report app launch times.
#
# Author:      Chuk Orakwue <chuk.orakwue@huawei.com>

#------------------------------------------------------------------------------

import glob
import os
import sys
from pandas import DataFrame
FTRACE_DIR = os.path.join(
    os.path.expanduser("~"),
    'Documents',
)
sys.path.append(FTRACE_DIR)
import ftrace
from ftrace import Ftrace

#**********************************
# Set BELOW
#**********************************
PATH = r'Z:\HaoWang\App_Launching_Time\After'

# Parses only .txt files in `PATH`
FILE_EXT = '.html'
#**********************************
# Set ABOVE
#**********************************

def parse_file(filepath):
    trace = Ftrace(filepath)
    return (filepath, trace)

if __name__ == '__main__':
    _files = glob.glob(r'{path}\*{file_ext}'.format(path=PATH, file_ext=FILE_EXT))
    F_DICT = {_fp: os.path.split(_fp)[1].split('.')[0] for _fp in _files}
    APPS = set(value.split('_')[0] for value in F_DICT.values())
    COLUMNS = set(int(value.split('_')[-1]) for value in F_DICT.values())
    ll = DataFrame(index=APPS, columns=COLUMNS)
    
    #pool = Pool(4)
    #results = pool.map(parse_file, _files)

    # Create dataframe with median of launch time.
    for _file in _files:
        try:
            _, trace = parse_file(_file)
            split = F_DICT[_file].split('_')
            ll.loc[split[0], int(split[-1])] = trace.android.app_launch_latencies()[0].interval.duration
        except:
            pass
    #ll.median(axis=1).to_csv(r'{path}\launch_latencies.csv'.format(path=PATH))