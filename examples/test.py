from pandas import DataFrame
from collections import defaultdict
import ftrace
from ftrace import Ftrace
from ftrace import Interval


#trace.gpu.busy_time(interval=it)/it.duration
#trace.gpu.idle_time(interval=it)/it.duration
#trace.gpu.lpm_time(interval=it, state=ftrace.gpu.BusyState.NAP)/it.duration
#trace.gpu.lpm_time(interval=it, state=ftrace.gpu.BusyState.SLUMBER)/it.duration

# processing scripts for each file in directory
trace = Ftrace(r'C:\Users\c00759961\Documents\systrace\Baidu_scroll.html')
#print trace.android.framerate()
#print trace.gpu.frequency_intervals(interval=it) # trace.clock.frequency_intervals(clock='oxili_gfx3d_clk', interval=it)
#trace.bus.bimc_aggregate_requests(interval=it)
#print trace.cpu.seen_tasks(cpu=0)
#print trace.android.event_intervals(name='VSYNC')
#ti = ftrace.Interval(0, 0.0005)
#print trace.thermal.
#print trace.cpu.task_intervals(cpu=4, interval=ti)
#print trace.cpu.runqueue_depth_intervals(cpu=4, interval=ti)
#print trace.cpu.task_intervals(task=tt)[0]
#print "Input Latency\n----------------\n"
#print trace.android.rendering_intervals() #'irq/13-fts_touc'
#print "Switch Camera Latency\n----------------\n"
#print trace.camera.switch_device_intervals()
#print trace.android.event_intervals('AndroidCamera.open')
#print "\n----------------\n"
#print "FPS: {}".format(trace.android.framerate())
##print trace.cpu.idle_intervals(cpu=0)
##print trace.cpu.runqueue_depth_intervals(cpu=0)
##
##print trace.cpu.idle_time(cpu=1)
##print trace.cpu.runqueue_depth_time(1, 0)
##lt = trace.android.launched_app_event().task
##print trace.cpu.task_intervals(task=lt)[0]
#print trace.android.app_launch_latencies()
#print trace.cpu.simultaneously_busy_intervals(interval=ftrace.Interval(2.1, 2.2))[:10]

#print trace.cpu.lpm_intervals(cpu=0)
##trace.cpu.frequency_intervals(0)
#for cpu in trace.seen_cpus:
#    print "CPU {}: busy={:.4f}, idle={:.4f}, cum={:.4f}".format(cpu, trace.cpu.busy_time(cpu=cpu), trace.cpu.idle_time(cpu=cpu), trace.duration)

# For SS Galaxy S6
#
#
##df = DataFrame( columns = trace.seen_cpus,
##                index=[400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 1104000, 1200000, 1296000, 1300000, 1400000, 1500000, 1600000, 1704000, 1800000, 1896000, 2000000, 2100000])
##
##for cpu in trace.seen_cpus:
##    frq_dict = defaultdict(lambda: 0)
##    frqs = trace.cpu.frequency_intervals(cpu=cpu)
##    if frqs:
##        for frq in frqs:
##            frq_dict[frq.frequency] += frq.interval.duration
##        df[cpu] = DataFrame(frq_dict.values(), index=frq_dict.keys())
##
##df.fillna(0, inplace=True)
##df = df / trace.duration
##
##df.to_csv(r'C:\Users\c00759961\Documents\systrace\ss_gs6_gmail_scroll_freq.csv')

# Task load on wakeup
#ddd = {}
#ddd[3239] = []
#ddd[2961] = []
#for event in filter(lambda x: x.tracepoint == 'sched_task_load' and x.task.pid in [3239, 2961], trace.events):
#    ddd[event.task.pid].append(event.data.demand/10e6)
#    