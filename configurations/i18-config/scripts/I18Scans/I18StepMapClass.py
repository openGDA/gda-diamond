from gda.epics import CAClient
from java.lang import *
#from gda.jython.scannable import ScannableBase
#from gda.jython.scannable import Scannable
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from org.python.modules.math import *
from time import sleep
from java.lang import *
from java.util import Vector
import jarray
from gda.scan import ScanDataPoint
from gda.jython import ScriptBase
from java.util import Date
from java.text import SimpleDateFormat
from gda.data import PathConstructor
#====================================================
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
#====================================================

class I18StepMapClass(ScriptBase):
    #====================================================
    #
    # Setup the I18 Step map class
    #
    #====================================================
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
        #
        self.xmotor=MicroFocusSampleX
        self.ymotor=MicroFocusSampleY
        self.das=finder.find("daserver")
        self.mcaList=[]
        self.ionchambers=SlaveCounterTimer()
        self.ionchamberData=[]
        # Windowing data
        self.windowValues=[]
        self.windowName=[]
        self.windowArrays=[]
        if(datafileNo == "default"):
            self.runs=NumTracker("tmp")
            self.fileno=self.runs.getCurrentFileNumber()+1
            self.runs.incrementNumber()
        else:
            self.fileno = datafileNo
        self.runext='.dat'
        self.xspress = finder.find("xspress2system")
        #self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
        self.datadir=PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
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
        self.createFile()
        # Set default windows
        self.setWindows('/dls/i18/software/gda/config/default.scas')
        self.createRGBfile()

    #====================================================
    #
    # I18 Step map class
    #
    #====================================================
    def stepmapscan(self,xstart,xend,xstep,ystart,yend,ystep,collectionTime):
        lock =0
        try:
            print 'locking express'
            lock  = self.xspress.tryLock(5,java.util.concurrent.TimeUnit.SECONDS)
            print "the lock value is " + str(lock)
            if not lock:
                print "Xspress detector is already locked"
                self.controller.update(None, "STOP")
                return
            nx=0
            ny=0
            totalion=[]
            self.mcaList=[]
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
            # Round to even or odd to ensure map can be read back in
            xcurrent=xstart
            ycurrent=ystart
            # Move to start positions
            self.checkForInterrupt()
            self.xmotor.moveTo(xcurrent)
            self.checkForInterrupt()
            self.ymotor.moveTo(ycurrent)
            self.checkForInterrupt()
            # set ion chamber collection time
            self.ionchambers.setCollectionTime(collectionTime)
            self.checkForInterrupt()
            estimatedTime=0.0
            for i in range(ny):
                self.windowArrays=[]
                for j in range(len(self.windowName)):
                    self.windowArrays.append(self.initArray1D(nx))
                #
                # Prepare detector for row
                # 
                self.ionchamberData=[]
                self.mcaList=[]
                self.checkForInterrupt()
                self.prepareDetectorForRow(nx,collectionTime)
                self.checkForInterrupt()
                self.checkForPause()
                #startTime=w.getPosition()
                for j in range(nx):
                    # Check beam is running
                    while(BeamMonitor.beamOn()==0):
                        print 'Beam lost : Pausing until resumed'
                        try:
                            sleep(60)
                        except:
                            self.interrupted=1    
                        self.checkForInterrupt()
                    #
                    # Check if detector is filling
                    #
                    while(BeamMonitor.isFilling()==1):
                        self.checkForInterrupt()
                        print 'Detector Filling : Pausing until completed'
                        try:
                            sleep(60)
                        except:
                            self.interrupted=1                    
                        self.checkForInterrupt()
                    # clear the ion chamber epics mca and prepare for trigger
                    self.ionchambers.clearAndPrepare()
                    self.checkForInterrupt()
                    # tell the tfg to continue
                    self.das.sendCommand("tfg cont")
                    self.checkForInterrupt()
                    # Wait for tfg to stop
                    self.das.sendCommand("tfg wait timebar")
                    self.checkForInterrupt()
                    # Have to wait until mca is ready to read
                    while(self.ionchambers.isBusy()>=1):
            
                        try:
                            sleep(0.05)
                        except:
                            self.interrupted=1    
                        self.checkForInterrupt()
                        pass
                    # collect ion chamber data
                    self.ionchamberData.append(self.ionchambers.collectData())
                    self.checkForInterrupt()
                    # Some info for the user
                    print xcurrent,ycurrent,self.ionchamberData[j][0],self.ionchamberData[j][1],self.ionchamberData[j][2]
                    # update the x motor position
                    xcurrent=xcurrent+xstep
                    self.checkForInterrupt()
                    try:
                        self.xmotor.moveTo(xcurrent)
                    except:
                        self.interrupted=1    
                    self.checkForInterrupt()
                #endTime=w.getPosition()
                # tell the tfg to continue
                #print 'Finished row',i,"Time Left:(minutes)",((ny-i)*(endTime-startTime))/60.0
                # Stop the detector and tfg
                self.checkForInterrupt()
                self.stopDetector()    
                self.checkForInterrupt()    
                # Dump the detector data to files
                self.writeDetectorFiles(i,nx)    
                self.checkForInterrupt()    
                # write the data to a file
                self.checkForInterrupt()
                self.writeSummary(ycurrent,xstart,xstep,nx,collectionTime)
                self.checkForInterrupt()
                # write rgb
                self.appendToRGB(nx,i,self.ionchamberData)
                self.checkForInterrupt()    
                # increment y
                ycurrent=ycurrent+ystep
                self.checkForInterrupt()
                try:
                    self.ymotor.moveTo(ycurrent)
                except:
                    self.interrupted=1
                self.checkForInterrupt()
                # return x to its start point
                xcurrent=xstart
                self.checkForInterrupt()
                self.xmotor.moveTo(xcurrent)
                self.checkForInterrupt()
            # Tell the GUI the script has stopped
            self.controller.update(None, "STOP")
            # Tell the user the map has stopped
            print 'Scan complete'
        finally:
            if(lock):
                print 'unlocking xpress'
                self.xspress.unlock()



    #====================================================
    #
    # Prepare the detector and tfg
    # Detector memory is wiped
    # Then  
    #
    #====================================================
    def prepareDetectorForRow(self,noOfFrames,collectionTime):
        self.das.sendCommand("disable 0")
        self.das.sendCommand("clear 0")
        self.das.sendCommand("enable 0")
        self.das.sendCommand("tfg init")
        command = "tfg setup-groups cycles 1 \n%d 1.0E-5 %f 0 1 1 0 \n-1 0 0 0 0 0 0 "  %(noOfFrames,collectionTime/1000.0)
        self.das.sendCommand(command)
        self.das.sendCommand("tfg start")

    #====================================================
    #
    # Output detector files
    #
    #
    #====================================================
    def writeDetectorFiles(self,yindex,nx):
        self.das.sendCommand("disable 0")
        for i in range(nx):
            name = "%s_yindex_%d_xindex_%d.xsp" % (self.mcarootname,yindex,i)
            sname = "%s_yindex_%d_xindex_%d_scalar.xsp" % (self.mcarootname,yindex,i)
            self.mcaList.append(name)
            command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw" % ( i, name)
            self.das.sendCommand(command)
            command = "read 0 0 %d 3 9 1 from 1 to-local-file \"%s\" raw intel" % ( i, sname)
            self.das.sendCommand(command)
            
    #====================================================
    #
    # Write out the data
    #
    #====================================================
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
            sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.mcaList[i],0)
            self.controller.update(None, sdp)
            print 'Reading and windowing:',self.mcaList[i]
            frameData=Xspress2Utilities.interpretDataFile(self.mcaList[i],0)
            for j in range(len(self.windowName)):
                totalw=0.0
                windowedData=[0.0]*9
                for k in range(9):
                    sumgrades=frameData[k]
                    windowedData[k]=windowedData[k]+self.windowData(sumgrades,self.windowValues[j][k][0],self.windowValues[j][k][1])
                for k in range(9):
                    totalw=totalw+windowedData[k]
                #
                # now set the data arrays with these values
                #
                self.windowArrays[j][i]=totalw            
        fid.close()

    #====================================================
    #
    # Stop the tfg and disable the detector
    #
    #====================================================
    def stopDetector(self):
        self.das.sendCommand("tfg init")
        self.das.sendCommand("disable 0")
        
    #====================================================
    #
    # Creates an srs data file
    #
    #====================================================
    def createFile(self):
        fid=open(self.datafilename,'w')
        # get datetime
        df = SimpleDateFormat('hh.mm.dd.MM.yyyy')
        today = df.format(Date()) 
        print "Writing data to file:"+self.datafilename
        print "Writing mca file to:"+self.mcadir
        # write datetime
        line=' &END'
        print>>fid,line
        print>>fid,'   '
        print>>fid,'   '
        fid.close()

    #====================================================
    #
    #  Checks to see if stop has been pressed and trys to nicely stop the script
    #
    #====================================================
    def checkForInterrupt(self):
        if(self.interrupted):
            print 'Stopping map:Writing out data taken'
            # write the data we have so far and return
            self.stopDetector()    
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

    #====================================================
    #
    #  Window the data
    #
    #====================================================
    def windowData(self,data,start,end):
        sum=0.0    
        for i in range(start,end):
            sum=sum+data[i]
        return sum    

    #====================================================
    #
    #  Store rgb file
    #
    #====================================================
    def createRGBfile(self):
        newdatafilename=self.datadir+'/'+str(self.fileno)+".rgb"
        print 'RGB file name',newdatafilename
        fid=open(newdatafilename,'w')
        mystr='row  column  i0  '
        for k in range(len(self.windowName)):
            mystr=mystr+self.windowName[k]
            if(k<(len(self.windowName)-1) ):
                mystr=mystr+"  "
        print >> fid,mystr
        fid.close()    

    #====================================================
    #
    #  Store rgb file
    #
    #====================================================
    def appendToRGB(self,nx,yindex,totalion):
        newdatafilename=self.datadir+'/'+str(self.fileno)+".rgb"
        fid=open(newdatafilename,'a')
        for j in range(nx):
            mystr=str(totalion[j][0])+" "
            for k in range(len(self.windowArrays)):
                mystr=mystr+str(self.windowArrays[k][j])
                if(k<(len(self.windowArrays)-1)):
                    mystr=mystr+" "
            print >> fid,yindex,j,mystr
        fid.close()

    #====================================================
    #
    #  Store rgb file
    #
    #====================================================
    def convertWindowsToRGB(self,nx,ny,totalion):
        newdatafilename=self.datadir+'/'+str(self.fileno)+".rgb"
        fid=open(newdatafilename,'w')
        mystr='row  column  i0  '

        for k in range(len(self.windowName)):
            mystr=mystr+self.windowName[k]
            if(k<(len(self.windowName)-1) ):
                mystr=mystr+"  "
        print >> fid,mystr
        for i in range(ny):
                for j in range(nx):
                    mystr=str(totalion[i][j][0])+" "
                    for k in range(len(self.windowArrays)):
                        mystr=mystr+str(self.windowArrays[k][j][i])
                        if(k<(len(self.windowArrays)-1)):
                            mystr=mystr+" "
                    print >> fid,i,j,mystr
        fid.close()

    #====================================================
    #
    #  Set the windows
    #
    #====================================================
    def setWindows(self,filename):
        infile=open(filename,'r')
        while infile:
            a=infile.readline()
            if(a.find("IONCHAMBER")>=0):
                continue    
            n = len(a)
            if n == 0:
                break
            temp=a.split('\t')
            tmpwindowValues=[[0,4095]]*9
            tmpwindowName=temp[0].strip().replace(' ','')
            print 'window name',tmpwindowName
            for j in range(len(temp)-1):
                index=j+1
                mytemp=temp[index].strip().replace('[','').replace(']','').split(',')
                mytemp=[int(mytemp[0]),int(mytemp[1])]
                tmpwindowValues[j]=mytemp 
                print 'window values chosen :',j,tmpwindowValues[j]
            self.windowValues.append(tmpwindowValues)
            self.windowName.append(tmpwindowName)
    #====================================================
    # return a 2D list filled with zeros
    #====================================================
    def initArray2D(self,rows,columns):
        a = []
        for x in range(rows):
            a.append([0.0] * columns)
        return a    

    #
    # return a 1D list filled with zeros        
    #
    def initArray1D(self,rows):
        a = []
        for x in range(rows):
            a.append(0.0)
        return a
