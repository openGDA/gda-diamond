from gda.epics import CAClient
from java.lang import *
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from org.python.modules.math import *
from time import sleep
from java.lang import *
from java.util import Vector
import jarray
from gda.scan import ScanDataPoint
from gda.jython import ScriptBase
import handle_messages
import shutil
from gda.data.fileregistrar import FileRegistrarHelper
import os
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

class I18ContinuousMapClass(ScriptBase):
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
        self.xmotor=finder.find("sample_x_motor")
        self.xpos_start=CAClient("BL18I-MO-TABLE-01:X:START")
        self.xpos_start.configure()
        self.xpos_end=CAClient("BL18I-MO-TABLE-01:X:END")
        self.xpos_end.configure()
        self.xpos_steps=CAClient("BL18I-MO-TABLE-01:X:STEPS")
        self.xpos_steps.configure()
        self.xpos_send = CAClient("BL18I-MO-TABLE-01:X:SEND.PROC")
        self.xpos_send.configure()
        self.xpos_enable=CAClient("BL18I-MO-TABLE-01:X:ENABLE")
        self.xpos_enable.configure()
        self.ymotor=MicroFocusSampleY
        self.das=finder.find("daserver")
        self.mcaList=[]
        self.pointTime=[]
        self.ionchambers=ionChambers
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
        self.createFile()
        # Set default windows
        self.setWindows('/dls/i18/software/gda/config/default.scas')
        self.archiveFileList=[]
        #self.archiveFileList.append(self.datafilename)
        #self.createRGBfile()

    #
    # Raster a map
    #
    def rastermapscan(self,startx,stopx,nxsteps,time,starty,stopy,nysteps):
        global mapRunning
        try:
            if(time<10.0):
                print 'Time is too short...must be at least 10 seconds'
                self.controller.update(None, "STOP")
                return
            self.checkForInterrupt()
            stepx=abs(stopx-startx)/nxsteps
            ##Note the nysteps -1 is to make sure the map is plotted correctly in GDA
            stepy = abs(stopy - starty) / (nysteps - 1)
            timestep=time/nxsteps
            overshootx=int((self.overShootTime/timestep)+0.5)*stepx
        
            #self.setupGUI(startx,stopx,stepx,starty,stopy,stepy,timestep)
    
            #try:
            # Move the motor to the start
            print 'here2'
            try:
                MicroFocusSampleY.moveTo(starty)
            except:
                self.interrupted = 1
            self.checkForInterrupt()
            currentypos=starty
            # Set ion chambers to collect for 10 seconds for a good average....    
            self.checkForInterrupt()
            print 'nxsteps ', nxsteps
            print 'nysteps ',nysteps,timestep*1000.0
            print 'stepx ', stepx
            print 'stepy ', stepy
            for i in range(nysteps):
                #
                # How to split up if topup is coming
                #
                self.checkForInterrupt()
                scanSections=[]
                topuptime=BeamMonitor.timeBeforeTopup()
                topuptime=1000.0
                # If you've got less than 10 seconds to wait for topup just wait it out....
                print 'topup wait1'
                if(topuptime<=10.0):
                    self.checkForInterrupt()
                    print 'topup wait'
                    try:
                        sleep(toptuptime)
                    except:
                        self.interrupted =1
                    self.checkForInterrupt()
                    while(BeamMonitor.collectBeforeTopupTime(time) == 1):
                        try:
                            sleep(1.0)
                        except:
                            self.interrupted =1
                        self.checkForInterrupt()
                else:
                    #
                    # Split up the scan if required
                    #
                    # topup will occur before end of the row
                    if(topuptime<time):
                        nsteps1=int((topuptime-2.0)/timestep)-2
                        nsteps2=int(nxsteps-(topuptime-2.0)/timestep)+2
                        startx1=startx
                        stopx1=startx1+nsteps1*stepx
                        startx2=stopx1
                        stopx2=stopx
                        scanSections.append([nsteps1,startx1,stopx1])
                        scanSections.append([nsteps2,startx2,stopx2])
                        self.checkForInterrupt()
                    else:
                        scanSections.append([nxsteps,startx,stopx])
                sectionindex=0
                print 'topup wait2',scanSections
                for section in scanSections:
                    print 'here2a',len(self.windowName),section[0]
                    self.windowArrays = []
                    for j in range(len(self.windowName)):
                        self.windowArrays.append(self.initArray1D(int(section[0]))) 
                    self.checkForInterrupt()
                    print 'here2b'
                    #
                    # clear detector and set to collect nsteps + 2
                    # Detector goes straight into a paused state...i.e. starts collecting in frame 1 
                    # So the first motor step will stop this collecting and jump forward.
                    # also add another point to the end. 
                    #
                    # Move the motor to the start - step
                    # Set the speed to maximum
                    #print 'here1'
                    try:
                        self.xmotor.setSpeed(1.0)
                
                    
                    # Move to start - 50 microns
                    except:
                        self.interrupted =1
                    self.checkForInterrupt()
                    #print 'here2'
                    try:
                        MicroFocusSampleX.moveTo(section[1]-overshootx)
                
                        #print 'here3'
                        self.prepareDetectorForRastering(section[0]+3)
                        self.checkForInterrupt()
                        self.ionchambers.mcaStop()
                        while(self.ionchambers.getMCAStatus()==1):
                            print 'ionchambers struck not ready: Waiting to start'
                            try:
                                sleep(0.050)
                            except:
                                self.interrupted=1
                        self.ionchambers.mcaEraseAndStart()
                        while(self.ionchambers.getMCAStatus()==0):
                            print 'ionchambers struck not ready: Waiting to start'
                            try:
                                sleep(0.050)
                            except:
                                self.interrupted=1
                        self.checkForInterrupt()
                        print 'Section',section
                        self.setRunSpeed(startx,stopx,time)
                        self.checkForInterrupt()
                        self.setPositionCompare(section[1],section[2],section[0],time)
                        self.checkForInterrupt()
                        # Move the motor to one step past the end
                        # This will account for any motor servo control at end so all points
                        # have roughly same dwell time.
                        # May have to tune this it depends on the data.........
                        #
                        #print 'move to end',section[2]+0.020
                        MicroFocusSampleX.asynchronousMoveTo(section[2]+overshootx)
                        self.checkForInterrupt()
                    #    print 'read out etc',i,section[0],sectionindex
                        self.writeoutDetectorDataRow(startx,stopx,stepx,currentypos,i,section[0],sectionindex)
                        self.checkForInterrupt()
                        self.checkForInterrupt()
                        MicroFocusSampleX.waitWhileBusy()
                        self.checkForInterrupt()
                        #
                        # make sure motor has stopped (testing only)
                        #
                        # disable the detector and readout
                    #    print 'stopping mca'
                        self.ionchambers.mcaStop()
                    #    print 'mca stopped'
                        self.stopDetector()
                        self.checkForInterrupt()
                        self.disablePositionCompare()
                        self.checkForInterrupt()
                    #    print 'read out ion chambers'
                        self.xmotor.setSpeed(1.0)
                        self.checkForInterrupt()
                        MicroFocusSampleX.asynchronousMoveTo(section[1]-overshootx)
                        self.checkForInterrupt()
                        #
                        # process output
                        #
                        print 'write out data'
                        self.ionchamberData=self.ionchambers.getMCAData(section[0]+1)
                    #    print 'ic data',self.ionchamberData
                        self.writeSummary(currentypos,i,section[1],stepx,section[0],sectionindex)
                        self.checkForInterrupt()
                        sectionindex=section[0]
                        MicroFocusSampleX.waitWhileBusy()
                        self.checkForInterrupt()
                    except:
                        self.interrupted =1
                    self.checkForInterrupt()
                    #
                    # Write out the detector data 
                    #
                currentypos=currentypos+stepy
                self.checkForInterrupt()
                # Move the y motor to its next position
                try:
                    MicroFocusSampleY.moveTo(currentypos)
                except:
                    self.interrupted =1
                self.checkForInterrupt()
            self.controller.update(None, "STOP")
        finally:
            if(os.path.exists(self.datafilename)):
                self.archiveFileList.append(self.datafilename)
                print "list of files to be archived are "
                print self.archiveFileList
                FileRegistrarHelper.registerFiles(self.archiveFileList)
        print 'scan complete'
        #except:
        #    type, exception, traceback = sys.exc_info()
        #    #update( controller,"Error calling raster map Scan. ", type, exception , traceback, True)


    def prepareDetectorForRastering(self,noOfFrames):
        self.das.sendCommand("disable 0")
        self.das.sendCommand("clear 0")
        self.das.sendCommand("enable 0")
        self.das.sendCommand("tfg init")
        command = "tfg setup-groups ext-start cycles 1\n%d 1.0E-5 1.0E-5 0 7 0 1\n-1 0 0 0 0 0 0"  %(noOfFrames)
        self.das.sendCommand(command)
        self.das.sendCommand("tfg start")

    #====================================================
    #
    # Stop the tfg and disable the detector
    #
    #====================================================
    def stopDetector(self):
        self.das.sendCommand("tfg stop")
        
    #====================================================
    #
    # Creates an srs data file
    #
    #====================================================
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
            resetMicroFocusPanel()
            self.interrupted=Boolean(0)
            self.paused=Boolean(0)
            self.xmotor.stop()
            self.xmotor.setSpeed(1.0)
            self.ymotor.stop()
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
    #  Store rgb file
    #
    #====================================================
    def createRGBfile(self):
        newdatafilename=self.datadir+'/'+str(self.fileno)+".rgb"
        self.archiveFileList.append(newdatafilename)
        print 'RGB file name',newdatafilename
        fid=open(newdatafilename,'w')
        mystr='row  column  time  i0  it  idrain  '
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
    def appendToRGB(self,xindex,yindex,times,totalion,windowsums):
        newdatafilename=self.datadir+'/'+str(self.fileno)+".rgb"
        fid=open(newdatafilename,'a')
        mystr=str(times)+" "+str(self.ionchamberData[0][xindex])+" "+str(self.ionchamberData[1][xindex])+" "+str(self.ionchamberData[2][xindex])+" "
        for k in range(len(windowsums)):
            mystr=mystr+str(windowsums[k])
            if(k<(len(windowsums)-1)):
                mystr=mystr+" "
        print >> fid,yindex,xindex,mystr
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

    def setPositionCompare(self,start,stop,steps,time):
        # set motor start stop step for pulses
        self.disablePositionCompare()
        self.xpos_start.caput(start)
        self.xpos_end.caput(stop)
        self.xpos_steps.caput(steps)
        self.xpos_send.caput(1)
        self.enablePositionCompare()

    def setRunSpeed(self,start,stop,time):
        speed=abs(stop-start)/time
        if(speed>1.0):
            print 'Max speed of x stage motor is 1.0mm per second and you are requesting %fmm/sec'%(speed)
            print 'I am setting the max speed of the x motor to 1.0mm/sec' 
            speed=1.0
        self.xmotor.setSpeed(speed)
        

    def disablePositionCompare(self):
        # set motor start stop step for pulses
        self.xpos_enable.caput(0)

    def enablePositionCompare(self):
        # set motor start stop step for pulses
        self.xpos_enable.caput(1)

    #
    # Stop the detector and clear the tfg
    #
    def stopDetector(self):
        self.das.sendCommand("tfg stop")
        self.das.sendCommand("tfg init")
        self.das.sendCommand("disable 0")


    #
    # To update the GUI etc.
    #
    def update(controller, msg, exceptionType=None, exception=None, traceback=None, Raise=False):
        handle_messages.log(controller, "I18ContinuousScan:"+msg, exceptionType, exception, traceback, Raise)


    #
    #
    # This method writes out the detector data and records the time from the time scaler from the detector
    # 
    #
    def writeoutDetectorDataRow(self,startx,stopx,stepx,currenty,yindex,noofxpoints,nameoffset):
        #
        # Threaded readout of files 
        #
        #print 'here write out',yindex,noofxpoints,nameoffset
        currentpoint=1
        self.mcaList=[]
        self.pointTime=[]
        #print 'here write out',yindex,noofxpoints,nameoffset,currentpoint
        while(currentpoint!=noofxpoints+1):
            while(self.das.sendCommand("tfg read frame")<(2+currentpoint*2)):
                print 'sleep 1 read again'
                sleep(1.0)
            print 'here write1',self.das.sendCommand("tfg read frame"),currentpoint,self.das.sendCommand("tfg read status")
            scalerTimeData=self.readScalarData(currentpoint)[3]
            timesum=0.0
            #print 'here write2',scalerTimeData
            for i in range(len(scalerTimeData)):
                timesum=timesum+scalerTimeData[i]
            timesum=12.5E-6*timesum/9.0
            self.pointTime.append(timesum)
            files=self.writeDetectorPointFile(yindex,currentpoint,nameoffset)
            currentpoint=currentpoint+1




    #
    # Write the mca and scaler data out at frame xindex and set the name using the yindex and xindex information
    #
    def writeDetectorPointFile(self, yindex,xindex,nameoffset):
        name = "%s_yindex_%d_xindex_%d.xsp" % (self.mcarootname,yindex,xindex+nameoffset-1)
        sname = "%s_yindex_%d_xindex_%d_scalar.xsp" % (self.mcarootname,yindex,xindex+nameoffset-1)
        self.mcaList.append(name)
        command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw" % (xindex, name)
        self.das.sendCommand(command)
        command = "read 0 0 %d 4 9 1 from 1 to-local-file \"%s\" raw intel" % (xindex, sname)
        self.das.sendCommand(command)
        #self.archiveFileList.append(name)
        #self.archiveFileList.append(sname)
        return [name,sname]


    #==============================================================
    # Read the scaler data from memory
    #==============================================================
    def readScalarDataNoRetry(self,point):
        scalarData=[]
        scalarstring=''
        command = "read 0 0 %d 4 9 1 from 1" % (point)
        scalarString=self.das.getData(command)
        if scalarString =="" :
            time.sleep(1)
            scalarString=self.das.getData(command)
        try:
            for j in range(4):
                scalarData.append(range(9))
            k=0
            for i in range(9):
                for j in range(4):
                    scalarData[j][i]=int(scalarString[k])
                    k=k+1
            return scalarData
        except:
            type, exception, traceback = sys.exc_info()
            self.readError = self.readError + 1
            self.readErrorList.append(point)
            handle_messages.log(None,"Error in readScalarDataNoRetry - scalarString = " + `scalarString` + " readErrorList = " + `self.readErrorList`, type, exception, None, True)

    #
    # VN routine to read scalar data
    # 
    def readScalarData(self,point):
        try:
            data = self.readScalarDataNoRetry(point)
            return data
        except:
            type, exception, traceback = sys.exc_info()
            handle_messages.log(None,"Error in readScalarData - retrying", type, exception, traceback, False)
        try:
            return self.readScalarDataNoRetry(point)
        except:
            type, exception, traceback = sys.exc_info()
            handle_messages.log(None,"Error in readScalarData - Giving up after 4 retries, returning zeroes", type, exception, traceback, False)
            scalarData=[]
            for j in range(4):
                scalarData.append(range(9))
                for i in range(9):
                    for j in range(4):
                        scalarData[j][i]=0                    
            return scalarData

    #====================================================
    #
    # Write out the data
    #
    #====================================================
    def writeSummary(self,currenty,yindex,startx,stepx,nx,offset):
        # lets window this mofo
        fid = open(self.datafilename,'a')
        for i in range(nx):
            val=(startx+(i*stepx))
            #print 'ic data again',i,self.ionchamberData,self.pointTime,self.mcaList
            line=str(val)+"\t"+str(currenty)+"\t"+str(self.pointTime[i])+"\t"+str(self.ionchamberData[0][i])+"\t"+str(self.ionchamberData[1][i])+"\t"+str(self.ionchamberData[2][i])+"\t"+str(self.mcaList[i])
            print >> fid,line
            print (startx+(i*stepx)),currenty,self.pointTime[i],self.ionchamberData[0][i],self.ionchamberData[1][i],self.ionchamberData[2][i],self.mcaList[i]
            # SDP Stuff
            detectorVector = Vector()
            detectorVector.add([self.ionchamberData[0][i],self.ionchamberData[1][i],self.ionchamberData[2][i]])
            detectorVector.add(self.mcaList[i])
            positionVector = Vector()
            positionVector.add(str(startx+(i*stepx)))
            positionVector.add(str(currenty))
            positionVector.add(str(self.pointTime[i]))
            sdp = ScanDataPoint("MicroFocus StepMap",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",str(self.mcaList[0]),0)
            sdp.setScanIdentifier(str(self.fileno))
            self.controller.update(None, sdp)
            try:
                FileRegistrarHelper.registerFile(self.mcaList[i])
            except:
                "unable to register files for archiving " + self.mcaList[i]
            print 'Reading and windowing:',self.mcaList[i]
            frameData=Xspress2Utilities.interpretDataFile(self.mcaList[i],0)
            windowsums=[0.0]*len(self.windowName)
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
                windowsums[j]=totalw
            print 'writing windowed data',windowsums,len(self.windowName)
            self.appendToRGB(i,yindex,self.pointTime[i],self.ionchamberData,windowsums)
        fid.close()


    #====================================================
    #
    #  Window the data
    #
    #====================================================
    def windowData(self,data,startw,endw):
        #print 'HERE!!',startw,endw    
        sum=0.0    
        for i in range(startw,endw):
            sum=sum+data[i]
        return sum    


    def setupGUI(xstart,xend,xstep,ystart,yend,ystep,collectionTime):
        global mapRunning
       # print command_server.getScriptStatus()
        while(mapRunning):
            sleep(5)
        mapRunning = 1
        scandata=Vector()
        # Type of scan
        scandata.add("MapScan")
        continuous = Boolean(1)
        fluscan  =Boolean(1)
        detectorToUse = gda.gui.microfocus.i18.I18MicroFocusPanel.XSPRESS
        scanstring = str(xstart) + " "+ str(xstep) + " "+str(xend)+" "+str(ystart) + " "+str(ystep)+ " "+ str(yend) + " "+str(collectionTime) +" " + str(continuous)  + " "+ str(fluscan)
        scandata.add(scanstring)
        scandata.add(detectorToUse)
        controller = finder.find("MicroFocusController")
        controller.update(None,scandata)

    setupGUI = staticmethod(setupGUI)
