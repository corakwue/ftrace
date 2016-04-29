# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 13:43:21 2016

@author: c00759961
"""
import os
import glob
import ftrace
from ftrace import Ftrace
from pandas import Series
from collections import defaultdict

PATH = r'Z:\EAS\Mate8_Default'

# Interval of interval, if None, looks at entire trace,
# Care only about 1s to 10s, then set to `Interval(1, 10)
INTERVAL = None
# Parses only .txt files in `PATH`
FILE_EXT = '.html'

LITTLE_CLUSTER_MASK = 0x0F
BIG_CLUSTER_MASK = 0xF0

LITTLE_CPUS = ftrace.common.unpack_bitmap(LITTLE_CLUSTER_MASK)
BIG_CPUS = ftrace.common.unpack_bitmap(BIG_CLUSTER_MASK)
ALL_CPUS = LITTLE_CPUS.union(BIG_CPUS)
        
def parse_file(filepath):
    trace = Ftrace(filepath)
    return (filepath, trace)

def sim_busy_times(trace, cpus, interval):
    data = {num_cores: trace.cpu.simultaneously_busy_time(num_cores, cpus=list(cpus), interval=INTERVAL) for num_cores in xrange(len(cpus)+1)}
    total_duration = trace.duration if not INTERVAL else INTERVAL.duration
    return Series(data=data.values(), index=data.keys(), name=trace.filename) / total_duration

_files = glob.glob(r'{path}\*{file_ext}'.format(path=PATH, file_ext=FILE_EXT))
F_DICT = {_fp: os.path.split(_fp)[1].split('.')[0] for _fp in _files}

little_idle_dict = defaultdict(list)
big_idle_dict = defaultdict(list)
    
for _file in _files:
    fp, trace = parse_file(_file)

    for cpu in ALL_CPUS:
        for item in trace.cpu.lpm_intervals(cpu=cpu, interval=INTERVAL):
            if item.cpu in BIG_CPUS:
                big_idle_dict[item.state].append(item.interval.duration)
            elif item.cpu in LITTLE_CPUS:
                little_idle_dict[item.state].append(item.interval.duration)
    

for k, v in little_idle_dict.iteritems():
    results = Series(v)*1e6
    results.to_csv(r'{path}\LITTLE_C{idx}.csv'.format(path=PATH, idx=k))

for k, v in big_idle_dict.iteritems():
    results = Series(v)*1e6
    results.to_csv(r'{path}\BIG_C{idx}.csv'.format(path=PATH, idx=k))