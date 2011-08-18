from gda.epics import CAClient
from java.lang import *
#from gda.device.scannable import ScannableBase
#from gda.device import Scannable
from gda.device.scannable import ScannableBase
from gda.device import Scannable

from org.python.modules.math import *
from time import sleep
from gda.jython import ScriptBase
import jarray
from java.util import Date
from java.text import SimpleDateFormat
from gda.data import PathConstructor
import os
#
#
#   A step map scan
#
#   Usage:
#   pdq=I18TransmissionMapClass()
#                                 xstart     xend    xstep        ystart     yend   ystep    time(ms)
#   pdq.stepmapscan(-7.474,  -6.613,   0.01,     6.178,   6.86,   0.01,  3000)#    
#
#
#   Does not plot as it runs but will produce a .dat file. 
#   Not ideal, but it works !
#
#

class I18TransmissionMapClass(ScriptBase):
    def __init__(self, datafileNo="default"):
        # Create some data vectors to hold the scan data (and names)
        self.scannableNamesVector=Vector()
        self.scannableNamesVector.add("MicroFocusSampleX")
        self.scannableNamesVector.add("MicroFocusSampleY")
        self.detectorNamesVector=Vector()
        self.detectorNamesVector.add("counterTimer01")
        # Find the script controller 
        self.controller = finder.find("MicroFocusController")    
        # Now motors and countertimers....
        self.xmotor=MicroFocusSampleX
        self.ymotor=MicroFocusSampleY
        self.das=finder.find("daserver")
        # File number tracking.......
        if(datafileNo == "default"):
            self.runs=NumTracker("tmp")
            self.fileno=self.runs.getCurrentFileNumber()+1
            self.runs.incrementNumber()
        else:
            self.fileno = datafileNo
        self.runext='.dat'
        #self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
        self.datadir=PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
        self.rgbdir=PathConstructor.createFromProperty("gda.data.scan.datawriter.rgbdatadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        ##This rgb file is created in the gui, registering this file for archiving causes 
        ## considerable delay .
        self.rgbfilename=self.rgbdir+'/'+str(self.fileno)+"_1.rgb"
        self.createFile()
        self.archiveFileList=[]
        self.fileArchiveCounter=0
        self.archiver = archiver
    #
    # Map scan
    #
    #
    def stepmapscan(self,xstart,xend,xstep,ystart,yend,ystep,collectionTime):
        global mapRunning
        try:
            nx=0
            ny=0
            nx=abs(xend-xstart)/xstep
            ny=abs(yend-ystart)/ystep
            # Determine no of points
            nx=int(round(nx+0.5))
            ny=int(round(ny+0.5))
            if(nx%2==0):
                print '=============================================='
                print '=================WARNING======================='
                print 'An even number of points in a map row may result in problems reading the data back in'
                print '=============================================='
                print '=============================================='
            xcurrent=xstart
            ycurrent=ystart
            # Move to start
            self.xmotor.moveTo(xcurrent)
            self.ymotor.moveTo(ycurrent)
            for i in range(ny):
                #
                # Prepare detector for row
                # 
                self.prepareTFGForRow(nx,collectionTime)
                counterTimer01.start()
                for j in range(nx):
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
                    #
                    # topup test
                    #
                    while(BeamMonitor.collectBeforeTopupTime(collectionTime/1000.0)==1):
                        print 'Top up coming : Pausing until resumed'
                        try:
                            sleep(2)
                        except:
                            self.interrupted=1    
                        self.checkForInterrupt()
                    counterTimer01.restart()
                    self.checkForInterrupt()
                    while(counterTimer01.getStatus()==1):
                        sleep(0.05)
                    self.checkForInterrupt()
                    # update the motor position
                    self.writeSummary(j,xcurrent,ycurrent,collectionTime)
                    xcurrent=xcurrent+xstep
                    try:
                        self.xmotor.moveTo(xcurrent)
                    except:
                        self.interrupted=1    
                    self.checkForInterrupt()
                print 'Finished row',i
                self.checkForInterrupt()
                self.stopTFG()
                #
                # increment y
                #
                #self.writeRowSummary(ycurrent,xstart,xstep,nx,collectionTime)
                ycurrent=ycurrent+ystep
                try:
                    self.ymotor.moveTo(ycurrent)    
                except:
                    self.interrupted=1
                self.checkForInterrupt()
                #
                # return x to its start point
                # 
                xcurrent=xstart
                try:
                    self.xmotor.moveTo(xcurrent)
                except:
                    self.interrupted=1
                self.checkForInterrupt()
            self.controller.update(None, "STOP")
            print 'Scan complete'
        finally:
            if(os.path.exists(self.datafilename)):
                self.archiveFileList.append(self.datafilename)
                if(os.path.exists(self.rgbfilename)):
                    self.archiveFileList.append(self.rgbfilename)
            try:
                if(len(self.archiveFileList ) != 0):
                    self.archiver.registerFiles("scan-" + str(self.fileno), self.archiveFileList)
            except:
                print "Unable archive files " + self.datafilename
            mapRunning = 0
      

    #====================================================
    #
    # Prepare TFG for row
    #
    #====================================================
    def prepareTFGForRow(self,noOfFrames,collectionTime):
        counterTimer01.clearFrameSets()
        deadTime=1.0e-4
        counterTimer01.addFrameSet(noOfFrames,deadTime,collectionTime,0,7,-1,0)
        counterTimer01.loadFrameSets()

    #====================================================
    #
    # Write out the data            
    #
    #====================================================
    def writeSummary(self,point_index,currentx,currenty,collectionTime):
        ionChamberData=counterTimer01.readFrame(0,4,point_index+1)[1:]
        fid = open(self.datafilename,'a')
        print >>fid,str(currentx),str(currenty),str(collectionTime),str(ionChamberData[0]),str(ionChamberData[1]),str(ionChamberData[2])
        fid.close()
        print str(currentx),str(currenty),str(collectionTime),str(ionChamberData[0]),str(ionChamberData[1]),str(ionChamberData[2])
        # SDP Stuff
        detectorVector = Vector()
        detectorVector.add(ionChamberData)
        positionVector = Vector()
        positionVector.add(str(currentx))
        positionVector.add(str(currenty))
        sdp = ScanDataPoint("Microfocus TransScan",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.datafilename,0)
        sdp.setScanIdentifier(str(self.fileno))
        self.controller.update(None, sdp)


    #====================================================
    #
    # Stop the tfg and disable the detector
    #
    #====================================================
    def stopTFG(self):
        self.das.sendCommand("tfg init")

    #====================================================
    #
    # Create SRS file for writing
    # 
    #
    #====================================================
    def createFile(self):
        fid=open(self.datafilename,'w')
        # get datetime
        df = SimpleDateFormat('hh.mm.dd.MM.yyyy')
        today = df.format(Date()) 
        print "Writing data to file:"+self.datafilename
        # write datetime
        line='SampleX  SampleY  Time  I0  It  Idrain'
        print>>fid,line


    #====================================================
    #
    #  Checks to see if stop has been pressed and trys to nicely stop the script
    #
    #====================================================
    def checkForInterrupt(self):
        if(self.interrupted):
            print 'Stopping map:Writing out data taken'
            # write the data we have so far and return
            self.stopTFG()    
            self.xmotor.stop()
            self.ymotor.stop()
            resetMicroFocusPanel()
            self.interrupted=Boolean(0)
            self.paused=Boolean(0)
            JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
            print  'Now the nasty bit: throw an exception to stop running'
            self.controller.update(None, "STOP")
            raise lang.InterruptedException()

    #====================================================
    #
    #  Checks to see if the pause script button has been pressed
    #
    #====================================================
    def checkForPause(self):
        if(self.paused):
            JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
            while(self.paused):
                try:
                    java.lang.Thread.sleep(10000)
                    print 'Pausing at start of a row-awaiting resume'
                except:
                    self.checkForInterrupt()




    def getDataFileName(self):
        return self.datafilename

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
        transscan  =Boolean(1)
        detectorToUse = gda.gui.microfocus.i18.I18MicroFocusPanel.XSPRESS
        scanstring = str(xstart) + " "+ str(xstep) + " "+str(xend)+" "+str(ystart) + " "+str(ystep)+ " "+ str(yend) + " "+str(collectionTime) +" " + str(continuous)  + " "+ str(transscan)
        scandata.add(scanstring)
        scandata.add(detectorToUse)
        controller = finder.find("MicroFocusController")
        controller.update(None,scandata)
    setupGUI = staticmethod(setupGUI)
