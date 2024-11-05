'''
Created on 15 May 2013

@author: fy65
'''
import os
from org.opengda.detector.electronanalyser.utils import OsUtil, FilenameUtil
from org.opengda.detector.electronanalyser.nxdetector import IAnalyserSequence
from gda.jython import InterfaceProvider
from gda.device.scannable import DummyScannable
from gda.device import Scannable
from types import TupleType, ListType, FloatType, IntType
from gda.device.scannable.scannablegroup import ScannableGroup
from gdascripts.scan.installStandardScansWithProcessing import scan
from gda.configuration.properties import LocalProperties

zeroScannable=DummyScannable("zeroScannable")
#Add to namespace so that it is findable during scans which is needed for extra region printing
InterfaceProvider.getJythonNamespace().placeInJythonNamespace(zeroScannable.getName(), zeroScannable);

def getSequenceFilename(arg):
    filename = arg
    if not os.path.isfile(arg):
        xmldir = InterfaceProvider.getPathConstructor().getVisitSubdirectory('xml') + os.sep;
        filename = os.path.join(xmldir, filename)
    if (OsUtil.isWindows()):
        FilenameUtil.setPrefix("D:")
        filename = FilenameUtil.convertSeparator(filename)
    return filename

def allElementsAreScannable(arg):
    for each in arg:
        if not isinstance(each, Scannable):
            return False
    return True

def allElementsAreListOfNumber(arg):
    for each in arg:
        if not type(each)==ListType:
            return False
        for item in each:
            if not (type(item)==FloatType or type(item)==IntType):
                return False
    return True

def allElementsAreNumber(arg):
    for each in arg:
        if not (type(each)==FloatType or type(each)==IntType):
            return False
    return True

def allElementsAreTuplesOfNumbers(arg):
    for each in arg:
        # Check its a tuple
        if not (type(each)==TupleType):
            return False
        # Check all elements of the tuple are numbers
        elif not allElementsAreNumber(each):
            return False
    return True

def analyserscan(*args):
    ''' a more generalised scan that extends standard GDA scan syntax to support
    1. scannable tuple (e.g. (s1,s2,...) argument) as scannable group and
    2. its corresponding path tuple (e.g. tuple of position lists), if exist, and
    3. detector that takes a region sequence file name as input, if exist, and
    4. syntax 'analyserscan detector "user.seq ...' for analyser scan only
    It parses input parameters described above before delegating to the standard GDA scan to do the actual data collection.
    Thus it can be used anywhere the standard GDA 'scan' is used.
    '''
    newargs=[]
    i=0;
    sequence_detector = None

    while i < len(args):
        arg = args[i]

        if isinstance(arg,  IAnalyserSequence):
            sequence_detector = arg
            xmldir = InterfaceProvider.getPathConstructor().getVisitSubdirectory('xml') + os.sep;

            newargs.append(sequence_detector)
            try:
                #Get file name and skip over this argument as only needed for setup, should not be added to newargs
                i = i + 1
                filename = args[i]
            except IndexError:
                raise IndexError("Next argument after " + sequence_detector.getName() + " needs to be a sequence file.")
            #Check if file exists, if not try with xmldir path added
            if not os.path.isfile(filename):
                filename = os.path.join(xmldir, filename)

            if (OsUtil.isWindows()) :
                FilenameUtil.setPrefix("D:")
                filename=FilenameUtil.convertSeparator(filename)

            if not os.path.isfile(filename):
                raise Exception("Unable to find file " + filename)

            sequence_detector.setSequenceFile(filename)

        elif type(arg)==TupleType:
            if allElementsAreScannable(arg):
                #parsing (scannable1, scannable2,...) as scannable group
                scannablegroup = ScannableGroup()
                for each in arg:
                    scannablegroup.addGroupMember(each)
                scannablegroup.setName("pathgroup")
                newargs.append(scannablegroup)
            elif allElementsAreListOfNumber(arg):
                #parsing scannable group's position lists
                newargs.append(arg)
            elif allElementsAreNumber(arg):
                #parsing scannable group's position lists
                newargs.append(arg)
            elif allElementsAreTuplesOfNumbers(arg):
                # This case is to fix BLIX-206 when using a scannable group with a tuple of tuples of positions
                newargs.append(arg)
            else:
                raise TypeError, "Only tuple of scannables, tuple of numbers, tuple of tuples of numbers, or list of numbers are supported."

        else:
            newargs.append(arg)

        i = i + 1

    #This ensures zeroscannable doesn't ever sneak into scan and add useless extra dimension.
    #Only ever added to newargs if no other scannable with suitable arguments qualifies.
    if check_needs_zeroscannable(newargs):
        newargs.insert(0, 1)
        newargs.insert(0, 0)
        newargs.insert(0, 0)
        newargs.insert(0, zeroScannable)

    if newargs[0] == sequence_detector:
        raise SyntaxError(sequence_detector.getName() + " with other scannables should be after scannable steps e.g 'analyserscan x 1 2 1 " + sequence_detector.getName() + " \"user.seq\" '")

    scan(newargs)

def check_needs_zeroscannable(args):
    """
    Loop through scannables with their arguments. We are checking to see if there is a
    valid scannable for the scan e.g "scan x 1 2 1" OR "scan x (1, 2, 3)". If there isn't,
    return True as need zeroscannable, otherwise False.
    """
    zero_scannable_needed = True
    scannableswithargs_list = scan.parseArgsIntoArgStruct(args)

    for scannablewithargs in scannableswithargs_list:
        for argindex in range(len(scannablewithargs)):
            if argindex > 1 or isinstance(scannablewithargs[argindex], tuple):
                zero_scannable_needed = False
                break
    return zero_scannable_needed

from gda.jython.commands.GeneralCommands import alias
alias("analyserscan")

BEAMLINE = LocalProperties.get("gda.beamline.name")
if BEAMLINE == "i09":
    from gdaserver import ew4000 #@UnresolvedImport
    detector = ew4000.getName()
elif BEAMLINE == "i09-1":
    from gdaserver import analyser #@UnresolvedImport
    detector = analyser.getName()
elif BEAMLINE == "p60":
    #ToDo - Add P60 here
    detector = "PLACEHOLDER"
else:
    raise RuntimeError("{} does not support analyserscan.".format(BEAMLINE))

print("-"*100)
print("Created 'analyserscan' command for the electron analyser. Wraps scan command to give sequence file to electron analyser that defines list of regions.")
print("    Syntax:  analyserscan [scannable1 start stop step ...] " + detector + " 'filename' [scannable2 [pos] ...] ")
print("")

# I09-70 Create a empty string to hold detectors to be used with the GUI
extraDetectors = ""
