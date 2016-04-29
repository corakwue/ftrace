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
# Purpose:     Analyze touch latencies
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
PATH = r'\\10.192.25.47\19. Power Team Room\HaoWang\DoU\MDA76\systrace\archive'

TOUCH_IRQ = 'irq/503-synapti'
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
    
    sb_all = DataFrame()
    
    for _file in _files:
        
        fp, trace = parse_file(_file)

        total_duration = trace.duration if INTERVAL is None else INTERVAL
        ss = Series((event.interval.duration * 1000 for event in trace.android.input_latencies(TOUCH_IRQ, interval=INTERVAL)))
        summary = ss.describe()
        summary['90%'] = ss.quantile(.9)
        summary['Janks Per Second'] = trace.android.jankrate(interval=INTERVAL)
        summary['Average FPS'] = trace.android.framerate(interval=INTERVAL)
        
        ss_first = Series((event.interval.duration * 1000 for event in trace.android.input_latencies(TOUCH_IRQ, interval=INTERVAL) if trace.cpu.frequency_intervals(cpu=0, interval=event.interval) and  trace.cpu.frequency_intervals(cpu=0, interval=event.interval)[0] == 384000))
        summary_first = ss_first.describe()
        summary_first['90%'] = ss_first.quantile(.9)
        summary_first['Janks Per Second'] = summary['Janks Per Second']
        summary_first['Average FPS'] = summary['Average FPS']
        
#        ss_rendering = Series((event.interval.duration * 1000 for event in trace.android.rendering_intervals(interval=INTERVAL)))
#        summary_ri = ss_rendering.describe()
#        summary_ri['90%'] = ss_rendering.quantile(.9)
#        #summary_ri['Janks Per Second'] = summary['Janks Per Second']
#        #summary_ri['Average FPS'] = summary['Average FPS']
        
        sb_all[F_DICT[fp]+'all'] = summary
        sb_all[F_DICT[fp]+'first'] = summary_first
#        sb_all[F_DICT[fp]+'rendering_interval'] = summary_ri
        
#        interaction_boost_delay = []
#        for event in trace.android.input_latencies(TOUCH_IRQ, interval=INTERVAL):
#            interaction_boost = False
#            for freq_event in trace.cpu.frequency_intervals(cpu=0, interval=event.interval):
#                if not freq_event.interval.start > event.interval.start:
#                    continue
#                elif freq_event.frequency == 1248000:
#                    interaction_boost = True
#                    break
#                
#            if interaction_boost:
#                interaction_boost_delay.append((freq_event.interval.start - event.interval.start) * 1000)
#                
#        boost_delay = Series(interaction_boost_delay)
#        summary_boost_delay = boost_delay.describe()
#        summary_boost_delay['90%'] = boost_delay.quantile(.9)
#        
#        sb_all[F_DICT[fp]+'boost_delay'] = summary_boost_delay
    
    sb_all.to_csv(r'{path}\input_latencies_stats.csv'.format(path=PATH))