'''
Created on May 5, 2022

@author: fy65
'''
from gdascripts.utils import caput
from gda.jython.commands.GeneralCommands import alias
import installation
        
def lightOn():
    if installation.isDummy():
        print("set 'BL21I-EA-SMPL-01:BOLED1' to 1")
    else:
        caput('BL21I-EA-SMPL-01:BOLED1', 1)
    
def lightOff():
    if installation.isDummy():
        print("set 'BL21I-EA-SMPL-01:BOLED1' to 0")
    else:
        caput('BL21I-EA-SMPL-01:BOLED1', 0)
        

alias("lightOn")
alias("lightOff")
