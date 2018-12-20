'''
Created on 15 Feb 2011

@author: fy65
'''
from peloop.functiongenerator import fg
from PEScan import pescan
#from localStation import mythen

# set acquisition parameters - need to be changes for each experiment
number_of_pre_cycles=1
fg.setFunction(2)
fg.setFrequency(0.1)
fg.setAmplitude(10.0)
fg.setShift(0.0)
fg.setSymmetry(50.0)
number_of_points_per_cycle=40.0
number_gates=1
number_frames=1

#derived parameters for pescan() function inputs
fg_frequency=fg.getFrequency()
fg_period=1/fg_frequency
pre_condition_time=number_of_pre_cycles * fg_period
stop_time=pre_condition_time+fg_period
gate_width=fg_period/number_of_points_per_cycle

pescan()
#pescan(starttime=pre_condition_time, stoptime=stop_time, gatewidth=gate_width, mythen1=mythen, ng=number_gates, nf=number_frames)
