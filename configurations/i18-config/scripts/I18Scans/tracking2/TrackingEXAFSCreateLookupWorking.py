#@PydevCodeAnalysisIgnore
from gda.epics import CAClient
from java.lang import *
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from org.python.modules.math import *
from gda.device.xspress import Xspress2Utilities
from gda.jython import ScriptBase
from time import sleep
from java.lang import *
from java.util import Calendar
from gda.data import NumTracker
from gda.jython import JythonServerFacade
from gda.jython import Jython
import gda.configuration.properties.LocalProperties
from gda.scan import ScanDataPoint
from java.io import DataInputStream
from java.io import FileInputStream
import os
import jarray
from java.util import Date
from java.text import SimpleDateFormat
from gda.util import Password
from gda.data import PathConstructor
import thread
import handle_messages 
from handle_messages import simpleLog
import sys
import time
import os

# ========================================
# EXAFS SCAN
# run Create_SESO_lookup.py
# run BeamMonitorClass.py
#
#    Example of a full SESO scan
#    myscan=I18SESOLookupExafsScanClass()
#    myscan.setSESOSleepTime(1.0)
#    myscan.setFileName("/dls/i18/tmp/sesolookup1.txt")
#    myscan.anglescan(8824.0,8739.460869565219,-3.8608695652174387,1000.0)
#    myscan.anglescan(8735.599999999999,8698.5,-0.6999999999999865,1000.0)
#    myscan.kscan(3.0,12.0,0.04,1000.0,1000.0,3,13.039848732586526,6.271000000000002)
#========================================

class I18SESOLookupExafsScanClass(ScriptBase):
    def __init__(self,detectorList=None):
        # EXAFS PANEL CODE
        self.energyController = JythonServerFacade.getInstance().getFromJythonNamespace(LocalProperties.get("gda.i18.energyController"))
        self.converter = finder.find("auto_mDeg_idGap_mm_converter")
        self.interrupted=Boolean(0)
        self.paused=Boolean(0)
        self.SESOSleepTime=1.0
        self.noOfPoints=0
        self.scanList=[]
        self.datafilename="/dls/i18/tmp/lookuptables/sesotest.txt"
        

    def addAngleScan(self,start,end,step,collectionTime):
        self.noOfPoints=self.noOfPoints+int((end-start)/step)
        self.scanList.append(['a',start,end,step,collectionTime])

    def addKScan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
        self.noOfPoints=self.noOfPoints+int((end-start)/step)
        self.scanList.append(['k',start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD])

    def clearScanList(self):
        self.scanList=[]

    def startScan(self):
        #
        # Send repeat and point information to the GUI
        # then start the scan
        ##selecting the harmonic and disabling the harmonic autoconversion
        ##to stay in the same harmonic for the whole of the scan
        if(self.scanList[0][0] =='a'):
            moveTo = self.scanList[0][1]
        elif(self.scanList[0][0]=='k'):
            moveTo =self.mDegForK(self.scanList[0][1], self.scanList[0][7],self.scanList[0][8])
        lookup = finder.find("lookup_name_provider")
        self.converter.enableAutoConversion()
        try:
            self.converter.enableAutoConversion()
            self.energyController.moveTo(moveTo)
            print 'moving to:',idgap.getPosition(),dcm_bragg.getPosition(),dcm_perp.getPosition()
            self.converter.disableAutoConversion()
            print 'Harmonic set to ',lookup.getConverterName()
        except:
            self.interrupted=1
            self.converter.enableAutoConversion()
            print 'Problem moving to initial position: Harmonic set to ',lookup.getConverterName()
        print self.scanList
        lock =0
        try:
            for j in range(len(self.scanList)):
                if(self.scanList[j][0]=='a'):
                   self.anglescan(self.scanList[j][1],self.scanList[j][2],self.scanList[j][3],self.scanList[j][4])
                elif(self.scanList[j][0]=='k'):
                    self.kscan(self.scanList[j][1],self.scanList[j][2],\
                    self.scanList[j][3],self.scanList[j][4],self.scanList[j][5],self.scanList[j][6],self.scanList[j][7],self.scanList[j][8])
            self.converter.enableAutoConversion()
        finally:
            self.converter.enableAutoConversion()

    def setFileName(self,filename):
        self.datafilename=filename               
                    
    #==================================================
    # Performs an angle scan in step mode
    # ==================================================
    def anglescan(self,start,end,step,collectionTime):
        i=0
        self.createFile()
        # create some empty lists
        difference = end - start
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        # start position
        currentpos=start
        print 'Clearing and Preparing Detector'
        # loop over npoints
        print 'Bragg Energy Time I0 It Idrain'
        self.checkForAngleInterrupt(0)
        oldpos=currentpos
        lookup = finder.find("lookup_name_provider")
        for i in range(npoints):
            self.checkForAnglePause((i-1))
            #
            # Check beam is running
            #
            while(BeamMonitor.beamOn()==0):
                self.checkForAngleInterrupt(i-1)
                print 'Beam lost : Pausing until resumed'
                try:
                    sleep(60)
                except:
                    self.interrupted=1                    
                self.checkForAngleInterrupt(i-1)
            #
            # Check if detector is filling
            #
            while(BeamMonitor.isFilling()==1):
                self.checkForAngleInterrupt(i-1)
                print 'Detector Filling : Pausing until completed'
                try:
                    sleep(60)
                except:
                    self.interrupted=1                    
                self.checkForAngleInterrupt(i-1)

            self.checkForAngleInterrupt((i-1))
            try:
                self.energyController.moveTo(currentpos)
            except:
                self.interrupted=1
            self.checkForAngleInterrupt((i-1))

            # print out some progress
            self.checkForAngleInterrupt((i-1))
            sleep(self.SESOSleepTime)
            xvalue=sesoX.getPosition()
            yvalue=sesoX.getPosition()
            self.writeSummary(currentpos,xvalue,yvalue)
            # Move the mono
            oldpos=currentpos
            currentpos=currentpos+step

        print 'Finished angle scan'


    #==================================================
    # Performs a kscan in step mode
    # ==================================================
    def kscan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
        i=0
        self.createFile()
        # check that step is negative when moving downwards to stop
        difference = end - start
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        currentpos=start
        oldpos=currentpos
        print 'Starting k scan'
        print 'Bragg Energy Time I0 It Idrain'
        self.checkForKScanInterrupt(0)
        lookup = finder.find("lookup_name_provider")
        for i in range(npoints):
            self.checkForKScanPause(i)
            # Check beam is running
            while(BeamMonitor.beamOn()==0):
                print 'Beam lost : Pausing until resumed'
                self.checkForKScanInterrupt(i-1)
                try:
                    sleep(60)
                except:
                    self.interrupted=1
                self.checkForKScanInterrupt(i-1)

            # Check if detector is filling
            while(BeamMonitor.isFilling()==1):
                self.checkForKScanInterrupt(i-1)
                print 'Detector Filling : Pausing until completed'
                try:
                    sleep(60)
                except:
                    self.interrupted=1                    
                self.checkForKScanInterrupt(i-1)

            mdegPosition = self.mDegForK(currentpos,edgeEnergy,twoD)
            self.checkForKScanInterrupt((i-1))
            # Move mono to start position
            try:
                self.energyController.moveTo(mdegPosition)
            except:
                self.interrupted=1
            self.checkForKScanInterrupt((i-1))
            sleep(self.SESOSleepTime)
            xvalue=sesoX.getPosition()
            yvalue=sesoX.getPosition()
            self.writeSummary(mdegPosition,xvalue,yvalue)
            self.checkForKScanInterrupt((i-1))
            # Move the mono
            oldpos=mdegPosition
            currentpos=currentpos+step
            #  write out at end
        self.checkForKScanInterrupt((i-1))
        print 'Finished k scan'


    # angle to radians
    def angleToRadians(self,angle):
        factor = 180.0/self.pi
        return angle/factor
    # sin angle
    def sind(self,value):
        valueradians=self.angleToRadians(value)
        sintheta=sin(valueradians)
        return sintheta
    #
    # Return energy for a given angle
    #
    def mDegToEnergy(self,angle):
        energy=1977.58/self.sind(angle/1000.0)
        return energy


    def setSESOSleepTime(self,sleeptime):
        self.SESOSleepTime=sleeptime
    #==================================================
    # mDegForK converts k value (in inverse angstroms) to mDeg by using the java
    # Converter class.
    #==================================================
    def mDegForK(self,k,edgeEnergy,twoD):
        return gda.gui.exafs.Converter.convert(k,gda.gui.exafs.Converter.PERANGSTROM, gda.gui.exafs.Converter.MDEG,edgeEnergy, twoD)

    #==================================================
    #
    #  Creates the file used for the EXAFS
    # 
    #==================================================
    def createFile(self):
        if(os.path.exists(self.datafilename)==0):
            fid=open(self.datafilename,'w')
            print "Writing data to file:"+self.datafilename
            fid.close()

    #==================================================
    #
    # Checks to see if an angle scan has been interrupted
    #
    #==================================================
    def checkForAngleInterrupt(self,npoints):
        #print 'angle interrupt '
        if(self.interrupted):
            print 'Stopping angle scan:Writing out data taken'
            self.interrupted=Boolean(0)
            self.paused=Boolean(0)
            self.converter.enableAutoConversion()
            JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
            print  'Now the nasty bit: throw an exception to stop running'
            raise lang.InterruptedException()


    #==================================================
    #
    # Checks to see if an angle scan has been paused
    #
    #==================================================
    def checkForAnglePause(self,npoints):
        if(self.paused):
            JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
            while(self.paused):
                try:
                    print 'Angle Scan paused - Awaiting resume'
                    java.lang.Thread.sleep(10000)
                except lang.InterruptedException:
                    self.checkForAngleInterrupt(npoints)


    #==================================================
    #
    # Checks to see if an angle scan has been paused
    #
    #==================================================
    def checkForKScanInterrupt(self,npoints):
        if(self.interrupted):
            print 'Stopping k scan:Writing out data taken'
            # write the data we have so far and return
            self.interrupted=Boolean(0)
            self.paused=Boolean(0)
            self.converter.enableAutoConversion()
            JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
            print  'Now the nasty bit: throw an exception to stop running'
            raise lang.InterruptedException()

    #==================================================
    #
    # Checks to see if an angle scan has been paused
    #
    #==================================================
    def checkForKScanPause(self,npoints):
        if(self.paused):
            JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
            while(self.paused):
                try:
                    print 'K Scan Scan paused - Awaiting resume'
                    java.lang.Thread.sleep(10000)
                except lang.InterruptedException:
                    self.checkForKScanInterrupt(npoints)

    def writeSummary(self,mdeg,x,y):
        fout=open(self.datafilename,'a')
        print>>fout,mdeg,x,y
        print mdeg,x,y
        fout.close()
        

        
