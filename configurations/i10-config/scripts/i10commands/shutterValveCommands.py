'''
Created on 16 Apr 2018

@author: fy65
'''
from gdaserver import shtr1, gv12
from utils.ExceptionLogs import localStation_exception
import sys
print "-"*100
print "Creating short hand command for shutter 1 and gate vale 12 controls: 'shtropen', 'shtrclose', 'gv12open', and 'gv12close'" 
try:
    shtropen = shtr1.moveTo("Open")
    shtrclose = shtr1.moveTo("Close")
    gv12open = gv12.moveTo("Open")
    gv12close = gv12.moveTo("Close")
except:
    localStation_exception(sys.exc_info(), "creating shutter & valve objects")
