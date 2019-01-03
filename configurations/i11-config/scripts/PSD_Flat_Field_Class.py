'''
This module implements flat field calibration of PSD detector described in document 
S:\Science\Beamlines\Approved\I11\Beamline Manuals\PSD\PSD_Flat_Field_notes_v0.4.doc.
It consists of two type of scans:
1. 2 quick scans of 1 minimum duration to calculate number of scans required for a full flat field calibration;
2. several slow scans for a full flat field data to the specified counts (>100000);
3. sum all slow scan raw count together to provide one single flat field calibration file;
4. plot the summed data to identify dead channels, so they can be set in the bad channel list file (outside this script);
5. set GDA to use this new flat field calibration data file for PSD.

It has the following default values:
START_ANGLE               = -15
STOP_ANGLE                = 80
REQUIRED_PIXEL_COUNT      =100000
QUICK_SCAN_TIME           = 60   # 1 min scan
SLOW_SCAN_TIME            = 1800 # 30 mins scn

PSD_FLATFIELD_DIR="/dls_sw/i11/software/var/mythen/diamond/flatfield"
PSD_CALIBRATION_DIR="/dls_sw/i11/software/var/mythen/diamond/calibration"
CURRENT_FLAT_FIELD_FILE="/dls_sw/i11/software/var/mythen/diamond/flatfield/current_flat_field_file"
BAD_CHANNEL_LIST=PSD_CALIBRATION_DIR+os.sep+"badchannel_detector.lst"

Usage:
    To run with default parameters, just type
    >>>flatfield
    To change start angle
    >>>flatfield.setStartAngle(-15)
    To change stop angle
    >>>flatfield.setStopAngle(79.5)
    To change quick scan time
    >>>flatfield.setQuickScanTime(60)
    To change slow scan time
    >>>flatfield.setSlowScanTime(1800)
    To set the required pixel count for the flat field
    >>>flatfield.setRequiredPixelCountForFlatFieldCalibration(100000)
    
It is recommended the pixel count for a good flat field calibration must be at least 100000.
    
Created on 25 Jul 2012
updated on 20 Jan 2014

@author: fy65
'''
import os
import datetime
#from localStation import getSubdirectory, setSubdirectory
from gda.device.scannable import ScannableMotionBase
from gda.jython.commands.GeneralCommands import alias
import math
import threading
from time import sleep
from plot import plot,RAW
from gda.data import NumTracker
from gdascripts.utils import caget

#default vaules
START_ANGLE               = -15
STOP_ANGLE                = 79.5
REQUIRED_PIXEL_COUNT      =100000
QUICK_SCAN_TIME           = 60   # 1 min scan
SLOW_SCAN_TIME            = 1800 # 30 mins scn

PSD_FLATFIELD_DIR="/dls_sw/i11/software/var/mythen/diamond/flatfield"
PSD_CALIBRATION_DIR="/dls_sw/i11/software/var/mythen/diamond/calibration"
CURRENT_FLAT_FIELD_FILE="/dls_sw/i11/software/var/mythen/diamond/flatfield/current_flat_field_calibration"
BAD_CHANNEL_LIST=PSD_CALIBRATION_DIR+os.sep+"badchannel_detector_standard.lst"
scanNumTracker = NumTracker("i11");

class FlatFieldCalibration(ScannableMotionBase):
    def __init__(self, name, motor=delta, detector=mythen, beamenergy=energy): #@UndefinedVariable
        self.setName(name)
        self.setInputNames([name])
        self.motor=motor
        self.detector=detector
        self.setLowerGdaLimits(START_ANGLE)
        self.setUpperGdaLimits(STOP_ANGLE)
        self.requiredpixelcount=REQUIRED_PIXEL_COUNT
        self.quickscantime=QUICK_SCAN_TIME
        self.slowscantime=SLOW_SCAN_TIME
        self.setLevel(3)
        self.setOutputFormat([])
        self.energy=beamenergy
        self.originalsubdir=None
        self.originaldeltavelocity=None
        self._busy=False
        self.originalflatfieldcalibrationfile=None
        self.sum_flat_field_file=None
        
    def setRequiredPixelCountForFlatFieldCalibration(self, count):
        self.requiredpixelcount=count
        
    def getRequiredPixelCountForFlatFieldCalibration(self):
        return self.requiredpixelcount
    
    def setQuickScanTime(self, time):
        self.quickscantime=time
    
    def getQuickScanTime(self):
        return self.quickscantime
    
    def setSlowScanTime(self,time):
        self.slowscantime=time
        
    def getSlowScanTime(self):
        return self.slowscantime
    
    def setStartAngle(self, start):
        self.setLowerGdaLimits(start)
    
    def getStartAngle(self):
        return self.getLowerGdaLimits()[0]
    
    def setStopAngle(self, stop):
        self.setUpperGdaLimits(stop)
        
    def getStopAngle(self):
        return self.getUpperGdaLimits()[0]
    
    def atScanStart(self):
        pass
    
    def prepareFlatFieldCollection(self):
        scanNumTracker.incrementNumber()
        self.originalsubdir=getSubdirectory()  # @UndefinedVariable
        self.originaldeltavelocity=float(self.motor.getSpeed())
        #create a new directory to store flat field calibration data if not yet exist
        setSubdirectory("PSD")  # @UndefinedVariable
        setSubdirectory("PSD/"+datetime.date.today().strftime("%Y%m%d"))  # @UndefinedVariable
        print "moving delta motor to start angle: " + str(float(self.getLowerGdaLimits()[0])) +" Please wait..."
        self.motor.setSpeed((float(self.getUpperGdaLimits()[0])-float(self.getLowerGdaLimits()[0]))/self.quickscantime)
        self.motor.moveTo(float(self.getLowerGdaLimits()[0]))
        print "delta motor is now at start angle: "+str(self.motor.getPosition())
        
    def atScanEnd(self):
        pass
    
    def stop(self):
        self.detector.stop()
        self.motor.stop()
        if self.originalsubdir is not None:
            setSubdirectory(self.originalsubdir)  # @UndefinedVariable
        if self.originaldeltavelocity is not None:
            self.motor.setSpeed(self.originaldeltavelocity)
        
        
    def rawAsynchronousMoveTo(self, count=None):
        t1=threading.Thread(target=self.flatFieldScan,name="FlatFieldScan", args=(count,))
        t1.start()
        
    def flatFieldScan(self, count=None):
        try:
            self._busy=True
            if count is not None:
                self.setRequiredPixelCountForFlatFieldCalibration(int(count))
            self.prepareFlatFieldCollection()
            print "starting 2 one minute scans to calculate how long to scan for a complete flat field calibration at energy %s" % str(self.energy.getPosition())
            #collect two 1min frames
            self.scanFlatField(2,self.quickscantime+10)
            averagecount=averageScanRawCount(2, self.detector)
            numberofscan=int(math.ceil(self.requiredpixelcount/averagecount*self.quickscantime/self.slowscantime))
    
            print "starting %d flat field calibration scans. Total time to complete is %f seconds." % (numberofscan, (self.slowscantime+30)*numberofscan)
            self.motor.setSpeed((float(self.getUpperGdaLimits()[0])-float(self.getLowerGdaLimits()[0]))/self.slowscantime)
            self.scanFlatField(numberofscan, self.slowscantime+30)
            
            print "Sum all scanned raw data into one flat field data file..."
            self.sum_flat_field_file = sumScanRawData(numberofscan)
            #plot and view flat field raw data in SWING GUI
            try:
                plot(RAW,self.sum_flat_field_file)
            except:
                print "Plot flat field data from .raw data file failed."
                print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]  # @UndefinedVariable
                            
            print "Please check the flat field file for any dead pixels, etc.and check that all the bad channels are in the bed channel list at "+BAD_CHANNEL_LIST
            #apply this flat field correction to PSD in GDA permanently
            self.applyFlatFieldCalibration()
        except:
            print "Flat field Collection aborted."
            print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]  # @UndefinedVariable
        finally:
            print "Flat Field Collection Completed."
            self.stop()
            self._busy=False
    
    def rawIsBusy(self):
        return self._busy
        
    def rawGetPosition(self):
        if self.sum_flat_field_file is None:
            print "New flat field file not created yet."
            return 0
        return self.sum_flat_field_file
        
    def scanFlatField(self, numberofscan, time):
        self.detector.setCollectionTime(time)
        scancounter=0
        self.detector.atScanStart() #to initialise collection number and scan number in GDA mythen object
        while scancounter < numberofscan:
            if (scancounter % 2 == 0):
                print "moving delta to %f ..." % (self.getUpperGdaLimits()[0])
                self.motor.asynchronousMoveTo(float(self.getUpperGdaLimits()[0]))
            else:
                print "moving delta to %f ..." % (self.getLowerGdaLimits()[0])
                self.motor.asynchronousMoveTo(float(self.getLowerGdaLimits()[0]))
            self.detector.collectData()
            sleep(2) #must give time for detector for detector to respond to request.
            while self.detector.isBusy():
            #while caget("BL11I-EA-DET-03:DET:Acquire")==1:
                sleep(1)
            sleep(1)
            self.detector.atPointEnd()
            scancounter += 1
        self.detector.atScanEnd()
        
    def applyFlatFieldCalibration(self):
        if self.sum_flat_field_file is not None:
            self.originalflatfieldcalibrationfile=os.readlink(CURRENT_FLAT_FIELD_FILE)
            os.unlink(CURRENT_FLAT_FIELD_FILE)
            os.symlink(self.sum_flat_field_file, CURRENT_FLAT_FIELD_FILE)
            print "Current Flat Field data file is update to " + os.readlink(CURRENT_FLAT_FIELD_FILE)
            changeFlatFieldCalibrationTo(CURRENT_FLAT_FIELD_FILE)
            #print "You now need to run 'reset_namespace' for this to take effect! "
            print "IMPORTANT: You must reset delta limits, theta position, and backstop now!!!"
        else:
            print "Flat field calibration file is not available."
        
    def revertFlatFieldCalibration(self):
        if self.originalflatfieldcalibrationfile is not None:
            os.unlink(CURRENT_FLAT_FIELD_FILE)
            os.symlink(self.originalflatfieldcalibrationfile, CURRENT_FLAT_FIELD_FILE)
            print "Current Flat Field data file is update to " + os.readlink(CURRENT_FLAT_FIELD_FILE)
            changeFlatFieldCalibrationTo(CURRENT_FLAT_FIELD_FILE)
            #print "You now need to run 'reset_namespace' for this to take effect! "
            print "IMPORTANT: You must reset delta limits, theta position, and backstop now!!!"
        else:
            print "There is no original flat field calibration file available."

    def whichFlatFieldCalibration(self):
        return "Current Flat Field data file is " + os.readlink(CURRENT_FLAT_FIELD_FILE)
            
def read_raw_data(filename):
    ''' Reads the lines from the specified Mythen raw data file, 
    and returns an array of (channel, count) tuples'''
    f=open(filename,"rb")
    lines=f.readlines()
    f.close()
    return [tuple(map(int, l.strip().split(" "))) for l in lines]

previous_flatfield_calibration_file=None

def changeFlatFieldCalibrationTo(real_flatfield_filename, detector=mythen):  # @UndefinedVariable
    if os.path.isfile(real_flatfield_filename):
        try:
            previous_flatfield_calibration_file=os.readlink(CURRENT_FLAT_FIELD_FILE)
            os.unlink(CURRENT_FLAT_FIELD_FILE)
            if os.path.isabs(real_flatfield_filename):
                os.symlink(real_flatfield_filename, CURRENT_FLAT_FIELD_FILE)
            else:
                os.symlink(os.path.join(PSD_FLATFIELD_DIR,real_flatfield_filename), CURRENT_FLAT_FIELD_FILE)
                
            print "Current Flat Field data file is update to " + str(os.readlink(CURRENT_FLAT_FIELD_FILE))
            from gda.device.detector.mythen.data import MythenRawDataset
            from java.io import File
            detector.getDataConverter().setFlatFieldData(MythenRawDataset(File(CURRENT_FLAT_FIELD_FILE)))
            print "Mythen detector will now use the new flatfield calibration data stored at " + str(os.readlink(CURRENT_FLAT_FIELD_FILE))
        except:
            raise(Exception("Update Flatfield Calibration Data Failed!"))
    else:
        print "Flat field calibration file "+ str(real_flatfield_filename) +" is not exist. Please ensure you provide the full path name."
            
def averageScanRawCount(numberofscan, detector=mythen): #@UndefinedVariable
    filenames = []
    for i in range(numberofscan):
        filenames.append(str(detector.getDataDirectory()) + str(os.sep) + str(detector.buildRawFilename(i+1)))
    rawdata=[]
    data = map(read_raw_data, filenames)
    for eachframe in data:
        rawdata += eachframe
    counts=[count for channel, count in rawdata] #@UnusedVariable
    average=int(sum(counts)/len(counts))
    print "Average count for 1 minute scan is %d " %  average
    return average


def sumScanRawData(numberofscan, beamenergy=energy, detector=mythen): #@UndefinedVariable
    filenames = []
    for i in range(numberofscan):
        filenames.append(str(detector.getDataDirectory()) + str(os.sep) + str(detector.buildRawFilename(i+1)))
    
    now = datetime.datetime.now()
    photonenergy = int(round(float(beamenergy.getPosition())))
    sum_flat_field_file = PSD_FLATFIELD_DIR + str(os.sep) + "Sum_Flat_Field_E" + str(photonenergy) + "keV_T" + str(photonenergy*1000/2) + "eV_" + now.strftime("%Y%m%d") + ".raw"
    summedfile = open(sum_flat_field_file, "w")
    data = map(read_raw_data, filenames)
    for channel in range(len(data[0])):
        values = [data[i][channel][1] for i in range(len(data))]
        summedfile.write("%d %d\n" % (channel, sum(values)))
    
    summedfile.flush()
    summedfile.close()
    print "Summation completed: Flat Field Calibration file is " + sum_flat_field_file
    return sum_flat_field_file

flatfield=FlatFieldCalibration("flatfield")
alias("faltfield")



    
    
    
    
    
