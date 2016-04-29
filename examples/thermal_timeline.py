import ftrace
from ftrace import Ftrace
from pandas import DataFrame, Timestamp
from pandas.tseries.offsets import Micro

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

trace = Ftrace(r'C:\Users\c00759961\Documents\temp\nina-MDA35B-camera-UHD-recording-after.html', 
               ['tsens_read', 'tsens_threshold_clear', 'tsens_threshold_hit', 
                'clock_set_rate', 'clock_enable', 'clock_disable'])
   
start = Timestamp('1/1/1970')
#end = start + Second(trace.duration)

NAMES = [TSENS_ALIAS[tsens] for tsens in trace.thermal.names if tsens in TSENS_ALIAS] + CLKS
df_therm = DataFrame(columns=NAMES)
#index=period_range(start=start, end=end, freq='1U')
for tsens in trace.thermal.names:
    for therm in trace.thermal.temp_intervals(tsens=tsens):
        df_therm.loc[start + Micro(therm.interval.end*1e6), TSENS_ALIAS[tsens]] = therm.temp

# lets look at clocks.
for clk in CLKS:
    for freq_event in trace.clock.frequency_intervals(clock=clk):
        df_therm.loc[start + Micro(freq_event.interval.end*1e6), clk] = freq_event.frequency

    for clk_event in trace.clock.clock_intervals(clock=clk, 
                                                 state=ftrace.clock.ClockState.DISABLED):
        df_therm.loc[start + Micro(clk_event.interval.end*1e6), clk] = 0
        
df_therm.sort(inplace=True)
# Resample to every 100milliseconds
df_therm = df_therm.asfreq('100L', method='ffill').fillna(method='ffill').fillna(-1)
df_therm.to_csv(r'C:\Users\c00759961\Documents\temp\nina-MDA35B-camera-UHD-recording-after-thermal-timeline.csv')