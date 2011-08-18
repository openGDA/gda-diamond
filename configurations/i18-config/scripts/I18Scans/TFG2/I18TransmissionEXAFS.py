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
import os
import jarray
from gda.data import PathConstructor
from gda.data.fileregistrar import FileRegistrarHelper
from gda.jython import JythonServerFacade
#
# TRANSMISSION EXAFS SCAN
# run SlaveCounterTimer.py
# run I18TransmissionExafsClass.py
#
# This doesn't plot data, it just collects it. ion chambers  which are synched via the tfg and adc.
#
# Create the class
#    myscan=I18TransmissionExafsScanClass()
#    myscan.anglescan(8824.0,8739.460869565219,-3.8608695652174387,1000.0)
#    myscan.anglescan(8735.599999999999,8698.5,-0.6999999999999865,1000.0)
#
# Now do the kscan with the values from the configure button in the exafs panel
#
#    myscan.kscan(3.0,12.0,0.04,1000.0,3000.0,3,13.039848732586526,6.271000000000002)
#
#
class I18TransmissionExafsScanClass(ScriptBase):
    def __init__(self):
        self.scannableNamesVector=Vector()
        self.scannableNamesVector.add(dcm_mono)
        self.detectorNamesVector=Vector()
        self.detectorNamesVector.add(counterTimer01)
        self.controller = finder.find("ExafsController")
        self.mcontroller = finder.find("MicroFocusController")
        self.das=finder.find("daserver")
        self.ionchambers=ionChambers
        self.converter = finder.find("auto_mDeg_idGap_mm_converter")
        self.energyController = JythonServerFacade.getInstance().getFromJythonNamespace(LocalProperties.get("gda.i18.energyController"))
        # default collect all
        self.title="TITLE"
        self.condition1="CONDITION1"
        self.condition2="CONDITION2"
        self.condition3="CONDITION3"
        self.xspress = finder.find("xspress2system")
        self.runs=NumTracker("tmp")
        self.runext='.dat'
        self.fileno=self.runs.getCurrentFileNumber()+1
        self.runs.incrementNumber()
        self.datadir=PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        self.scanList=[]
        self.noOfRepeats=1
        self.noOfPoints=0
        self.interrupted=0
        self.archiveFileList=[]
        self.fileArchiveCounter=0
        self.archiver = archiver


    def addAngleScan(self,start,end,step,collectionTime):
        self.noOfPoints=self.noOfPoints+int((end-start)/step)
        self.scanList.append(['a',start,end,step,collectionTime])

    def addKScan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
        self.noOfPoints=self.noOfPoints+int((end-start)/step)
        self.scanList.append(['k',start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD])


    def setNoOfRepeats(self,repeats):
        self.noOfRepeats=repeats

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

    def startScan(self):
        #
        # Send repeat and point information to the GUI
        # then start the scan
        #
        self.setupGUI()
        for i in range(self.noOfRepeats):
            if(i>0):                
                self.incrementFilename()
                
            ##selecting the harmonic
            if(self.scanList[0][0] =='a'):
                moveTo = self.scanList[0][1]
            elif(self.scanList[0][0]=='k'):
                moveTo =self.mDegForK(self.scanList[0][1], self.scanList[0][7],self.scanList[0][8])
            print 'harmonic selector ', moveTo
            lookup = finder.find("lookup_name_provider")
            try:
                self.converter.enableAutoConversion()
                self.energyController.moveTo(moveTo)
                #comboDCM_nogap.moveTo(moveTo)
                print 'moving to:',idgap.getPosition(),dcm_bragg.getPosition(),dcm_perp.getPosition()
                self.converter.disableAutoConversion()
            except:
                print 'Probem setting harmonic for EXAFS: Enabling autoconversion'
                self.interrupted=1
                self.converter.enableAutoConversion()
            print 'Harmonic set to ',lookup.getConverterName()
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
                
                if(lock):
                    print 'unlocking xpress'
                    self.xspress.unlock()
                if(os.path.exists(self.datafilename)):
                    self.archiveFileList.append(self.datafilename)
                try:
                    if(len(self.archiveFileList ) != 0):
                        self.archiver.registerFiles("scan-" + str(self.fileno), self.archiveFileList)
                except:
                    print "Unable archive files " + self.datafilename
                self.converter.enableAutoConversion()

    
    def setupGUI(self):
        scandata=Vector()
        # Type of scan
        scandata.add("TransScan")
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

    #
    # Performs an angle scan in step mode
    # 
    def anglescan(self,start,end,step,collectionTime):
        self.createFile()
        # find no of points
        difference = end - start
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        currentpos=start*1.0
        # Set collection times
        self.prepareDetectorForCollection(npoints,collectionTime)
        # loop over npoints
        print 'Starting angle scan'
        print 'Angle \t Energy \tTime \tI0\t It\t Idrain\t'
        self.checkForInterrupt()
        for i in range(npoints):
            self.checkForPause()
            # Check beam is running
            while(BeamMonitor.beamOn()==0):
                self.checkForInterrupt()
                print 'Beam lost : Pausing until resumed'
                try:
                    sleep(60)
                except:
                    self.interrupted=1                    
                self.checkForInterrupt()
            # Move mono to start position
            self.checkForInterrupt()
            try:
                self.energyController.moveTo(currentpos)
            except:
                self.interrupted=1
            self.checkForInterrupt()
            #
            # topup test
            #
            while(BeamMonitor.collectBeforeTopupTime(collectionTime/1000.0)==1):
                print 'Top up coming : Pausing until resumed'
                try:
                    sleep(1)
                except:
                    self.interrupted=1    
                self.checkForInterrupt()

            self.checkForInterrupt()
            #
            # tfg starts paused so tell it to continue
            #
            if(i==0):
                counterTimer01.start()
            counterTimer01.restart()
            self.checkForInterrupt()
            while(counterTimer01.getStatus()==1):
                sleep(0.05)     
            print 'readit',counterTimer01.readFrame(0)

            self.checkForInterrupt()
            self.writeSummary(i,currentpos,collectionTime)
            # Move the mono
            currentpos=currentpos+step
        print 'Finished angle scan'

    #
    # In a scan you create a new scan object for each scan
    # You can  reuse the i18exafs scan
    #  This simply increments the file no.s etc.
    #
    def reset(self):
        self.fileno=self.runs.getCurrentFileNumber()+1
        self.runs.incrementNumber()
        self.datadir=PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
        self.mcarootname=self.mcadir+str(self.fileno)
        if not os.path.isdir(self.mcadir):
            os.mkdir(self.mcadir)
        self.tag=1
        self.createFile()
        self.interrupted=Boolean(0)
        

    #
    # Performs a kscan in step mode
    # 
    def kscan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
        self.createFile()
        # check that step is negative when moving downwards to stop
        difference = end - start
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        currentpos=start
        # prepare detector for collection
        print 'Preparing TFG'
        self.prepareDetectorForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
        print 'Starting k scan'
        print 'Angle\tEnergy\tTime\tI0\tIt\tIdrain\t'
        self.checkForInterrupt()
        for i in range(npoints):
            self.checkForPause()
            # Check beam is running
            while(BeamMonitor.beamOn()==0):
                print 'Beam lost : Pausing until resumed'
                try:
                    sleep(60)
                except:
                    self.interrupted=1
                self.checkForInterrupt()

            mdegPosition = self.mDegForK(currentpos,edgeEnergy,twoD)
            self.checkForInterrupt()
            secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
            self.checkForInterrupt()
            try:
                self.energyController.moveTo(mdegPosition)
            except:
                self.interrupted=1
            self.checkForInterrupt()
            #
            # topup test
            #
            while(BeamMonitor.collectBeforeTopupTime(secTime/1000.0)==1):
                print 'Top up coming : Pausing until resumed'
                try:
                    sleep(1)
                except:
                    self.interrupted=1    
                self.checkForInterrupt()

            #
            # tfg starts paused so tell it to continue
            #
            if(i==0):
                counterTimer01.start()
            counterTimer01.restart()
            self.checkForInterrupt()
            while(counterTimer01.getStatus()==1):
                sleep(0.05)            
            self.checkForInterrupt()
            self.writeSummary(i,mdegPosition,secTime)
            # Move the mono
            currentpos=currentpos+step
        print 'Finished k scan'


    #==================================================
    #  Disables, Clears and enables the detector
    #  Sets up tfg for a given noOfFrames and  collectionTime
    #  pausing in the dead frame and dead port=1 for adc triggering
    #  and finally starts the tfg which means it sits waiting for a software based continue command
    #==================================================
    def prepareDetectorForCollection(self,noOfFrames,collectionTime):
        self.setupTFGForAngleScan(noOfFrames,collectionTime)
    #==================================================
    #  Disables, Clears and enables the detector
    #  Sets up tfg for a set of possibly variable length time frames
    #  and finally starts the tfg which means it sits waiting for a software based continue command
    #==================================================
    def prepareDetectorForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
        self.setupTFGForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
    #
    # Stop the tfg and disable the detector
    #
    def stopTFG(self):
        self.das.sendCommand("tfg init")

    def writeSummary(self,point_index,currentpos,collectionTime):
        print counterTimer01.readFrame(0),point_index
        data=counterTimer01.readFrame(point_index)
        print currentpos,comboDCM_eV.getPosition(),collectionTime,data[0],data[1],data[2]
        fid = open(self.datafilename,'a')        
        print >>fid,currentpos,comboDCM_eV.getPosition(),collectionTime,data[0],data[1],data[2]
        fid.close()
        detectorVector = Vector()
        newdata=[data[0],data[1],data[2],0.0]    
        detectorVector.add(newdata)
        positionVector = []
        positionVector.append(currentpos)
        sdp = ScanDataPoint()
        sdp.setUniqueName("Exafs TransScan")
        for s in self.scannableNamesVector:
            sdp.addScannable(s)
        for d in self.detectorNamesVector:
            sdp.addDetector(d)
        for p in positionVector:
            sdp.addScannablePosition(p,["%.4f"] )
        sdp.addDetectorData(newdata,["%5.2g","%5.2g","%5.2g", "%5.2g"])
        sdp.setCurrentFilename(self.datafilename)
        sdp.setScanIdentifier(str(self.fileno))
        self.controller.update(None, sdp)
        self.mcontroller.update(None, sdp)
    #
    # Return energy for a given angle
    #
    def mDegToEnergy(self,angle):
        energy=1977.06581693/self.sind(bragg)
        return energy

    #
    # mDegForK converts k value (in inverse angstroms) to mDeg by using the java
    # Converter class.
    #
    def mDegForK(self,k,edgeEnergy,twoD):
        return gda.gui.exafs.Converter.convert(k,gda.gui.exafs.Converter.PERANGSTROM, gda.gui.exafs.Converter.MDEG,edgeEnergy, twoD)

    #
    # timeForK calculates the appropriate counting time for a particular k value
    # 
    def timeForK(self,k,start,end,kWeighting,kEndTime,kStartTime):
        a = Math.pow(k - start, kWeighting)
        b = Math.pow(end - start, kWeighting)
        c = (kEndTime - kStartTime)
        time = kStartTime + (a * c) / b
        # round to nearest 10milliseconds as this is all the ion chambers can collect in
        time=Math.round(time/10.0) * 10.0
        return time

    #==================================================
    #
    # Produces the tfg setup-groups used for kscans
    # In kscans you may want a time increase from start to finish
    # This method produces a series of individual tfg time frames for each time step in the scan
    #==================================================
    def setupTFGForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
        counterTimer01.clearFrameSets()
        difference = end - start;
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        currentpos = start
        deadTime=1.0e-4
        for  j in range(npoints+1):
            secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
            counterTimer01.addFrameSet(1,deadTime,secTime,0,0,-1,0)
            currentpos = currentpos + step
        counterTimer01.loadFrameSets()

    #==================================================
    #
    # Produces the tfg setup-groups used for kscans
    # In kscans you may want a time increase from start to finish
    # This method produces a series of individual tfg time frames for each time step in the scan
    #==================================================
    def setupTFGForAngleScan(self,noOfFrames,collectionTime):
        print collectionTime,noOfFrames
        counterTimer01.clearFrameSets()
        deadTime=1.0e-4
        counterTimer01.addFrameSet(noOfFrames,deadTime,collectionTime,0,0,-1,0)
        counterTimer01.loadFrameSets()
    #
    #
    # If a user presses the halt or stop button on the gui
    # stops the scan
    #
    # def checkForInterupts(self):
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
            # write datetime
            line = " I18_EXAFS_RUN="+ str(self.fileno)+" "+ today
            print>>fid,line
            print>>fid,self.title
            print>>fid,self.condition1
            print>>fid,self.condition2
            print>>fid,self.condition3
            print>>fid,'Sample X=',MicroFocusSampleX.getPosition(),'Sample Y=',MicroFocusSampleY.getPosition()
            print>>fid,'angle energy time I0 It Idrain'
            fid.close()


    # ========================================
    #  Read in a window to be used on the mca files 
    # ========================================
    def setWindows(self,filename,desiredWindow):
        print 'Do nothing'

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
    # Checks to see if an angle scan has been paused
    #
    #==================================================
    def checkForPause(self):
        if(self.paused):
            JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
            while(self.paused):
                try:
                    print 'Scan paused - Awaiting resume'
                    java.lang.Thread.sleep(10000)
                except lang.InterruptedException:
                    self.stopTFG()    
                    self.interrupted=Boolean(0)
                    self.paused=Boolean(0)
                    JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
                    print  'Now the nasty bit: throw an exception to stop running'
                    raise lang.InterruptedException()
                    
    #==================================================
    #
    # Checks to see if an angle scan has been interrupted
    #
    #==================================================
    def checkForInterrupt(self):
        #if(self.facade.getScanStatus()==0 and self.facade.getScriptStatus()==0):
        if(self.interrupted):
            print 'Stopping angle scan:'
            #Writing out data taken'
            # write the data we have so far and return
            self.stopTFG()    
            self.interrupted=Boolean(0)
            self.paused=Boolean(0)
            self.converter.enableAutoConversion()
            JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
            scandata = Vector()
            scandata.add("STOP")
            self.controller.update(None, scandata)
            self.mcontroller.update(None, scandata)
            self.interrupted =0
            print  'Now the nasty bit: throw an exception to stop running'
            raise lang.InterruptedException()
            raise lang.InterruptedException()

    #
    # In a scan you create a new scan object for each scan
    # You can  reuse the i18exafs scan
    #  This simply increments the file no.s etc.
    #
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
    #
    #
    #
    def getDataFileName(self):
        return self.datafilename
