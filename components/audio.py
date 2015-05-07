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
#
# Authors:
#       Chuk Orakwue <chuk.orakwue@huawei.com>

try:
    from logbook import Logger
except ImportError:
    import logging
    logging.basicConfig()
    from logging import getLogger as Logger

from collections import namedtuple
from ftrace.interval import Interval, IntervalList
from ftrace.ftrace import register_api, FTraceComponent
from ftrace.utils.decorators import requires, memoize
from ftrace.common import filter_by_task, percentile
from ftrace.audio import GlitchType

log = Logger('Audio')

# For audio jitter & latency
AudioJitter = namedtuple('AudioJitter', ['interval', 'latency'])
AudioLatency = namedtuple('AudioLatency', ['glitch_type', 'interval', 'latency'])

@register_api('audio')
class Audio(FTraceComponent):
    """
    Class with APIs to process android trace events
    written to the trace buffer for the audio components.
    Below tags must be enabled in trace:

           input - Input
            view - View System
              wm - Window Manager
              am - Activity Manager
           audio - Audio
             hal - Hardware Modules

    See `adb shell atrace --list_categories`.

    Audio Performance:
        - Input Latency
        - Output Latency
        - RoudTrip Latency (Input + Output Latency)
    
    Reference:
    ----------
    http://source.android.com/devices/audio/index.html
    https://www.youtube.com/watch?v=d3kfEeMZ65c
    https://android.googlesource.com/platform/frameworks/av/+/master/services/audioflinger/FastMixer.cpp
    
    """
    def __init__(self, trace):
        self._trace = trace
        self._events = trace.events
        
        self.buffer_size_frames = None

    def _initialize(self):
        self._audio_flinger_handler()


    @requires('tracing_mark_write')
    @memoize
    def num_frames_written(self, interval=None):
        """
        Returns number of frames written within specified interval.
        """
        raise NotImplementedError
        
    @requires('tracing_mark_write')
    @memoize
    def num_write_errors(self, interval=None):
        """
        Returns number of write errors within specified interval.
        """
        raise NotImplementedError

    @requires('tracing_mark_write')
    @memoize
    def num_glitches(self, interval=None, buffer_size_frames=None):
        """
        Returns number of audio glitches within specified interval.
        """
        return self.num_overruns(interval=interval, 
                                 buffer_size_frames=buffer_size_frames) +\
            self.num_underruns(interval=interval,
                               buffer_size_frames=buffer_size_frames)
    
    
    @requires('tracing_mark_write')
    @memoize
    def num_overruns(self, interval=None, buffer_size_frames=None):
        """
        Returns number of overruns within specified interval.
        """
        # hard to detect as we are still unsure of buffer_size.
        glitches = self.audio_glitches(interval=interval, 
                                       buffer_size_frames=buffer_size_frames)
        filter_func = lambda audio_glitch: audio_glitch.glitch_type is GlitchType.OVERRUN
        return len(filter(filter_func, glitches))


    @requires('tracing_mark_write')
    @memoize
    def num_underruns(self, interval=None, buffer_size_frames=None):
        """
        Returns number of underruns within specified interval.
        """
        glitches = self.audio_glitches(interval=interval, 
                                       buffer_size_frames=buffer_size_frames)
        filter_func = lambda audio_glitch: audio_glitch.glitch_type in GlitchType.underruns()
        return len(filter(filter_func, glitches))
    
    
    @requires('tracing_mark_write')
    @memoize
    def audio_glitches(self, interval=None, buffer_size_frames=None):
        """
        Returns number of underruns within specified interval.
        """
        try:
            self._fRdy2s
        except AttributeError:
            self._audio_flinger_handler(buffer_size_frames=buffer_size_frames)
        
        audio_glitches = IntervalList()
        for frdy in self._fRdy2s.slice(interval=interval):
            if frdy.value  == 0:
                 # framesReady() is zero, total underrun
                glitch_type = GlitchType.UNDERRUN_EMPTY
            elif frdy.value < self.buffer_size_frames:
                # framesReady() is non-zero but < full frame count
                glitch_type = GlitchType.UNDERRUN_PARTIAL
            elif frdy.value == self.buffer_size_frames:
                #glitch_type = GlitchType.UNDERRUN_FULL
                continue
            elif frdy.value > self.buffer_size_frames:
                glitch_type = GlitchType.OVERRUN
                
            audio_glitches.append(AudioLatency(glitch_type=glitch_type,
                                               interval=frdy.interval,
                                               latency=frdy.interval.duration))
            
        return audio_glitches
        
    @requires('tracing_mark_write')
    @memoize
    def frame_write_intervals(self, interval=None):
        """
        Returns list of intervals frames were written within specified interval.
        """
        raise NotImplementedError
    
    @requires('tracing_mark_write')
    @memoize
    def jitter_intervals(self, interval=None, buffer_size_frames=None):
        """
        Returns list of intervals of audio jitter within specified interval.
        
        Jitter = Expected callback time - Actual callback time.
        """
        try:
            self._cbk_jitters
        except AttributeError:
            self._audio_flinger_handler(buffer_size_frames=buffer_size_frames)

        return self._cbk_jitters.slice(interval=interval)


    def _audio_flinger_handler(self, buffer_size_frames=None):
        """
        Parses audio callback routines.
        """
        
        all_tasks = self._trace.cpu.task_intervals()
        self._OSL_cbks = IntervalList(filter_by_task(all_tasks, 'name', 'OSLcbk', 'any'))

        self._fRdy2s = self._trace.android.event_intervals(name='fRdy2')
        
        # Lets estimate buffer size (in seconds)
        # By taking geomean of intervals between OSL callbacks
        cbk_delta = [cbk_b.interval.start - cbk_a.interval.start \
            for cbk_a, cbk_b in zip(self._OSL_cbks, self._OSL_cbks[1:])]
        
        self.buffer_size_seconds = round(percentile(cbk_delta, 0.9), 3)
        
        # Find audio jitter intervals
        # This is delta (in seconds) between expected OSL callback arrival time
        # and actual arrival time. We want this interval reasonably small.
        self._cbk_jitters = IntervalList()
        for cbk_a, cbk_b in zip(self._OSL_cbks, self._OSL_cbks[1:]):
            expected_cbk_arrival_time = \
                cbk_a.interval.start  + self.buffer_size_seconds
            delta = cbk_b.interval.start - expected_cbk_arrival_time
            interval = Interval(cbk_a.interval.start, cbk_b.interval.start)
            self._cbk_jitters.append(AudioJitter(interval=interval, latency=delta))
        
        if self.buffer_size_frames is None:
            # Estimate buffer sizes (frames)
            self.buffer_size_frames = int(percentile([frdy.value for frdy in self._fRdy2s if frdy.value >= 0], 0.9))
        else:
            self.buffer_size_frames = buffer_size_frames