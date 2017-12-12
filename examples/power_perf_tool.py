import glob
import os
import sys
import ftrace
from ftrace import Ftrace, Interval
from pandas import Series, DataFrame, MultiIndex, Timestamp
from pandas.tseries.offsets import Micro


LITTLE_CLUSTER_MASK = 0x0F
BIG_CLUSTER_MASK = 0xF0

LITTLE_CPUS = ftrace.common.unpack_bitmap(LITTLE_CLUSTER_MASK)
BIG_CPUS = ftrace.common.unpack_bitmap(BIG_CLUSTER_MASK)
ALL_CPUS = LITTLE_CPUS.union(BIG_CPUS)


def sim_busy_all_clusters(trace):
    """
    Returns DataFrame of simultaneously busy cores irrespectively of cluster.
    """
    data = {num_cores: trace.cpu.simultaneously_busy_time(num_cores, interval=None) for num_cores in xrange(len(ALL_CPUS)+1)}
    total_duration = trace.duration if not INTERVAL else INTERVAL.duration
    return Series(data=data.values(), index=data.keys(), name=trace.filename) / total_duration

def sim_busy_by_clusters(trace, cpus):
    """
    Returns Series of simultaneously busy cores per `cpus` in cluster.
    """
    data = {num_cores: trace.cpu.simultaneously_busy_time(num_cores, cpus=list(cpus), interval=None) for num_cores in xrange(len(cpus)+1)}
    total_duration = trace.duration if not INTERVAL else INTERVAL.duration
    return Series(data=data.values(), index=data.keys(), name=trace.filename) / total_duration

def parse_file(filepath):
    trace = Ftrace(filepath)
    return (filepath, trace)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Power/Performance analysis of HMP platforms!')

    parser.add_argument('-f', '--file', dest='file',
                        help='File (systrace/ftrace log) to parse')

    args = parser.parse_args()


    # Multi-core usage
    sb_all = DataFrame(columns=ALL_CPUS)
    arrays = [['BIG']*5 + ['LITTLE']*5, range(5) + range(5)]
    multi_index = MultiIndex.from_tuples(list(zip(*arrays)), names=['cluster', 'num_cores'])
    sb_by_cluster = DataFrame(index=multi_index)

    trace = Ftrace(args.file)
    total_duration = trace.duration

    # Freq
    df_freq = DataFrame(index = ALL_CPUS)
    df_freq.fillna(0, inplace=True)

    # LPM
    LPM_states = {-1: 'Busy', 0: 'WFI', 1: 'Retention', 2: 'SPC (GDHS)', 3: 'PC'}
    df_lpm = DataFrame( index=ALL_CPUS, columns= LPM_states.values())
    df_lpm.fillna(0, inplace=True)

    # CLock Active
    df_clk = DataFrame(index=trace.clock.names, columns = [0, 'UNKNOWN'])
    df_clk.fillna(0, inplace=True)


    for cpu in ALL_CPUS: # assumes 8-cores
        # top tasks
        df_tasks = DataFrame(columns=['Name', 'PID', 'Priority', 'Exec Time (s)'])
        for task in trace.cpu.seen_tasks(cpu=cpu):
            if task.pid != 0:
                df_tasks.loc[task.pid] = [task.name,
                    task.pid, task.prio,
                        trace.cpu.task_time(task=task, cpu=cpu,
                                            interval=None)]
        busy_time = trace.cpu.busy_time(cpu=cpu, interval=None)
        if busy_time != 0.0:
            df_tasks['Exec Time %'] = df_tasks['Exec Time (s)'] / busy_time
        df_tasks.sort(['Exec Time (s)'], inplace=True, ascending=False)
        df_tasks.set_index('PID', inplace=True)
        df_tasks.to_csv(r'top_tasks_cpu{cpu}.csv'.format(cpu=cpu))


    for cpu in range(8):
        for lpm in trace.cpu.lpm_intervals(cpu=cpu, interval=None):
            df_lpm.loc[cpu, LPM_states[lpm.state]] += lpm.interval.duration
        # accounting for time in idle loop.
        df_lpm.loc[cpu, 'Busy'] = total_duration - df_lpm.loc[cpu].sum()

    df_lpm = df_lpm / total_duration
    df_lpm.to_csv(r'lpm_dist.csv')

    # Multi-core usage
    sb_all.loc[trace.filename] = sim_busy_all_clusters(trace)
    big_sim_usage = sim_busy_by_clusters(trace, cpus=BIG_CPUS)
    little_sim_usage = sim_busy_by_clusters(trace, cpus=LITTLE_CPUS)
    merged = big_sim_usage.append(little_sim_usage)
    merged.index = multi_index
    sb_by_cluster[trace.filename] = merged

    sb_by_cluster.T.to_csv(r'summary_by_cluster.csv')
    sb_all.to_csv(r'summary_all_cluster.csv')

    for clk in trace.clock.names:
        for clk_event in trace.clock.clock_intervals(clock=clk, state=ftrace.clock.ClockState.ENABLED, interval=None):
            for freq_event in trace.clock.frequency_intervals(clock=clk, interval=clk_event.interval):
                freq = 'UNKNOWN' if freq_event.frequency == -1 else freq_event.frequency
                if not freq in df_clk.columns:
                  df_clk[freq] = 0 # assign it
                df_clk.loc[clk, freq] += freq_event.interval.duration

        for clk_event in trace.clock.clock_intervals(clock=clk, state=ftrace.clock.ClockState.DISABLED, interval=None):
            df_clk.loc[clk, 0] += clk_event.interval.duration

        if df_clk.loc[clk].sum() != total_duration: # unaccounted.
            df_clk.loc[clk, 'UNKNOWN'] = total_duration - df_clk.loc[clk].sum()

    df_clk = df_clk / total_duration
    df_clk.sort(axis=1, inplace=True)
    df_clk.to_csv(r'clocks.csv')
