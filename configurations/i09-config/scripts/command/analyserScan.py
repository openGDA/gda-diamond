'''
Created on 15 May 2013

@author: fy65
'''
from org.opengda.detector.electronanalyser.scan import RegionScannable, RegionPositionProvider
from gda.jython.commands.ScannableCommands import scan
from gda.factory import Finder
from org.opengda.detector.electronanalyser.event import SequenceFileChangeEvent
from gda.jython import InterfaceProvider
import os
from org.opengda.detector.electronanalyser.utils import OsUtil, FilenameUtil
from org.opengda.detector.electronanalyser.nxdetector import EW4000,\
    EW4000CollectionStrategy
from time import sleep
from gda.jython import InterfaceProvider, JythonStatus
import time
from gda.device.scannable import DummyScannable
from gdascripts.utils import caput
from gda.device import Scannable
from types import TupleType, ListType, FloatType, IntType
from gda.device.scannable.scannablegroup import ScannableGroup
#from localStation import setSubdirectory

ENABLEZEROSUPPLIES=False
PRINTTIME=False
zeroScannable=DummyScannable("zeroScannable")

def zerosupplies():
    caput("BL09I-EA-DET-01:CAM:ZERO_SUPPLIES", 1)
    

def getSequenceFilename(arg, xmldir):
    filename = xmldir + arg
    if (OsUtil.isWindows()):
        FilenameUtil.setPrefix("D:")
        filename = FilenameUtil.convertSeparator(filename)
    return filename

def isRegionValid(regionValidator, region, elementset, excitationenergy):
        if region.isEnabled():
            if not regionValidator.isValidRegion(region, elementset, excitationenergy):
                print "Region '"+region.getName()+"' is not valid."
                return False
        return True
    
def analyserscancheck(*args):
    finder=Finder.getInstance()
    regionValidator=finder.find("regionvalidator")
    dcmenergy=finder.find("dcmenergy")
    pgmenergy=finder.find("pgmenergy")
    xmldir = InterfaceProvider.getPathConstructor().getVisitSubdirectory('xml') +os.sep;
    i=0
    arg=args[i]
    i=i+1
    if isinstance(arg, EW4000):
        filename = getSequenceFilename(args[i], xmldir)
        NotEnergyScan=True
    elif isinstance(arg, Scannable):
        if arg.getName()=="ienergy" or arg.getName()=="dcmenergy" or arg.getName()=="jenergy" or arg.getName()=="pgmenergy" :
            excitationEnergy_start=args[i]
            i=i+1
            excitationEnergy_stop=args[i]
            i=i+1
            NotEnergyScan=False
        else:
            i=i+2
            NotEnergyScan=True
        while i<len(args):
            arg=args[i]
            i=i+1
            if isinstance( arg,  EW4000 ):
                filename = getSequenceFilename(args[i], xmldir)
                break
    arg.setSequenceFilename(filename)
    sequence=arg.loadSequenceData(filename)
    allRegionsValid=True
    for region in sequence.getRegion():
        if NotEnergyScan:
            if region.getExcitationEnergy()>arg.getCollectionStrategy().getXRaySourceEnergyLimit():
                excitationEnergy=float(dcmenergy.getPosition())
            else:
                excitationEnergy=float(pgmenergy.getPosition())
            allRegionsValid=isRegionValid(regionValidator, region, sequence.getElementSet(), excitationEnergy) and allRegionsValid
            if not allRegionsValid:
                print "Sequence file "+filename+" contains selected invalid regions for fixed excitation energy "+str(excitationEnergy)+"."
            else:
                print "All regions in the sequence file "+filename+" are valid."
        else:
            allRegionsValid=isRegionValid(regionValidator, region, sequence.getElementSet(), excitationEnergy_start) and allRegionsValid
            if not allRegionsValid:
                print "Sequence file "+filename+" contains selected invalid regions for the start energy "+str(excitationEnergy_start)+" in an energy scan."
            else:
                print "All regions in the sequence file "+filename+" are valid for the start energy "+str(excitationEnergy_start)+" in an energy scan."

            allRegionsValid=isRegionValid(regionValidator, region, sequence.getElementSet(), excitationEnergy_stop) and allRegionsValid
            if not allRegionsValid:
                print "Sequence file "+filename+" contains selected invalid regions for the stop energy "+str(excitationEnergy_stop)+" in an energy scan."
            else:
                print "All regions in the sequence file "+filename+" are valid for the stop energy "+str(excitationEnergy_stop)+" in an energy scan."

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
    3. EW4000 analyser detector that takes a reion sequence file name as input, if exist, and
    4. syntax 'analyserscan ew4000 "user.seq ...' for analyser scan only
    It parses input parameters described above before delegating to the standard GDA scan to do the actual data collection.
    Thus it can be used anywhere the standard GDA 'scan' is used.
    '''
    starttime=time.ctime()
    if PRINTTIME: print "=== Scan started: "+starttime
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        if i==0 and isinstance(arg, EW4000):
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
        if isinstance( arg,  EW4000 ):
            controller = Finder.getInstance().find("SequenceFileObserver")
            xmldir = InterfaceProvider.getPathConstructor().getVisitSubdirectory('xml') +os.sep;
            filename=xmldir+args[i];
            if (OsUtil.isWindows()) :
                FilenameUtil.setPrefix("D:")
                filename=FilenameUtil.convertSeparator(filename)
            controller.update(controller,SequenceFileChangeEvent(filename)) #update client sequence view
            sleep(2.0)
            jythonServerStatus=InterfaceProvider.getJythonServerStatusProvider().getJythonServerStatus()
            while (jythonServerStatus.isScriptOrScanPaused()):
                sleep(1.0) # wait for user saving dirty file
            arg.setSequenceFilename(filename)
            sequence=arg.loadSequenceData(filename)
            if isinstance(arg.getCollectionStrategy(), EW4000CollectionStrategy):
                arg.getCollectionStrategy().setSequence(sequence)
            i=i+1
    scan(newargs)
    if ENABLEZEROSUPPLIES:
        zerosupplies()  # @UndefinedVariable
    
    if PRINTTIME: print ("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time()-starttime))


def analyserscan_v1(*args):
    starttime=time.ctime()
    if PRINTTIME: print "=== Scan started: "+starttime
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        newargs.append(arg)
        i=i+1
        if isinstance( arg,  RegionScannable ):
            controller = Finder.getInstance().find("SequenceFileObserver")
            xmldir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()+"xml"+os.sep;
            filename=xmldir+args[i];
            if (OsUtil.isWindows()) :
                FilenameUtil.setPrefix("D:")
                filename=FilenameUtil.convertSeparator(filename)
            controller.update(controller,SequenceFileChangeEvent(filename))
            sleep(1.0)
            while (InterfaceProvider.getScanStatusHolder().getScanStatus()==JythonStatus.PAUSED):
                sleep(1.0)
            newargs.append( RegionPositionProvider(filename) )
            #newargs.append( arg ) # to read the actual position
            i=i+1
    scan(newargs)
    if PRINTTIME: print ("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time()-starttime))


