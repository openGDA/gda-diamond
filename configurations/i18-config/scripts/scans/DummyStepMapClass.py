from gda.epics import CAClient
from java.lang import *
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from org.python.modules.math import *
from time import sleep
import jarray
from java.util import Vector
from gda.scan import ScanDataPoint
from gda.gui.microfocus.i18 import MicroFocusScan
import shutil

#
#
#   A step map scan
#
#   Usage:
#   pdq=I18StepMapClass()
#                                 xstart     xend    xstep        ystart     yend   ystep    time(ms)
#   pdq.stepmapscan(-7.474,  -6.613,   0.01,     6.178,   6.86,   0.01,  3000)#    
#
#
#   Does not plot as it runs but will produce a .dat file. You can use the load command in GDA Microfocus window 
#   to produce a map from the .dat file later
#
mapRunning = 0
class DummyStepMapClass:
    def __init__(self, datafileNo="default"):
        # Create some data vectors to hold the scan data (and names)
        self.scannableNamesVector=Vector()
        self.scannableNamesVector.add("MicroFocusSampleX")
        self.scannableNamesVector.add("MicroFocusSampleY")
        self.detectorNamesVector=Vector()
        self.detectorNamesVector.add("counterTimer01")
        self.detectorNamesVector.add("counterTimer02")
        # Find the script controller 
        self.controller = finder.find("MicroFocusController")    
        self.xspress = finder.find('xspress2system')
        print self.xspress
        self.xmotor=finder.find("sample_x_motor")
        self.ymotor=MicroFocusSampleY
        #self.das=finder.find("daserver")
        self.mcaList=[]
        self.ionchambers=DummySlaveCounterTimer()
        self.ionchamberData=[]
        self.mcaList=[]
        if(datafileNo == "default"):
            self.runs=NumTracker("tmp")
            self.fileno=self.runs.getCurrentFileNumber()+1
            self.runs.incrementNumber()
        else:
            self.fileno = datafileNo
        self.runext = '.dat'    
        self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        #
        # Make a directory to store the mca files in
        #
        self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
        self.mcarootname=self.mcadir+str(self.fileno)
        #
        if not os.path.isdir(self.mcadir):
            os.mkdir(self.mcadir)
        self.tag=1
        # Set default windows
         # Windowing data
        self.windowValues=[]
        self.windowName=[]
        self.windowArrays=[]
        self.setWindows('/home/nv23/workspaces/gdatrunk_sep09ws/configurations/diamond/i18/default.scas')
        self.createFile()
        

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
        detectorToUse = gda.gui.microfocus.i18.I18MicroFocusPanel.XSPRESS
        scanstring = str(xstart) + " "+ str(xstep) + " "+str(xend)+" "+str(ystart) + " "+str(ystep)+ " "+ str(yend) + " "+str(collectionTime) +" " + str(continuous)  + " "+ str(transscan)
        scandata.add(scanstring)
        scandata.add(detectorToUse)
        controller = finder.find("MicroFocusController")
        controller.update(None,scandata)
        
        
    def stepmapscan(self,xstart,xend,xstep,ystart,yend,ystep,collectionTime):
        global mapRunning
        #mfs=MicroFocusScan()
        self.mcaList=[]
        nx=abs(xend-xstart)/xstep
        ny=abs(yend-ystart)/ystep
        nx=int(round(nx+0.5))
        ny=int(round(ny+0.5))
        xcurrent=xstart
        ycurrent=ystart
        # Move to start
        self.xmotor.moveTo(xcurrent)
        self.ymotor.moveTo(ycurrent)
        self.ionchambers.setCollectionTime(collectionTime/1000.0)

        for i in range(ny):
            #
            # Prepare detector for row
            # 
            self.ionchamberData=[]
            self.mcaList=[]
            self.prepareDetectorForRow(nx,collectionTime)
            try:
                for j in range(nx):
                    # Ready the ion chambers
                    self.ionchambers.clearAndPrepare()
        
                    #self.das.sendCommand("tfg cont")
                    #while (self.das.sendCommand("tfg read status") == 'RUNNING'):
                    #    sleep(0.10)
                    #    pass
                    #while(self.ionchambers.isBusy()==1):
                    #    sleep(0.10)
                    #    pass

                    self.ionchamberData.append(self.ionchambers.collectData())
                    print xcurrent,ycurrent,self.ionchamberData[j][0],self.ionchamberData[j][1],self.ionchamberData[j][2]
                
                    # update the motor position
                    xcurrent=xcurrent+xstep
                    self.xmotor.moveTo(xcurrent)
                    # tell the tfg to continue
                print 'Finished row',i
                self.stopDetector()    
                #
                # Dump the detector data to files
                #
                self.writeDetectorFiles(i,nx)        
                #
                # increment y
                #
                self.writeSummary(ycurrent,xstart,xstep,nx,collectionTime)
                ycurrent=ycurrent+ystep
                self.ymotor.moveTo(ycurrent)    
                #
                # return x to its start point
                # 
                xcurrent=xstart
                self.xmotor.moveTo(xcurrent)  
            
            except:
                print 'errror in angle scan'
                tyep,exception,traceback=sys.exc_info()
                print exception
                mapRunning =0
                self.controller.update(None, "STOP")
            else:
            	mapRunning = 0  
             
            
                
        self.controller.update(None, "STOP")
        print 'Scan complete'

    def stopScan(self):
        self.controller.update(None, "STOP")
        return
    
    def prepareDetectorForRow(self,noOfFrames,collectionTime):
        # Don't need to do anything for dummy
        return

    def writeDetectorFiles(self,yindex,nx):
        #self.das.sendCommand("disable 0")
        for i in range(nx):
            name = "%s_yindex_%d_xindex_%d.xsp" % (self.mcarootname,yindex,i)
            self.mcaList.append(name)
            #command = "read 0 0 %d 65536 9 1 from 0 to-local-file \"/dls/i18/tmp/%s\" raw intel" % ( i, name)
            command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw intel" % ( i, name)
            rawname = self.xspress.readout()
            print rawname
            print name
            #os.rename(rawname, name)
            shutil.copyfile(rawname,name)
            
            

    def writeSummary(self,currenty,startx,stepx,nx,collectionTime):
        # lets window this mofo
        fid = open(self.datafilename,'a')
        for i in range(nx):
            val=(startx+(i*stepx))
            line=str(val)+"\t"+str(currenty)+"\t"+str(collectionTime)+"\t"+str(self.ionchamberData[i][0])+"\t"+str(self.ionchamberData[i][1])+"\t"+str(self.ionchamberData[i][2])+"\t"+str(self.mcaList[i])
            print >> fid,line
            print (startx+(i*stepx)),currenty,collectionTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],self.mcaList[i]
            # SDP Stuff
            detectorVector = Vector()
            detectorVector.add(self.ionchamberData[i])
            detectorVector.add(self.mcaList[i])
            positionVector = Vector()
            positionVector.add(str(startx+(i*stepx)))
            positionVector.add(str(currenty))
            #sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,positionVector,detectorVector,"Panel Name","I18 Custom SDP","Header String",self.mcaList[i])
            #ScanDataPoint(String scanName, Vector<String> scannables,
            #Vector<String> detectors, Vector<String> monitors,
            #Vector<String> scannableHeader, Vector<String> detectorHeader,
            #Vector<String> monitorHeader, Vector<String> positions,
            #Vector<Object> data, Vector<String> monitorPositions,
            #String creatorPanelName, String tostring, String headerString,
            #String currentFilename, boolean hasChild)
            sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.mcaList[i],0)
            self.controller.update(None, sdp)
        fid.close()

    # Stop the tfg and disable the detector
    #
    def stopDetector(self):
        return
        

        
        
    def setWindows(self, filename):
        infile=open(filename, 'r')
        while infile:
            a=infile.readline()
            if(a.find("IONCHAMBER")>=0):
                continue    
            n = len(a)
            if n == 0:
                break
            temp=a.split('\t')
            tmpwindowValues=[[0, 4095]]*9
            tmpwindowName=temp[0].strip().replace(' ', '')
            print 'window name', tmpwindowName
            for j in range(len(temp)-1):
                index=j+1
                mytemp=temp[index].strip().replace('[', '').replace(']', '').split(',')
                mytemp=[int(mytemp[0]), int(mytemp[1])]
                tmpwindowValues[j]=mytemp 
                print 'window values chosen :', j, tmpwindowValues[j]
            self.windowValues.append(tmpwindowValues)
            self.windowName.append(tmpwindowName)

    #
    #
    # If a user presses the halt or stop button on the gui
    # stops the scan
    #
    # def checkForInterupts(self):
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
        print "Writing mca file to:"+self.mcadir
        # write datetime
        line =' &SRS'
        line=' &END'
        print>>fid,line
        print>>fid,'   '
        print>>fid,'   '
        fid.close()
    setupGUI = staticmethod(setupGUI)
