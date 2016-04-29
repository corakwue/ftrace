import ftrace
from ftrace import Ftrace
from ftrace.sched_hmp import HMPMigrate
from pandas import DataFrame

LITTLE_CLUSTER_MASK = 0x0F
BIG_CLUSTER_MASK = 0xF0

LITTLE_CPUS = ftrace.common.unpack_bitmap(LITTLE_CLUSTER_MASK)
BIG_CPUS = ftrace.common.unpack_bitmap(BIG_CLUSTER_MASK)
ALL_CPUS = LITTLE_CPUS.union(BIG_CPUS)

# processing scripts for each file in directory
trace = Ftrace(r'Z:\EAS\Mate8_Default\music1.html')
##ti = trace.cpu.task_intervals()
##tasks = trace.cpu.seen_tasks()
##trace.cpu.task_intervals(cpu=1)
##print trace.cpu.task_intervals(cpu=0, interval=ftrace.Interval(0, 0.2))
#PATH = r'C:\Users\c00759961\Documents\systrace'
#total_migrations = len(trace.events)
#
#def get_hmp_migrations():
#    """
#    Does not include task migrations on fork ...
#    It seems the fork migrations are rare thing in EAS RFCv5.2
#    Forked processed (sched_process_fork), can and do get migrated to
#    different clusters ("sched_migrate_task"). This behavior contradicts
#    expectation that forked processes get put on BIG cluster!
#
#    sample results:
#
#                count   %
#    IDLE_PULL      6  0.150 <<---LITTLE to BIG
#    WAKEUP        35  0.875
#    FORCE          0  0.000 <<--- LITTLE to BIG
#    OFFLOAD        0  0.000 <<--- BIG to LITTLE
#    UNKNOWN        0  0.000
#
#    Generally, we want the L->B migrations to be low.
#    Also want the inter-cluster migrations to be low.
#
#    """
#    df = DataFrame(index=HMPMigrate.universe(), columns=['count'])
#    df.fillna(0, inplace=True)
#    events = filter(lambda x: x.tracepoint == 'sched_hmp_migrate', trace.events)
#    for event in events:
#        df.loc[event.data.force, 'count'] += 1
#
#    df['%'] = df['count'] / len(events)
#
#    df.to_csv(r'{path}\hmp_migrations.csv'.format(path=PATH))
#
#def get_all_migrations():
#    """
#    Tracks all migrations (inter-cluster and intra-cluster migrations).
#    Generally, we want the L->B migrations to be low.
#    Also want the inter-cluster migrations to be low.
#
#    sample results:
#
#            	count	 %
#    INTER-L2B	1886	14%
#    INTER-B2L	1886	14%
#    INTRA-LITTLE	7580	57%
#    INTRA-BIG	3892	29%
#
#    """
#    df = DataFrame(index=['INTER-L2B', 'INTER-B2L', 'INTRA-LITTLE', 'INTRA-BIG'], columns=['count'])
#    df.fillna(0, inplace=True)
#    events = filter(lambda x: x.tracepoint == 'sched_migrate_task', trace.events)
#    for event in events:
#        fro_to = (event.data.orig_cpu, event.data.dest_cpu)
#        if LITTLE_CPUS.issuperset(fro_to):
#            df.loc['INTRA-LITTLE', 'count'] += 1
#        elif BIG_CPUS.issuperset(fro_to):
#            df.loc['INTRA-BIG', 'count'] += 1
#        elif fro_to[0] in LITTLE_CPUS:
#            df.loc['INTER-L2B', 'count'] += 1
#        elif fro_to[0] in BIG_CPUS:
#            df.loc['INTER-B2L', 'count'] += 1
#
#    df['%'] = df['count'] / len(events)
#
#    df.to_csv(r'{path}\all_migrations.csv'.format(path=PATH))
#
#
## Intercluster migration latency
#
#
#get_all_migrations()
#get_hmp_migrations()