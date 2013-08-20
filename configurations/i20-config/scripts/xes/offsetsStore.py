from gda.configuration.properties import LocalProperties
from gda.util.persistence import LocalParameters

from BeamlineParameters import JythonNameSpaceMapping

from xes import setOffsets

import os

#
# This script stores the offsets of all the motors in the spectrometer GroupScannable and records them in 
# an xml file.
# 
# Normally offsets would be recorded in the GDAs XML configuration files, but this provides a quick way for anyone to save the files.
#
#
# It has methods to record the offsets in specifically named files if required and to view the saved offsets and 
# to set the spectrometer offsets from a named store.
#
# There is an unamed default store for convenience. the underlying file for this is xes_store.

global DEFAULT_STORE_NAME,STORE_DIR,STORE_IN_USE_NAME
TEMP_STORE_NAME="xes_temp"
STORE_IN_USE_NAME="current_store"
STORE_DIR = LocalProperties.getVarDir() +"/xes_offsets/"

def list():
    """
    Lists the available stores (xml files) which each hold a collection of offsets
    """
    
    print "Current stores available :"
    
    files = os.listdir(STORE_DIR)
    for name in files:
        if name.endswith(".xml"):
            name_length = len(name)
            print name[0:name_length-4]

def write():
    """
    Stores the current Spectrometer offsets in the default store. This is available, but not applied, on GDA 
    restart. But will be overwritten the next time the offsets are saved so should be saved to a named store 
    as soon as they are considered correct. 
    """
    writeas(TEMP_STORE_NAME)

def writeas(storeName):
    """
    Stores the current Spectrometer offsets in the named store. This store will not be re-loaded on GDA restart.
    """
    jython_mapper = JythonNameSpaceMapping()
    scannables = jython_mapper.spectrometer.getGroupMembers()
    store = LocalParameters.getXMLConfiguration(STORE_DIR,storeName,True)
    
    for scannable in scannables:
        name = scannable.getName()
        # now store the offset, not the motor position
        value = scannable.getOffset()
        if value == None:
            value = 0
        store.setProperty(name,value)
    store.save()
    
def reapply():
    print "Reapplying previous spectrometer offsets..."
    applyfrom(STORE_IN_USE_NAME)
    
def applyfrom(storeName):
    """
    Loads and sets the Spectrometer offsets from the named store.
    """
    
    jython_mapper = JythonNameSpaceMapping()
    scannables = jython_mapper.spectrometer.getGroupMembers()
    store = LocalParameters.getXMLConfiguration(STORE_DIR,storeName,False)

    valuesDict = {}
    print "Applying offsets from store",storeName,"..."
    for scannable in scannables:
        name = scannable.getName()
        prop = store.getProperty(name)
        if prop == None:
            prop = 0.0
        valuesDict[name] = float(prop)
    #setOffsets.setFromExpectedValues(valuesDict)
    # set the offsets directly
    setOffsets._setFromDict(valuesDict)
    writeas(STORE_IN_USE_NAME)
    print "Offsets applied."

    
def viewstore(storeName):
    """
    Views the Spectrometer offsets held in the named store.
    """
    jython_mapper = JythonNameSpaceMapping()
    scannables = jython_mapper.spectrometer.getGroupMembers()
    store = LocalParameters.getXMLConfiguration(STORE_DIR,storeName,False)
    
    print "Spectrometer offsets in store",storeName,":"
    
    for scannable in scannables:
        name = scannable.getName()
        value = float(store.getProperty(name))
        print "%20s : %.2f" % (name, value)
        
def current():
    """
    Lists the current live Spectrometer offsets.
    """
    jython_mapper = JythonNameSpaceMapping()
    spectrometer = jython_mapper.spectrometer
    scannables = jython_mapper.spectrometer.getGroupMembers()
    
    print "Spectrometer current GDA offsets:"
    
    for scannable in scannables:
        name = scannable.getName()
        offset = spectrometer.getGroupMember(name).getOffset()
        if offset == None:
            offset = [0]
        offset = offset[0]
        print "%20s : %.2f" % (name, offset)


def removeAllOffsets():
    """
    Sets all the offsets to 0. Does not save the values to an xml store.
    """
    
    jython_mapper = JythonNameSpaceMapping()
    scannables = jython_mapper.spectrometer.getGroupMembers()

    for scannable in scannables:
        scannable.setOffset(0.0)
