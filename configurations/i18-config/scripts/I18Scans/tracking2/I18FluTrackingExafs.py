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
# run SlaveCounterTimer.py
# run I18ExafsClass.py
# run BeamMonitorClass.py
#
#    Example of a full Pb scan
#    myscan=I18ExafsScanClass()
#    myscan.setWindows('/home/i18user/i18windows.windows','Pblalpha1')
#    myscan.anglescan(8824.0,8739.460869565219,-3.8608695652174387,1000.0)
#    myscan.anglescan(8735.599999999999,8698.5,-0.6999999999999865,1000.0)
#    myscan.kscan(3.0,12.0,0.04,1000.0,1000.0,3,13.039848732586526,6.271000000000002)
#========================================
class I18ExafsScanClass(ScriptBase):
    def __init__(self,detectorList=None):
        # EXAFS PANEL CODE
        self.scannableNamesVector=Vector()
        self.scannableNamesVector.add("dcm_mono")
        self.detectorNamesVector=Vector()
        self.detectorNamesVector.add("counterTimer01")
        self.detectorNamesVector.add("counterTimer02") 
        self.controller = finder.find("ExafsController")
        self.mcontroller = finder.find("MicroFocusController")
        self.energyController = JythonServerFacade.getInstance().getFromJythonNamespace(LocalProperties.get("gda.i18.energyController"))
        self.title="TITLE"
        self.condition1="CONDITION1"
        self.condition2="CONDITION2"
        self.condition3="CONDITION3"
        # Script code
        self.das=finder.find("daserver")
        self.ionchambers=ionChambers
        #self.ionchambers=vortex_trigger
        self.converter = finder.find("auto_mDeg_idGap_mm_converter")
        self.windowValues=[[0,4095]]*9
        self.windowName='ALL'
        self.ionchamberData=[]
        self.mcaList=[]
        self.scalarList=[]
        #self.interrupted=0
        self.interrupted=Boolean(0)
        self.paused=Boolean(0)
        self.runs=NumTracker("tmp")
        self.runprefix='i18exafs'
        self.runext='.dat'
        # define pi
        self.pi=4.0*atan(1.0)
        self.fileno=self.runs.getCurrentFileNumber()+1
        self.runs.incrementNumber()
        self.datadir=PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        if(detectorList!=None):
            self.detectorMask=detectorList
        else:
            self.detectorMask=[1,1,1,1,1,1,1,1,1]

        self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
        self.mcarootname=self.mcadir+str(self.fileno)
        if not os.path.isdir(self.mcadir):
            os.mkdir(self.mcadir)
        ftppassfile=LocalProperties.get("gda.i18.ftpserver.passwordfile")
        #print ftppassfile
        self.ftppassword= Password.readFromFile(ftppassfile)
        #print self.ftppassword
        self.tag=1
        self.facade=JythonServerFacade.getInstance()
        self.xspress = finder.find("xspress2system")
        self.scanList=[]
        self.noOfRepeats=1
        self.noOfPoints=0
        self.headerOffset=7
        self.dtc_filename= "dtcfilenametobeset"
        self.readError = 0
        self.readErrorList=[]
        self.archiveFileList=[]
        self.fileArchiveCounter=0
        self.archiver = archiver
        self.move_braggset=[]
        self.move_xmov=[]
        self.move_ymov=[]

        


    def addAngleScan(self,start,end,step,collectionTime):
        self.noOfPoints=self.noOfPoints+int((end-start)/step)
        self.scanList.append(['a',start,end,step,collectionTime])

    def addKScan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
        self.noOfPoints=self.noOfPoints+int((end-start)/step)
        self.scanList.append(['k',start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD])

    def clearScanList(self):
        self.scanList=[]


    def setNoOfRepeats(self,repeats):
        self.noOfRepeats=repeats

    def startScan(self):
        #
        # Send repeat and point information to the GUI
        # then start the scan
        #
        self.setupGUI()
        for i in range(self.noOfRepeats):
            if(i>0):                
                self.incrementFilename()
                
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
                #comboDCM_d.moveTo(moveTo)
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
                print 'locking express'
                lock  = self.xspress.tryLock(5,java.util.concurrent.TimeUnit.SECONDS)
                print "the lock value is " + str(lock)
                if not lock:
                    print "Xspress detector is already locked"
                    self.controller.update(None, "STOP")
                    return
                for j in range(len(self.scanList)):
                    if(self.scanList[j][0]=='a'):
                        self.anglescan(self.scanList[j][1],self.scanList[j][2],self.scanList[j][3],self.scanList[j][4])
                    elif(self.scanList[j][0]=='k'):
                        self.kscan(self.scanList[j][1],self.scanList[j][2],\
                        self.scanList[j][3],self.scanList[j][4],self.scanList[j][5],self.scanList[j][6],self.scanList[j][7],self.scanList[j][8])
                ##to update the gui panels about the end of repeat scans
                if((i+1) == self.noOfRepeats):
                    self.incrementGUIRepeat(1)
                else:
                    self.incrementGUIRepeat(0)
                self.converter.enableAutoConversion()
            finally:
                
                self.converter.enableAutoConversion()
                if(lock):
                    print 'unlocking xpress'
                    self.xspress.unlock()
                if(os.path.exists(self.datafilename)):
                    self.archiveFileList.append(self.datafilename)
                    if(os.path.exists(self.dtc_filename)):
                        self.archiveFileList.append(self.dtc_filename)
                try:
                    if(len(self.archiveFileList ) != 0):
                        self.archiver.registerFiles("scan-" + str(self.fileno), self.archiveFileList)
                except:
                    print "Unable archive files " + self.dtc_filename

                   
                    
        
    
    def setupGUI(self):
        scandata=Vector()
        # Type of scan
        scandata.add("FluScan")
        # No of Repeats
        # No of Points
        scandata.add(self.noOfPoints)
        scandata.add(self.noOfRepeats)
        self.controller.update(None,scandata)
        self.mcontroller.update(None,scandata)

    def incrementGUIRepeat(self, repeatDone):
        scandata=Vector()
        # Type of scan
        scandata.add("ScanComplete")
        scandata.add(repeatDone)
        self.controller.update(None,scandata)
        self.mcontroller.update(None,scandata)

                        
        
    # ========================================
    #  Read in a window to be used on the mca files 
    # ========================================
    def setWindows(self,filename,desiredWindow):
        infile=open(filename,'r')
        tmpwindowValues=[[0,4095]]*9
        tmpwindowName=''
        while infile:
            # Read in the line file
            a=infile.readline()    
            n = len(a)
            if n == 0:
                break
            temp=a.split('\t')
            tmpwindowName=temp[0].strip().replace(' ','')
            if(tmpwindowName.lower().find(desiredWindow.lower())>=0):
                for j in range(len(temp)-1):
                    index=j+1
                    mytemp=temp[index].strip().replace('[','').replace(']','').split(',')
                    mytemp=[int(mytemp[0]),int(mytemp[1])]
                    tmpwindowValues[j]=mytemp 
                    ##to set the window values in the scaler
                    self.setScalerWindows(j, tmpwindowValues[j][0], tmpwindowValues[j][1])
                    print 'window values chosen :',j,tmpwindowValues[j]
                self.windowValues= tmpwindowValues
                self.windowName= tmpwindowName
        if(self.windowName=='ALL'):
            print '======================'
            print '========WARNING========'
            print 'No window has been found or set'
            print '======WARNING=========='
            print '======================'
            

    #==================================================
    # Performs an angle scan in step mode
    # ==================================================
    def anglescan(self,start,end,step,collectionTime):
        #self.converter.enableAutoConversion()
        #scanStart=time.asctime()
    
        i=0
        self.createFile()
        # create some empty lists
        self.mcaList=[]
        self.ionchamberData=[]
        self.scalarList=[]
        # find no of points
        difference = end - start
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        # start position
        currentpos=start
        print 'Clearing and Preparing Detector'
        # set collection time
        self.prepareDetectorForCollection(npoints,collectionTime/1000.0)
        # loop over npoints
        print 'Bragg Energy Time I0 It Idrain'
        self.checkForAngleInterrupt(0)
        oldpos=currentpos
        lookup = finder.find("lookup_name_provider")
        #starttime=time.time()
        # Ready the ion chambers
        self.ionchambers.clearAndPrepare()
        mysleeptime=collectionTime*0.95/1000.0
       # self.timeList=[]
        for i in range(npoints):
            #self.timeList.append(time.time()-starttime)
           # starttime=time.time()
            self.checkForAnglePause((i-1))
            # Check beam is running
            #
            # Check beam is running
            #
            #print 'check beam running'
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
           # print 'cheeck detector  filling'
            while(BeamMonitor.isFilling()==1):
                self.checkForAngleInterrupt(i-1)
                print 'Detector Filling : Pausing until completed'
                try:
                    sleep(60)
                except:
                    self.interrupted=1                    
                self.checkForAngleInterrupt(i-1)
            
            # topup test
            #
           # print 'check topup'
            while(BeamMonitor.collectBeforeTopupTime(collectionTime/1000.0)==1):
                print 'Top up coming : Pausing until resumed'
                try:
                    sleep(1)
                except:
                    self.interrupted=1    
                self.checkForAngleInterrupt(i-1)

            self.ionchambers.clearAndPrepare()
            # A check to make sure the struck is started (i.e. cleared and waiting for a trigger signal)
            # Early runs occassionally threw odd numbers or zeros out...
            # so put in some check the struck is the right state 
            while(self.ionchambers.isClear()==0 or self.ionchambers.getStatus()==0):
                print 'ionchambers struck not ready: Waiting to clear'
                try:
                    sleep(0.050)
                except:
                    self.interrupted=1
                self.checkForAngleInterrupt(i-1)
                self.ionchambers.clearAndPrepare()
                try:
                    sleep(0.050)
                except:
                    self.interrupted=1
                self.checkForAngleInterrupt(i-1)

            # Move mono to start position
            self.checkForAngleInterrupt((i-1))
            try:
                #comboDCM_d.moveTo(currentpos)
                self.energyController.moveTo(currentpos)
            except:
                self.interrupted=1
            self.checkForAngleInterrupt((i-1))
#            sleep(0.5)
            # tfg starts paused so tell it to continue
            if(i==0):
                 self.das.sendCommand("tfg start")

            self.das.sendCommand("tfg cont")
            try:
               sleep(mysleeptime)
            except:
                self.interrupted=1
            self.checkForAngleInterrupt(i-1)
            # Wait until collection is finished
            self.das.sendCommand("tfg wait")
            self.checkForAngleInterrupt((i-1))
            #  stop detector
            self.ionchambers.stop()
            # Now while collecting data, output the last point....
            if(i>=1):
                ##get the mca data for the previous point
                thread.start_new_thread(self.writeDetectorFileAtPoint,(i-1,))
                totalw=self.writeSummaryAtPoint(i-1,oldpos,collectionTime)
                print lookup.getConverterName(),oldpos,self.mDegToEnergy(oldpos),collectionTime,self.ionchamberData[i-1][0],self.ionchamberData[i-1][1],self.ionchamberData[i-1][2],totalw
            self.checkForAngleInterrupt((i-1))
            # read out the ion chambers
            self.ionchamberData.append(self.ionchambers.getPosition())
            if(i==npoints-1):
                self.stopDetector()
                 ##get the mca data for the previous point
                self.writeDetectorFileAtPoint(i)
                totalw=self.writeSummaryAtPoint(i,currentpos,collectionTime)
                print currentpos,self.mDegToEnergy(currentpos),collectionTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],totalw

            # print out some progress
            self.checkForAngleInterrupt((i-1))
            # Move the mono
            oldpos=currentpos
            currentpos=currentpos+step
            #  stop detector
            self.ionchambers.stop()

        ##shift the header offset so that dTC data is written at the corrected position in the _dtc file
        self.shiftHeaderOffset(npoints)
        self.tag=self.tag+1
        #scanEnd=time.asctime()
        print 'Finished angle scan'
        #handle_messages.simpleLog("Angle Scan Start " + str(scanStart))
        #handle_messages.simpleLog("Angle Scan End " + str(scanEnd))
        #handle_messages.simpleLog("Angle Scan Point time list " + `self.timeList`)
        handle_messages.simpleLog("Angle Read error count " + str(self.readError))
        handle_messages.simpleLog("Angle Read error points list " + `self.readErrorList`)


    #==================================================
    # Performs a kscan in step mode
    # ==================================================
    def kscan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
        #self.converter.enableAutoConversion()
        #scanStart=time.asctime()
        i=0
        #try:
        self.createFile()
        self.mcaList=[]
        self.ionchamberData=[]
        self.scalarList=[]
        # check that step is negative when moving downwards to stop
        difference = end - start
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        currentpos=start
        oldpos=currentpos
        secTime=1000.0
        # Ready the ion chambers
        self.ionchambers.clearAndPrepare() 	
        # prepare detector for collection
        print 'Clearing and Preparing Detector'
        self.prepareDetectorForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
        print 'Starting k scan'
        print 'Bragg Energy Time I0 It Idrain'
        self.checkForKScanInterrupt(0)
        lookup = finder.find("lookup_name_provider")
        #starttime=time.time()
        for i in range(npoints):
           # self.timeList.append(time.time()-starttime)
          #  starttime=time.time()
            # Check for pause!
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
            # check for topup
            oldsecTime=secTime
            secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
            mysleeptime=int(100.0*(secTime*0.95/1000.0))/100.0
            while(BeamMonitor.collectBeforeTopupTime(secTime/1000.0)==1):
                print 'Top up coming : Pausing until resumed'
                try:
                    sleep(1)
                except:
                    self.interrupted=1    
                self.checkForKScanInterrupt(i-1)

            mdegPosition = self.mDegForK(currentpos,edgeEnergy,twoD)
            #secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
            # Ready the ion chambers
            self.ionchambers.clearAndPrepare()
            # A check to make sure the struck is started (i.e. cleared and waiting for a trigger signal)
            # Early runs occassionally threw odd numbers or zeros out...
            # so put in some check the struck is the right state 
            while(self.ionchambers.isClear()==0 or self.ionchambers.getStatus()==0):
                print 'ionchambers struck not ready: Waiting to clear'
                try:
                    sleep(0.050)
                except:
                    self.interrupted=1
                self.checkForKScanInterrupt((i-1))
                self.ionchambers.clearAndPrepare()
                self.checkForKScanInterrupt((i-1))
                try:
                    sleep(0.050)
                except:
                    self.interrupted=1
                self.checkForKScanInterrupt((i-1))

            self.checkForKScanInterrupt((i-1))
            # Move mono to start position
            try:
                #comboDCM_d.moveTo(mdegPosition)
                self.energyController.moveTo(mdegPosition)
            except:
                self.interrupted=1
            self.checkForKScanInterrupt((i-1))
#            sleep(0.5)
            self.checkForKScanInterrupt((i-1))
            if(i==0):
                 self.das.sendCommand("tfg start")

            # tfg starts paused so tell it to continue

            self.das.sendCommand("tfg cont")
            try:
               sleep(mysleeptime)
            except:
                self.interrupted=1
            self.checkForKScanInterrupt((i-1))
            self.das.sendCommand("tfg wait")
            self.checkForKScanInterrupt((i-1))
            if(i>=1):
                ##get the mca data for the previous point
                thread.start_new_thread(self.writeDetectorFileAtPoint,(i - 1,))
                #self.writeDetectorFileAtPoint(i - 1)
                totalw=self.writeSummaryAtPoint(i-1,oldpos,oldsecTime)
                print oldpos,self.mDegToEnergy(oldpos),oldsecTime,self.ionchamberData[i-1][0],self.ionchamberData[i-1][1],self.ionchamberData[i-1][2],totalw
            self.checkForKScanInterrupt((i-1))
            self.ionchamberData.append(self.ionchambers.getPosition())
            self.checkForKScanInterrupt((i-1))
            if(i==npoints-1):
                self.stopDetector()
                ##get the mca data for the previous point
                self.writeDetectorFileAtPoint(i)
                totalw=self.writeSummaryAtPoint(i,mdegPosition,secTime)
                print lookup.getConverterName(),mdegPosition,self.mDegToEnergy(mdegPosition),secTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],totalw
            # Move the mono
            oldpos=mdegPosition
            currentpos=currentpos+step
            # Ready the ion chambers
            self.ionchambers.stop()
            #  write out at end
        self.checkForKScanInterrupt((i-1))
        #self.stopDetector()    
        ##shift the header offset so that dTC data is written at the corrected position in the _dtc file
        self.shiftHeaderOffset(npoints)
        #self.converter.enableAutoConversion()
        self.checkForKScanInterrupt((i-1))
        #self.writeDetectorFiles(npoints)
        self.tag=self.tag+1
      #  scanEnd=time.asctime()
        print 'Finished k scan'
        #handle_messages.simpleLog("Kscan start time " + str(scanStart))
       # handle_messages.simpleLog("Kscan end time " + str(scanEnd))
      #  handle_messages.simpleLog("Kscan point time list  " + `self.timeList`)
        handle_messages.simpleLog("Read error count " + str(self.readError))
        handle_messages.simpleLog("Read error points list " + `self.readErrorList`)

    #==================================================
    #  Disables, Clears and enables the detector
    #  Sets up tfg for a given noOfFrames and  collectionTime
    #  pausing in the dead frame and dead port=1 for adc triggering
    #  and finally starts the tfg which means it sits waiting for a software based continue command
    #==================================================
    def prepareDetectorForCollection(self,noOfFrames,collectionTime):
        self.das.sendCommand("disable 0")
        self.das.sendCommand("clear 0")
        self.das.sendCommand("enable 0")
        self.das.sendCommand("tfg init")
        command = "tfg setup-groups cycles 1 \n%d 0.01 %f 0 7 -1 0 \n-1 0 0 0 0 0 0 "  %(noOfFrames,collectionTime)
        self.das.sendCommand(command)
        #self.das.sendCommand("tfg start")

    #==================================================
    #  Disables, Clears and enables the detector
    #  Sets up tfg for a set of possibly variable length time frames
    #  and finally starts the tfg which means it sits waiting for a software based continue command
    #==================================================
    def prepareDetectorForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
        self.das.sendCommand("disable 0")
        self.das.sendCommand("clear 0")
        self.das.sendCommand("enable 0")
        self.das.sendCommand("tfg init")
        command = self.getTFGCommandForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
        self.das.sendCommand(command)
        #self.das.sendCommand("tfg start")

    #==================================================
    # Stop the tfg and disable the detector
    #==================================================
    def stopDetector(self):
        self.das.sendCommand("tfg init")
        self.das.sendCommand("disable 0")

    #==================================================
    # Write the detector data to files
    #==================================================
    def writeDetectorScalerFile(self,point,scalerfile):
        sname = scalerfile
        print 'Writing scalar point',point,'to',sname
        #scalarFile.append(sname)
        #command = "read 0 0 %d 9 3 1 from 1 to-local-file \"%s\" raw intel" % ( point, sname)
        command = "read 0 0 %d 3 9 1 from 1 to-local-file \"%s\" raw intel" % ( point, sname)
        self.das.sendCommand(command)
        return sname

    #==================================================
    # Write out the scalar data and dead time correct the existing data
    #==================================================
    def writeDTC(self,point, scalar_files):
        # Now read in the SRS file and correct the windows
        # read in the datafile
        fid=open(self.datafilename)
        a=fid.read()
        fid.close()
        a=a.split("\n")
        self.dtc_filename=self.datadir+'/'+str(self.fileno)+"_dtc.dat"
        #self.archiveFileList.append(dtc_filename)
        if(os.path.exists(self.dtc_filename)==0):
            fid=open(self.dtc_filename,'w')
            print >>fid,a[0:5]
            fid.close()

        fid=open(self.dtc_filename,'a')
        floatWindows=[]
        splitup=a[point+self.headerOffset].split(" ")
        aline=splitup[6:]
        collectionTime=float(splitup[2])/1000.0
        ##this loop is no longer needed as the windowed data is now read from the scaler
        ##6-11-08
        for j in range(len(aline)):
            floatWindows.append(float(aline[j]))
        #print "flaot windows",point,floatWindows[0:]
        # now convert float to....
        #corrWindows,totalW=self.deadTimeCorrectWindows(scalar_files[0],collectionTime)
        print 'scalar files', scalar_files
        corrWindows=Xspress2Utilities.deadTimeCorrectWindows2(scalar_files,collectionTime/12.5e-9)
        totalW=Xspress2Utilities.getWindowTotal()
        lengthW=len(corrWindows)
        line=''
        for k in range(lengthW):
            if( k != lengthW -1 ):
                line=line + str(corrWindows[k])+ " " 
            else:
                line=line + str(corrWindows[k])
        print >> fid,a[point+self.headerOffset],line,totalW
        #print >> fid,a[point+self.headerOffset],str(corrWindows[0:]).strip('[]').replace(',',''),totalW
        # now close the file
        fid.close()
        
    def shiftHeaderOffset(self, npoints):
        # Now shift the header offset
        self.headerOffset=self.headerOffset+npoints


    #==================================================
    # Write the detector data to files
    #==================================================
    def writeDetectorFileAtPoint(self,point):
        # Can only right MCA on the fly....
        mcaname = "%s_scan_%d_index_%d.dat" % (self.mcarootname, self.tag, point)
        print 'Writing scan point', point, 'to', mcaname
        command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw " % (point, mcaname)
        self.das.sendCommand(command)
        scalername = "%s_scan_%d_index_%d_scalar.dat" % (self.mcarootname, self.tag, point)
        self.writeDetectorScalerFile(point, scalername)
        try:
            if(os.path.exists(mcaname)):
                self.archiveFileList.append(mcaname)
                self.fileArchiveCounter += 1
            if(os.path.exists(scalername)):
                self.archiveFileList.append(scalername)
                self.fileArchiveCounter += 1
            if(self.fileArchiveCounter >= 100):
                self.archiver.registerFiles("scan-" + str(self.fileno), self.archiveFileList)
                self.fileArchiveCounter = 0
                self.archiveFileList = []
       
        except:
            print "unable to register files for archiving " + mcaname
        return mcaname, scalername

    
   
    #==================================================
    # Write the data to a file
    #==================================================
    def writeSummaryAtPoint(self,point_index,position,collectionTime):
        ##read the windowed data directly from memory
        scalerData=self.readScalarData(point_index)
        windowedData=scalerData[2]
        totalw=0
        for j in range(9):
            if(self.detectorMask[j]==1):
                totalw=totalw+windowedData[j]
        
        fid = open(self.datafilename,'a')
        print >>fid,position,self.mDegToEnergy(position),collectionTime,self.ionchamberData[point_index][0],\
            self.ionchamberData[point_index][1],self.ionchamberData[point_index][2],str(windowedData[0:]).strip('[]').replace(',',''), totalw
        fid.close()
        ##do the dead time correction
        self.writeDTC(point_index, scalerData)
        ##to include the dead time corrected values instead of the raw values replace the above lines with the follwoing 
        ##four lines
        #corrWindows,totalW=self.deadTimeCorrectWindows(self.writeDetectorScalerFile(point_index)[0],collectionTime)
        #fid = open(self.datafilename,'a')
        #print >>fid,position,comboDCM.calcEnergy(position/1000.0),collectionTime,self.ionchamberData[point_index][0],\
        #    self.ionchamberData[point_index][1],self.ionchamberData[point_index][2],str(corrWindows[0:]).strip('[]').replace(',',''), totalW
        #fid.close()
        # SDP Stuff
        detectorVector = Vector()
        detectorVector.add(self.ionchamberData[point_index])
        detectorVector.add(windowedData)
        positionVector = Vector()
        positionVector.add(str(position))
        #sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,positionVector,detectorVector,"Panel Name","I18 Custom SDP","Header String",self.datafilename)
        sdp = ScanDataPoint("Exafs FluAngleScan",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.datafilename,0)
        sdp.setScanIdentifier(str(self.fileno))
        self.controller.update(None, sdp)
        self.mcontroller.update(None, sdp)
        return totalw

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

    #==================================================
    # Window an mca contained in data between two values, start and end
    #==================================================
    def windowData(self,data,start,end):
        sum=0.0    
        for i in range(start,end):
            sum=sum+data[i]
        return sum    
                    
    #==================================================
    # mDegForK converts k value (in inverse angstroms) to mDeg by using the java
    # Converter class.
    #==================================================
    def mDegForK(self,k,edgeEnergy,twoD):
        return gda.gui.exafs.Converter.convert(k,gda.gui.exafs.Converter.PERANGSTROM, gda.gui.exafs.Converter.MDEG,edgeEnergy, twoD)

    #==================================================
    # timeForK calculates the appropriate counting time for a particular k value
    # ==================================================
    def timeForK(self,k,start,end,kWeighting,kEndTime,kStartTime):
        a = Math.pow(k - start, kWeighting)
        b = Math.pow(end - start, kWeighting)
        c = (kEndTime - kStartTime)
        time = kStartTime + (a * c) / b
        # round to nearest 1miliseconds as this is all the ion chambers can collect in
        time=Math.round(time/10.0) * 10.0
        return time

    #==================================================
    #
    # Produces the tfg setup-groups used for kscans
    # In kscans you may want a time increase from start to finish
    # This method produces a series of individual tfg time frames for each time step in the scan
    #==================================================
    def getTFGCommandForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
        difference = end - start;
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        currentpos = start
        tfglist="tfg setup-groups cycles 1 \n"
        for  j in range(npoints+1):
            secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
            tfglist = tfglist + "1 0.01 %f 0 7 -1 0 \n" %(secTime/1000.0)
            currentpos = currentpos + step
        tfglist=tfglist+"-1 0 0 0 0 0 0 "
        return tfglist

    #==================================================
    #
    #  Creates the file used for the EXAFS
    # 
    #==================================================
    def createFile(self):
        if(os.path.exists(self.datafilename)==0):
            fid=open(self.datafilename,'w')
            df = SimpleDateFormat('hh.mm.dd.MM.yyyy')
            today = df.format(Date()) 
            print "Writing data to file:"+self.datafilename
            print "Writing mca file to:"+self.mcadir
            # write datetime
            line = " I18_EXAFS_RUN="+ str(self.fileno)+" "+ today
            print>>fid,line
            print>>fid,self.title
            print>>fid,self.condition1
            print>>fid,self.condition2
            print>>fid,self.condition3
            print>>fid,'Sample X=',MicroFocusSampleX.getPosition(),'Sample Y=',MicroFocusSampleY.getPosition()
            print>>fid,'comboDCM energy time I0 It drain flu1 flu2 flu3 flu4 flu5 flu6 flu7 flu8 flu9 flutot'
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
            # write the data we have so far and return
            try:
                self.stopDetector()
                # Need to read scalars and dtc correct the data    
                self.writeScalarsAndDTC(npoints)
                #self.writeSummary(npoints,start,end,step,collectionTime)
            except:
                print 'error in checkforInterrupt'
            self.interrupted=Boolean(0)
            self.paused=Boolean(0)
            self.converter.enableAutoConversion()
            JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
            scandata = Vector()
            scandata.add("STOP")
            self.controller.update(None, scandata)
            self.mcontroller.update(None, scandata)
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
            try:
                self.stopDetector()
                self.writeScalarsAndDTC(npoints)    
                #self.writeKScanSummary(npoints,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
            except:
                print 'error in Kscan interrupt'
            self.interrupted=Boolean(0)
            self.paused=Boolean(0)
            self.converter.enableAutoConversion()
            JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
            scandata = Vector()
            scandata.add("STOP")
            self.controller.update(None, scandata)
            self.mcontroller.update(None, scandata)
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

    #==================================================
    # To set the resolution binning used by xspress
    #  Usage
    #  setResMode(0)   .. all grades processed
    #  setResMode(1)   .. variable all grades summed into 1 grade
    #  setResMode(1,8)   variable all grades from 0-7 put in one grade and 8-15 in next grade
    #==================================================
    def setResMode(self,mode,map=None):
        if(mode==0):
            command="xspress2 set-resmode \"xsp1\" 0 0"
            self.das.sendCommand(command)
        else:
            if(map==None or map < 0 or map > 15):
                command="xspress2 set-resmode \"xsp1\" 1 0"
            else:
                command="xspress2 set-resmode \"xsp1\" 1 %d" %(map)
            self.das.sendCommand(command)

    #==================================================
    #
    # To set the header info used in the script
    #
    #==================================================
    def setHeaderInfo(self,title,condition1,condition2,condition3):
        self.title=title
        self.condition1=condition1
        self.condition2=condition2
        self.condition3=condition3
    #==================================================
    #
    # Get corrected counts 
    #
    #==================================================
    def getCorrectedCounts(self,countData,resetData,liveTime):
        realCounts=[]
        for i in range(len(countData)):
            realCounts.append(countData[i]*(1.0/(liveTime-((12.5e-9)*resetData[i]))))
        return realCounts
    #==================================================
    #
    # Get corrected counts 
    #
    #==================================================
    def reLinearizeCounts(self,corrCounts):
        process_times=[3.4e-07,3.8e-07,3.7e-07,3.0e-07,3.4e-07,3.5e-07,3.3e-07,3.0e-07,3.3e-07]
        realCounts=[]
        for i in range(len(process_times)):
            a=process_times[i]*corrCounts[i]
            aa=a*a
            eqn1=(-10.0+27.0*a+5.196152423*sqrt(4-20.0*a+27.0*aa))**(1.0/3.0)
            eqn2=(1.0/(3.0*process_times[i]))
            eqn3= eqn2*eqn1 - 2*eqn2/eqn1 + 2*eqn2  
            realCounts.append(eqn3)
        return realCounts

    #==================================================
    #
    # Read in a scalar data file and return array
    #
    #==================================================
    def readScalarDataFile(self,scalarfile):
        scalarData=[] 
        for j in range(3):
            scalarData.append(range(9))
        fis =FileInputStream(scalarfile)
        dis =DataInputStream(fis)
        scalerBytes =jarray.zeros(27*4,'b')
        dis.read(scalerBytes, 0, 27*4)
        fis.close()
        offset = 0
        #for j in range(3):
         #   for l in range(0,36,4):
         #       scalarData[j][l/4]= (0x000000FF & scalerBytes[offset+l+0]) + ((0x000000FF & scalerBytes[offset+l+1])<<8)+((0x000000FF & scalerBytes[offset+l+2])<<16)+((0x000000FF & scalerBytes[offset+l+3])<<24)
          #  offset=offset+36
        for l in range(9):
            for j in range(0,12,4):
                scalarData[j/4][l]= (0x000000FF & scalerBytes[offset+j+0]) + ((0x000000FF & scalerBytes[offset+j+1])<<8)+((0x000000FF & scalerBytes[offset+j+2])<<16)+((0x000000FF & scalerBytes[offset+j+3])<<24)
            offset=offset+12    
        fis.close()
        return scalarData

#==============================================================
# Read the scaler data from memory
#==============================================================

    def readScalarDataNoRetry(self,point):
        scalarData=[]
        scalarstring=''
        command = "read 0 0 %d 3 9 1 from 1" % (point)
        scalarString=self.das.getData(command)
        for t in range(10):
            if scalarString =="" :
                print str(t),"reading scaler from memory "
                time.sleep(1)
                scalarString=self.das.getData(command)
            else:
                break
            
        try:
            for j in range(3):
                 scalarData.append(range(9))
            k=0
            for i in range(9):
                for j in range(3):
                    scalarData[j][i]=int(scalarString[k])
                    k=k+1
            return scalarData
        except:
            type, exception, traceback = sys.exc_info()
            self.readError = self.readError + 1
            self.readErrorList.append(point)
            #handle_messages.log(None,"Error in readScalarDataNoRetry - scalarString = " + `scalarString` + " readErrorList = " + `self.readErrorList`, type, exception, None, True)

    def readScalarData(self,point):
        #timeout = self.das.getSocketTimeOut()
        try:
            #self.das.setSocketTimeOut(10)
            #for i in range(20):
             #   self.readScalarDataNoRetry(point)
             #   thread.start_new_thread(self.readScalarDataNoRetry, (point,))
            data = self.readScalarDataNoRetry(point)
            #self.das.setSocketTimeOut(timeout)
            return data
        except:
            type, exception, traceback = sys.exc_info()
            #handle_messages.log(None,"Error in readScalarData - retrying", type, exception, traceback, False)
        #retry once
        #self.das.setSocketTimeOut(timeout)
        try:
            return self.readScalarDataNoRetry(point)
        except:
            type, exception, traceback = sys.exc_info()
            #handle_messages.log(None,"Error in readScalarData - Giving up after 4 retries, returning zeroes", type, exception, traceback, False)
            scalarData=[]
            for j in range(3):
                 scalarData.append(range(9))
            for i in range(9):
                for j in range(3):
                    scalarData[j][i]=0                    
            return scalarData
    #==================================================
    # Dead time correct some windowed data
    #==================================================
    def deadTimeCorrectWindows(self,scalarFile,collectionTimeSecs):
        #
        # now read scalar data
        # 
        scalarData=self.readScalarDataFile(scalarFile)
        liveTime=collectionTimeSecs
        corrCounts=self.getCorrectedCounts(scalarData[0],scalarData[1],liveTime)
        measuredCounts=scalarData[0]
        ##windowed values are stored in the scaler
        windowedData= scalarData[2]
        relinCounts=self.reLinearizeCounts(corrCounts)
        factor=[]
        for j in range(len(relinCounts)):
            if(relinCounts[j]==0 or measuredCounts[j]==0):
                val=1
                factor.append(1.0)
            else:
                val = (relinCounts[j]/measuredCounts[j])
                factor.append(val*liveTime)
        correctWindows=[]
        corrWindTot=0.0
        for j in range(9):
            correctW=float(windowedData[j])*factor[j]
            corrWindTot=corrWindTot+correctW
            correctWindows.append(correctW)
        return correctWindows,corrWindTot




    #==================================================
    #  This simply increments the file no.s etc.
    # useful if doing repeats or resusing the scan class
    #==================================================
    def incrementFilename(self):
        self.fileno=self.runs.getCurrentFileNumber()+1
        self.runs.incrementNumber()
        self.datadir=PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
        self.mcarootname=self.mcadir+str(self.fileno)
        if not os.path.isdir(self.mcadir):
            os.mkdir(self.mcadir)
        self.tag=1
        self.interrupted=Boolean(0)
        
        
    def setScalerWindows(self, detector,windowMin, windowMax):
        command="xspress2 set-window \"xsp1\" %d %d %d" %(detector, windowMin, windowMax)
        self.das.sendCommand(command)

    def getDataFileName(self):
        return self.datafilename

    #
    # read in a lookup table
    #
    def read_movement_lookuptable(self):
	f=open(self.movement_table)
	AA=f.read()
	AA=AA.split('\n')
	for i in range(len(AA)-1):
		a = AA[i].split(" ")
		print a
		self.move_braggset.append(a[0])
		self.move_xmov.append(a[1])
		self.move_ymov.append(a[2])

	f.close()
          # wrong order for interpolation...should be increasing angle so just reverse the lists...
	self.move_braggset.reverse()
	self.move_xmov.reverse()
	self.move_ymov.reverse()

    # lookup x move
    #	
    def lookup_x_move(self,bragg):
	newxmov= self.simpleInterpolate(bragg,self.move_braggset, self.move_xmov)
	return newxmov

    #
    # lookup y move
    #	
    def lookup_y_move(self,bragg):
	newymov= self.simpleInterpolate(bragg,self.move_braggset, self.move_ymov)
	return newymov

    def simpleInterpolate(self,x,xdata,ydata):
        lindex=0
        hindex=len(xdata)
        while(hindex-lindex>1):
            mindex=(hindex+lindex)/2
            if(x < xdata[mindex]):
                hindex=mindex
            elif(x > xdata[mindex]):
                lindex=mindex
        slope=(ydata[hindex]-ydata[lindex])/(xdata[hindex]-xdata[lindex])
        dx=x-xdata[lindex]
        dy=dx*slope
        return ydata[lindex]+dy

    #
    # Sample movement lookup table
    #
    def setSampleMovementLookupTable(self,filename):
	self.movement_table=filename
	self.read_movement_lookuptable()

   #
   # track the x,y movement during a scan
   #
   def updateStagePosition(self,bragg):
       ymove=self.lookup_y_move(bragg)
       xmove=self.lookup_y_move(bragg)
       inc MicroFocusSampleY ymove
       inc MicroFocusSampleX xmove



