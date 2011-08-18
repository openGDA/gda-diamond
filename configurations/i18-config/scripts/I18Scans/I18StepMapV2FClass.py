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
from java.util.concurrent import TimeUnit
import jarray
from gda.scan import ScanDataPoint
from gda.jython import ScriptBase
from java.util import Date
from java.text import SimpleDateFormat
from gda.data import PathConstructor
import thread
import time
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

class I18StepMapClass(ScriptBase):
    #====================================================
    #
    # Setup the I18 Step map class
    #
    #====================================================
    def __init__(self, datafileNo="default"):
        # Create some data vectors to hold the scan data (and names)
        self.scannableNamesVector=Vector()
        self.scannableNamesVector.add(MicroFocusSampleX)
        self.scannableNamesVector.add(MicroFocusSampleY)
        self.detectorNamesVector=Vector()
        self.detectorNamesVector.add(counterTimer01)
        self.detectorNamesVector.add(finder.find("mapdetector"))
        # Find the script controller 
        self.controller = finder.find("MicroFocusController")    
        #
        self.xmotor=MicroFocusSampleX
        self.ymotor=MicroFocusSampleY

        self.das=finder.find("daserver")
        self.mcaList=[]
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
        #self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
        self.datadir=PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
        self.rgbdir=PathConstructor.createFromProperty("gda.data.scan.datawriter.rgbdatadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        ##This rgb file is created in the gui, registering this file for archiving causes 
        ## considerable delay .
        self.rgbfilename=self.rgbdir+'/'+str(self.fileno)+"_1.rgb"
        #
        # Make a directory to store the mca files in
        #
        self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
        self.mca_row_dir=self.mcadir	
        self.mcarootname=self.mcadir+str(self.fileno)
        self.mca_row_rootname=self.mcarootname
        #
        if not os.path.isdir(self.mcadir):
            os.mkdir(self.mcadir)
        self.tag=1
        self.createFile()
        self.xspress = finder.find("xspress2system")
        # Set default windows
        self.setWindows('/dls_sw/i18/software/gda/config/default.scas')
        #self.createRGBfile()
        self.readXindex=-1
        self.readYindex=-1
        self.archiveFileList=[]
        self.fileArchiveCounter=0
        self.archiver = archiver
        
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

           
    #====================================================
    #
    # I18 Step map class
    #
    #====================================================
    def stepmapscan(self,xstart,xend,xstep,ystart,yend,ystep,collectionTime):
        print xstep
        print ystep
        global mapRunning
        mapRunning =1
        lock =0
        try:
            print 'locking express'
            lock  = self.xspress.tryLock(5,TimeUnit.SECONDS)
            print "the lock value is " + str(lock)
            if not lock:
                print "Xspress detector is already locked"
                self.controller.update(None, "STOP")
                return
            scanStart = time.asctime()
            print scanStart
            nx = 0
            ny = 0
            totalion = []
            self.mcaList = []
            nx = abs(xend - xstart) / xstep
            ny = abs(yend - ystart) / ystep
            # Determine no of points
            nx = int(round(nx + 0.5))
            ny = int(round(ny + 0.5))
            # Round to even or odd to ensure map can be read back in
            xcurrent = xstart
            ycurrent = ystart
            # Move to start positions
            self.checkForInterrupt()
            self.xmotor.moveTo(xcurrent)
            self.checkForInterrupt()
            self.ymotor.moveTo(ycurrent)
            self.checkForInterrupt()
            estimatedTime = 0.0
            #startTime=w.getPosition()
            self.timeList = []
            mysleeptime=int(100.0*(collectionTime*0.95/1000.0))/100.0
            for i in range(ny):

                # Row by row data output directory
                self.mca_row_dir=self.mcadir+("row%d/" %i)
                if not os.path.isdir(self.mca_row_dir):
                    os.mkdir(self.mca_row_dir)
                self.mcarootname=self.mca_row_dir+str(self.fileno)
                self.readCounter = 0
                self.windowArrays = []
                for j in range(len(self.windowName)):
                    self.windowArrays.append(self.initArray1D(nx))          
               
                #print 'initialsiing ionc hamber data'
                self.ionchamberData = []
                self.mcaList = []
                self.checkForInterrupt()
                        #
                # Prepare detector for row
                # 
                self.prepareDetectorForRow(nx, collectionTime)
                self.checkForInterrupt()
                self.checkForPause()
                self.xindex = 0
                self.mcafiles = []
                startTime = time.time()
                for j in range(nx):
                    # Check beam is running
                    self.timeList.append(time.time() - startTime)
                    startTime = time.time()
                    self.xindex = j
                    while(BeamMonitor.beamOn() == 0):
                        print 'Beam lost : Pausing until resumed'
                        try:
                            sleep(60)
                        except:
                            self.interrupted = 1    
                        self.checkForInterrupt()
                    #
                    # Check if detector is filling
                    #
                    while(BeamMonitor.isFilling() == 1):
                    #while(False):
                        self.checkForInterrupt()
                        print 'Detector Filling : Pausing until completed'
                        try:
                            sleep(60)
                        except:
                            self.interrupted = 1                    
                        self.checkForInterrupt()
                        ##end  of beam while
                    #
                    # topup test
                    #
                    while(BeamMonitor.collectBeforeTopupTime(collectionTime / 1000.0) == 1):
                        print 'Top up coming : Pausing until resumed'
                        try:
                            sleep(1)
                        except:
                            self.interrupted = 1    
                        self.checkForInterrupt()
                        #end of topup while
                    # clear the ion chamber epics mca and prepare for trigger
                    self.ionchambers.clearAndPrepare()
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

                    # tell the tfg to continue
                    self.das.sendCommand("tfg cont")
                    self.checkForInterrupt()
                    # Wait for tfg to stop
                    try:
                        sleep(mysleeptime)
                    except:
                        self.interrupted = 1    
                    self.checkForInterrupt()
                    self.das.sendCommand("tfg wait")
                    self.checkForInterrupt()
                    self.ionchambers.stop()
                    # collect ion chamber data
                    self.ionchamberData.append(self.ionchambers.getPosition())
                    self.checkForInterrupt()
                    # Some info for the user
                    print xcurrent, ycurrent, self.ionchamberData[j][0], self.ionchamberData[j][1], self.ionchamberData[j][2]
                    ## write the data file from detector to file
                    self.mcafiles.append(self.writeDetectorPointFile(i, j))              
                    self.checkForInterrupt()
                    try:
                        ##no data is available for the first point in the scan
                        if(j >= 1):
                           ##Starting a new thread to read the data from the detector while the motor is moving
                           ##during the ystage move to the next position or should this go in the xstage movement ??
                           ###or the data can be read while the motor is moved asynchronously
                           thread.start_new_thread(self.getDetectorDataPoint, (i, (j - 1), ycurrent, xcurrent - xstep, collectionTime, self.mcafiles[j - 1]))
                        # update the x motor position
                        xcurrent = xcurrent + xstep
                        self.xmotor.moveTo(xcurrent)
                    except:
                        self.interrupted = 1  
                        #end of try catch  
                    self.checkForInterrupt()
                    ##end of j for loop
                #print 'Finished row',i,"Time Left:(minutes)",((ny-i)*(endTime-startTime))/60.0
                # Stop the detector and tfg
                ##read the last point of the row from the detector
                thread.start_new_thread(self.getDetectorDataPoint, (i, self.xindex, ycurrent, xcurrent - xstep, collectionTime, self.mcafiles[self.xindex]))
                ##if the xmotor is moved asynchronously then the last point of the row should be collected after the xmotor
                ##is finished moving
    
                self.checkForInterrupt()
                self.stopDetector()    
                self.checkForInterrupt()    
                self.checkForInterrupt()    
                # increment y
                ycurrent = ycurrent + ystep
                self.checkForInterrupt()
                try:
                    
                    self.ymotor.moveTo(ycurrent)
                    
                except:
                    self.interrupted = 1
                    #end of try catch
                self.checkForInterrupt()
                # return x to its start point
                xcurrent = xstart
                self.checkForInterrupt()
                self.xmotor.moveTo(xcurrent)
                self.checkForInterrupt()
                ##make sure the last data point of the previous row has been read before 
                ##clearing the detector or reseeting any of the previous values
                ##this check is not required if the motor is moved asynchronously
                readLoopCounter = 0 
                         
                while(1):
                    readLoopCounter = readLoopCounter + 1
                    if((self.readXindex == self.xindex and self.readYindex == (i)) or
                       (readLoopCounter >= 100) or self.readCounter == nx):
                      break
                    else:
                        print 'waiting for file to be appear ' + str(readLoopCounter)
                        sleep(1)
            # Tell the GUI the script has stopped
            self.controller.update(None, "STOP")
            # Tell the user the map has stopped
            scanEnd = time.asctime()
            print 'Scan complete'
        finally:
            
            if(lock):
                print 'unlocking xpress'
                self.xspress.unlock()
            mapRunning =0
            print "list of files to be archived are "
            print self.archiveFileList
            if(os.path.exists(self.datafilename)):
                self.archiveFileList.append(self.datafilename)
                if(os.path.exists(self.rgbfilename)):
                    self.archiveFileList.append(self.rgbfilename)
            try:
                if(len(self.archiveFileList ) != 0):
                    self.archiver.registerFiles("scan-" + str(self.fileno), self.archiveFileList)
            except:
                print "Unable archive files " + self.datafilename
        print self.timeList
        print scanStart
        print scanEnd



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
        command = "tfg setup-groups cycles 1 \n%d 1.0E-7 %f 0 7 -1 0 \n-1 0 0 0 0 0 0 "  %(noOfFrames,collectionTime/1000.0)
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
            command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw intel" % ( i, name)
            self.das.sendCommand(command)
            command = "read 0 0 %d 9 3 1 from 1 to-local-file \"%s\" raw intel" % ( i, sname)
            self.das.sendCommand(command)
            
            
    def writeDetectorPointFile(self, yindex,xindex):
        #self.das.sendCommand("disable 0")
        name = "%s_yindex_%d_xindex_%d.xsp" % (self.mcarootname,yindex,xindex)
        sname = "%s_yindex_%d_xindex_%d_scalar.xsp" % (self.mcarootname,yindex,xindex)
        self.mcaList.append(name)
        command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw" % (xindex, name)
        self.das.sendCommand(command)
        command = "read 0 0 %d 3 9 1 from 1 to-local-file \"%s\" raw intel" % (xindex, sname)
        self.das.sendCommand(command)        
        return [name,sname]
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
            sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.mcaList[i],0)
            sdp.setScanIdentifier(str(self.fileno))
            self.controller.update(None, sdp)
        fid.close()

    #====================================================
    #
    # Write out the data
    #
    #====================================================
    def writeSummaryAtPoint(self,currentx,currenty,xindex,yindex,collectionTime):
        files=self.writeDetectorPointFile(yindex,xindex)
        fid = open(self.datafilename,'a')
        line=str(currentx)+"\t"+str(currenty)+"\t"+str(collectionTime)+"\t"+str(self.ionchamberData[xindex][0])+"\t"+str(self.ionchamberData[xindex][1])+"\t"+str(self.ionchamberData[xindex][2])+"\t"+str(files[0])
        print >> fid,line
       
        print currentx,currenty,collectionTime,self.ionchamberData[xindex][0],self.ionchamberData[xindex][1],self.ionchamberData[xindex][2],files[0]
        fid.close()
        # SDP Stuff
        detectorVector = Vector()
        detectorVector.add(self.ionchamberData[xindex])
        detectorVector.add(files[0])
        positionVector = Vector()
        positionVector.add(str(currentx))
        positionVector.add(str(currenty))
        sdp = ScanDataPoint("MicroFocus StepMap",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",files[0],0)
        sdp.setScanIdentifier(str(self.fileno))
        self.controller.update(None, sdp)

#====================================================
    #
    # Write out the data to the data file and ScanDataPoint
    # Data from the Xspress has to be written before this and filenames should
    # be passed in as a parameter
    #
    #====================================================
    def writeSummaryAtPoint2(self,currentx,currenty,xindex,yindex,collectionTime,files):
        ##files=self.writeDetectorPointFile(yindex,xindex)
        fid = open(self.datafilename,'a')
        ##wait for the files to appear
        fileExists=0
        while(fileExists):
            fileExists=os.access(files[0], os.F_OK)
            if(fileExists):
                break
            else:
                sleep(0.1)
        try:
            self.archiveFileList.append(files[0])
            self.fileArchiveCounter += 1
            self.archiveFileList.append(files[1])
            self.fileArchiveCounter += 1
            if(self.fileArchiveCounter >= 100):
                self.archiver.registerFiles("scan-" + str(self.fileno), self.archiveFileList)
                self.fileArchiveCounter = 0
                self.archiveFileList = []
       
        except:
            print "unable to register files for archiving " + files[0]
        line=str(currentx)+"\t"+str(currenty)+"\t"+str(collectionTime)+"\t"+str(self.ionchamberData[xindex][0])+"\t"+str(self.ionchamberData[xindex][1])+"\t"+str(self.ionchamberData[xindex][2])+"\t"+str(files[0])
        print >> fid,line
       
        print currentx,currenty,collectionTime,self.ionchamberData[xindex][0],self.ionchamberData[xindex][1],self.ionchamberData[xindex][2],files[0]
        fid.close()
        # SDP Stuff
        detectorVector = Vector()
        detectorVector.add(self.ionchamberData[xindex])
        detectorVector.add(files[0])
        positionVector = []
        positionVector.append(currentx)
        positionVector.append(currenty)
        print 'FILE',str(files[0])
        #sdp = ScanDataPoint("MicroFocus StepMap",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",str(files[0]),0)
        sdp = ScanDataPoint()
        sdp.setUniqueName("MicroFocus StepMap")
        for s in self.scannableNamesVector:
            sdp.addScannable(s)
        for d in self.detectorNamesVector:
            sdp.addDetector(d)
        for p in positionVector:
            sdp.addScannablePosition(p,["%.4f"] )
        sdp.addDetectorData(self.ionchamberData[xindex],["%5.2g","%5.2g","%5.2g"])
        sdp.addDetectorData(files[0],["%s"] )
        sdp.setCurrentFilename(self.datafilename)
        sdp.setScanIdentifier(str(self.fileno))
        self.controller.update(None, sdp)

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
        print>>fid,str(sample_z.getPosition())
        print>>fid,str(comboDCM_eV.getPosition())
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
        self.archiveFileList.append(newdatafilename)
        print 'RGB file name',newdatafilename
        fid=open(newdatafilename,'w')
        mystr='row  column  i0  '
        for k in range(len(self.windowName)):
            mystr=mystr+self.windowName[k]
            if(k<(len(self.windowName)-1) ):
                mystr=mystr+"  "
        print >> fid,mystr
        fid.close()    


    def appendToRGB(self,xindex,yindex,ionchamber,windows):
        newdatafilename=self.datadir+'/'+str(self.fileno)+".rgb"
        fid=open(newdatafilename,'a')
        mystr=str(ionchamber[0])+" "
        for k in range(len(windows)):
            mystr=mystr+str(windows[k])
            if(k<(len(windows)-1)):
                mystr=mystr+" "
        print >> fid,yindex,xindex,mystr
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
        infile.close()
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

    def getDetectorDataRow(self,yindex,yvalue, xstart, xstep, noofxpoints, collectionTime):
        self.writeDetectorFiles(yindex,noofxpoints)    
        self.checkForInterrupt()    
            # write the data to a file
        self.checkForInterrupt()
        self.writeSummary(yvalue,xstart,xstep,noofxpoints,collectionTime)
        self.checkForInterrupt()
        # write rgb
        #self.appendToRGB(noofxpoints,yindex,self.ionchamberData)
        
    def getDetectorDataPoint(self,yindex,xindex, yvalue, xvalue,collectionTime,files):
        self.checkForInterrupt()    
            # write the data to a file
        self.writeSummaryAtPoint2(xvalue,yvalue,xindex,yindex,collectionTime, files)
        self.checkForInterrupt()
        self.readXindex=xindex
        self.readYindex = yindex
        self.readCounter=self.readCounter+1  
        #print 'read ', str(self.readCounter) 

    def getDataFileName(self):
        return self.datafilename    
    setupGUI = staticmethod(setupGUI)
  


