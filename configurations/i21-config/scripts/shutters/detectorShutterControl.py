'''
functions to switch detector fast shutter source control for andor, Polandor_H or Polandor_V detector.
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

def erio():
    if installation.isDummy():
        print("set '%s' to 1" % SOURCE_CONTROL_PV)
    else:
        caput(SOURCE_CONTROL_PV, 1)

def primary():
    if installation.isDummy():
        print("set '%s' to 2" % SOURCE_CONTROL_PV)
    else:
        caput(SOURCE_CONTROL_PV, 2)

def spare():
    if installation.isDummy():
        print("set '%s'to 3" % SOURCE_CONTROL_PV)
    else:
        caput(SOURCE_CONTROL_PV, 3)
    
def polpi():
    if installation.isDummy():
        print("set '%s'to 4" % SOURCE_CONTROL_PV)
    else:
        caput(SOURCE_CONTROL_PV, 4)

def polsigma():
    if installation.isDummy():
        print("set '%s'to 5" % SOURCE_CONTROL_PV)
    else:
        caput(SOURCE_CONTROL_PV, 5)
    
alias("fsxas")
alias("erio")
alias("primary")
alias("spare")
alias("polpi")
alias("polsigma")

