# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 13:43:21 2016

@author: c00759961
"""
import os
import glob
import ftrace
from ftrace import Ftrace
from pandas import DataFrame, Series
import nltk.classify.util
from nltk.util import ngrams
from nltk.classify import NaiveBayesClassifier
from nltk.probability import LaplaceProbDist
from collections import defaultdict

PATH = r'C:\Users\c00759961\Documents\Charters\EAS\mate_8'

# Interval of interval, if None, looks at entire trace,
# Care only about 1s to 10s, then set to `Interval(1, 10)
INTERVAL = ftrace.Interval(0, 5.0)
# Parses only .txt files in `PATH`
FILE_EXT = '.html'

LITTLE_CLUSTER_MASK = 0x0F
BIG_CLUSTER_MASK = 0xF0

LITTLE_CPUS = ftrace.common.unpack_bitmap(LITTLE_CLUSTER_MASK)
BIG_CPUS = ftrace.common.unpack_bitmap(BIG_CLUSTER_MASK)
ALL_CPUS = LITTLE_CPUS.union(BIG_CPUS)

TRAIN_WITH = 0.5 # how much data to use for training (higher = more history)
MIN_ONLINE_CORES = 1 # min cores we should have online at anytime
NGRAM_RANGE = 10 # how many (n) in n-grams to evaluate

# todo: include duration as feature set?
        
def parse_file(filepath):
    trace = Ftrace(filepath)
    return (filepath, trace)
    
def get_features(conc):
    return [({'active': n}, active) for (n, active) in conc]
    
def get_labels(conc, n):
    return [(con[:n], max(con[-1], MIN_ONLINE_CORES)) for con in conc]

def sim_busy_times(trace, cpus, interval):
    data = {num_cores: trace.cpu.simultaneously_busy_time(num_cores, cpus=list(cpus), interval=INTERVAL) for num_cores in xrange(len(cpus)+1)}
    total_duration = trace.duration if not INTERVAL else INTERVAL.duration
    return Series(data=data.values(), index=data.keys(), name=trace.filename) / total_duration

_files = glob.glob(r'{path}\*{file_ext}'.format(path=PATH, file_ext=FILE_EXT))
F_DICT = {_fp: os.path.split(_fp)[1].split('.')[0] for _fp in _files}

b_results = DataFrame(columns=range(1, NGRAM_RANGE))
l_results = DataFrame(columns=range(1, NGRAM_RANGE))

for _file in _files:
    fp, trace = parse_file(_file)

    b_df = DataFrame(columns=["count", "duration"])
    l_df = DataFrame(columns=["count", "duration"])
    
    print "processing"
    for item in trace.cpu.simultaneously_busy_intervals(interval=INTERVAL):
        b_df.loc[len(b_df)] = (len(item.cpus.intersection(BIG_CPUS)), item.interval.duration)
        l_df.loc[len(l_df)] = (len(item.cpus.intersection(LITTLE_CPUS)), item.interval.duration)
       
    little_idle_df = DataFrame(columns=range(4))
    big_idle_df = collections.de
    for item in trace.cpu.idle_intervals(interval=INTERVAL):
        if item.cpu in BIG_CPUS:
            big_idle_df.loc[len(big_idle_df)] = item
        
#    b_df['duration'] *= 1000
#    l_df['duration'] *= 1000
    
    b_df['count'][b_df['count'] < MIN_ONLINE_CORES] = MIN_ONLINE_CORES
    concurrency = b_df['count'].tolist()
    train = int(len(concurrency)*TRAIN_WITH)

    print "yoo---big cores"
    rd = {} 
    for n in range(1, NGRAM_RANGE):
        # we add one more (future) to ngram- tuple, but remove/use it as label in 'get_labels' function
        trainfeats = get_features(get_labels(ngrams(concurrency[0:train], n+1), n))
        testfeats = get_features(get_labels(ngrams(concurrency[train:], n+1), n))
        
        classifier = NaiveBayesClassifier.train(trainfeats, estimator=LaplaceProbDist)
        rd[n] = nltk.classify.util.accuracy(classifier, testfeats)
    b_results.loc[trace.filename] = Series(data=rd.values(), index=rd.keys(), name=trace.filename)
    #----------------------------------------------------------------------        
    print "yoo---little cores"
    
    l_df['count'][l_df['count'] == 0] = MIN_ONLINE_CORES
    concurrency = l_df['count'].tolist()
    train = int(len(concurrency)*TRAIN_WITH)
            
    rd = {} 
    for n in range(1, NGRAM_RANGE):
        trainfeats = get_features(get_labels(ngrams(concurrency[0:train], n+1), n))
        testfeats = get_features(get_labels(ngrams(concurrency[train:], n+1), n))
        
        classifier = NaiveBayesClassifier.train(trainfeats)
        rd[n] = nltk.classify.util.accuracy(classifier, testfeats)
    l_results.loc[trace.filename] = Series(data=rd.values(), index=rd.keys(), name=trace.filename)
    
b_results.to_csv(r'{path}\big_cluster_hotplug_accuracies.csv'.format(path=PATH))
l_results.to_csv(r'{path}\little_cluster_hotplug_accuracies.csv'.format(path=PATH))

#sim_busy_times(trace, BIG_CPUS, None)
#sim_busy_times(trace, LITTLE_CPUS, None)