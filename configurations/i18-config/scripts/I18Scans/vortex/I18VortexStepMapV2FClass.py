from gda.epics import CAClient
from java.lang import *
#from gda.jython.scannable import ScannableBase
#from gda.jython.scannable import Scannable
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from gda.jython import ScriptBase
from gda.scan import ScanDataPoint
from org.python.modules.math import *
from time import sleep
from gda.analysis import *
from jarray import array
from gda.data import PathConstructor
import os
import time
#
#
#   A step map scan
#
#   Usage:
#   pdq=I18VortexMapPlotClass()
#                                 xstart     xend    xstep        ystart     yend   ystep    time(ms)
#   pdq.stepmapscan(-7.474,  -6.613,   0.01,     6.178,   6.86,   0.01,  3000)#    
#
#
#   Does not plot as it runs but will produce a .dat file. 
#   Not ideal, but it works !
#
#

class I18VortexStepMapClass(ScriptBase):
    def __init__(self, datafileNo="default"):
        self.scannableNamesVector=Vector()
        self.scannableNamesVector.add(MicroFocusSampleX)
        self.scannableNamesVector.add(MicroFocusSampleY)
        self.detectorNamesVector=Vector()
        self.detectorNamesVector.add(counterTimer01)
        self.detectorNamesVector.add(finder.find("vortexmapdetector"))
        # Find the script controller 
        self.controller = finder.find("MicroFocusController") 
        self.tfg = finder.find("tfg")   
        self.xmotor=MicroFocusSampleX
        self.ymotor=MicroFocusSampleY
        self.das=finder.find("daserver")
        self.xspress = finder.find("sw_xspress2system")
        self.ionchambers=ionChambers
        self.vortex=xmapMca
        #self.vortexDTCparams=vortexDTCparameters
        self.ionchamberData=[]
        if(datafileNo == "default"):
            self.runs=NumTracker("tmp")
            self.fileno=self.runs.getCurrentFileNumber()+1
            self.runs.incrementNumber()
        else:
            self.fileno = datafileNo
        self.runext='.dat'
        self.datadir=PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
        self.rgbdir=PathConstructor.createFromProperty("gda.data.scan.datawriter.rgbdatadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        self.rgbdatafilename=self.rgbdir+'/'+str(self.fileno)+"_1.rgb"
        self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
        self.mcarootname=self.mcadir+str(self.fileno)
        if not os.path.isdir(self.mcadir):
            os.mkdir(self.mcadir)
            
        self.fluData=[]
        self.createFile()
        # Set default windows
        self.windowValues=[]
        self.windowName=[]
        self.windowArrays=[]
        windowdir = PathConstructor.createFromProperty("gda.microfocus.defaultvortexscasfile")
        self.setWindows(windowdir)
        self.archiveFileList=[]
        self.fileArchiveCounter=0
        self.archiver = archiver
    

    #
    # Vortex step by step map
    #
    def stepmapscan(self,xstart,xend,xstep,ystart,yend,ystep,collectionTime):
        global mapRunning
        try:
            print 'locking express'
            lock  = self.xspress.tryLock(5,java.util.concurrent.TimeUnit.SECONDS)
            print "the lock value is " + str(lock)
            if not lock:
                print "Xspress detector is already locked"
                self.controller.update(None, "STOP")
                return
            mapRunning =1
            scanStart = time.asctime()
            nx=abs(xend-xstart)/xstep
            ny=abs(yend-ystart)/ystep
            nx=int(round(nx+0.5))
            ny=int(round(ny+0.5))
            print "number of points " + str(nx) + " "+str(ny)
            xcurrent=xstart
            ycurrent=ystart
            # Move to start
            self.checkForInterrupt()
            try:
                self.xmotor.moveTo(xcurrent)
            except:
                self.interrupted = 1  
            self.checkForInterrupt()
            try:
                self.ymotor.moveTo(ycurrent)
            except:
                self.interrupted = 1  

            self.checkForInterrupt()
            # Create the dataset
            self.checkForInterrupt()
            self.ionchambers.clearAndPrepare()
            self.vortex.stop()
            mysleeptime=int(100.0*(collectionTime*0.95/1000.0))/100.0
            for i in range(ny):
                #
                # Prepare detector for row
                # 

                # Row by row data
                self.mca_row_dir=self.mcadir+("row%d/" %i)
                if not os.path.isdir(self.mca_row_dir):
                    os.mkdir(self.mca_row_dir)
                self.mcarootname=self.mca_row_dir+str(self.fileno)
                self.ionchamberData=[]
                self.checkForInterrupt()
                self.prepareTFGForRow(nx,collectionTime)
                self.checkForInterrupt()
                for j in range(nx):
                    # Check beam is running
                    while(BeamMonitor.beamOn()==0):
                        print 'Beam lost : Pausing until resumed'
                        try:
                            sleep(60)
                        except:
                            self.interrupted = 1  
                            print 'Trying to stop during sleep'
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
                    # Ready the ion chambers and vortex
                    self.ionchambers.clearAndPrepare()
                    self.checkForInterrupt()
                    self.vortex.clearAndStart()
                    self.checkForInterrupt()
                    # A check to make sure the struck is started (i.e. cleared and waiting for a trigger signal)
                    # Early runs occassionally threw odd numbers or zeros out...
                    # so put in some check the struck is the right state 
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
                    self.das.sendCommand("tfg cont")
                    self.checkForInterrupt()
                    try:
                        sleep(mysleeptime)
                    except:
                        self.interrupted = 1    
                    self.checkForInterrupt()
                    self.das.sendCommand("tfg wait")
                    self.checkForInterrupt()
                    self.vortex.stop()
                    self.ionchambers.stop()
                    self.checkForInterrupt()
                    ionChambersData=self.ionchambers.getPosition()
                    self.checkForInterrupt()
                    while(self.vortex.getStatus() == 1):
                        print 'waiting for vortex to stop'
                        try:
                            sleep(0.1)
                        except:
                            self.interrupted = 1
                    vortexdata=self.vortex.getROIsSum()
                    self.checkForInterrupt()
                    vortexSpectrum = self.vortex.getData()
                    self.checkForInterrupt()
                    print xcurrent,ycurrent,ionChambersData[0],ionChambersData[1],ionChambersData[2],vortexdata
                    # update the motor position
                    self.writeSummary(xcurrent,ycurrent,j,i,ionChambersData,collectionTime,vortexdata,vortexSpectrum)
                    self.checkForInterrupt()
                    xcurrent=xcurrent+xstep
                    try:
                        self.xmotor.moveTo(xcurrent)    
                    except:
                        self.interrupted = 1
                    self.checkForInterrupt()

                    # tell the tfg to continue
                print 'Finished row',i
                self.stopTFG()
                #
                # increment y
                #
                ycurrent=ycurrent+ystep
                self.checkForInterrupt()
                try:
                    self.ymotor.moveTo(ycurrent)    
                except:
                    self.interrupted = 1
                self.checkForInterrupt()
                #
                # return x to its start point
                # 
                xcurrent=xstart
                self.checkForInterrupt()
                try:
                    self.xmotor.moveTo(xcurrent)
                except:
                    self.interrupted = 1
                self.checkForInterrupt()
            # Tell the GUI the script has stopped
            self.controller.update(None, "STOP")
            scanEnd = time.asctime()
            print 'Scan complete'
        finally:
            
            if(lock):
                print 'unlocking xpress'
                self.xspress.unlock()
            mapRunning =0
            if(os.path.exists(self.datafilename)):
                self.archiveFileList.append(self.datafilename)
                if(os.path.exists(self.rgbdatafilename)):
                    self.archiveFileList.append(self.rgbdatafilename)
            try:
                if(len(self.archiveFileList ) != 0):
                    self.archiver.registerFiles("scan-" + str(self.fileno), self.archiveFileList)
            except:
                print "Unable archive files " + self.datafilename
        print scanStart
        print scanEnd
    
    def prepareTFGForRow(self,noOfFrames,collectionTime):
        self.das.sendCommand("tfg init")
        command = "tfg setup-groups cycles 1 \n%d 1.0E-5 %f 0 7 -1 0 \n-1 0 0 0 0 0 0 "  %(noOfFrames,collectionTime/1000.0)
        self.das.sendCommand(command)
        self.das.sendCommand("tfg start")

            

    def writeSummary(self,currentx,currenty,xindex,yindex,ionChambers,collectionTime,vortexdata,vortexSpectrum):
        ##spectrum file
        filename = "%s_yindex_%d_xindex_%d.mca" % (self.mcarootname, yindex, xindex)
        filenameScalar = "%s_yindex_%d_xindex_%d_scalar.dat" % (self.mcarootname, yindex, xindex)
        #self.vortexDTCparams.dumpVortexDTCParamsToFile(filenameScalar)        
        #self.archiveFileList.append(filename)
        for data in vortexSpectrum:
            datacounter = 0
            datalen = len(data)
            line =''
            sfid = open(filename, 'a')
            for j in data:
                datacounter = datacounter + 1
                if( datacounter  == datalen):
                    line =line + str(j) 
                else:
                    line = line + str(j) + ' '
            print >>sfid, line
            sfid.close()
        try:
            if(os.path.exists(filename)):
                self.archiveFileList.append(filename)
                self.fileArchiveCounter += 1
            if(os.path.exists(filenameScalar)):
                self.archiveFileList.append(filenameScalar)
                self.fileArchiveCounter += 1
            if(self.fileArchiveCounter >= 100):
                self.archiver.registerFiles("scan-" + str(self.fileno), self.archiveFileList)
                self.fileArchiveCounter = 0
                self.archiveFileList = []
       
        except:
            print "unable to register files for archiving " + filename
        fid = open(self.datafilename,'a')
        print >>fid,str(currentx),str(currenty),str(collectionTime),str(ionChambers[0]),str(ionChambers[1]),str(ionChambers[2]),filename
        fid.close()
        # SDP Stuff
        detectorVector = Vector()
        detectorVector.add(ionChambers)
        vortexVector = Vector()
        vortexVector.add(vortexdata)
        vortexVector.add(filename)
        detectorVector.add(vortexVector)
        positionVector = [currentx, currenty]
        #sdp = ScanDataPoint("MicroFocus VortexStepMap", self.scannableNamesVector, self.detectorNamesVector, None, None, None, None, positionVector, detectorVector, None, "Panel Name", "I18 Custom SDP", "Header String", self.datafilename, 0)
        sdp = ScanDataPoint()
        sdp.setUniqueName("MicroFocus VortexStepMap")
        for s in self.scannableNamesVector:
            sdp.addScannable(s)
        for d in self.detectorNamesVector:
            sdp.addDetector(d)
        for p in positionVector:
            sdp.addScannablePosition(p,["%.4f"] )
        sdp.addDetectorData(ionChambers,["%5.2g","%5.2g","%5.2g"])
        format=[]
        mydata=[]
        for i in range(len(vortexdata)):
            format.append("%5.2g")
            mydata.append(vortexdata[i])
        format.append("%s")
        mydata.append(filename)
        print format
        print mydata
        sdp.addDetectorData(mydata,format )
        sdp.setCurrentFilename(self.datafilename)
        sdp.setScanIdentifier(str(self.fileno))
        sdp.setScanIdentifier(str(self.fileno))
        self.controller.update(None, sdp)

    # Stop the tfg and disable the detector
    #
    def stopTFG(self):
        self.das.sendCommand("tfg init")


    def getNorm(self,a):
        max=a.get([0,0])
        min=a.get([0,0])
        newdataset=DataSet([a.getDimensions()[0],a.getDimensions()[1]])
        for i in range(a.getDimensions()[0]):
            for j in range(a.getDimensions()[1]):
                value=a.get([i,j])
                if(value>max):
                    max=value
                if(value<min):
                    min=value
        if(max==0):
            return a
        else:
            for i in range(a.getDimensions()[0]):
                for j in range(a.getDimensions()[1]):
                    value=a.get([i,j])
                    value=value-min
                    value=value/max
                    #print 'value',value
                    newdataset.set(value,[i,j])
            return newdataset    
            

    def createFile(self):
        fid=open(self.datafilename,'w')
        # get datetime
        rightNow = Calendar.getInstance()
        year = rightNow.get(Calendar.YEAR)
        month = rightNow.get(Calendar.MONTH)
        day = rightNow.get(Calendar.DAY_OF_MONTH)
        hour = rightNow.get(Calendar.HOUR)
        minute = rightNow.get(Calendar.MINUTE)
        second = rightNow.get(Calendar.SECOND)
        print "Writing data to file:"+self.datafilename
        # write datetime
        line1 =' &SRS'
        detector = 'Vortex Xmap'
        line2=' &END'
        print>>fid,line1
        print>>fid,detector
        print>>fid,line2
        print>>fid,'   '
        print>>fid,'   '
        fid.close()


    def setWindows(self):
        pass

    def setWindows(self, filename):
        infile=open(filename, 'r')
        windowCount =0
        while infile:
            a=infile.readline()
            if(a.find("IONCHAMBER")>=0):
                continue    
            n = len(a)
            if n == 0:
                break
            temp=a.split('\t')
            tmpwindowValues=[[0.0, 4095]]*4
            tmpwindowName=temp[0].strip().replace(' ', '')
            print 'window name', tmpwindowName
            
            for j in range(len(temp)-1):
                index=j+1
                mytemp=temp[index].strip().replace('[', '').replace(']', '').split(',')
                mytemp=[float(mytemp[0]), float(mytemp[1])]
                tmpwindowValues[j]=mytemp 
                print 'window values chosen :', j, tmpwindowValues[j]
            self.windowValues.append(tmpwindowValues)
            print tmpwindowValues
            xmapMca.setNthROI(array(tmpwindowValues,java.lang.Class.forName("[D")),windowCount)
            windowCount = windowCount + 1
            self.windowName.append(tmpwindowName)
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
            self.xmotor.stop()
            self.ymotor.stop()
            self.interrupted=Boolean(0)
            self.paused=Boolean(0)
            self.stopTFG()
            JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
            print  'Now the nasty bit: throw an exception to stop running'
            self.controller.update(None, "STOP")
            raise lang.InterruptedException()

    def setupGUI(xstart,xend,xstep,ystart,yend,ystep,collectionTime):        
        global mapRunning
       # print command_server.getScriptStatus()
        while(mapRunning):
            sleep(5)
        mapRunning = 1
        scandata=Vector()
        # Type of scan
        scandata.add("MapScan")
        continuous = Boolean(0)
        transscan  =Boolean(0)
        detectorToUse = gda.gui.microfocus.i18.I18MicroFocusPanel.VORTEX
        scanstring = str(xstart) + " "+ str(xstep) + " "+str(xend)+" "+str(ystart) + " "+str(ystep)+ " "+ str(yend) + " "+str(collectionTime) +" " + str(continuous)  + " "+ str(transscan)
        scandata.add(scanstring)
        scandata.add(detectorToUse)
        controller = finder.find("MicroFocusController")
        controller.update(None,scandata)
    setupGUI=staticmethod(setupGUI)
