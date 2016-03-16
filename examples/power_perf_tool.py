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
PATH = r'some_path'

FREQ_ALL_CORES = [0, 384000, 460800, 480000, 600000, 633600, 672000,
                 768000, 864000, 960000, 1248000,
                 1344000, 1440000, 1478400, 1536000, 1555200,
                 1632000, 1728000, 1824000, 1958400]

# Interval of interval, if None, looks at entire trace,
# Care only about 1s to 10s, then set to `Interval(1, 10)
INTERVAL = None
# Parses only .txt files in `PATH`
FILE_EXT = '.html'

THERMAL_TIMELINE_RESOLUTION = '500L' # Resample to every 100Milliseconds
#**********************************
# Set ABOVE
#**********************************

LITTLE_CLUSTER_MASK = 0x0F
BIG_CLUSTER_MASK = 0xF0

LITTLE_CPUS = ftrace.common.unpack_bitmap(LITTLE_CLUSTER_MASK)
BIG_CPUS = ftrace.common.unpack_bitmap(BIG_CLUSTER_MASK)
ALL_CPUS = LITTLE_CPUS.union(BIG_CPUS)

# Valid for 8994 only.
TSENS_ALIAS = {
    "tsens_tz_sensor2": "pop_mem",
    "tsens_tz_sensor6": "cpu7",
    "tsens_tz_sensor7": "cpu0",
    "tsens_tz_sensor8": "cpu1",
    "tsens_tz_sensor9": "cpu2",
    "tsens_tz_sensor10": "cpu3",
    "tsens_tz_sensor12": "gpu",
    "tsens_tz_sensor13": "cpu4",
    "tsens_tz_sensor14": "cpu5",
    "tsens_tz_sensor15": "cpu6",
}

start = Timestamp('1/1/1970')

CLKS =['a57_clk', 'a53_clk', 'oxili_gfx3d_clk']

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
    #pool = Pool(1)
    #results = pool.map(, _files)

    # Multi-core usage
    sb_all = DataFrame(columns=ALL_CPUS)
    arrays = [['BIG']*5 + ['LITTLE']*5, range(5) + range(5)]
    multi_index = MultiIndex.from_tuples(list(zip(*arrays)), names=['cluster', 'num_cores'])
    sb_by_cluster = DataFrame(index=multi_index)

    for _file in _files:
        fp, trace = parse_file(_file)
        # duration
        total_duration = trace.duration if not INTERVAL else INTERVAL.duration

        # Freq
        df_freq = DataFrame( index = ALL_CPUS, columns=FREQ_ALL_CORES)
        df_freq.fillna(0, inplace=True)

        # LPM
        LPM_states = {-1: 'Busy', 0: 'WFI', 1: 'Retention', 2: 'SPC (GDHS)', 3: 'PC'}
        df_lpm = DataFrame( index=ALL_CPUS, columns= LPM_states.values())
        df_lpm.fillna(0, inplace=True)

        # CLock Active
        df_clk = DataFrame(index=trace.clock.names, columns = [0, 'UNKNOWN'])
        df_clk.fillna(0, inplace=True)

#        # Bus Request Intervals
#        # TODO
#        df_bus = DataFrame(index=trace.bus.names, columns = [0, 'UNKNOWN'])
#        df_bus.fillna(0, inplace=True)

#        # Cluster
#        # TODO
#        df_cluster = DataFrame(index=trace.cluster.names, columns=trace.cluster.BusyState.universe())
#        df_cluster.fillna(0, inplace=True)

        for cpu in range(8): # assumes 8-cores!
            for busy_interval in trace.cpu.busy_intervals(cpu=cpu, interval=INTERVAL):
                freq_cpu = 0 if cpu in LITTLE_CPUS else 4 # same cluster, same freq.
                for freq in trace.cpu.frequency_intervals(cpu=freq_cpu, interval=busy_interval.interval):
                    df_freq.loc[cpu, freq.frequency] += freq.interval.duration
            df_freq.loc[cpu, 0] = trace.cpu.lpm_time(cpu=cpu, interval=INTERVAL)

            # top tasks
            df_tasks = DataFrame(columns=['Name', 'PID', 'Priority', 'Exec Time (s)'])
            for task in trace.cpu.seen_tasks(cpu=cpu):
                if task.pid != 0:
                    df_tasks.loc[task.pid] = [task.name,
                        task.pid, task.prio,
                            trace.cpu.task_time(task=task, cpu=cpu,
                                                interval=INTERVAL)]
            busy_time = trace.cpu.busy_time(cpu=cpu, interval=INTERVAL)
            if busy_time != 0.0:
                df_tasks['Exec Time %'] = df_tasks['Exec Time (s)'] / busy_time
            df_tasks.sort(['Exec Time (s)'], inplace=True, ascending=False)
            df_tasks.set_index('PID', inplace=True)
            df_tasks.to_csv(r'{path}\{fp}_top_tasks_cpu{cpu}.csv'.format(path=PATH,
                                                                         fp=F_DICT[fp], cpu=cpu))

        df_freq = df_freq / total_duration
        df_freq.to_csv(r'{path}\{fp}_cpu_freq_dist.csv'.format(path=PATH, fp=F_DICT[fp]))

        for cpu in range(8):
            for lpm in trace.cpu.lpm_intervals(cpu=cpu, interval=INTERVAL):
                df_lpm.loc[cpu, LPM_states[lpm.state]] += lpm.interval.duration
            # accounting for time in idle loop.
            df_lpm.loc[cpu, 'Busy'] = total_duration - df_lpm.loc[cpu].sum()

        df_lpm = df_lpm / total_duration
        df_lpm.to_csv(r'{path}\{fp}_lpm_dist.csv'.format(path=PATH, fp=F_DICT[fp]))

        # Multi-core usage
        sb_all.loc[trace.filename] = sim_busy_all_clusters(trace)
        big_sim_usage = sim_busy_by_clusters(trace, cpus=BIG_CPUS)
        little_sim_usage = sim_busy_by_clusters(trace, cpus=LITTLE_CPUS)
        merged = big_sim_usage.append(little_sim_usage)
        merged.index = multi_index
        sb_by_cluster[trace.filename] = merged

        sb_by_cluster.T.to_csv(r'{path}\{fp}_summary_by_cluster.csv'.format(path=PATH, fp=F_DICT[fp]))
        sb_all.to_csv(r'{path}\{fp}_summary_all_cluster.csv'.format(path=PATH, fp=F_DICT[fp]))

        for clk in trace.clock.names:
            for clk_event in trace.clock.clock_intervals(clock=clk, state=ftrace.clock.ClockState.ENABLED, interval=INTERVAL):
                for freq_event in trace.clock.frequency_intervals(clock=clk, interval=clk_event.interval):
                    freq = 'UNKNOWN' if freq_event.frequency == -1 else freq_event.frequency
                    if not freq in df_clk.columns:
                      df_clk[freq] = 0 # assign it
                    df_clk.loc[clk, freq] += freq_event.interval.duration

            for clk_event in trace.clock.clock_intervals(clock=clk, state=ftrace.clock.ClockState.DISABLED, interval=INTERVAL):
                df_clk.loc[clk, 0] += clk_event.interval.duration

            if df_clk.loc[clk].sum() != total_duration: # unaccounted.
                df_clk.loc[clk, 'UNKNOWN'] = total_duration - df_clk.loc[clk].sum()

        df_clk = df_clk / total_duration
        df_clk.sort(axis=1, inplace=True)
        df_clk.to_csv(r'{path}\{fp}_clocks.csv'.format(path=PATH, fp=F_DICT[fp]))

        # Thermal
#        NAMES = [TSENS_ALIAS[tsens] for tsens in trace.thermal.names if tsens in TSENS_ALIAS] + CLKS
#        df_therm = DataFrame(columns=NAMES)
#        #index=period_range(start=start, end=end, freq='1U')
#        for tsens in trace.thermal.names:
#            for therm in trace.thermal.temp_intervals(tsens=tsens, interval=INTERVAL):
#                df_therm.loc[start + Micro(therm.interval.start*1e6), TSENS_ALIAS[tsens]] = therm.temp
#
#        # lets look at clocks.
#        for clk in CLKS:
#            for freq_event in trace.clock.frequency_intervals(clock=clk, interval=INTERVAL):
#                df_therm.loc[start + Micro(freq_event.interval.start*1e6):start + Micro(freq_event.interval.end*1e6), clk] = freq_event.frequency
#
#            for clk_event in trace.clock.clock_intervals(clock=clk, state=ftrace.clock.ClockState.DISABLED, interval=INTERVAL):
#                df_therm.loc[start + Micro(clk_event.interval.start*1e6): start + Micro(clk_event.interval.end*1e6), clk] = 0
#
#        df_therm.sort(inplace=True)
#        df_therm = df_therm.asfreq(THERMAL_TIMELINE_RESOLUTION, method='ffill').fillna(method='ffill').fillna(-1)
#        df_therm.to_csv(r'{path}\{fp}_thermal_timeline.csv'.format(path=PATH, fp=F_DICT[fp]))
