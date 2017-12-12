import glob
import os
import sys
import ftrace
from ftrace import Ftrace, Interval
from pandas import Series

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Per-core frequencies')
    parser.add_argument('-f', '--file', dest='file',
                        help='File to parse')
    args = parser.parse_args()

    trace = Ftrace(args.file)

    frame_durations = Series((event.interval.duration for event in trace.android.render_frame_intervals(interval=None)))
    frame_durations = frame_durations * 1000. # to milliseconds
    summary = frame_durations.describe()
    summary['90%'] = frame_durations.quantile(.9)
    summary['Janks'] = trace.android.num_janks(interval=None)
    summary['Janks Per Second'] = summary['Janks']/trace.duration
    summary['Average FPS'] = trace.android.framerate(interval=None)
    summary.to_csv(r'frame_stats.csv')
        