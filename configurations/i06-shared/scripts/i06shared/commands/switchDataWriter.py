'''
Created on 1 Mar 2018

@author: fy65
'''
from gda.configuration.properties import LocalProperties
from gda.jython.commands.GeneralCommands import alias

print "-"*100
print "Create data file format commands:"
print "    1. 'nexusformat' - switch to write Nexus data file. This is GDA default data file format."
print "    2. 'asciiformat' - switch to write ASCII data file. This format is being deprecated!"
print "    3. 'whichformat' - query which data file format is set in GDA currently."

def nexusformat():
    LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "NexusScanDataWriter")
    
def asciiformat():
    LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "SrsDataFile")

def whichformat():
    return LocalProperties.get(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT)

alias("nexusformat")
alias("asciiformat")
alias("whichformat")

