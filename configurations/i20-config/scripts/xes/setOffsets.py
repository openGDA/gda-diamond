from BeamlineParameters import JythonNameSpaceMapping

#
# This script will change the offsets for the motors in the spectrometer, based on supplied values from the user.
#

def setFromExpectedValues(expectedValuesDict):
    """ 
    Using the supplied dictionary of expected motor positions, this calculates the required offsets and sets them on the GDA Scannables.
    
    """
    _checkDictNames(expectedValuesDict)
    
    jython_mapper = JythonNameSpaceMapping()
    spectrometer = jython_mapper.spectrometer

    offsetsDict = {}
    for name in expectedValuesDict.keys():
        expected = expectedValuesDict[name]
        print "\t %s %f" % (name,expected)
        newOffset = _calcOffset(name,expected)
        offsetsDict[name] = newOffset
        
    print offsetsDict
    _setFromDict(offsetsDict)

    from xes import offsetsStore
    offsetsStore.write()

def _setFromDict(offsetsDict):
    """ 
    Sets the supplied dictionary of offsets to the GDA Scannables.
    
    The optional second argument is a boolean, if true this will store the new offsets to the default xml store of offsets as well.
    
    """

    _checkDictNames(offsetsDict)
    
    jython_mapper = JythonNameSpaceMapping()
    spectrometer = jython_mapper.spectrometer
    
    print "Setting the spectrometer offsets:"
    for name in offsetsDict.keys():
        offset = offsetsDict[name]
        print "\t %20s offset -> %.9f" % (name,offset)
        spectrometer.getGroupMember(name).setOffset([offset])    

def _checkDictNames(valuesDict):

    jython_mapper = JythonNameSpaceMapping()
    spectrometer = jython_mapper.spectrometer    
    for name in valuesDict.keys():
        scannable = spectrometer.getGroupMember(name)
        if scannable == None:
            message = "scannable " + name +" could not be found. Will not apply offsets"
            raise ValueError(message)

def _calcOffset(name,expectedReadback):
    
    jython_mapper = JythonNameSpaceMapping()
    spectrometer = jython_mapper.spectrometer
    scannable = spectrometer.getGroupMember(name)
    
    if scannable == None:
        raise ValueError("scannable '{}' could not be found. Will not apply offsets".format(name))

    readback = scannable()
    
    currentOffset = scannable.getOffset()
    if currentOffset == None:
        currentOffset = [0]
    currentOffset = currentOffset[0]
    
    newOffset = expectedReadback - (readback - currentOffset)
    
    return newOffset
