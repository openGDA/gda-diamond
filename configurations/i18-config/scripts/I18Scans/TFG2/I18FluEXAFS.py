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
        self.scannableNamesVector.add(dcm_mono)
        self.detectorNamesVector=Vector()
        self.detectorNamesVector.add(counterTimer01)
        self.detectorNamesVector.add(counterTimer02)
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
                self.headerOffset=7
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
        self.clearDetector()
        self.setupTFGForAngleScan(npoints,collectionTime)
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
            while(BeamMonitor.collectBeforeTopupTime(collectionTime/1000.0)==1):
                print 'Top up coming : Pausing until resumed'
                try:
                    sleep(1)
                except:
                    self.interrupted=1    
                self.checkForAngleInterrupt(i-1)

            # Move mono to start position
            self.checkForAngleInterrupt((i-1))
            try:
                self.energyController.moveTo(currentpos)
            except:
                self.interrupted=1
            self.checkForAngleInterrupt((i-1))
            # tfg starts paused so tell it to continue
            if(i==0):
                 counterTimer01.start()
            counterTimer01.restart()
            while(counterTimer01.getStatus()==1):
                sleep(0.05)
            self.checkForAngleInterrupt(i-1)
            # Now while collecting data, output the last point....
            if(i>=1):
                ##get the mca data for the previous point
                thread.start_new_thread(self.writeDetectorFileAtPoint,(i-1,))
                self.writeSummaryAtPoint(i-1,oldpos,collectionTime)
            self.checkForAngleInterrupt((i-1))
            if(i==npoints-1):
                self.stopDetector()
                ##get the mca data for the previous point
                self.writeDetectorFileAtPoint(i)
                totalw=self.writeSummaryAtPoint(i,currentpos,collectionTime)
            # print out some progress
            self.checkForAngleInterrupt((i-1))
            # Move the mono
            oldpos=currentpos
            currentpos=currentpos+step

        ##shift the header offset so that dTC data is written at the corrected position in the _dtc file
        self.shiftHeaderOffset(npoints)
        self.tag=self.tag+1
        print 'Finished angle scan'
        handle_messages.simpleLog("Angle Read error count " + str(self.readError))
        handle_messages.simpleLog("Angle Read error points list " + `self.readErrorList`)


    #==================================================
    # Performs a kscan in step mode
    # ==================================================
    def kscan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
        i=0
        self.createFile()
        self.mcaList=[]
        self.scalarList=[]
        # check that step is negative when moving downwards to stop
        difference = end - start
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        currentpos=start
        oldpos=currentpos
        secTime=1000.0
        # prepare detector for collection
        print 'Clearing and Preparing Detector'
        self.clearDetector()
        self.setupTFGForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
        print 'Starting k scan'
        print 'Bragg Energy Time I0 It Idrain'
        self.checkForKScanInterrupt(0)
        lookup = finder.find("lookup_name_provider")
        for i in range(npoints):
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
            while(BeamMonitor.collectBeforeTopupTime(secTime/1000.0)==1):
                print 'Top up coming : Pausing until resumed'
                try:
                    sleep(1)
                except:
                    self.interrupted=1    
                self.checkForKScanInterrupt(i-1)

            mdegPosition = self.mDegForK(currentpos,edgeEnergy,twoD)
            # Move mono to start position
            try:
                self.energyController.moveTo(mdegPosition)
            except:
                self.interrupted=1
            self.checkForKScanInterrupt((i-1))
            # First time start tfg
            if(i==0):
                counterTimer01.start()
            # else tfg continue
            counterTimer01.restart()
            while(counterTimer01.getStatus()==1):
                sleep(0.05)
            self.checkForKScanInterrupt((i-1))
            if(i>=1):
                ##get the mca data for the previous point
                thread.start_new_thread(self.writeDetectorFileAtPoint,(i - 1,))
                self.writeSummaryAtPoint(i-1,oldpos,oldsecTime)

            self.checkForKScanInterrupt((i-1))
            self.ionchamberData.append(self.ionchambers.getPosition())
            self.checkForKScanInterrupt((i-1))
            if(i==npoints-1):
                self.stopDetector()
                ##get the mca data for the previous point
                self.writeDetectorFileAtPoint(i)
                totalw=self.writeSummaryAtPoint(i,mdegPosition,secTime)
            # Move the mono
            oldpos=mdegPosition
            currentpos=currentpos+step
            # Ready the ion chambers
            self.ionchambers.stop()
            #  write out at end
        self.checkForKScanInterrupt((i-1))
        self.shiftHeaderOffset(npoints)
        self.checkForKScanInterrupt((i-1))
        self.tag=self.tag+1
        print 'Finished k scan'
        handle_messages.simpleLog("Read error count " + str(self.readError))
        handle_messages.simpleLog("Read error points list " + `self.readErrorList`)

    #==================================================
    #  Disables, Clears and enables the detector
    #  Sets up tfg for a given noOfFrames and  collectionTime
    #  pausing in the dead frame and dead port=1 for adc triggering
    #  and finally starts the tfg which means it sits waiting for a software based continue command
    #==================================================
    def clearDetector(self):
        self.das.sendCommand("disable 0")
        self.das.sendCommand("clear 0")
        self.das.sendCommand("enable 0")


    #==================================================
    # Stop the tfg and disable the detector
    #==================================================
    def stopDetector(self):
        self.das.sendCommand("disable 0")
        counterTimer01.stop()

    #==================================================
    # Write the detector data to files
    #==================================================
    def writeDetectorScalerFile(self,point,scalerfile):
        sname = scalerfile
        print 'Writing scalar point',point,'to',sname
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
        ionChamberData=counterTimer01.readFrame(point_index)
        windowedData=scalerData[2]
        totalw=0
        for j in range(9):
            if(self.detectorMask[j]==1):
                totalw=totalw+windowedData[j]
        fid = open(self.datafilename,'a')
        print >>fid,position,self.mDegToEnergy(position),collectionTime,ionChamberData[0],\
            ionChamberData[1],ionChamberData[2],str(windowedData[0:]).strip('[]').replace(',',''), totalw
        fid.close()
        ##do the dead time correction
        self.writeDTC(point_index, scalerData)
        # SDP Stuff
        detectorVector = Vector()
        ### dummy val;ue added at the end, as the CounterTimer01 is supposed to return 4 values
        detectorVector.add(ionChamberData)
        detectorVector.add(windowedData)
        positionVector = []
        positionVector.append(position)
        sdp = ScanDataPoint()
        sdp.setUniqueName("Exafs FluAngleScan")
        for s in self.scannableNamesVector:
            sdp.addScannable(s)
        for d in self.detectorNamesVector:
            sdp.addDetector(d)
        for p in positionVector:
            sdp.addScannablePosition(p,["%.4f"] )
        newdata=[ionChamberData[0],ionChamberData[1],ionChamberData[2],0.0]
        sdp.addDetectorData(newdata,["%5.2g","%5.2g","%5.2g","%5.2g"])
        sdp.addDetectorData(windowedData,["%5.2g","%5.2g","%5.2g","%5.2g","%5.2g","%5.2g","%5.2g","%5.2g","%5.2g"] )
        sdp.setCurrentFilename(self.datafilename)
        self.controller.update(None, sdp)
        self.mcontroller.update(None, sdp)
        print position,self.mDegToEnergy(position),collectionTime,ionChamberData[0],ionChamberData[1],ionChamberData[2],totalw        

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
            counterTimer01.addFrameSet(1,deadTime,secTime,0,7,-1,0)
            currentpos = currentpos + step
        counterTimer01.loadFrameSets()

    #==================================================
    #
    # Produces the tfg setup-groups used for kscans
    # In kscans you may want a time increase from start to finish
    # This method produces a series of individual tfg time frames for each time step in the scan
    #==================================================
    def setupTFGForAngleScan(self,noOfFrames,collectionTime):
        counterTimer01.clearFrameSets()
        deadTime=1.0e-4
        counterTimer01.addFrameSet(noOfFrames,deadTime,collectionTime,0,0,-1,0)
        counterTimer01.loadFrameSets()

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
        try:
            data = self.readScalarDataNoRetry(point)
            return data
        except:
            type, exception, traceback = sys.exc_info()
        try:
            return self.readScalarDataNoRetry(point)
        except:
            type, exception, traceback = sys.exc_info()
            scalarData=[]
            for j in range(3):
                 scalarData.append(range(9))
            for i in range(9):
                for j in range(3):
                    scalarData[j][i]=0                    
            return scalarData


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
