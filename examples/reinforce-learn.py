# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 15:31:30 2015

@author: c00759961
"""
import random

random.seed(1)

def value(rewards):
    """
    sample averaging method for rewards receieved
    """
    return sum(rewards)/float(rewards) if rewards else 0.0
    
#num = how many time have I seen this action.
def greedy(actions, selected):
    """
    greedy greedy - always best action
    """
    rv = None
    for action, rewards in actions.iteritems():
        if value(rewards) > rv:
            rv = action
    return rv
    
def e_greedy(actions, e=0.01):
    """
    greedy greedy - always plus some noise
    """
    for action, rewards in actions.iteritems():
        if value(rewards) > rv:
            rv = int(action + random.gauss(0, e))
    return rv
    
actions = dict.fromkeys(range(10),[])

import numpy as np
from pandas import DataFrame
from pandas.stats.moments import rolling_mean

df = DataFrame(index=range(100), columns=['0.0', '0.01', '0.1'])
for step in range(100):  
    num_times_greedy=dict.fromkeys(range(10),0.0)
    arms = np.round(np.random.normal(0,1,2000)*10) # 10 random arms
        value[action].append(value(action))
    selected = greedy(actions, num_times_greedy[a])
    num_times_greedy[selected] +=1
    num_times_greedy[greedy(actions, num_times_greedy[greedy(actions)])] +=1
    df.loc[step,'0.0'] = num_times_greedy[greedy(actions)]
    df.loc[step,'0.01'] = e_greedy(actions, 0.01)
    df.loc[step,'0.1'] = e_greedy(actions, 0.1)
    #print "Step: {}".format(step)
  
mv_ag_df = rolling_mean(df,1)  
mv_ag_df.plot()   