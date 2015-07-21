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

log = Logger('Camera')

# For camera latency
CameraLatency = namedtuple('CameraLatency', ['op', 'interval', 'latency'])

@register_api('camera')
class Camera(FTraceComponent):
    """
    Class with APIs to process android trace events
    written to the trace buffer for the camera components.
    Below tags must be enabled in trace:

             gfx - Graphics
           input - Input
            view - View System
              wm - Window Manager
              am - Activity Manager
          camera - Camera
             hal - Hardware Modules

    See `adb shell atrace --list_categories`.

    CAMERA Performance (still image or video):
	- 3A (AF/AE/AWB Time)
	- CaptureTime: time from createCaptureRequest() --> onCaptureComplete
	- Re-configure Camera (per-settings control) for use [see HAL]
	- Camera Switch Time (from Rear2Front or Front2Rear Camera) [x]
	- Time to Open camera device [x]
	- ShutterLag Time [x]
	- Shot2ShotTime
	- JPEGCallBackFinish Time
	- PictureDisplayToJPEGCallback Time
	- Store Image/AddToMediaStore Time [x]
	- deleteImageTime
	- Continous AF Time
	- Switch Operating Mode Time (Still Capture to Video Recording)

     Ideally, we would love to include metadata entries (per-settings control)
     for each image taken. However, this is not possible. Hence it's highly recommended
     that user records the camera settings for each trace captured.

    """
    def __init__(self, trace):
        self._trace = trace
        self._events = trace.events

    def _initialize(self):
        pass

    @requires('tracing_mark_write')
    @memoize
    def open_camera_intervals(self, interval=None):
        """
        Returns list of intervals to open camera device.
        Camera open should return in 200ms, and must return in 500ms.

        References:
        [1] http://source.android.com/devices/camera/camera3_requests_hal.html
        [2] https://android.googlesource.com/platform/hardware/libhardware/+/master/include/hardware/camera3.h
        """
        rv = IntervalList()
        # Several device vendors have different names
        
        cam_open_events = self._trace.android.event_intervals(
            name='openCameraDevice', interval=interval) # Typical of SS
        if not cam_open_events:
            cam_open_events = self._trace.android.event_intervals(
                name='AndroidCamera.open', interval=interval) # Huawei
        for cam_open_event in cam_open_events:
            interval = cam_open_event.interval
            if interval.duration > 0.5:
                log.warn("Camera open exceeded 500ms recommended time")
            rv.append(CameraLatency(op="Open Camera Device", interval=interval,
                                    latency=interval.duration))
        return rv


    @requires('tracing_mark_write')
    @memoize
    def store_image_intervals(self, interval=None):
        """
        Returns list of intervals to store image intervals.
        
        # IMPORTANT: Not supported on Huawei devices yet. Missing markers.
        """
        rv = IntervalList()
        for store_image_event in self._trace.android.event_intervals(
            name='storeImage',interval=interval):
            interval = store_image_event.interval
            rv.append(CameraLatency(op="Store Image/ Add To Media Store",
                                    interval=interval,
                                    latency=interval.duration))
        return rv

    #--------------------------------------------------------------------------
    """
    Utility script to estimate shutter lag.

    We define shutter lag latency as time from when camera app consumes
    input event `DeliverInputEvent` for image capture, to time when
    still-image is saved. Technically speaking, this is referred to as
    'shoot-to-save' latency.

    IMPORTANT: We do not account for delays such as input latency.

    """
    @requires('tracing_mark_write')
    @memoize
    def shutter_lag_intervals(self, interval=None):
        """
        Returns list of intervals for shutter lag.

        Basically the time difference between when the shutter button
        is clicked in your camera and when the picture is recorded
        in the album (i.e. stores in media)

        # TODO: Handle ZSL.
        # IMPORTANT: Not supported on Huawei devices yet. Missing markers.
        """
        try:
            return self._shutter_lag_latencies.slice(interval=interval)
        except AttributeError:
            return self._shutter_lag_latency_handler().slice(interval=interval)


    def _shutter_lag_latency_handler(self):
        """
        Returns list of all input events
        """
        self._shutter_lag_latencies = IntervalList()
        deliver_inputs = self._trace.android.event_intervals("deliverInputEvent")

        def _still_capture_intervals():
            """
            Generator that yields intervals when still images are captured
            """
            last_timestamp = self._trace.interval.start
            for tp_event in self._trace.android.event_intervals('doTakePictureAsync'):
                yield Interval(last_timestamp, tp_event.interval.start)
                last_timestamp = tp_event.interval.start

        for interval in _still_capture_intervals():
            touch_events = deliver_inputs.slice(interval=interval, trimmed=False)
            # Necessary as we may be interested in different IRQ name
            if touch_events:
                # Use last input event within this interval
                start_ts = touch_events[-1].interval.start
                end_ts = start_ts
                post_touch_interval = Interval(interval.end, self._trace.duration)
                si_events = self._trace.android.event_intervals(name='storeImage',
                                                 interval=post_touch_interval)
                if si_events:
                    end_ts = si_events[0].interval.end
                shutter_lag_interval = Interval(start=start_ts, end=end_ts)
                self._shutter_lag_latencies.append(
                    CameraLatency("Shutter Lag",
                                  interval=shutter_lag_interval,
                                  latency=shutter_lag_interval.duration))

            return self._shutter_lag_latencies

    #---------------------------------------------------------------------------
    """
    Utility script to estimate time to switch from rear-to-front
    or front-to-rear camera devices.

    We define shutter lag latency as time from when camera app consumes
    Input event `DeliverInputEvent` for switch camera device, to time when
    preview of new camera device is complete. Technically speaking,
    this is referred to as 'switch_input-to-preview' latency.

    IMPORTANT: We do not account for delays such as input latency.
    It includes latencies to:
        1) stop preview of prior camera device
        2) tear down (flush) pending requests
        3) open new camera device
        4) configure new device per settings control.
        5) start preview of new camera device

    """
    @requires('tracing_mark_write')
    @memoize
    def switch_device_intervals(self, interval=None):
        """
        Returns list of intervals for shutter lag.

        Basically the time difference between when the switch mode button
        is clicked in your camera and when preview from new camera device is
        started.
        """
        try:
            return self._switch_latencies.slice(interval=interval)
        except AttributeError:
            return self._switch_device_latency_handler().slice(interval=interval)


    def _switch_device_latency_handler(self):
        """
        Returns list of all input events
        """
        self._switch_latencies = IntervalList()
        deliver_inputs = self._trace.android.event_intervals("deliverInputEvent")

        def _preview_intervals():
            """
            Generator that yields intervals when still images are captured
            """
            last_timestamp = self._trace.interval.start
            sp_events = self._trace.android.event_intervals('doStopPreviewSync')
            if not sp_events:
                preview_events = self._trace.android.event_intervals('AndroidCamera.startPreview')
                if preview_events:
                    camera_task = preview_events[0].event.task
                    sp_events = (context for context in \
                        self._trace.android.event_intervals('disconnect') \
                        if context.event.task.pid == camera_task.pid)
            
            for sp_event in sp_events:
                yield Interval(last_timestamp, sp_event.interval.start)
                last_timestamp = sp_event.interval.start

        for interval in _preview_intervals():
            touch_events = deliver_inputs.slice(interval=interval, trimmed=False)
            if touch_events:
                start_ts = touch_events[-1].interval.start
                end_ts = start_ts
                post_touch_interval = Interval(start_ts, self._trace.duration)
                si_events = self._trace.android.event_intervals(name='StartPreviewThread',
                                                 interval=post_touch_interval)
                if not si_events:
                    si_events = self._trace.android.event_intervals(name='AndroidCamera.startPreview',
                                                 interval=post_touch_interval)
                if si_events:
                    end_ts = si_events[0].interval.end
                shutter_lag_interval = Interval(start=start_ts, end=end_ts)
                self._switch_latencies.append(
                    CameraLatency("Camera Switch",
                                  interval=shutter_lag_interval,
                                  latency=shutter_lag_interval.duration))

        return self._switch_latencies