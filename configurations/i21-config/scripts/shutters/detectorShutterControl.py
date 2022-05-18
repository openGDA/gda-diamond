'''
functions to switch detector fast shutter source control 
Created on May 5, 2022

@author: fy65
'''
import installation
from gdascripts.utils import caput
from gda.jython.commands.GeneralCommands import alias

SOURCE_CONTROL_PV = "BL21I-OP-SHTR-01:SRC"

def erio():
    if installation.isDummy():
        print("set '%s' to 0" % SOURCE_CONTROL_PV)
    else:
        caput(SOURCE_CONTROL_PV, 0)

def primary():
    if installation.isDummy():
        print("set '%s' to 1" % SOURCE_CONTROL_PV)
    else:
        caput(SOURCE_CONTROL_PV, 1)

def polarimeter():
    if installation.isDummy():
        print("set '%s'to 2" % SOURCE_CONTROL_PV)
    else:
        caput(SOURCE_CONTROL_PV, 2)
    
    
alias("erio")
alias("primary")
alias("polarimeter")

