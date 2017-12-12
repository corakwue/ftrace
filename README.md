# Ftrace

Ftrace is a Python library for parsing and analyzing performance/power of Linux-based platform (e.g.Android).
It relies on Function Tracer (Ftrace) - an internal tracing framework introduced in Linux kernel (>= 2.6.27).
For complete documentation, see [here](http://elinux.org/Ftrace).

Android devices are shipped with ```atrace``` binary that utilizes Ftrace and supports enabling and profiling 
of useful android events. In addition, [Systrace](developer.android.com/tools/help/systrace.html) tool 
- Python/HTML-based wrapper - was developed by Google for profiling and visualizing via ```chrome://tracing/``` on Chrome browser.

# Prerequisites

## Ftrace
Ftrace must be configured/enabled in the kernel. This requires CONFIG_FTRACE and other Ftrace options.

## debugfs
Requires a kernel with CONFIG_DEBUG_FS option enabled (debugfs was added in 2.6.10-rc3). 
The debugfs needs to be mounted:

```
# mount -t debugfs nodev /sys/kernel/debug
```
> Most non-rooted (production) devices ship with some support for Ftrace and restrictions on what can be traced.

# Quick Start

Ftrace parsing library provides API for in-depth analysis of both performance/power related issues.
A version of this tool was used at Qualcomm (by previous employer) for development of big.LITTLE scheduler,
UX analysis (application launch time), HMP usage and much more. To get started, lets load a trace file.

### Loading a trace file.
```python
trace = Ftrace(r'/some/path/to/trace.html')
# how long is this trace (in seconds)
print trace.interval
print trace.duration
```

### CPU API examples
```python

# Task intervals
print trace.cpu.task_intervals(cpu=0) # you can filter to specific task with task argument

# Idle/busy times for CPU0
print trace.cpu.idle_intervals(cpu=0)
print trace.cpu.idle_time(cpu=0)
print trace.cpu.busy_intervals(cpu=0)
print trace.cpu.busy_time(cpu=0)

# Run-Queue information for CPU0
print trace.cpu.runqueue_depth_time(cpu=0, rq_depth=3) # time we has 3 things runnable in queue
print trace.cpu.runqueue_interval(cpu=0)

# Low Power Modes (LPM) for CPU0
print trace.cpu.lpm_time(cpu=0)
print trace.cpu.lpm_intervals(cpu=0)

# Simultaneously busy cores
print trace.cpu.simultaneously_busy_time(num_cores=2) # time when 2 cores were busy
print trace.cpu.simultaneously_busy_intervals(num_cores=2, cpus=[0,1,2,3]) # when 2 or more cpus in list were busy

# Frequency intervals
print trace.cpu.frequency_intervals(cpu=0)
```

### Android API examples
```python
# Android events intervals. There are 3 types (sync context, async context and counters)
print trace.android.event_intervals(name='postFramebuffer') # postFramebuffer events only.
# Dump events seen
print trace.android.names

# Get launch-time for an app (assuming an app was launched during trace)
print trace.android.app_launch_latency()
```

### Clk API examples
```python
# Dump clks seen
print trace.clk.names
# Clock intervals
print trace.clk.frequency_intervals(clk='oxili_gfx3d_clk') # for Adreno GPU on Qualcomm Snapdragon
```
