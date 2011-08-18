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
        self.title="TITLE"
        self.condition1="CONDITION1"
        self.condition2="CONDITION2"
        self.condition3="CONDITION3"
        # Script code
        self.das=finder.find("daserver")
        self.ionchambers=SlaveCounterTimer()
        self.converter = finder.find("auto_mDeg_idGap_mm_converter")
        self.windowValues=[[0,4095]]*9
        self.windowName='ALL'
        self.ionchamberData=[]
        self.mcaList=[]
        self.scalarList=[]
        self.runs=NumTracker("tmp")
        self.runprefix='i18exafs'
        self.runext='.dat'
        self.fileno=self.runs.getCurrentFileNumber()+1
        self.runs.incrementNumber()
        self.datadir=PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        if(detectorList!=None):
            self.detectorMask=detectorList
        else:
            self.detectorMask=[1,1,1,1]
        #print self.ftppassword
        self.tag=1
        self.facade=JythonServerFacade.getInstance()
        self.scanList=[]
        self.noOfRepeats=1
        self.noOfPoints=0
        self.headerOffset=7


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
            #print 'harmonic selector ', moveTo
            lookup = finder.find("lookup_name_provider")
            try:
                self.converter.enableAutoConversion()
                comboDCM_d.moveTo(moveTo)
                print 'moving to:',idgap.getPosition(),dcm_bragg.getPosition(),dcm_perp.getPosition()
                self.converter.disableAutoConversion()
            
            except:
                self.interrupted=1
                self.converter.enableAutoConversion()
            print 'Harmonic set to ',lookup.getConverterName()
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
            print '======================'
            print '========WARNING========'
            print 'This uses the windows defined in ROI-1 of each vortex MCA'
            print '======WARNING=========='
            print '======================'
            

    #==================================================
    # Performs an angle scan in step mode
    # ==================================================
    def anglescan(self,start,end,step,collectionTime):
        #self.converter.enableAutoConversion()
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
        # Set the collection time
        self.ionchambers.setCollectionTime(collectionTime)
        # loop over npoints
        #print 'Starting angle scan'
        print 'Bragg Energy Time I0 It Idrain'
        self.checkForAngleInterrupt(0)
        oldpos=currentpos
        lookup = finder.find("lookup_name_provider")
        for i in range(npoints):
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

            # Move mono to start position
            self.checkForAngleInterrupt((i-1))
            try:
                
                comboDCM_d.moveTo(currentpos)
                print 'moving to:',idgap.getPosition(),dcm_bragg.getPosition(),dcm_perp.getPosition()
            except:
                self.interrupted=1
            self.checkForAngleInterrupt((i-1))
            # Ready the ion chambers
            self.ionchambers.clearAndPrepare()
            self.checkForAngleInterrupt((i-1))
            # tfg starts paused so tell it to continue
            if(i==0):
                 self.das.sendCommand("tfg start")

            self.das.sendCommand("tfg cont")
            self.checkForAngleInterrupt((i-1))
            # Now while collecting data, output the last point....
            if(i>=1):
                ##get the mca data for the previous point
                thread.start_new_thread(self.writeDetectorFileAtPoint,(i-1,))
                totalw=self.writeSummaryAtPoint(i-1,oldpos,collectionTime)
                print lookup.getConverterName(),oldpos,comboDCM.calcEnergy(oldpos/1000.0),collectionTime,self.ionchamberData[i-1][0],self.ionchamberData[i-1][1],self.ionchamberData[i-1][2],totalw
            # Wait until collection is finished
            self.das.sendCommand("tfg wait timebar")
            self.checkForAngleInterrupt((i-1))
            # read out the ion chambers
            while(self.ionchambers.isBusy()>=1):
                self.checkForAngleInterrupt((i-1))
                try:
                    sleep(0.05)
                except:
                    self.interrupted=1
                pass
            self.ionchamberData.append(self.ionchambers.collectData())
            if(i==npoints-1):
                self.stopDetector()
                 ##get the mca data for the previous point
                self.writeDetectorFileAtPoint(i)
                totalw=self.writeSummaryAtPoint(i,currentpos,collectionTime)
                print oldpos,comboDCM.calcEnergy(currentpos/1000.0),collectionTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],totalw

            # print out some progress
            self.checkForAngleInterrupt((i-1))
            # Move the mono
            oldpos=currentpos
            currentpos=currentpos+step
            #  stop detector
        #self.stopDetector()
        ##shift the header offset so that dTC data is written at the corrected position in the _dtc file
        self.shiftHeaderOffset(npoints)
        #self.converter.enableAutoConversion()
        #self.writeDetectorFiles(npoints)
        self.tag=self.tag+1
        
        print 'Finished angle scan'


    #==================================================
    # Performs a kscan in step mode
    # ==================================================
    def kscan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
        #self.converter.enableAutoConversion()
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
        # prepare detector for collection
        print 'Clearing and Preparing Detector'
        self.prepareDetectorForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
        print 'Starting k scan'
        print 'Bragg Energy Time I0 It Idrain'
        self.checkForKScanInterrupt(0)
        lookup = finder.find("lookup_name_provider")
        for i in range(npoints):
            # Check for pause!
            self.checkForKScanPause(i)
            # Check beam is running
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
            #secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
            self.checkForKScanInterrupt((i-1))
            # Set the collection time
            self.ionchambers.setCollectionTime(secTime)
            # Move mono to start position
            try:
                comboDCM_d.moveTo(mdegPosition)
                #comboDCM_nogap.moveTo(mdegPosition)
                #dcm_bragg.moveTo(moveTo)
                #sleep(0.5)
                print 'moving to:',idgap.getPosition(),dcm_bragg.getPosition(),dcm_perp.getPosition()
                #self.converter.disableAutoConversion()
                #ScannableBase.waitForScannable(comboDCM)
            except:
                self.interrupted=1
            self.checkForKScanInterrupt((i-1))
            # Ready the ion chambers
            self.ionchambers.clearAndPrepare()
            self.checkForKScanInterrupt((i-1))
            if(i==0):
                 self.das.sendCommand("tfg start")

            # tfg starts paused so tell it to continue

            self.das.sendCommand("tfg cont")
            self.checkForKScanInterrupt((i-1))
            if(i>=1):
                ##get the mca data for the previous point
                thread.start_new_thread(self.writeDetectorFileAtPoint,(i - 1,))
                #self.writeDetectorFileAtPoint(i - 1)
                totalw=self.writeSummaryAtPoint(i-1,oldpos,oldsecTime)
                print oldpos,comboDCM.calcEnergy(oldpos/1000.0),oldsecTime,self.ionchamberData[i-1][0],self.ionchamberData[i-1][1],self.ionchamberData[i-1][2],totalw
            self.das.sendCommand("tfg wait timebar")
            self.checkForKScanInterrupt((i-1))
            while(self.ionchambers.isBusy()>=1):
                self.checkForKScanInterrupt((i-1))
                try:
                    sleep(0.05)
                except:
                    self.interrupted=1
                pass
            self.ionchamberData.append(self.ionchambers.collectData())
            self.checkForKScanInterrupt((i-1))
            if(i==npoints-1):
                self.stopDetector()
                ##get the mca data for the previous point
                #thread.start_new_thread(self.writeDetectorFileAtPoint,(i,))
                self.writeDetectorFileAtPoint(i)
                totalw=self.writeSummaryAtPoint(i,mdegPosition,secTime)
                print lookup.getConverterName(),mdegPosition,comboDCM.calcEnergy(mdegPosition/1000.0),secTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],totalw
            # Move the mono
            oldpos=mdegPosition
            currentpos=currentpos+step
            #  write out at end
        self.checkForKScanInterrupt((i-1))
        #self.stopDetector()    
        ##shift the header offset so that dTC data is written at the corrected position in the _dtc file
        self.shiftHeaderOffset(npoints)
        #self.converter.enableAutoConversion()
        self.checkForKScanInterrupt((i-1))
        #self.writeDetectorFiles(npoints)
        self.tag=self.tag+1
        print 'Finished k scan'

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
        command = "tfg setup-groups cycles 1 \n%d 0.01 %f 0 1 1 0 \n-1 0 0 0 0 0 0 "  %(noOfFrames,collectionTime)
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
        dtc_filename=self.datadir+'/'+str(self.fileno)+"_dtc.dat"
        if(os.path.exists(dtc_filename)==0):
            fid=open(dtc_filename,'w')
            print >>fid,a[0:5]
            fid.close()

        fid=open(dtc_filename,'a')
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
        corrWindows=Xspress2Utilities.deadTimeCorrectWindows(scalar_files,collectionTime)
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
        mcaname = "%s_scan_%d_index_%d.dat" % (self.mcarootname,self.tag,point)
        print 'Writing scan point',point,'to',mcaname
        #mcaname = mcaname.replace('/dls/i18', '/exports')
        #print 'mcaname is ', mcaname
        #command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw intel " % ( point, mcaname)
        command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw " % ( point, mcaname)
        ##writing file to a ftp server
        #command =    "read 0 0 %d 4096 9 1 from 0 to-remote-file \"%s\" on \"172.23.118.41\" user \"i18user\" password \"bTFjcjBmMGN1cyE=\" raw intel" %(point,mcaname)
        #print 'command =', command
        self.das.sendCommand(command)
        scalername="%s_scan_%d_index_%d_scalar.dat" % (self.mcarootname,self.tag,point)
        self.writeDetectorScalerFile(point, scalername)
        return mcaname,scalername
    
   
    #==================================================
    # Write the data to a file
    #==================================================
    def writeSummaryAtPoint(self,point_index,position,collectionTime):
        ##read the windowed data directly from memory
        scalerData=self.readScalarData(point_index)
        windowedData=scalerData[2]
       # print "windowed",windowedData
        #print "window values",self.windowValues
        totalw=0
        for j in range(9):
            if(self.detectorMask[j]==1):
                totalw=totalw+windowedData[j]
        
        fid = open(self.datafilename,'a')
        print >>fid,position,comboDCM.calcEnergy(position/1000.0),collectionTime,self.ionchamberData[point_index][0],\
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
        self.controller.update(None, sdp)
        self.mcontroller.update(None, sdp)
        return totalw


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
            tfglist = tfglist + "1 0.01 %f 0 1 1 0 \n" %(secTime/1000.0)
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

    def readScalarData(self,point):
        command = "read 0 0 %d 3 9 1 from 1" % (point)
        scalarString=self.das.getData(command)
        #scalarString=['40', '4114', '0', '10', '2657', '0', '12', '3064', '0', '2', '2635', '0', '3', '2627', '0', '5', '2830', '0', '218', '31987', '0', '17', '3119', '0', '936', '158804', '0']
        scalarData=[]
        for j in range(3):
            scalarData.append(range(9))
        k=0
        for i in range(9):
            for j in range(3):
                scalarData[j][i]=int(scalarString[k])
                k=k+1
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
