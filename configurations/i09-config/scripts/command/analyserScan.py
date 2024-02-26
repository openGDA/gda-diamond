'''
Created on 15 May 2013

@author: fy65
'''
from org.opengda.detector.electronanalyser.scan import RegionScannable, RegionPositionProvider
from gda.factory import Finder
from org.opengda.detector.electronanalyser.event import SequenceFileChangeEvent
import os
from org.opengda.detector.electronanalyser.utils import OsUtil, FilenameUtil
from org.opengda.detector.electronanalyser.nxdetector import EW4000
from time import sleep
from gda.jython import InterfaceProvider, JythonStatus
import time
from gda.device.scannable import DummyScannable
from gdascripts.utils import caput
from gda.device import Scannable
from types import TupleType, ListType, FloatType, IntType
from gda.device.scannable.scannablegroup import ScannableGroup
from gdascripts.scan.installStandardScansWithProcessing import scan


ENABLEZEROSUPPLIES=False
PRINTTIME=False
zeroScannable=DummyScannable("zeroScannable")

def zerosupplies():
    caput("BL09I-EA-DET-01:CAM:ZERO_SUPPLIES", 1)

def getSequenceFilename(arg):
    filename = arg
    if not os.path.isfile(arg):
        xmldir = InterfaceProvider.getPathConstructor().getVisitSubdirectory('xml') + os.sep;
        filename = os.path.join(xmldir, filename)
    if (OsUtil.isWindows()):
        FilenameUtil.setPrefix("D:")
        filename = FilenameUtil.convertSeparator(filename)
    return filename

def isRegionValid(regionValidator, region, elementset, excitationenergy):
    if region.isEnabled():
        if not regionValidator.isValidRegion(region, elementset, excitationenergy):
            return False
    return True

def analyserscancheck(*args):
    
    region_validator=Finder.find("regionvalidator")

    ew4000 = None
    
    energy_scan = False
    
    pgm_excitation_energy_start = []
    pgm_excitation_energy_stop  = []
    
    dcm_excitation_energy_start = []
    dcm_excitation_energy_stop  = []
    
    args = list(args)

    scannable_name = ""

    i = 0
    while i < len(args):
        arg = args[i]
        
        if isinstance( arg,  EW4000 ):
            ew4000 = arg     
            filename = getSequenceFilename(args[i + 1])
            i = i + 1
            continue
        
        elif not isinstance(arg, Scannable):
            i = i + 1
            continue
        
        #If energy scan values are used, we need to validate our regions against these
        elif arg.getName() =="ienergy" or arg.getName()=="dcmenergy" or arg.getName()=="dcmenergyEv" or arg.getName()=="jenergy" or arg.getName()=="pgmenergy" :
            try:
                scannable_name = arg.getName()

                if isinstance(args[i + 1], tuple):
                    params = args[i + 1]
                    i = i + 1
                else:
                    params = tuple(args[i + 1], args[i + 2], args[i + 3])
                    i = i + 3
                
                if arg.getName() =="ienergy" or arg.getName()=="dcmenergy" or arg.getName()=="dcmenergyEv":
                    min_param = min(params)
                    max_param = max(params)
                    #Convert from keV to eV
                    if arg.getName() =="ienergy" or arg.getName()=="dcmenergy":
                        min_param = min_param * 1000
                        max_param = max_param * 1000
                    dcm_excitation_energy_start.append(min_param)
                    dcm_excitation_energy_stop.append(max_param)

                    
                elif arg.getName() =="jenergy" or arg.getName()=="pgmenergy":

                    pgm_excitation_energy_start.append(min(params))
                    pgm_excitation_energy_stop.append(max(params))
                    
            except IndexError:
                raise SyntaxError(
                    "Incorrect syntax for " + arg.getName()
                )
            energy_scan = True
                
        i = i + 1
        
    sequence = ew4000.loadSequenceData(filename)
    regions = sequence.getRegion()
    print("")
    
    element_set = ew4000.getAnalyser().getPsuMode()
    xray_limit = ew4000.getRegionDefinitionResourceUtil().getXRaySourceEnergyLimit()
    
    invalid_regions = []
    
    def print_invalid_message(region, exctiation_energy):
        
        if not valid_region:
            invalid_regions.append(region.getName())
            print("Region " + region.getName() + " is not valid at " + scannable_name + " " + str(exctiation_energy) + " eV.")
    
    for region in regions:
        
        valid_region = False
        
        if energy_scan:
            
            for i in range(0, len(dcm_excitation_energy_start)):
                
                #If this is a pgm, we only want to check it's valid against pgm and not the dcm scannable args
                if region.getExcitationEnergy() < xray_limit:
                    valid_region = isRegionValid(region_validator, region, element_set, region.getExcitationEnergy())
                    print_invalid_message(region, region.getExcitationEnergy())
                    break
                #Check all dcm scannable args are valid for region
                else:
                    valid_region = isRegionValid(region_validator, region, element_set, dcm_excitation_energy_start[i])
                    print_invalid_message(region, dcm_excitation_energy_start[i])
                    
                    valid_region = isRegionValid(region_validator, region, element_set, dcm_excitation_energy_stop[i])
                    print_invalid_message(region, dcm_excitation_energy_stop[i])
                
            for i in range(0, len(pgm_excitation_energy_start)):
                
                if region.getExcitationEnergy() > xray_limit:
                    valid_region = isRegionValid(region_validator, region, element_set, region.getExcitationEnergy())
                    print_invalid_message(region, region.getExcitationEnergy())
                    break
                    
                else:      
                    valid_region = isRegionValid(region_validator, region, element_set, pgm_excitation_energy_start[i])
                    print_invalid_message(region, pgm_excitation_energy_start[i])
                    
                    valid_region = isRegionValid(region_validator, region, element_set, pgm_excitation_energy_stop[i])
                    print_invalid_message(region, pgm_excitation_energy_stop[i])
        else:
            dcmenergy=Finder.find("dcmenergyEv")
            pgmenergy=Finder.find("pgmenergy")
            
            excitation_energy = float(pgmenergy.getPosition())
            if region.getExcitationEnergy() > xray_limit:
                excitation_energy = float(dcmenergy.getPosition())
                
            valid_region = isRegionValid(region_validator, region, element_set, excitation_energy)
            print_invalid_message(region, excitation_energy)
            
    if len(invalid_regions) == 0:
        print("All regions are valid!")

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

from gda.configuration.properties import LocalProperties  
from gda.device.scannable import ScannableBase
from gda.device import Detector
from gda.data.scan.datawriter import NexusScanDataWriter

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
    
    scannables = []
    ew4000 = None
    
    while i < len(args):
        arg = args[i]
            
        if isinstance(arg,  EW4000):
            ew4000 = arg
            controller = Finder.find("SequenceFileObserver")
            xmldir = InterfaceProvider.getPathConstructor().getVisitSubdirectory('xml') + os.sep;
            
            newargs.append(ew4000)
            try:
                #Get file name and skip over this argument as only needed for setup, should not be added to newargs
                i = i + 1
                filename = args[i]
            except IndexError:
                raise IndexError("Next argument after " + ew4000.getName() + " needs to be a sequence file.")
            #Check if file exists, if not try with xmldir path added
            if not os.path.isfile(filename):
                filename = os.path.join(xmldir, filename)

            if (OsUtil.isWindows()) :
                FilenameUtil.setPrefix("D:")
                filename=FilenameUtil.convertSeparator(filename)

            if not os.path.isfile(filename):
                raise Exception("Unable to find file " + filename)

            if controller is not None:
                controller.update(controller, SequenceFileChangeEvent(filename)) #update client sequence view
            sleep(2.0)
            jython_server_status = InterfaceProvider.getJythonServerStatusProvider().getJythonServerStatus()
            while (jython_server_status.isScriptOrScanPaused()):
                sleep(1.0) # wait for user saving dirty file
            ew4000.loadSequenceData(filename)
            
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
    if analyserscancheckneedszeroscannable(newargs):
        newargs.insert(0, 1)
        newargs.insert(0, 0)
        newargs.insert(0, 0)
        newargs.insert(0, zeroScannable)
        
    if newargs[0] == ew4000:
        raise SyntaxError(ew4000.getName() + " with other scannables should be after scannable steps e.g 'analyserscan x 1 2 1 " + ew4000.getName() + " \"user.seq\" '")
      
    #For extra ew4000 region printing, give it only scannables 
    for i in newargs:
        if isinstance(i, ScannableBase) and not isinstance(i, Detector):
            scannables.append(i)   
    if ew4000 is not None and ew4000.isExtraRegionPrinting():
        ew4000.configureExtraRegionPrinting(scannables)
    
    cached_file_at_scan_start_value = LocalProperties.check(NexusScanDataWriter.PROPERTY_NAME_CREATE_FILE_AT_SCAN_START, False)
    cached_datawriter_value =  LocalProperties.get(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT)
    try:
        #For region data to be written straight away rather than caching, the 
        #file needs to be created at start of scan instead after the first 
        #point in scan
        LocalProperties.set(NexusScanDataWriter.PROPERTY_NAME_CREATE_FILE_AT_SCAN_START, True)
        LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "NexusScanDataWriter")
        scan(newargs)
    finally:
        LocalProperties.set(NexusScanDataWriter.PROPERTY_NAME_CREATE_FILE_AT_SCAN_START, cached_file_at_scan_start_value)
        LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, cached_datawriter_value)
        
    if ENABLEZEROSUPPLIES:
        zerosupplies()  # @UndefinedVariable
    
    if PRINTTIME: print ("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time()-starttime))

def analyserscancheckneedszeroscannable(args):
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
            controller = Finder.find("SequenceFileObserver")
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

