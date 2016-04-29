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
# Version:    v1.0
#
# Purpose:    Frame Stats for Render Thread.
#             Represents actual formation/issuing of drawing commands to GPU
#
# Output:
#             frame_stats.csv - Frame stats 
#
# Author:      Chuk Orakwue <chuk.orakwue@huawei.com>

#------------------------------------------------------------------------------

import glob
import os
import sys
from pandas import Series, DataFrame
FTRACE_DIR = os.path.join(
    os.path.expanduser("~"),
    'Documents',
)
sys.path.append(FTRACE_DIR)
import ftrace
from ftrace import Ftrace, Interval

#**********************************
# Set BELOW
#**********************************
PATH = r'\\10.192.25.47\19. Power Team Room\HaoWang\DoU\MDA76\systrace'


# Interval of interval, if None, looks at entire trace,
# Care only about 1s to 10s, then set to `Interval(1, 10)
INTERVAL = None
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
    
    sb_all = DataFrame(columns=F_DICT.values())
    
    for _file in _files:
        
        fp, trace = parse_file(_file)

        total_duration = trace.duration if INTERVAL is None else INTERVAL
        ss = Series((event.interval.duration for event in trace.android.render_frame_intervals(interval=INTERVAL)))
        ss = ss * 1000. #
        summary = ss.describe()
        summary['90%'] = ss.quantile(.9)
        summary['Janks'] = trace.android.num_janks(interval=INTERVAL)
        summary['Janks Per Second'] = summary['Janks']/total_duration
        summary['Average FPS'] = trace.android.framerate(interval=INTERVAL)
        sb_all[F_DICT[fp]] = summary
    
    sb_all.to_csv(r'{path}\frame_stats.csv'.format(path=PATH))
        