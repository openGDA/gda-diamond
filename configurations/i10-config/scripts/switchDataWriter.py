'''
Created on 1 Mar 2018

@author: fy65
'''
from gda.configuration.properties import LocalProperties
from gda.jython.commands.GeneralCommands import alias

def nexusformat():
    LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "NexusDataWriter")
    
def acsiiformat():
    LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "SrsDataFile")

def whichformat():
    return LocalProperties.get(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT)

alias("nexusformat")
alias("acsiiformat")
alias("whichformat")