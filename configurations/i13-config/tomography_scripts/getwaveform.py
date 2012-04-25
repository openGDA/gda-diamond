#!/bin/env dls-python2.6
import os, sys, csv
from pprint import *
from pkg_resources import require
require('cothread')

import cothread
from cothread.catools import *
import time

        
# function to grab the current snapshot of the first 5 channels
# of i12's Analog to Digital converter
# and record the theta stage position at which the routine was called

#
# intended to be called when the test scan script detects that there's a long time gap between images 
#

def getwaves(fpath):
   tstamp=time.time()
   #
   #This should grab the most recent 10 seconds of data 
   #
   data=caget(["BL12I-EA-ADC-01:WAVE:00","BL12I-EA-ADC-01:WAVE:01","BL12I-EA-ADC-01:WAVE:02","BL12I-EA-ADC-01:WAVE:03","BL12I-EA-ADC-01:WAVE:04","BL12I-EA-ADC-01:WAVE:05"])

   # ... and the associated angle
   # not 100% guaranteed to be at the same time as above but to a first approximation
   # I'm not worried so far
   #
   angle=caget("BL12I-MO-TAB-02:ST1:THETA.RBV")
   print "Image time gap at ",tstamp,angle

   #
   #Write out the file
   #
   # for test purpose I don't care if this 
   # delays the following frame. In practice 
   # it did not seem to 
   #
   odata=open(fpath,"w")
   for i in range(0,len(data[0])):
      odata.write("%i\t%f\t"%(i,tstamp + i * 0.001))
      for j in range(0,len(data)):
         odata.write("%.3f\t"%(data[j][i]))
      odata.write("\n")
   odata.close()
   
if __name__=="__main__":
   getwaves("data.dat")

    
