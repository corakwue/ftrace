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
#             Find migrations that caused:
#                   - already idle cluster to wakeup
#                   - cluster to increase its OOP
#
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
    'ftrace',
)
sys.path.append(FTRACE_DIR)
import ftrace
from ftrace import Ftrace

#**********************************
# Set BELOW
#**********************************
PATH = r'some_path'


# Interval of interval, if None, looks at entire trace,
# Care only about 1s to 10s, then set to `Interval(1, 10)
INTERVAL = None
# Parses only .txt files in `PATH`
FILE_EXT = '.html'

#**********************************
# Set ABOVE
#**********************************

LITTLE_CLUSTER_MASK = 0x0F
BIG_CLUSTER_MASK = 0xF0

LITTLE_CPUS = ftrace.common.unpack_bitmap(LITTLE_CLUSTER_MASK)
BIG_CPUS = ftrace.common.unpack_bitmap(BIG_CLUSTER_MASK)
ALL_CPUS = LITTLE_CPUS.union(BIG_CPUS)


def parse_file(filepath):
    trace = Ftrace(filepath, tracepoints='sched_hmp_migrate')
    return (filepath, trace)

if __name__ == '__main__':
    _files = glob.glob(r'{path}\*{file_ext}'.format(path=PATH, file_ext=FILE_EXT))
    F_DICT = {_fp: os.path.split(_fp)[1].split('.')[0] for _fp in _files}

    for _file in _files:
        fp, trace = parse_file(_file)

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
