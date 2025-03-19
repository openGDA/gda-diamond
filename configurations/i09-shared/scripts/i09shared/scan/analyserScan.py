'''
Created on 15 May 2013

@author: fy65
'''
import os
from org.opengda.detector.electronanalyser.nxdetector import IAnalyserSequence #@UnresolvedImport
from gda.jython import InterfaceProvider #@UnresolvedImport
from gda.device.scannable import DummyScannable #@UnresolvedImport
from types import TupleType
from gda.device.scannable.scannablegroup import ScannableGroup #@UnresolvedImport
from gdascripts.scan.installMultiRegionalScanWithProcessing import mrscan # @UnusedImport
from i09shared.utils.check_scan_arguments import all_elements_are_list_of_number, all_elements_are_number, all_elements_are_scannable, all_elements_are_tuples_of_numbers

from org.opengda.detector.electronanalyser.api import SESSequence, SESSequenceHelper #@UnresolvedImport

zeroScannable = DummyScannable("zeroScannable")
#Add to namespace so that it is findable during scans which is needed for extra region printing
InterfaceProvider.getJythonNamespace().placeInJythonNamespace(zeroScannable.getName(), zeroScannable);

def get_sequence_filename(arg):
    filename = arg
    if not os.path.isfile(arg):
        xmldir = InterfaceProvider.getPathConstructor().getVisitSubdirectory('xml') + os.sep;
        filename = os.path.join(xmldir, filename)
    return filename

def check_needs_zeroscannable(args):
    """
    Loop through scannables with their arguments. We are checking to see if there is a
    valid scannable for the scan e.g "scan x 1 2 1" OR "scan x (1, 2, 3)". If there isn't,
    return True as need zeroscannable, otherwise False.
    """
    zero_scannable_needed = True
    scannableswithargs_list = mrscan.parseArgsIntoArgStruct(args)

    for scannablewithargs in scannableswithargs_list:
        for argindex in range(len(scannablewithargs)):
            if argindex > 1 or isinstance(scannablewithargs[argindex], tuple):
                zero_scannable_needed = False
                break
    return zero_scannable_needed


def analyserscan(*args):
    """
    USAGE:
    analyserscan scannable1 start stop step ... detector 'filename' [scannable2 [pos] ...]
    analyserscan scannable1 ([start stop step], ...) ... detector 'filename' [scannable2 [pos] ...]

    Wraps mrscan command but gives sequence file to electron analyser that defines list of regions.
    """
    newargs=[]
    i=0;
    sequence_detector = None

    while i < len(args):
        arg = args[i]

        if isinstance(arg,  IAnalyserSequence):
            sequence_detector = arg
            newargs.append(sequence_detector)
            try:
                #Get file name and skip over this argument as only needed for setup, should not be added to newargs
                i = i + 1
                sequence_arg = args[i]
            except IndexError:
                raise IndexError("Next argument after " + sequence_detector.getName() + " needs to be a sequence file or sequence object")
            if isinstance(sequence_arg, str):
                filename = get_sequence_filename(sequence_arg)
            elif isinstance(sequence_arg, SESSequence):
                filename = sequence_arg.getFileName()
                print("Saving sequence object to file: " + filename)
                #Save sequence first so that any changes user made are reflected in the UI
                sequence_arg.save()
            else:
                raise ValueError("The argument after " + sequence_detector.getName() + " must be of type str or SESSequence.")
            sequence_detector.setSequenceFile(filename)

        elif type(arg)==TupleType:
            if all_elements_are_scannable(arg):
                #parsing (scannable1, scannable2,...) as scannable group
                scannablegroup = ScannableGroup()
                for each in arg:
                    scannablegroup.addGroupMember(each)
                scannablegroup.setName("pathgroup")
                newargs.append(scannablegroup)
            elif all_elements_are_list_of_number(arg):
                #parsing scannable group's position lists
                newargs.append(arg)
            elif all_elements_are_number(arg):
                #parsing scannable group's position lists
                newargs.append(arg)
            elif all_elements_are_tuples_of_numbers(arg):
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
        newargs = [zeroScannable, 0, 0, 1] + newargs

    if newargs[0] == sequence_detector:
        raise SyntaxError(sequence_detector.getName() + " with other scannables should be after scannable steps e.g 'analyserscan x 1 2 1 " + sequence_detector.getName() + " \"user.seq\" '")

    mrscan(newargs)

from gda.jython.commands.GeneralCommands import alias
alias("analyserscan")

# I09-70 Create a empty string to hold detectors to be used with the GUI
extraDetectors = ""
