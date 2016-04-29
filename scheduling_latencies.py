import glob
import os
import sys
import ftrace
from ftrace import Ftrace
from pandas import DataFrame
from ftrace.task import TaskState


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

# processing scripts for each file in directory
PATH = r'Z:\EAS\Mate8_Default'

"""
Scheduling latency accounts for waking tasks (due to placement)
and that due to forced migration of already runnable/running task.

migration_type:
---------------
    0   :   Intra
    1   :   Inter
    
Useful to tune sched_migration_cost for HMP system.
We want to account for scheduling cost in evaluating whether to migrate a task.
""" 

def parse_file(filepath):
    trace = Ftrace(filepath)
    return (filepath, trace)

def sched_latencies(trace):
    """
    Scheduling latencies.
    """
    df = DataFrame(columns=['task_prio', 'latency', 'dest_cpu_rq_length', #'dest_cpu_rq_prios',
                            'src_cpu_freq', 'dest_cpu_freq', 'dest_cpu_idle_state', 'migration_type'])
    
    row_count = 0
    consider_for_latency = set((TaskState.RUNNABLE, TaskState.RUNNING, TaskState.TASK_WAKING))
    runnables = set((TaskState.RUNNABLE, TaskState.RUNNING))
    
    for task in trace.cpu.seen_tasks():
        if task.pid == 0:
            continue
        task_intervals = trace.cpu.task_intervals(task=task)
        last_task_interval = None
        #print "Analyzing task: {task}".format(task=task)
        for current_task_interval in task_intervals:
            
            if last_task_interval is not None and current_task_interval.cpu != last_task_interval.cpu:
                if last_task_interval.state not in consider_for_latency or \
                    current_task_interval.state not in runnables:
                    continue
                # if is waking
                task_prio = current_task_interval.task.prio
                latency = current_task_interval.interval.start - last_task_interval.interval.end
                
                if latency < 0:
                    print "Error, latency is {latency}ms".format(latency=latency*1e6)
                
                rq_lengths = []
                for rqi in trace.cpu.runqueue_depth_intervals(cpu=current_task_interval.cpu, interval=last_task_interval.interval):
                    rq_lengths.append(rqi.runnable)
                dest_cpu_rq_length = sum(rq_lengths)/len(rq_lengths) if rq_lengths else -1
                
    #            dest_cpu_rq_prios = []
    #            for ti in trace.cpu.task_intervals(cpu=current_task_interval.cpu,
    #                                               interval=last_task_interval.interval):
    #                dest_cpu_rq_prios.append(ti.task.prio)
                
                cpu_freq = []
                for freq in trace.cpu.frequency_intervals(cpu=last_task_interval.cpu, interval=last_task_interval.interval):
                    cpu_freq.append(freq.frequency)
                src_cpu_freq = sum(cpu_freq)/len(cpu_freq) if cpu_freq else -1
                
                cpu_freq = []
                for freq in trace.cpu.frequency_intervals(cpu=current_task_interval.cpu, interval=current_task_interval.interval):
                    cpu_freq.append(freq.frequency)
                dest_cpu_freq = sum(cpu_freq)/len(cpu_freq) if cpu_freq else -1
                
                idleness = []
                for idle in trace.cpu.lpm_intervals(cpu=last_task_interval.cpu, interval=current_task_interval.interval):
                    idleness.append(idle.state)
                dest_cpu_idle_state = sum(idleness)/len(idleness) if idleness else -1    
                
                # within same cluster (0)
                # across cluster (1)
                fro_to = (last_task_interval.cpu, current_task_interval.cpu)
                if LITTLE_CPUS.issuperset(fro_to) or BIG_CPUS.issuperset(fro_to):
                    migration_type = 0
                else:
                    migration_type = 1

                df.loc[row_count] = (task_prio, latency, dest_cpu_rq_length, #dest_cpu_rq_prios,
                                    src_cpu_freq, dest_cpu_freq, dest_cpu_idle_state, migration_type)
                row_count += 1 
                                                                        
            last_task_interval = current_task_interval
    
    df = df[df['latency'] > 0]
    df['src_dest_cpu_freq_ratio'] = df['src_cpu_freq'] / df['dest_cpu_freq']
    
    return df   

if __name__ == '__main__':
    _files = glob.glob(r'{path}\*{file_ext}'.format(path=PATH, file_ext=FILE_EXT))
    F_DICT = {_fp: os.path.split(_fp)[1].split('.')[0] for _fp in _files}

    for _file in _files:
        fp, trace = parse_file(_file)
        total_duration = trace.duration if not INTERVAL else INTERVAL.duration
        df_latency = sched_latencies(trace)
        df_latency.to_csv(r'{path}\{fp}_sched_latency.csv'.format(path=PATH, fp=F_DICT[fp]))

    
    