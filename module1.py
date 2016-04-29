import ftrace
from ftrace import Ftrace
from pandas import DataFrame

LITTLE_CLUSTER_MASK = 0x0F
BIG_CLUSTER_MASK = 0xF0

FREQ_ALL_CORES = [0, 480000, 807000, 1018000, 1210000, 1306000,
                  1517000, 1805000, 2016000, 2304000, 2515000]

LITTLE_CPUS = ftrace.common.unpack_bitmap(LITTLE_CLUSTER_MASK)
BIG_CPUS = ftrace.common.unpack_bitmap(BIG_CLUSTER_MASK)
ALL_CPUS = LITTLE_CPUS.union(BIG_CPUS)

# processing scripts for each file in directory
trace = Ftrace(r'Z:\EAS\Mate8_Default\music1.html')

df_freq = DataFrame( index = ALL_CPUS, columns=FREQ_ALL_CORES)
df_freq.fillna(0, inplace=True)
for cpu in range(8):
    for busy_interval in trace.cpu.busy_intervals(cpu=cpu):
        print "busy: " + str(busy_interval)
        for freq in trace.cpu.frequency_intervals(cpu=cpu, interval=busy_interval.interval):
            print "freq: " + str(freq)
            df_freq.loc[cpu, freq.frequency] += freq.interval.duration