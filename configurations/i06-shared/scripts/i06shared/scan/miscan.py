'''
Created on 31 Jan 2017

@author: fy65
'''
import time
from gda.device.detector import NXDetector
from types import TupleType, ListType, FloatType, IntType
from gda.device.scannable import DummyScannable
from gda.device import Scannable
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.device.detector.addetector.collectionstrategy import AutoSummingProcessDecorator,\
    ImageModeDecorator
from gda.jython.commands.ScannableCommands import scan

print "-"*100
print "Creating 'miscan' - multiple image per scan data point"
print "    Syntax: miscan (scannable1, scannable2) [(1,2), (3,4),(5,6)] pixis 0.1 10"

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
    starttime=time.ctime()
    if PRINTTIME: print "=== Scan started: "+starttime
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
            if allElementsAreScannable(arg):
                #parsing (scannable1, scannable2,...) as scannable group
                scannableGroup=ScannableGroup()
                for each in arg:
                    scannableGroup.addGroupMember(each)
                scannableGroup.setName("pathgroup")
                newargs.append(scannableGroup)
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
        i=i+1
        if isinstance( arg,  NXDetector ):
            decoratee = arg.getCollectionStrategy().getDecoratee()
            if isinstance(decoratee, ImageModeDecorator):
                if i<len(args)-1 and type(args[i])==IntType and (type(args[i+1])==IntType or type(args[i+1])== FloatType):
                    #support the miscan command - first input after detector is number of images per data point
                    decoratee.setNumberOfImagesPerCollection(args[i])
                elif type(args[i])==FloatType:
                    raise TypeError, "Number of images to collect per scan data point must be Int type."
                   
            else: #exposure time is the last one in the scan command
                newargs.append(args[i]) #single image per data point
            i=i+1
    scan([e for e in newargs])

    if PRINTTIME: print ("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time()-starttime))

from gda.jython.commands.GeneralCommands import alias 
alias("miscan")
