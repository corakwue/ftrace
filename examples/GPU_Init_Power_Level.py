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
# Purpose:    Power/Performance analysis of HMP platforms!
#
# Output:
#             *_clocks.csv - Clock residency %
#             *_summary_all_cluster.csv - Concuurently busy CPU irrespective of cluster
#             *_summary_by_cluster.csv - Concuurently busy CPU grouped by cluster
#             *_lpm_dist.csv - LPM residency per core %
#             *_freq_dist.csv - Frequency residency per core %
#
# todo: Add top-tasks per core, bus requenct intervals, cluster LPM states
#
# Author:      Chuk Orakwue <chuk.orakwue@huawei.com>

#------------------------------------------------------------------------------

import glob
import os
import sys
from pandas import Series, DataFrame, MultiIndex, Timestamp
from pandas.tseries.offsets import Micro
#from multiprocessing import Pool
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
PATH = r'C:\Users\c00759961\Documents\temp'

FREQ_ALL_CORES = [0, 384000, 460800, 480000, 600000, 633600, 672000,
                 768000, 864000, 960000, 1248000,
                 1344000, 1440000, 1478400, 1536000, 1555200,
                 1632000, 1728000, 1824000, 1958400]

# Interval of interval, if None, looks at entire trace,
# Care only about 1s to 10s, then set to `Interval(1, 10)
INTERVAL = None
# Parses only .txt files in `PATH`
FILE_EXT = '.html'

THERMAL_TIMELINE_RESOLUTION = '100L' # Resample to every 100Milliseconds
#**********************************
# Set ABOVE
#**********************************

LITTLE_CLUSTER_MASK = 0x0F
BIG_CLUSTER_MASK = 0xF0

LITTLE_CPUS = ftrace.common.unpack_bitmap(LITTLE_CLUSTER_MASK)
BIG_CPUS = ftrace.common.unpack_bitmap(BIG_CLUSTER_MASK)
ALL_CPUS = LITTLE_CPUS.union(BIG_CPUS)


def sim_busy_all_clusters(trace):
    """
    Returns DataFrame of simultaneously busy cores irrespectively of cluster.
    """
    data = {num_cores: trace.cpu.simultaneously_busy_time(num_cores, interval=INTERVAL) for num_cores in xrange(len(ALL_CPUS)+1)}
    total_duration = trace.duration if not INTERVAL else INTERVAL.duration
    return Series(data=data.values(), index=data.keys(), name=trace.filename) / total_duration

def sim_busy_by_clusters(trace, cpus):
    """
    Returns Series of simultaneously busy cores per `cpus` in cluster.
    """
    data = {num_cores: trace.cpu.simultaneously_busy_time(num_cores, cpus=list(cpus), interval=INTERVAL) for num_cores in xrange(len(cpus)+1)}
    total_duration = trace.duration if not INTERVAL else INTERVAL.duration
    return Series(data=data.values(), index=data.keys(), name=trace.filename) / total_duration

def parse_file(filepath):
    trace = Ftrace(filepath)
    return (filepath, trace)

if __name__ == '__main__':
    _files = glob.glob(r'{path}\*{file_ext}'.format(path=PATH, file_ext=FILE_EXT))
    F_DICT = {_fp: os.path.split(_fp)[1].split('.')[0] for _fp in _files}
    
    # Multi-core usage
    sb_all = DataFrame(columns=ALL_CPUS)
    arrays = [['BIG']*5 + ['LITTLE']*5, range(5) + range(5)]
    multi_index = MultiIndex.from_tuples(list(zip(*arrays)), names=['cluster', 'num_cores'])
    sb_by_cluster = DataFrame(index=multi_index)

    for _file in _files:
        fp, trace = parse_file(_file)

        # Freq
        df_clk = DataFrame(columns=FREQ_ALL_CORES)
        df_clk.fillna(0, inplace=True)

        total_duration = 0.0
        for slumber_event in trace.gpu.pwrstate_intervals(device='kgsl-3d0', state=ftrace.gpu.BusyState.SLUMBER):
            post_slumber = Interval(slumber_event.interval, trace.duration)
            next_events = trace.gpu.pwrstate_intervals(device='kgsl-3d0', state=ftrace.gpu.BusyState.ACTIVE, interval=post_slumber)
            if next_events:
                post_se = next_events[0]
            end = input_event.interval.start + 0.08
            interval = Interval(input_event.interval.start + 0.04, end)
            total_duration += interval.duration
            for clk_event in trace.clock.clock_intervals(clock='a53_clk', state=ftrace.clock.ClockState.ENABLED, interval=interval):
                for freq_event in trace.clock.frequency_intervals(clock='a53_clk', interval=clk_event.interval):
                    freq = 'UNKNOWN' if freq_event.frequency == -1 else freq_event.frequency
                    if not freq in df_clk.columns:
                      df_clk[freq] = 0 # assign it
                    df_clk.loc[fp, freq] += freq_event.interval.duration

            if df_clk.loc[fp].sum() != total_duration: # unaccounted.
                df_clk.loc[fp, 'UNKNOWN'] = total_duration - df_clk.loc[fp].sum()

        df_clk.ix[fp] = df_clk.ix[fp] / total_duration
    
    df_clk.sort(axis=1, inplace=True)
    df_clk.to_csv(r'input_clocks.csv')
    
    jps = trace.android.num_janks()/trace.duration
    # Also dump framestats
    # Chuck to share
        