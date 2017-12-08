#!/usr/bin/env python

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
#

from .register import PARSERS
# CPU
from .sched_switch import sched_switch
from .sched_wakeup import sched_wakeup
from .sched_migrate_task import sched_migrate_task
from .cpufreq_interactive_setspeed import cpufreq_interactive_setspeed
from .cpufreq_interactive_target import cpufreq_interactive_target
from .cpufreq_interactive_already import cpufreq_interactive_already
# GPU
from .gpu_sched_switch import gpu_sched_switch
from .kgsl_pwr_set_state import kgsl_pwr_set_state
from .kgsl_gpubusy import kgsl_gpubusy
from .kgsl_buslevel import kgsl_buslevel
from .kgsl_pwrlevel import kgsl_pwrlevel
from .kgsl_rail import kgsl_rail
from .kgsl_bus import kgsl_bus
from .kgsl_irq import kgsl_irq
from .kgsl_clk import kgsl_clk
from .mali_job_slots_event import mali_job_slots_event
from .mali_pm_status import mali_pm_status
from .mali_pm_power_on import mali_pm_power_on
from .mali_pm_power_off import mali_pm_power_off
# Bus
from .memory_bus_usage import memory_bus_usage
from .bus_update_request import bus_update_request #msm
# Android
from .tracing_mark_write import tracing_mark_write
# Work Queue
from .workqueue_execute_start import workqueue_execute_start
from .workqueue_execute_end import workqueue_execute_end
from .workqueue_queue_work import workqueue_queue_work
from .workqueue_activate_work import workqueue_activate_work
# Disk
from .block_rq_issue import block_rq_issue
from .block_rq_complete import block_rq_complete
from .block_rq_insert import block_rq_insert
from .ext4_da_write_begin import ext4_da_write_begin
from .ext4_da_write_end import ext4_da_write_end
from .ext4_sync_file_enter import ext4_sync_file_enter
from .ext4_sync_file_exit import ext4_sync_file_exit
from .f2fs_sync_file_enter import f2fs_sync_file_enter
from .f2fs_sync_file_exit import f2fs_sync_file_exit
from .f2fs_write_begin import f2fs_write_begin
from .f2fs_write_end import f2fs_write_end
# Power/Clock
from .cluster_enter import cluster_enter
from .cluster_exit import cluster_exit
from .cpu_idle_enter import cpu_idle_enter
from .cpu_idle_exit import cpu_idle_exit
from .cpu_frequency import cpu_frequency
from .cpu_frequency_switch_start import cpu_frequency_switch_start
from .cpu_frequency_switch_end import cpu_frequency_switch_end
from .cpu_idle import cpu_idle
from .clock_set_rate import clock_set_rate
from .clock_enable import clock_enable
from .clock_disable import clock_disable
# Thermal [MSM]
from .tsens_threshold_clear import tsens_threshold_clear
from .tsens_threshold_hit import tsens_threshold_hit
from .tsens_read import tsens_read
# IRQ
from .irq_handler_entry import irq_handler_entry
from .irq_handler_exit import irq_handler_exit
from .softirq_raise import softirq_raise
from .softirq_entry import softirq_entry
from .softirq_exit import softirq_exit
# SYNC
from .sync_pt import sync_pt
from .sync_timeline import sync_timeline
from .sync_wait import sync_wait
# Qualcomm's HMP
from .sched_task_load import sched_task_load
# Linaro/ARM's HMP
from .sched_hmp_migrate import sched_hmp_migrate
from .sched_rq_nr_running import sched_rq_nr_running
from .sched_rq_runnable_load import sched_rq_runnable_load
from .sched_rq_runnable_ratio import sched_rq_runnable_ratio
from .sched_task_load_contrib import sched_task_load_contrib
from .sched_task_runnable_ratio import sched_task_runnable_ratio
from .sched_task_usage_ratio import sched_task_usage_ratio
# Linaro/ARM's EAS work
from .cpu_capacity import cpu_capacity
from .sched_boost_cpu import sched_boost_cpu
from .sched_contrib_scale_f import sched_contrib_scale_f
from .sched_load_avg_task import sched_load_avg_task
from .sched_load_avg_cpu import sched_load_avg_cpu
# Android binder
from .binder_ioctl import binder_ioctl
from .binder_return import binder_return
from .binder_lock import binder_lock
from .binder_unlock import binder_unlock
from .binder_locked import binder_locked
from .binder_command import binder_command
from .binder_wait_for_work import binder_wait_for_work
from .binder_transaction_buffer_release import binder_transaction_buffer_release
from .binder_transaction import binder_transaction
from .binder_transaction_alloc_buf import binder_transaction_alloc_buf
from .binder_write_done import binder_write_done
from .binder_read_done import binder_read_done
from .binder_ioctl_done import binder_ioctl_done
from .binder_transaction_received import binder_transaction_received
from .binder_transaction_ref_to_node import binder_transaction_ref_to_node
from .binder_transaction_node_to_ref import binder_transaction_node_to_ref
from .binder_transaction_fd import binder_transaction_fd
from .binder_transaction_ref_to_ref import binder_transaction_ref_to_ref
from .binder_update_page_range import binder_update_page_range
