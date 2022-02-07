'''
'miscan' - a scan that collects multiple images at each scan data point. It extends the standard 'scan' syntax and 
configure the detector number of images to be collected before scan starts.

It records both 'miscan' command as well as the actual standard 'scan' command in the data file.
This command only works with detector 'mpx' which is configured to collect images in Multiple mode.
 
Created on 31 Jan 2017

@author: fy65
'''
import time
from gda.device.detector import NXDetector
from types import TupleType, ListType, FloatType, IntType, StringType
from gda.device.scannable import DummyScannable
from gda.device import Scannable
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.device.detector.addetector.collectionstrategy import ImageModeDecorator
from gda.jython.commands.ScannableCommands import scan
from gdascripts.metadata.nexus_metadata_class import meta

print("-"*100)
print("Creating 'miscan' - multiple images per scan data point")
print("    Syntax: miscan (scannable1, scannable2) [(1,2), (3,4),(5,6)] mpx 10 0.1")

PRINTTIME=False
zeroScannable=DummyScannable("zeroScannable")

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

def allElementsAreString(arg):
    for each in arg:
        if not (type(each)==StringType):
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

def miscan(*args):
    '''   a more generalised scan that extends standard GDA scan syntax to support 
        1. scannable tuple (e.g. (s1,s2,...) argument) as scannable group, 
        2. its corresponding path tuple (e.g. list of position tuples), if exist, and
        3. area detector that takes 2 input numbers - 1st input is the number of images to be collected at each point,
           if omitted it default to 1, and 2nd input is detector exposure time which must be provided,
        4. syntax 'miscan mpx 10 0.1 ...' is supported for collecting 10 images at a single point.
    
        It parses input parameters described above before delegating to the standard GDA scan to do the actual data collection.
        Thus it can be used anywhere the standard GDA 'scan' is used.
    '''
    command = "miscan " # rebuild the input command as String so it can be recored into data file
    
    starttime = time.ctime()
    start = time.time()
    if PRINTTIME: print("=== Scan started: " + starttime)
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        if i==0 and isinstance(arg, NXDetector):
            newargs.append(zeroScannable)
            newargs.append(0)
            newargs.append(0)
            newargs.append(1)
            newargs.append(arg)
        elif type(arg)==TupleType:
            command += "(" 
            if allElementsAreScannable(arg):
                #parsing (scannable1, scannable2,...) as scannable group
                scannable_group=ScannableGroup()
                scannable_names = []
                for each in arg:
                    scannable_group.addGroupMember(each)
                    scannable_names.append(each.getName())
                command += ",".join(scannable_names)
                scannable_group.setName("pathgroup")
                newargs.append(scannable_group)
            elif allElementsAreListOfNumber(arg):
                #parsing scannable group's position lists
                newargs.append(arg)
                list_of_lists = []
                for each in arg:
                    list_of_lists.append("[" + ",".join([str(x) for x in each]) +"]")
                command += ",".join(list_of_lists)
            elif allElementsAreNumber(arg):
                #parsing scannable group's position lists
                newargs.append(arg)
                command += ",".join([str(x) for x in arg])
            elif allElementsAreTuplesOfNumbers(arg):
                # This case is to fix BLIX-206 when using a scannable group with a tuple of tuples of positions
                newargs.append(arg)
                list_of_tuples = []
                for each in arg:
                    list_of_tuples.append("(" + ",".join([str(x) for x in each]) +")")
                command += ",".join(list_of_lists)                
            elif allElementsAreString(arg):
                newargs.append(arg)
                command += ",".join(arg)
            else:
                raise TypeError, "Only tuple of scannables, tuple of numbers, tuple of tuples of numbers, list of numbers, or tuple of Strings are supported."
            command += ") "
        else:
            newargs.append(arg)
            if isinstance(arg, Scannable):
                command += arg.getName() + " "
            if type(arg)==IntType or type(arg)== FloatType:
                command += str(arg) + " "
        i=i+1
        if isinstance( arg,  NXDetector ):
            if str(arg.getName()) == "medipix":
                command += "mpx "
            else:
                command += str(arg.getName()) + " "
            CACHE_PARAMETER_TOBE_CHANGED = False 
            cs = arg.getCollectionStrategy()
            decoratee = cs.getDecoratee()
            adbase = cs.getDecoratee().getDecoratee().getDecoratee().getDecoratee().getDecoratee().getAdBase()
            if adbase is not None:
                #capture current detector settings before change them
                image_mode = adbase.getImageMode()
                num_images = adbase.getNumImages()
                CACHE_PARAMETER_TOBE_CHANGED = True
            if isinstance(decoratee, ImageModeDecorator):
                decoratee.setImageMode(1) #this will make sure metadata in detector setting are correct as decoratee setting comes after metadata are collected
                if i<len(args)-1: # more than 2 arguments following detector
                    if type(args[i])==IntType and (type(args[i+1])==IntType or type(args[i+1])== FloatType):
                        #support the miscan command - first input after detector is number of images per data point
                        decoratee.setNumberOfImagesPerCollection(args[i])
                    elif type(args[i])==FloatType and (type(args[i+1])==IntType or type(args[i+1])== FloatType):
                        raise TypeError, "Number of images to collect per scan data point must be Int type."
                    elif type(args[i])==FloatType and not (type(args[i+1])==IntType or type(args[i+1])== FloatType):
                        decoratee.setNumberOfImagesPerCollection(1)
                    command += str(args[i]) + " "
                elif i==len(args)-1: #followed by only one argument - must be exposure time
                    decoratee.setNumberOfImagesPerCollection(1)
            else: #exposure time is the last one in the scan command
                newargs.append(args[i]) #single image per data point
                command += str(args[i])
            i=i+1
    
    meta.addScalar("user_input", "command", command)
    try:
        scan([e for e in newargs])
    finally:
        #restore detector settings
        if CACHE_PARAMETER_TOBE_CHANGED:
            adbase.setImageMode(image_mode)
            adbase.setNumImages(num_images)
            
        meta.rm("user_input", "command")    

    if PRINTTIME: print("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time() - start))

from gda.jython.commands.GeneralCommands import alias 
alias("miscan")
