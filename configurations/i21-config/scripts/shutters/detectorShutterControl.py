'''
functions to switch detector fast shutter source control for andor or Polandor_H detector.
Created on May 5, 2022

@author: fy65
'''
import installation
from gdascripts.utils import caput
from gda.jython.commands.GeneralCommands import alias

SOURCE_CONTROL_PV = "BL21I-OP-SHTR-01:SRC"

def fsxas():
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

def erio():
    if installation.isDummy():
        print("set '%s' to 3" % SOURCE_CONTROL_PV)
    else:
        caput(SOURCE_CONTROL_PV, 3)
    
    
alias("fsxas")
alias("primary")
alias("polarimeter")
alias("erio")

