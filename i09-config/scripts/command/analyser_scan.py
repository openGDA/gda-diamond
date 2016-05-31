'''
Created on 15 May 2013

@author: fy65
'''
from org.opengda.detector.electronanalyser.scan import RegionScannable, RegionPositionProvider
from gda.jython.commands.ScannableCommands import scan
from gda.factory import Finder
from org.opengda.detector.electronanalyser.event import SequenceFileChangeEvent
from gda.data import PathConstructor
import os
from org.opengda.detector.electronanalyser.utils import OsUtil, FilenameUtil
from org.opengda.detector.electronanalyser.nxdetector import EW4000,\
    EW4000CollectionStrategy
from time import sleep
from gda.jython import InterfaceProvider, Jython
import time
from gda.device.scannable import DummyScannable
from gdascripts.utils import caput
from gda.device import Scannable
#from localStation import setSubdirectory

ENABLEZEROSUPPLIES=True
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
    xmldir = PathConstructor.createFromDefaultProperty()+"xml"+os.sep;
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

def analyserscan(*args):
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
        i=i+1
        if isinstance( arg,  EW4000 ):
            controller = Finder.getInstance().find("SequenceFileObserver")
            xmldir = PathConstructor.createFromDefaultProperty()+"xml"+os.sep;
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
            xmldir = PathConstructor.createFromDefaultProperty()+"xml"+os.sep;
            filename=xmldir+args[i];
            if (OsUtil.isWindows()) :
                FilenameUtil.setPrefix("D:")
                filename=FilenameUtil.convertSeparator(filename)
            controller.update(controller,SequenceFileChangeEvent(filename))
            sleep(1.0)
            while (InterfaceProvider.getScanStatusHolder().getScanStatus()==Jython.PAUSED):
                sleep(1.0)
            newargs.append( RegionPositionProvider(filename) )
            #newargs.append( arg ) # to read the actual position
            i=i+1
    scan(newargs)
    if PRINTTIME: print ("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time()-starttime))

def analyserscanenergyfirst(*args):
    argsbeforeregions=[]
    argsafterregions=[]
    i=0;
    while i< len(args):
        arg = args[i]
        argsbeforeregions.append(arg)
        i=i+1
        if isinstance( arg,  RegionScannable ):
            controller = Finder.getInstance().find("SequenceFileObserver")
            filename= os.path.join(PathConstructor.createFromDefaultProperty(),"xml",args[i])
            #xmldir = PathConstructor.createFromDefaultProperty()+"xml"+os.sep;
            #filename=xmldir+args[i];
            if (OsUtil.isWindows()) :
                os.path.join("D:", filename)
                #FilenameUtil.setPrefix("D:")
                #filename=FilenameUtil.convertSeparator(filename)
            posProvider=RegionPositionProvider(filename)
            controller.update(controller,SequenceFileChangeEvent(filename))
            regionlist=[]
            for index in range(posProvider.size()):
                #print index
                regionlist.append( posProvider.get(index) )
                #scanargs[j].append( arg ) # to read the actual position
            break
    i=i+1
    while i < len(args):
        arg = args[i]
        argsafterregions.append(arg)
        i=i+1

    for region in regionlist:
        newargs=[]
        newargs=argsbeforeregions + [RegionPositionProvider(region)] + argsafterregions
        #print str(newargs)
        print "performing scan for "+region.getName() +" data collection ..."
        scan(newargs)
        
