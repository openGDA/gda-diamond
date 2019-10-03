#The device class used on the Magnetic Dichroism Spectroscopy and Microscopy.


from gda.device.detector import PseudoDetector
from gda.device.scannable import PseudoDevice
from gda.device import Detector


from gda.analysis.io import PilatusTiffLoader, JPEGLoader, TIFFImageLoader
from gda.analysis import ScanFileHolder
from gda.analysis import RCPPlotter;

from gda.jython import InterfaceProvider
from gda.data import NumTracker;
from gda.jython import ScriptBase;

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
        dataDir = InterfaceProvider.getPathConstructor().createFromDefaultProperty();
        
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

    def prepare(self, trackerName='xmd', pathPrefix='xmd_'):

        #To setup the new directory for images
        self.detector.scanImageDirectory();
        
        #To create a new xmcd folder based on xmcd run number
        #get current scan number
        nt = NumTracker(trackerName);
        r=nt.getCurrentFileNumber();
        subDir=pathPrefix + str(r);
        targetDir = self.createPrecessingDir(subDir);
        #increase the scan number for next run
        nt.incrementNumber();
        return targetDir;

    
    #To mvoe the energy, shot multiple shots and copy file to a processing directory    
    def action(self, energy, numberOfImages, integrationTime, targetDir):
#        ScriptBase.checkForPauses();
        self.setEnergy(energy);
        energy=self.getEnergy();
        pol=self.getPolarisation();
        print "----> Energy: " + str( energy ) + ", Polarisation: " + str( pol );

        logger.simpleLog( "To take images..." );
        self.detector.setCollectionTime(integrationTime);
        fileList = self.detector.multiShot(numberOfImages, None, False);
        self.copyFiles(fileList, targetDir);
        
        return [[energy]*len(fileList), [pol]*len(fileList), fileList];

    def saveSRSData(self, energy, pol, fileList):
        srsHeader=[" &SRS\n", " SRSRUN=null,SRSDAT=null,SRSTIM=null,\n", " SRSSTN='null',SRSPRJ='null    ',SRSEXP='null    ',\n", " SRSTLE='                                                            ',\n", " SRSCN1='        ',SRSCN2='        ',SRSCN3='        ',\n", " &END\n"];

        try:
            runs=NumTracker("tmp")
            currentNum = runs.getCurrentFileNumber()
            #currentNum = runs.incrementNumber()
            path = InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir")
            fileName = path + "/" + str(currentNum) + ".dat"
#            print fileName
            fh=open(fileName, 'w');

            #SRS Header
            for i in range(len(srsHeader)):
                fh.write(srsHeader[i]);

            titleLine='%(v1)s \t %(v2)s \t %(v3)s \n' %{'v1': self.energyDevice.getName(), 'v2': self.polarisationDevice.getName(), 'v3': self.detector.getName()};
            fh.write(titleLine);
            
            nf=len(fileList);
            for n in range(nf):
                #print i, arrayEnergyPGM[i], arrayEnergyIDGAP[i], arrayChannel01[i], arrayChannel02[i], arrayChannel03[i], arrayChannel04[i];
                newLine='%(v1).8f \t %(v2)s \t %(v3)s \n' %{'v1': energy[n], 'v2': pol[n], 'v3': fileList[n]};
                fh.write(newLine);
            fh.close();
            print "Scan complete. File saved in " + fileName;
        except:
            print "ERROR: Could not save data into file."
    
    #X-ray magnetic circular dichroism
    def xmcd(self, startEnergy, endEnergy, numberOfImages, integrationTime):
        logger.simpleLog( "X-ray magnetic circular dichroism images acquisition...");
        #To create a new xmcd folder based on xmcd run number
        #To prepare the xmd tracker and directory
        targetDir=self.prepare();
        energy=[];pol=[];source=[];
        
        try:
            #To change to Positive Circular Polarisation
            logger.simpleLog( "To change polarisation and energy...");
            self.setPolarisation('PositiveCircular');
            
            #To take multiple shots at start energy point
            [e, p, s]=self.action(startEnergy, numberOfImages, integrationTime, targetDir);
            energy.extend(e);pol.extend(p), source.extend(s);
            #To take multiple shots at end energy point
            [e, p, s]=self.action(endEnergy, numberOfImages, integrationTime, targetDir)
            energy.extend(e);pol.extend(p), source.extend(s);
            
            #To change to Negative Circular Polarisation
            logger.simpleLog( "To change polarisation and energy...");
            self.setPolarisation('NegativeCircular');
            #To take multiple shots at start energy point
            [e, p, s]=self.action(startEnergy, numberOfImages, integrationTime, targetDir)
            energy.extend(e);pol.extend(p), source.extend(s);
            #To take multiple shots at end energy point
            [e, p, s]=self.action(endEnergy, numberOfImages, integrationTime, targetDir)
            energy.extend(e);pol.extend(p), source.extend(s);
            
            #To create a SRS data file for this scan
            self.saveSRSData(energy, pol, source);
            
        except (PolarisationError, EnergyError), e:
            print e;
        except:
            raise;
        
        print "For analysis, images are copied to : " + targetDir;
        return targetDir;

    def xmld(self, startEnergy, endEnergy, numberOfImages, integrationTime):
        logger.simpleLog( "X-ray magnetic linear dichroism images acquisition...");
        #To create a new xmld folder based on xmld run number
        #To prepare the xmd tracker and directory
        targetDir=self.prepare();
        energy=[];pol=[];source=[];
        
        try:
            logger.simpleLog( "To change polarisation and energy...");
            #To change to Linear Horizontal Polarisation
            self.setPolarisation('LinearHorizontal');
            #To take multiple shots at start energy point
            [e,p,s]=self.action(startEnergy, numberOfImages, integrationTime, targetDir)
            energy.extend(e);pol.extend(p), source.extend(s);
            #To take multiple shots at end energy point
            [e,p,s]=self.action(endEnergy, numberOfImages, integrationTime, targetDir)
            energy.extend(e);pol.extend(p), source.extend(s);
            
            logger.simpleLog( "To change polarisation and energy...");
            #To change to Linear Vertical Polarisation
            self.setPolarisation('LinearVertical');
            #To take multiple shots at start energy point
            [e,p,s]=self.action(startEnergy, numberOfImages, integrationTime, targetDir)
            energy.extend(e);pol.extend(p), source.extend(s);
            #To take multiple shots at end energy point
            [e,p,s]=self.action(endEnergy, numberOfImages, integrationTime, targetDir)
            energy.extend(e);pol.extend(p), source.extend(s);
            
            #To create a SRS data file for this scan
            self.saveSRSData(energy, pol, source);
            
        except (PolarisationError, EnergyError), e:
            print e;
        except:
            raise;
        
        print "For analysis, images are copied to : " + targetDir;
        return targetDir;

    #X-ray magnetic dichroism
    def xmd(self, startEnergy, endEnergy, numberOfImages, integrationTime):
        logger.simpleLog( "X-ray magnetic dichroism images acquisition...");
        
        #To prepare the xmd tracker and directory
        targetDir=self.prepare();
        energy=[];pol=[];source=[];
        
        try:
            logger.simpleLog( "To change energy...");
            #To take multiple shots at start energy point
            [e,p,s]=self.action(startEnergy, numberOfImages, integrationTime, targetDir)
            energy.extend(e);pol.extend(p), source.extend(s);
            #To take multiple shots at end energy point
            logger.simpleLog( "To change energy...");
            [e,p,s]=self.action(endEnergy, numberOfImages, integrationTime, targetDir)
            energy.extend(e);pol.extend(p), source.extend(s);
            
            #To create a SRS data file for this scan
            self.saveSRSData(energy, pol, source);
            
        except (PolarisationError, EnergyError), e:
            print e;
        except:
            raise;
        
        print "For analysis, images are copied to : " + targetDir;
        return targetDir;

    def xmlde(self, startEnergy, endEnergy, numberOfImages, integrationTime):
        return self.xmd(startEnergy, endEnergy, numberOfImages, integrationTime);

    
#Example:

#md=MagneticDichroismDevice("md", imageDetector, energyDevice, polarisationDevice);
#md=MagneticDichroismDevice("md", dummyCamera, testMotor1, iddpol);

#md.xmcd(400, 500, 10, 0.5);
#md.xmld(400, 500, 10, 0.5);
#md.xmlde(400, 500, 10, 0.5);

   