#@PydevCodeAnalysisIgnore
'''
This is a temporary solution to the problems encountered in EPICS sample stage 2 motors:
1. EPICS motor putcallback does not work;
2. VAL need to be set twice before motor moves in PMAC controller.

THIS FILE SHOULD NOT BE USED AFTER EPICS MOTOR RECORDS FOR THE SAMPEL SATGE 2 BEING FIXED.

Created on 27 Oct 2010

@author: fy65
'''
from gda.jython.commands.ScannableCommands import pos, scan
from gdascripts.utils import frange

mstep = 0.5
mstart = 410.0
mstop = 420.0
time = 0.1

for p in frange(mstart, mstop, mstep):
    pos ss2.y p 
    pos ss2.y p 
    scan dum.a 1 1 1 edxd time 
    
