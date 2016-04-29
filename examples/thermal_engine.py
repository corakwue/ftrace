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
FILEPATH = r'C:\Users\c00759961\Documents\Charters\congitive-thermal-engine\res\AngryBirds-N6P-MMB29B.html'

FREQ_ALL_CORES = [0, 384000, 460800, 480000, 600000, 633600, 672000,
                 768000, 864000, 960000, 1248000,
                 1344000, 1440000, 1478400, 1536000, 1555200,
                 1632000, 1728000, 1824000, 1958400]

# Interval of interval, if None, looks at entire trace,
# Care only about 1s to 10s, then set to `Interval(1, 10)
INTERVAL = None
# Parses only .txt files in `PATH`
FILE_EXT = '.html'

THERMAL_TIMELINE_RESOLUTION = '200L' # Resample to this Milliseconds
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


def parse_file(filepath):
    trace = Ftrace(filepath, ['tsens_threshold_hit', 'tsens_read', 'tsens_threshold_clear', 'clock_set_rate'])
    return (filepath, trace)

if __name__ == '__main__':
    fp, trace = parse_file(FILEPATH)

    # duration
    total_duration = trace.duration if not INTERVAL else INTERVAL.duration

    # Thermal
    NAMES = [TSENS_ALIAS[tsens] for tsens in trace.thermal.names if tsens in TSENS_ALIAS] + CLKS
    df_therm = DataFrame(columns=NAMES)
    for tsens in trace.thermal.names:
        for therm in trace.thermal.temp_intervals(tsens=tsens, interval=INTERVAL):
            df_therm.loc[start + Micro(therm.interval.start*1e6), TSENS_ALIAS[tsens]] = therm.temp

    # lets look at clocks.
    for clk in CLKS:
        for freq_event in trace.clock.frequency_intervals(clock=clk, interval=INTERVAL):
            i_start=start + Micro(freq_event.interval.start*1e6)
            i_end=start + Micro(freq_event.interval.end*1e6)
            try:
                df_therm.loc[i_start:i_end, clk] = freq_event.frequency
            except KeyError:
                print "Error logging " + str(freq_event)
                df_therm[start + Micro(freq_event.interval.start*1e6):start + Micro(freq_event.interval.end*1e6), clk] = freq_event.frequency
        for clk_event in trace.clock.clock_intervals(clock=clk, state=ftrace.clock.ClockState.DISABLED, interval=INTERVAL):
            df_therm.loc[start + Micro(clk_event.interval.start*1e6): start + Micro(clk_event.interval.end*1e6), clk] = 0

    df_therm.sort(inplace=True)
    df_therm = df_therm.asfreq(THERMAL_TIMELINE_RESOLUTION, method='ffill').fillna(method='ffill').fillna(-1)
    df_therm.to_csv(r'{C:\Users\c00759961\Documents\Charters\congitive-thermal-engine\res\thermal_timeline.csv')
