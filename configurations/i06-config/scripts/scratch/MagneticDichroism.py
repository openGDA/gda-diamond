#The device class used on the Magnetic Dichroism Spectroscopy and Microscopy.


from gda.device.detector import PseudoDetector
from gda.device.scannable import PseudoDevice
from gda.device import Detector


from gda.analysis.io import PilatusTiffLoader, JPEGLoader, TIFFImageLoader
from gda.analysis import ScanFileHolder
from gda.analysis import RCPPlotter;

from gda.data import PathConstructor
from gda.data import NumTracker;

#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();


from time import sleep;
import math;
import sys, os, stat, shutil;


#import cPickle as pickle
#import threading;
#import synchronize;

import __main__ as gdamain

class PolarisationError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)
    
class EnergyError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)
    
class MagneticDichroismDevice(object):
                           #Reference            Real value                 
    PolarisationCommand={   'LinearHorizontal' : 'Horizontal',
                            'LinearVertical'   : 'Vertical',
                            'PositiveCircular' : 'PosCirc',
                            'NegativeCircular' : 'NegCirc' };

    
    def __init__(self, name, imageDetector, energyDevice, polarisationDevice):
        self.name = name;
        
        self.detector = imageDetector;
        self.energyDevice = energyDevice;
        self.polarisationDevice=polarisationDevice;

    def setImageDetector(self, imageDetector):
        self.detector = imageDetector;
    
    def setEnergyDevice(self, energyDevice):
        self.energyDevice = energyDevice;
        return self.energyDevice.getPosition();
    
    def setPolarisationDevice(self, polarisationDevice):
        self.polarisationDevice = polarisationDevice;
        return self.polarisationDevice.getPosition();
    
    def multiShot(self, numberOfImages, integrationTime):
        self.detector.setCollectionTime(integrationTime);
        return self.detector.multiShot(numberOfImages);
        
    def setEnergy(self, energy):
        try:
            self.energyDevice.moveTo(energy);
        except :
            exceptionType, exception, traceback=sys.exc_info();
            print "XXXXXXXXXX:  Errors when changing the energy."
            logger.dump("---> ", exceptionType, exception, traceback)
            raise EnergyError("Eenergy Error");
        
    def getEnergy(self):
        try:
            return self.energyDevice.getPosition();
        except:
            exceptionType, exception, traceback=sys.exc_info();
            print "XXXXXXXXXX:  Errors when changing the energy."
            logger.dump("---> ", exceptionType, exception, traceback)
            raise EnergyError("Eenergy Error");
        
    def setPolarisation(self, polarisation):
        try:
            self.polarisationDevice.moveTo(MagneticDichroismDevice.PolarisationCommand[polarisation]);
        except:
            exceptionType, exception, traceback=sys.exc_info();
            print "XXXXXXXXXX:  Errors when changing the polarisation."
            logger.dump("---> ", exceptionType, exception, traceback)
            raise PolarisationError("Polarisation Error");
        
    def getPolarisation(self):
        try:
            return self.polarisationDevice.getPosition();
        except:
            exceptionType, exception, traceback=sys.exc_info();
            print "XXXXXXXXXX:  Errors when getting the polarisation."
            logger.dump("---> ", exceptionType, exception, traceback)
            raise PolarisationError("Polarisation Error");
        
    def createPrecessingDir(self, subDir):
        """Set file path and name"""
        #Get the current data directory
        dataDir = PathConstructor.createFromDefaultProperty();
        
        fullPath = os.path.join(dataDir, "processing", subDir);
        
        if not os.path.exists(fullPath):
            #logger.simpleLog( "Warning: Image processing directory does not exist. Create new" );
            #print "OS Command: " + "umask 0002; mkdir -p " + fullPath;
            os.system("umask 0002; mkdir -p " + fullPath);
            
#        Check the new path created.        
        if not os.path.exists(fullPath):
            logger.simpleLog( "Error: Image processing directory does not exist and can not be created")
            raise Exception("Directory can not be created.");
            return;

        #logger.simpleLog("Image processing path: " + fullPath);
        return fullPath;

    def copyFiles(self, fileList, targetDir):
        for f in fileList:
#            os.system("cp -p " + f + " " + targetDir);
            shutil.copy2(f, targetDir);
            
        
    def getFullFileName(self):
        """Returns file path of the LAST CREATED image"""
        return self.detector.getFullFileName();

    def prepareFoCollection(self):
        return;
    
        
    def acquireImages(self, numberOfImages, integrationTime):
        self.multishot(numberOfImages, integrationTime);


    #To mvoe the energy, shot multiple shots and copy file to a processing directory    
    def action(self, energy, numberOfImages, integrationTime, targetDir):
        self.setEnergy(energy);
        print "----> Energy: " + str( self.getEnergy() );
        fileList = self.multiShot(numberOfImages, integrationTime);
        print "------> Take images.";
        self.copyFiles(fileList, targetDir);
    
    #X-ray magnetic circular dichroism
    def xmcd(self, startEnergy, endEnergy, numberOfImages, integrationTime):
        logger.simpleLog( "X-ray magnetic circular dichroism images acquisition...");
        #To create a new xmcd folder based on xmcd run number
        #get current scan number
        nt = NumTracker('xmcd');
        r=nt.getCurrentFileNumber();
        subDir='xmcd_' + str(r);
        targetDir = self.createPrecessingDir(subDir);
        #increase the scan number for next run
        nt.incrementNumber();
        
        try:
            #To change to Positive Circular Polarisation
            self.setPolarisation('PositiveCircular');
            print "--> Polarisation: " + str( self.getPolarisation() );
            #To take multiple shots at start energy point
            self.action(startEnergy, numberOfImages, integrationTime, targetDir)
            #To take multiple shots at end energy point
            self.action(endEnergy, numberOfImages, integrationTime, targetDir)
            
            #To change to Negative Circular Polarisation
            self.setPolarisation('NegativeCircular');
            print "--> Polarisation: " + str( self.getPolarisation() );
            #To take multiple shots at start energy point
            self.action(startEnergy, numberOfImages, integrationTime, targetDir)
            #To take multiple shots at end energy point
            self.action(endEnergy, numberOfImages, integrationTime, targetDir)
            
        except (PolarisationError, EnergyError), e:
            print e;
        except:
            raise;
        
        print "Done. Images in: " + targetDir;
        return targetDir;

    #X-ray magnetic linear dichroism
    def xmld(self, startEnergy, endEnergy, numberOfImages, integrationTime):
        logger.simpleLog( "X-ray magnetic linear dichroism images acquisition...");
        #To create a new xmld folder based on xmld run number
        #get current scan number
        nt = NumTracker('xmld');
        r=nt.getCurrentFileNumber();
        subDir='xmld_' + str(r);
        targetDir = self.createPrecessingDir(subDir);
        #increase the scan number for next run
        nt.incrementNumber();
        
        try:
            #To change to Linear Horizontal Polarisation
            self.setPolarisation('LinearHorizontal');
            print "--> Polarisation: " + str( self.getPolarisation() );
            #To take multiple shots at start energy point
            self.action(startEnergy, numberOfImages, integrationTime, targetDir)
            #To take multiple shots at end energy point
            self.action(endEnergy, numberOfImages, integrationTime, targetDir)
            
            #To change to Linear Vertical Polarisation
            self.setPolarisation('LinearVertical');
            print "--> Polarisation: " + str( self.getPolarisation() );
            #To take multiple shots at start energy point
            self.action(startEnergy, numberOfImages, integrationTime, targetDir)
            #To take multiple shots at end energy point
            self.action(endEnergy, numberOfImages, integrationTime, targetDir)
            
            
        except (PolarisationError, EnergyError), e:
            print e;
        except:
            raise;
        
        print "Done. Images in: " + targetDir;
        return targetDir;

    #X-ray magnetic dichroism
    def xmlde(self, startEnergy, endEnergy, numberOfImages, integrationTime):
        logger.simpleLog( "X-ray magnetic dichroism images acquisition...");
        #To create a new xmcd folder based on xmcd run number
        #get current scan number
        nt = NumTracker('xmlde');
        r=nt.getCurrentFileNumber();
        subDir='xmlde_' + str(r);
        targetDir = self.createPrecessingDir(subDir);
        #increase the scan number for next run
        nt.incrementNumber();
        
        try:
            print "--> Polarisation: " + str( self.getPolarisation() );

            #To take multiple shots at start energy point
            self.action(startEnergy, numberOfImages, integrationTime, targetDir)
            #To take multiple shots at end energy point
            self.action(endEnergy, numberOfImages, integrationTime, targetDir)
            
        except (PolarisationError, EnergyError), e:
            print e;
        except:
            raise;
        
        print "Done. Images in: " + targetDir;
        return targetDir;
    
#Example:

#md=MagneticDichroismDevice("md", imageDetector, energyDevice, polarisationDevice);
#md=MagneticDichroismDevice("md", dummyCamera, testMotor1, iddpol);

#md.xmcd(400, 500, 10, 0.5);
#md.xmld(400, 500, 10, 0.5);
#md.xmlde(400, 500, 10, 0.5);

   