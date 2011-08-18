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
from jarray import array
from java.util import Date
from java.text import SimpleDateFormat
from gda.util import Password
from gda.data import PathConstructor
#
# EXAFS SCAN USING ION CHAMBERS AND STRUCK 
#
#
# Create the class
#    myscan=I18TransmissionExafsScanClass()
#    myscan.anglescan(8824.0,8739.460869565219,-3.8608695652174387,1000.0)
#    myscan.anglescan(8735.599999999999,8698.5,-0.6999999999999865,1000.0)
#    myscan.kscan(3.0,12.0,0.04,1000.0,3000.0,3,13.039848732586526,6.271000000000002)
#
#
class I18VortexExafsScanClass(ScriptBase):
#class I18ExafsScanClass(ScriptBase):
    def __init__(self):
        self.das=finder.find("daserver")
        self.ionchambers=ionChambers
        self.vortex=xmapMca
        #self.vortexDTCparams=vortexDTCparameters
        # default collect all
        self.ionchamberData=[]
        self.runs=NumTracker("tmp")
        self.runext='.dat'
        self.fileno=self.runs.getCurrentFileNumber()+1
        self.runs.incrementNumber()
        self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        self.scanList=[]
        self.noOfRepeats=1
        self.noOfPoints=0
        self.headerOffset=7
        # EXAFS PANEL CODE
        self.scannableNamesVector=Vector()
        self.scannableNamesVector.add(dcm_mono)
        self.detectorNamesVector=Vector()
        self.detectorNamesVector.add(counterTimer01)
        self.detectorNamesVector.add(xmapMca) 
        self.controller = finder.find("ExafsController")
        self.mcontroller = finder.find("MicroFocusController")
        self.energyController = JythonServerFacade.getInstance().getFromJythonNamespace(LocalProperties.get("gda.i18.energyController"))
        self.tfg = finder.find("tfg")
        self.converter = finder.find("auto_mDeg_idGap_mm_converter")
        self.xspress = finder.find("xspress2system")
        self.title="TITLE"
        self.condition1="CONDITION1"
        self.condition2="CONDITION2"
        self.condition3="CONDITION3"
        self.windowValues=[[0,4095]]*4
        self.windowName='ALL'
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
            try:
                self.converter.enableAutoConversion()
                #comboDCM_d.moveTo(moveTo)
                self.energyController.moveTo(moveTo)
                print 'Harmonic set to ',lookup.getConverterName()
                self.converter.disableAutoConversion()
            except:
                self.interrupted=1
                self.converter.enableAutoConversion()
                print 'Error setting initial harmonic: Harmonic set to ',lookup.getConverterName()
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
                try:
                    if(len(self.archiveFileList ) != 0):
                        self.archiver.registerFiles("scan-" + str(self.fileno), self.archiveFileList)
                except:
                    print "Unable archive files " + self.datafilename
                    
    def clearScanList(self):
        self.scanList=[]
    
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
        currentpos=start
        self.checkForInterrupt()
        self.prepareDetectorForCollection(npoints,collectionTime/1000.0)
        # loop over npoints
        print 'Starting angle scan'
        print 'Bragg\t Energy\tI0\tIt\tIdrain\tVortex'
        self.checkForInterrupt()
        self.ionchambers.clearAndPrepare()
        mysleeptime=collectionTime*0.95/1000.0
        self.vortex.stop()
        for i in range(npoints):
            while(BeamMonitor.beamOn()==0):
                print 'Beam lost : Pausing until resumed'
                try:
                    sleep(60)
                except:
                    print 'Trying to stop during sleep'

            while(BeamMonitor.collectBeforeTopupTime(collectionTime/1000.0)==1):
                print 'Top up coming : Pausing until resumed'
                try:
                    sleep(1)
                except:
                    print 'Trying to stop during sleep - topup'

            # Move mono to start position
            self.vortex.clearAndStart()
            try: 
                #comboDCM_d.moveTo(currentpos)
                self.energyController.moveTo(currentpos)
            except:
                self.interrupted = 1    
            self.checkForInterrupt()
            # Ready the ion chambers
            self.ionchambers.clearAndPrepare()
            # A check to make sure the struck is started (i.e. cleared and waiting for a trigger signal)
            # Early runs occassionally threw odd numbers or zeros out...
            # so put in some check the struck is the right state 
            self.checkForInterrupt()
            while(self.ionchambers.isClear()==0 or self.ionchambers.getStatus()==0):
                print 'ionchambers struck not ready: Waiting to clear'
                try:
                    sleep(0.1)
                except:
                    self.interrupted = 1    
                self.checkForInterrupt()
                self.ionchambers.clearAndPrepare()
                self.checkForInterrupt()
                try:
                    sleep(0.1)
                except:
                    self.interrupted = 1    
                self.checkForInterrupt()
#
# you may have to comment out this block
#
            while(self.vortex.getStatus() == 0):
                print 'vortex not ready: Waiting to clear'
                try:
                    sleep(0.5)
                except:
                    self.interrupted = 1    
                self.checkForInterrupt()
                self.vortex.clearAndStart()
                try:
                    sleep(2.0)
                except:
                    self.interrupted = 1    
                self.checkForInterrupt()
#
# end of block to comment
#
            self.checkForInterrupt()
            #
            # tfg starts paused so tell it to continue
            #
            self.das.sendCommand("tfg cont")
            #
            # wait until it is finished running
            #
            try:
                sleep(mysleeptime)
            except:
                self.interrupted = 1    
            self.checkForInterrupt()
            self.das.sendCommand("tfg wait")
            # read out the ion chambers
            # Update the vortex status
            self.vortex.stop()
            self.ionchambers.stop()
            while(self.vortex.getStatus() == 1):
                print 'waiting for vortex to stop'
                try:
                    sleep(0.1)
                except:
                    self.interrupted = 1
            
            self.checkForInterrupt()
            mydata=self.ionchambers.getPosition()
            self.checkForInterrupt()
            vortexdata=self.vortex.getROICounts(0)
            vortexCorrectedData = self.vortex.getDeadTimeCorrectedROICounts(0)
            self.checkForInterrupt()
            vortexdatasum=self.vortex.getROIsSum()
            self.checkForInterrupt()
            #vortexDTCdata=self.vortexDTCparams.getVortexDTCParams()
            #self.checkForInterrupt()
            #self.writeSummary(currentpos,mydata,vortexdata,vortexdatasum,vortexDTCdata,collectionTime)
            self.writeSummary(currentpos,mydata,vortexdata,vortexCorrectedData, vortexdatasum,collectionTime)
            self.checkForInterrupt()
            # Move the mono
            self.ionchambers.stop()
            currentpos=currentpos+step
        #        
        self.stopTFG()    
        print 'Finished angle scan'

    #
    # In a scan you create a new scan object for each scan
    # You can  reuse the i18exafs scan
    #  This simply increments the file no.s etc.
    #
    def reset(self):
        self.fileno=self.runs.getCurrentFileNumber()+1
        self.runs.incrementNumber()
        self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
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
        self.checkForInterrupt()
        print 'Preparing TFG'
        self.prepareDetectorForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
        print 'Starting k scan'
        print 'Bragg\t Energy\tI0\tIt\tIdrain\tVortex'
        self.checkForInterrupt()
        self.ionchambers.clearAndPrepare()
        self.vortex.stop()
        for i in range(npoints):
            while(BeamMonitor.beamOn()==0):
                print 'Beam lost : Pausing until resumed'
                try:
                    sleep(60)
                except:
                    print 'Trying to stop during sleep'
            mdegPosition = self.mDegForK(currentpos,edgeEnergy,twoD)
            secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
            mysleeptime=int(100.0*(secTime*0.95/1000.0))/100.0
            # print 'check topup'
            while(BeamMonitor.collectBeforeTopupTime(secTime/1000.0)==1):
                print 'Top up coming : Pausing until resumed'
                try:
                    sleep(1)
                except:
                    print 'Trying to stop during sleep - topup'

            # Set the collection time
            self.checkForInterrupt()
            self.vortex.clearAndStart()
            # Move mono to start position
            try: 
                #comboDCM_d.moveTo(mdegPosition)
                self.energyController.moveTo(mdegPosition)
            except:
                self.interrupted = 1    
            self.checkForInterrupt()
            # Ready the ion chambers and vortex
            self.ionchambers.clearAndPrepare()
            # A check to make sure the struck is started (i.e. cleared and waiting for a trigger signal)
            # Early runs occassionally threw odd numbers or zeros out...
            # so put in some check the struck is the right state 
            self.checkForInterrupt()
            while(self.ionchambers.isClear()==0 or self.ionchambers.getStatus()==0):
                print 'ionchambers struck not ready: Waiting to clear'
                try:
                    sleep(0.1)
                except:
                    self.interrupted = 1    
                self.checkForInterrupt()
                self.ionchambers.clearAndPrepare()
                try:
                    sleep(0.1)
                except:
                    self.interrupted = 1    
                self.checkForInterrupt()
#
# May have to comment this block
#
#
            while(self.vortex.getStatus() == 0):
                print 'vortex not ready: Waiting to clear'
                try:
                    sleep(0.5)
                except:
                    self.interrupted = 1    
                self.checkForInterrupt()
                self.vortex.clearAndStart()
                try:
                    sleep(2.0)
                except:
                    self.interrupted = 1    
                
                self.checkForInterrupt()
#
# end of region to comment
#
            #
            # tfg starts paused so tell it to continue
            #
            self.checkForInterrupt()
            self.das.sendCommand("tfg cont")
            #
            # wait until it is finished running
            #
            try:
                sleep(mysleeptime)
            except:
                self.interrupted = 1    
            self.checkForInterrupt()
            self.das.sendCommand("tfg wait")
            # Update the vortex status
            self.vortex.stop()
            self.checkForInterrupt()
            self.ionchambers.stop()
            self.checkForInterrupt()
            while(self.vortex.getStatus() == 1):
                print 'waiting for vortex to stop'
                try:
                    sleep(0.1)
                except:
                    self.interrupted = 1
            mydata=self.ionchambers.getPosition()
            self.checkForInterrupt()
            vortexdata=self.vortex.getROICounts(0)
            vortexCorrectedData = self.vortex.getDeadTimeCorrectedROICounts(0)
            self.checkForInterrupt()
            vortexdatasum=self.vortex.getROIsSum()
            self.checkForInterrupt()
            #print mdegPosition,comboDCM_eV.getPosition(),secTime,mydata[0],mydata[1],mydata[2],vortexdata,vortexdatasum
            self.checkForInterrupt()
            #vortexDTCdata=self.vortexDTCparams.getVortexDTCParams()
            #self.checkForInterrupt()
            #self.writeSummary(mdegPosition,mydata,vortexdata,vortexdatasum,vortexDTCdata,secTime)
            self.writeSummary(mdegPosition,mydata,vortexdata,vortexCorrectedData, vortexdatasum,secTime)
            self.checkForInterrupt()
            # Move the mono
            currentpos=currentpos+step
            self.ionchambers.stop()
        #
        #  write out at end
        #        
        self.stopTFG()    
        print 'Finished k scan'

    def setWindows(self,filename,desiredWindow):
        infile=open(filename, 'r')
        windowCount =0
        while infile:
            a=infile.readline()
        
            n = len(a)
            if n == 0:
                break
            temp=a.split('\t')
            tmpwindowValues=[[0.0, 4095]]*4
            tmpwindowName=temp[0].strip().replace(' ', '')
            print 'window name', tmpwindowName
            if(tmpwindowName.lower().find(desiredWindow.lower())>=0):
                for j in range(len(temp)-1):
                    index=j+1
                    mytemp=temp[index].strip().replace('[', '').replace(']', '').split(',')
                    mytemp=[float(mytemp[0]), float(mytemp[1])]
                    tmpwindowValues[j]=mytemp 
                    print 'window values chosen :', j, tmpwindowValues[j]
                xmapMca.setNthROI(array(tmpwindowValues,java.lang.Class.forName("[D")),0)
            self.windowValues= tmpwindowValues
            self.windowName= tmpwindowName
        if(self.windowName=='ALL'):
            print '======================'
            print '========WARNING========'
            print 'No window has been found or set'
            print '======WARNING=========='
            print '======================'
            
    #
    #  Disables, Clears and enables the detector
    #  Sets up tfg for a given noOfFrames and  collectionTime
    #  pausing in the dead frame and dead port=1 for adc triggering
    #  and finally starts the tfg which means it sits waiting for a software based continue command
    #
    def prepareDetectorForCollection(self,noOfFrames,collectionTime):
        self.das.sendCommand("tfg init")
        command = "tfg setup-groups cycles 1 \n%d 0.01 %f 0 7 -1 0 \n -1 0 0 0 0 0 0 "  %(noOfFrames,collectionTime)
        print "tfg command", command
        self.das.sendCommand(command)
        self.das.sendCommand("tfg start")
    #
    #  Disables, Clears and enables the detector
    #  Sets up tfg for a set of possibly variable length time frames
    #  and finally starts the tfg which means it sits waiting for a software based continue command
    #
    def prepareDetectorForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
        self.das.sendCommand("tfg init")
        command = self.getTFGCommandForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
        self.das.sendCommand(command)
        self.das.sendCommand("tfg start")
    #
    # Stop the tfg and disable the detector
    #
    def stopTFG(self):
        self.das.sendCommand("tfg init")

    def writeSummary(self,currentpos,data,vortexdata,vortexCorrectedData, vortexdatasum,collectionTime):
        fid = open(self.datafilename,'a')
        vortexdata2 =[]
        mydata=[]
        for i in range(4):
            vortexdata2.append(vortexdata[i])
            mydata.append(vortexdata[i])
        vortexCorrectedData2 =[]
        vortexCorrectedDataSum=0
        for j in range(4):
            vortexCorrectedData2.append(vortexCorrectedData[j])
            vortexCorrectedDataSum +=vortexCorrectedData[j]
        print currentpos,comboDCM_eV.getPosition(),collectionTime,data[0],data[1],data[2],str(vortexdata2[0:]).strip('[]').replace(',',''),vortexdatasum[0], str(vortexCorrectedData2[0:]).strip('[]').replace(',',''),vortexCorrectedDataSum      
        print >>fid,currentpos,comboDCM_eV.getPosition(),collectionTime,data[0],data[1],data[2],str(vortexdata2[0:]).strip('[]').replace(',',''),vortexdatasum[0], str(vortexCorrectedData2[0:]).strip('[]').replace(',',''),vortexCorrectedDataSum
        fid.close()
        detectorVector = [data[0],data[1],data[2]]
        mydata.append(vortexdatasum[0])
        positionVector = []
        positionVector.append(currentpos)
        #sdp = ScanDataPoint("Exafs FluScan",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.datafilename,0)
        sdp = ScanDataPoint()
        sdp.setUniqueName("Exafs FluScan")
        for s in self.scannableNamesVector:
            sdp.addScannable(s)
        for d in self.detectorNamesVector:
            sdp.addDetector(d)
        for p in positionVector:
            sdp.addScannablePosition(p,["%.4f"] )
        sdp.addDetectorData(detectorVector,["%5.2g","%5.2g","%5.2g"])
        sdp.addDetectorData(mydata, ["%5.2g","%5.2g","%5.2g","%5.2g","%5.2g"])
        sdp.setCurrentFilename(self.datafilename)
        sdp.setScanIdentifier(str(self.fileno))
        self.controller.update(None, sdp)
        self.mcontroller.update(None, sdp)

    def setROIUsed(self,roiindex):
        self.roiindex=roiindex

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
    #
    #
    # Produces the tfg setup-groups used for kscans
    # In kscans you may want a time increase from start to finish
    # This method produces a series of individual tfg time frames for each time step in the scan
    #
    def getTFGCommandForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
        difference = end - start;
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        currentpos = start
        tfglist="tfg setup-groups cycles 1\n"
        for  j in range(npoints+1):
            secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
            tfglist = tfglist + "1 0.01 %f 0 7 -1 0\n" %(secTime/1000.0)
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
            # write datetime
            line = " I18_EXAFS_RUN="+ str(self.fileno)+" "+ today
            print>>fid,line
            print>>fid,self.title
            print>>fid,self.condition1
            print>>fid,self.condition2
            print>>fid,self.condition3
            print>>fid,'Sample X=',MicroFocusSampleX.getPosition(),'Sample Y=',MicroFocusSampleY.getPosition()
            print>>fid,'comboDCM energy time I0 It drain vortex'
            fid.close()


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
    #
    # In a scan you create a new scan object for each scan
    # You can  reuse the i18exafs scan
    #  This simply increments the file no.s etc.
    #
    def incrementFilename(self):
        self.fileno=self.runs.getCurrentFileNumber()+1
        self.runs.incrementNumber()
        self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
        self.mcarootname=self.mcadir+str(self.fileno)
        if not os.path.isdir(self.mcadir):
            os.mkdir(self.mcadir)
        self.tag=1

     #====================================================
    #
    #  Checks to see if stop has been pressed and trys to nicely stop the script
    #
    #====================================================
    def checkForInterrupt(self):
        if(self.interrupted):
            print 'Stopping map:Writing out data taken'
            # write the data we have so far and return
            self.vortex.stop()    
            self.stopTFG()
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
