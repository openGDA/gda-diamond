from gda.jython.commands.Input import requestInput

from BeamlineParameters import JythonNameSpaceMapping
from xes import storeOffsets

#
# This script will change the offsets for the motors in the spectrometer, based on supplied values from the user.
#

def setAll():
    """ 
    Asks the user for the expected motor positions, this calculates the required offsets and sets them on the GDA Scannables.
    
    The user is given the option to save the offset values to the default offsets store.
    
    """

    jython_mapper = JythonNameSpaceMapping()
    spectrometer = jython_mapper.spectrometer
    scannableNames = spectrometer.getGroupMemberNames()
    
    for name in scannableNames:
        message = "Please enter the expected value for " + name
        expected  = float(requestInput(message))
        newOffset = _calcOffset(name,expected)
        print "\tSetting %s offset to %.2f" % (name,newOffset)
        spectrometer.getGroupMember(name).setOffset([newOffset])
    
    choice = requestInput("Would you like to save these offsets to the default Spectrometer offset store?")
    if (choice.lower().startswith("y")):
        storeOffsets.store()
    
def set(xtal_minus1_x_expected,\
    xtal_minus1_y_expected,\
    xtal_minus1_rot_expected, \
    xtal_minus1_pitch_expected,\
    xtal_central_y_expected,\
    xtal_central_rot_expected, \
    xtal_central_pitch_expected,\
    xtal_plus1_x_expected,\
    xtal_plus1_y_expected,\
    xtal_plus1_rot_expected,\
    xtal_plus1_pitch_expected,\
    det_x_expected,\
    det_y_expected,\
    det_rot_expected,\
    xtal_x_expected,\
    spec_rot_expected):
    """ 
    Using the supplied expected motor positions, this calculates the required offsets and sets them on the GDA Scannables.
    
    The user is given the option to save the offset values to the default offsets store.
    
    """
    
    names = {'xtal_minus1_x' : xtal_minus1_x_expected,\
    'xtal_minus1_y' :  xtal_minus1_y_expected,\
    'xtal_minus1_rot' : xtal_minus1_rot_expected,\
    'xtal_minus1_pitch' : xtal_minus1_pitch_expected,\
    'xtal_central_y' : xtal_central_y_expected,\
    'xtal_central_rot' : xtal_central_rot_expected,\
    'xtal_central_pitch' : xtal_central_pitch_expected,\
    'xtal_plus1_x' : xtal_plus1_x_expected,\
    'xtal_plus1_y' : xtal_plus1_y_expected,\
    'xtal_plus1_rot' : xtal_plus1_rot_expected,\
    'xtal_plus1_pitch' : xtal_plus1_pitch_expected,\
    'det_x': det_x_expected, \
    'det_y' : det_y_expected,\
    'det_rot' : det_rot_expected,\
    'xtal_x' : xtal_x_expected,\
    'spec_rot' : spec_rot_expected }
    
    setFromDict(names)
    
def setFromDict(dict):
    """ 
    Using the supplied expected motor positions, this calculates the required offsets and sets them on the GDA Scannables.
    
    The user is given the option to save the offset values to the default offsets store.
    
    """

    
    jython_mapper = JythonNameSpaceMapping()
    spectrometer = jython_mapper.spectrometer
    
    print "Using the dictionary of expected values to change the offsets..."
    
    for name in dict.keys():
        expected = dict[name]
        newOffset = _calcOffset(name,expected)
        print "\tSetting %s offset to %.2f" % (name,newOffset)
        spectrometer.getGroupMember(name).setOffset([newOffset])
        
    if len(dict.keys()) < 16:
        print "Other offsets unchanged."
    
    choice = requestInput("Would you like to save these offsets to the default Spectrometer offset store?")
    if (choice.lower().startswith("y")):
        storeOffsets.store()

def _calcOffset(name,expectedReadback):
    
    jython_mapper = JythonNameSpaceMapping()
    spectrometer = jython_mapper.spectrometer
    scannable = spectrometer.getGroupMember(name)
    
    readback = scannable()
    
    currentOffset = scannable.getOffset()
    if currentOffset == None:
        currentOffset = [0]
    currentOffset = currentOffset[0]
    
    newOffset = expectedReadback - (readback - currentOffset)
    
    return newOffset
    