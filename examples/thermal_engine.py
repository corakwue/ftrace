import glob
import os
import sys
from pandas import Series, DataFrame, MultiIndex, Timestamp
from pandas.tseries.offsets import Micro
import ftrace
from ftrace import Ftrace, Interval


THERMAL_TIMELINE_RESOLUTION = '200L' # Resample to this Milliseconds


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

CLKS =['a57_clk', 'a53_clk', 'oxili_gfx3d_clk']

start = Timestamp('1/1/1970')


if __name__ == '__main__':

    trace = Ftrace(filepath, ['tsens_threshold_hit', 'tsens_read', 'tsens_threshold_clear', 'clock_set_rate'])

    # duration
    total_duration = trace.duration

    # Thermal
    NAMES = [TSENS_ALIAS[tsens] for tsens in trace.thermal.names if tsens in TSENS_ALIAS] + CLKS
    df_therm = DataFrame(columns=NAMES)
    for tsens in trace.thermal.names:
        for therm in trace.thermal.temp_intervals(tsens=tsens, interval=None):
            df_therm.loc[start + Micro(therm.interval.start*1e6), TSENS_ALIAS[tsens]] = therm.temp

    # lets look at clocks.
    for clk in CLKS:
        for freq_event in trace.clock.frequency_intervals(clock=clk, interval=None):
            i_start=start + Micro(freq_event.interval.start*1e6)
            i_end=start + Micro(freq_event.interval.end*1e6)
            try:
                df_therm.loc[i_start:i_end, clk] = freq_event.frequency
            except KeyError:
                print "Error logging " + str(freq_event)
                df_therm[start + Micro(freq_event.interval.start*1e6):start + Micro(freq_event.interval.end*1e6), clk] = freq_event.frequency
        for clk_event in trace.clock.clock_intervals(clock=clk, state=ftrace.clock.ClockState.DISABLED, interval=None):
            df_therm.loc[start + Micro(clk_event.interval.start*1e6): start + Micro(clk_event.interval.end*1e6), clk] = 0

    df_therm.sort(inplace=True)
    df_therm = df_therm.asfreq(THERMAL_TIMELINE_RESOLUTION, method='ffill').fillna(method='ffill').fillna(-1)
    df_therm.to_csv(r'thermal_timeline.csv')
