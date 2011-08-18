from java.lang import *
from gda.configuration.properties import LocalProperties
from gda.data import NumTracker
from gda.device.xspress import Xspress2Utilities
from gda.jython import JythonServerFacade
from gda.scan import ScanDataPoint
from java.io import DataInputStream
from java.io import FileInputStream
from java.util import Calendar
from java.util import Vector
import os
import jarray
import sys
from org.python.modules.math import *

class DummyExafsScanClass(ScriptBase):
    def __init__(self):
        # Create some data vectors to hold the scan data (and names)
        self.scannableNamesVector=Vector()
        self.scannableNamesVector.add("dcm_mono")
        self.detectorNamesVector=Vector()
        self.detectorNamesVector.add("counterTimer01")
        self.detectorNamesVector.add("counterTimer02")
        # 
        self.controller = finder.find("ExafsController")
        self.mcontroller = finder.find("MicroFocusController")
        #
        self.xsp=finder.find("xspress2system")
        self.ionchambers=DummySlaveCounterTimer()
        self.converter = finder.find("auto_mDeg_idGap_mm_converter")
        #
        self.title="TITLE"
        self.condition1="CONDITION1"
        self.condition2="CONDITION2"
        self.condition3="CONDITION3"
        # define pi
        self.pi=4.0*atan(1.0)
        # default collect all
        self.windowValues=[[0, 4095]]*9
        self.windowName='ALL'
        self.ionchamberData=[]
        self.mcaList=[]
        self.scalarList=[]
        self.runs=NumTracker("tmp")
        self.runprefix='i18exafs'
        self.runext='.dat'
        self.fileno=self.runs.getCurrentFileNumber()+1
        self.runs.incrementNumber()
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
        self.facade=JythonServerFacade.getInstance()
        self.scanList=[]
        self.noOfRepeats=1
        self.noOfPoints=0
         
    def addAngleScan(self, start, end, step, collectionTime):
        self.noOfPoints=self.noOfPoints+int((end-start)/step)
        self.scanList.append(['a',start,end,step,collectionTime])
		  
    def addKScan(self, start, end, step, kStartTime, kEndTime, kWeighting, edgeEnergy, twoD):
        self.noOfPoints=self.noOfPoints+int((end-start)/step)
        self.scanList.append(['k',start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD])
		  
    def setNoOfRepeats(self, repeats):
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
			  for j in range(len(self.scanList)):
				  if(self.scanList[j][0]=='a'):
					  self.anglescan(self.scanList[j][1],self.scanList[j][2],self.scanList[j][3],self.scanList[j][4])
				  elif(self.scanList[j][0]=='k'):
					  self.kscan(self.scanList[j][1],self.scanList[j][2],\
					  self.scanList[j][3],self.scanList[j][4],self.scanList[j][5],self.scanList[j][6],self.scanList[j][7],self.scanList[j][8])
			  self.incrementGUIRepeat()
			  
    def setupGUI(self):    
		  scandata=Vector()
		  # Type of scan
		  scandata.add("FluScan")
		  # No of Repeats
		  # No of Points
		  scandata.add(self.noOfPoints)
		  scandata.add(self.noOfRepeats)
		  self.controller.update(None,scandata)
		  
    def incrementGUIRepeat(self):
		  scandata=Vector()
		  # Type of scan
		  scandata.add("ScanComplete")
		  self.controller.update(None,scandata)
		  
    def setResMode(self,mode,map=None):
        return
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
        for j in range(2):
           scalerData.append(range(9))
        fis =FileInputStream(self.scalarList[i])
        dis =DataInputStream(fis)
        scalerBytes =jarray.zeros(18*4,'b')
        dis.read(scalerBytes, 0, 18*4)
        fis.close()
        offset = 0
        for j in range(2):
           for l in range(0,36,4):
              scalarData[j][l/4]= (0x000000FF & scalerBytes[offset+l+0]) + ((0x000000FF & scalerBytes[offset+l+1])<<8)+((0x000000FF & scalerBytes[offset+l+2])<<16)+((0x000000FF & scalerBytes[offset+l+3])<<24)
           offset=offset+36	
        fis.close()
        return scalarData
	 
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
        self.interrupted=Boolean(0)
	 
    def calcEnergy(self,bragg):
        energy=1977.42/self.sind(bragg)
        return energy
     
    def sind(self,value):
        valueradians=self.angleToRadians(value)
        sintheta=sin(valueradians)
        return sintheta

    def asind(self,value):
        valueradians=self.angleToRadians(value)
        asintheta=asin(valueradians)
        return asintheta

    def cosd(self,value):
        valueradians=self.angleToRadians(value)
        costheta=cos(valueradians)
        return costheta

    def angleToRadians(self,angle):
        factor = 180.0/self.pi
        return angle/factor

    def radiansToAngle(self,angle):
        factor = 180.0/self.pi
        return angle*factor

    #
    #  Read in a window to be used on the mca files 
    #
    def setWindows(self, filename, desiredWindow):
        infile=open(filename, 'r')
        tmpwindowValues=[[0, 4095]]*9
        tmpwindowName=''
        while infile:
            a=infile.readline()    
            n = len(a)
            if n == 0:
                break
            temp=a.split('\t')
            tmpwindowName=temp[0].strip().replace(' ', '')
            if(tmpwindowName.lower().find(desiredWindow.lower())>=0):
                for j in range(len(temp)-1):
                    index=j+1
                    mytemp=temp[index].strip().replace('[', '').replace(']', '').split(',')
                    mytemp=[int(mytemp[0]), int(mytemp[1])]
                    tmpwindowValues[j]=mytemp 
                    print 'window values chosen :', j, tmpwindowValues[j]
                self.windowValues= tmpwindowValues
                self.windowName= tmpwindowName

    #
    # Performs an angle scan in step mode
    # 
    def anglescan(self,start,end,step,collectionTime):
        if(self.interrupted):
            return
        self.mcaList=[]
        self.ionchamberData=[]
        self.scalarList=[]
        # find no of points
        difference = end - start
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        currentpos=start
        # Check to see if a user has asked to pause the script
        self.checkForPauses()
        # Set the collection time
        self.ionchambers.setCollectionTime(collectionTime/1000.0)
        # loop over npoints
        print 'Starting angle scan'
        print 'Mono\tI0\t It\t'
        try:
            for i in range(npoints):
                # Move mono to start position
                comboDCM.moveTo(currentpos)
                comboDCM.waitWhileBusy()
                self.converter.disableAutoConversion()
                #dcm_mono.waitWhileBusy()
                ##ScannableBase.waitForScannable(dcm_mono)
                self.ionchamberData.append(self.ionchambers.collectData())
                # print out some progress
                print dcm_mono.getPosition(),self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]             
                # Check to see if a user has asked to pause or halt the script
                self.checkForAnglePauseOrInterrupt(i,start,end,step)
                # Move the mono
                currentpos=currentpos+step
        except:
            type, exception, traceback = sys.exc_info()
            self.converter.enableAutoConversion()
            self.controller.update(None, "error")
            self.mcontroller.update(None, "error")
        #
        #  write out
        #        
        self.stopDetector()    
        self.writeSummary(npoints,start,end,step)
        self.tag=self.tag+1
        self.converter.enableAutoConversion()
        self.controller.update(None, "complete")
        self.mcontroller.update(None, "complete")
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
        if(self.interrupted):
            return
        self.mcaList=[]
        self.ionchamberData=[]
        self.scalarList=[]
        # check that step is negative when moving downwards to stop
        difference = end - start
        if (difference < 0 and step > 0):
            step = -step
        npoints = int(difference / step)
        currentpos=start
        # prepare detector for collection
        print 'Clearing and Preparing Detector'
        self.prepareDetectorForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
        # loop over npoints
        if(self.interrupted):
            return

        print 'Starting k scan'
        print 'Mono\tI0\t It\t'
        for i in range(npoints):
            mdegPosition = self.mDegForK(currentpos,edgeEnergy,twoD)
            secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
            # Set the collection time
            self.ionchambers.setCollectionTime(secTime/1000.0)
            # Move mono to start position

            dcm_mono.asynchronousMoveTo(mdegPosition)
            #ScannableBase.waitForScannable(dcm_mono)
            dcm_mono.waitWhileBusy()

            # Ready the ion chambers
            self.ionchambers.clearAndPrepare()

            self.ionchamberData.append(self.ionchambers.collectData())
            # print out some progress
            #print mdegPosition,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]
            print mdegPosition,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]             
            # Check to see if a user has asked to pause or halt the script
            self.checkForKScanPauseOrInterrupt(i,start,end,step,edgeEnergy, twoD)
            # Move the mono
            currentpos=currentpos+step
                
        #
        #  write out at end
        #        
        self.stopDetector()    
        self.writeKScanSummary(npoints,start,end,step,edgeEnergy, twoD)
        self.tag=self.tag+1
        print 'Finished k scan'

    #
    #  Disables, Clears and enables the detector
    #  Sets up tfg for a given noOfFrames and  collectionTime
    #  pausing in the dead frame and dead port=1 for adc triggering
    #  and finally starts the tfg which means it sits waiting for a software based continue command
    #
    def prepareDetectorForCollection(self,noOfFrames,collectionTime):
        # Do nothing for dummy
        return
    #
    #  Disables, Clears and enables the detector
    #  Sets up tfg for a set of possibly variable length time frames
    #  and finally starts the tfg which means it sits waiting for a software based continue command
    #
    def prepareDetectorForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
        return
    
    #
    # Stop the tfg and disable the detector
    #
    def stopDetector(self):
        return


    def writeDetectorFile(self,npoints):
        #self.das.sendCommand("disable 0")
        for i in range(npoints):
            name = "%s_scan_%d_index_%d.dat" % (self.mcarootname,self.tag,i)
            sname = "%s_scan_%d_index_%d_scalar.dat" % (self.mcarootname,self.tag,i)
            print 'Writing scan point',i,'to',name
            self.mcaList.append(name)
            self.scalarList.append(sname)
            detfile = self.xsp.writeDummyFile()
            scafile = self.xsp.writeDummyScalerFile()
            os.rename(detfile, name)
            os.rename(scafile, sname)
            

    def writeSummary(self,npoints,start,end,step):
        self.writeDetectorFile(npoints)
        # lets window this mofo
        fid = open(self.datafilename,'a')
        current=start
        for i in range(npoints):
            windowedData=[0.0]*9
            print 'Reading and windowing:',self.mcaList[i]
            frameData=Xspress2Utilities.interpretDataFile(self.mcaList[i],0)
            totalw=0.0    
            for j in range(9):
                sumgrades=frameData[j]
                windowedData[j]=windowedData[j]+self.windowData(sumgrades,self.windowValues[j][0],self.windowValues[j][1])
            for j in range(9):
                totalw=totalw+windowedData[j]
            #
            # now read scalar data
            # 
            scalarData=[] 
            for j in range(2):
                scalarData.append(range(9))
            fis =FileInputStream(self.scalarList[i])
            dis =DataInputStream(fis)
            scalerBytes =jarray.zeros(18*4,'b')
            dis.read(scalerBytes, 0, 18*4)
            offset = 0
            for j in range(2):
                for l in range(0,36,4):
                    scalarData[j][l/4]= (0x000000FF & scalerBytes[offset+l+0]) + ((0x000000FF & scalerBytes[offset+l+1])<<8)+((0x000000FF & scalerBytes[offset+l+2])<<16)+((0x000000FF & scalerBytes[offset+l+3])<<24)
                offset=offset+36            
            print >>fid,current,self.calcEnergy(current/1000.0),self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],str(windowedData[0:]).strip('[]').replace(',',''), \
                totalw,str(scalarData[0:1]).strip('[]').replace(',',''),str(scalarData[1:2]).strip('[]').replace(',', '')
            # pdq added for plotting
            current=current+step
            # SDP Stuff
            #print "Creating SDP..."
            detectorVector = Vector()
            detectorVector.add(self.ionchamberData[i])
            detectorVector.add(windowedData)
            #detectorVector.add(jarray.array(self.ionchamberData[i][0:2],'d'))
            #detectorVector.add(jarray.array(windowedData,'d'))
            positionVector = Vector()
            positionVector.add(str(current))
            #sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,positionVector,detectorVector,"Panel Name","I18 Custom SDP","Header String",self.datafilename)
            #sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,positionVector,detectorVector,"Panel Name","I18 Custom SDP","Header String",self.mcaList[i])
            #ScanDataPoint(String scanName, Vector<String> scannables,
            #Vector<String> detectors, Vector<String> monitors,
            #Vector<String> scannableHeader, Vector<String> detectorHeader,#Vector<String> monitorHeader, Vector<String> positions,#Vector<Object> data, Vector<String> monitorPositions,
            #String creatorPanelName, String tostring, String headerString,#String currentFilename, boolean hasChild)
            sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.datafilename,0)
            self.controller.update(None, sdp)
            self.mcontroller.update(None, sdp)
        fid.close()

    def writeKScanSummary(self,npoints,start,end,step,edgeEnergy,twoD):
        self.writeDetectorFile(npoints)
        current=start
        # lets window this mofo
        fid = open(self.datafilename,'a')
        current=start
        for i in range(npoints):
            windowedData=[0.0]*9
            print 'Reading and windowing:',self.mcaList[i]
            frameData=Xspress2Utilities.interpretDataFile(self.mcaList[i].strip(),0)
            totalw=0.0
            for j in range(9):
                #sumgrades=Xspress2Utilities.sumGrades(frameData[j], 0, 15)
                sumgrades=frameData[j]
                windowedData[j]=windowedData[j]+self.windowData(sumgrades,self.windowValues[j][0],self.windowValues[j][1])
            for j in range(9):
                totalw=totalw+windowedData[j]
            #
            # now read scalar data
            # 
            scalarData=[] 
            for j in range(2):
                scalarData.append(range(9))
            fis =FileInputStream(self.scalarList[i])
            dis =DataInputStream(fis)
            scalerBytes =jarray.zeros(18*4,'b')
            dis.read(scalerBytes, 0, 18*4)
            offset = 0
            for j in range(2):
                for l in range(0,36,4):
                    scalarData[j][l/4]= (0x000000FF & scalerBytes[offset+l+0]) + ((0x000000FF & scalerBytes[offset+l+1])<<8)+((0x000000FF & scalerBytes[offset+l+2])<<16)+((0x000000FF & scalerBytes[offset+l+3])<<24)
                offset=offset+36            
            print>>fid,self.mDegForK(current,edgeEnergy,twoD),self.calcEnergy(self.mDegForK(current,edgeEnergy,twoD)/1000.0),\
                self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],str(windowedData[0:]).strip('[]').replace(',',''), \
                totalw,str(scalarData[0:1]).strip('[]').replace(',',''),str(scalarData[1:2]).strip('[]').replace(',', '')

            #print >> fid,self.mDegForK(current,edgeEnergy,twoD),self.ionchamberData[i][0],self.ionchamberData[i][1],self.mcaList[i],str(windowedData[0:]).strip('[]').replace(',', '')
            #print >> fid,self.mDegForK(current,edgeEnergy,twoD),self.ionchamberData[i][0][0],self.ionchamberData[i][1][0],self.ionchamberData[i][2][0],str(windowedData[0:]).strip('[]').replace(',', ''),totalw,totalw/self.ionchamberData[i][0][0]
            #print >> fid,self.mDegForK(current,edgeEnergy,twoD),self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],str(windowedData[0:]).strip('[]').replace(',', ''),totalw
            current=current+step
            # SDP Stuff
            print "Creating SDP..."
            detectorVector = Vector()
            detectorVector.add(self.ionchamberData[i])
            #detectorVector.add(jarray.array(self.ionchamberData[i][0:2],'d'))
            detectorVector.add(windowedData[0:])
            #detectorVector.add(jarray.array(windowedData,'d'))
            positionVector = Vector()
            positionVector.add(str(current))
            #sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.mcaList[i])
            sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.mcaList[i],0)
            self.controller.update(None, sdp)
            self.mcontroller.update(None, sdp)
        fid.close()

    def windowData(self,data,start,end):
        sum=0.0    
        for i in range(start,end):
            sum=sum+data[i]
        return sum                        
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
        tfglist="tfg setup-groups cycles 1\r\n"
        for  j in range(npoints+1):
            secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
            tfglist = tfglist + "1 0.01 %f 0 1 1 0\r\n" %(secTime/1000.0)
            currentpos = currentpos + step
        tfglist=tfglist+"-1 0 0 0 0 0 0\r\n"
        return tfglist

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
        line = " I18_EXAFS_RUN="+ str(self.fileno)+" "+ str(year)+" "+str(month)+" "+ str(day)+" "+str(hour)+" "+str(minute)+" "+str(second) + "\n"
        print>>fid,line
        print>>fid,'dcm_bragg energy I0 It drain flu1 flu2 flu3 flu4 flu5 flu6 flu7 flu8 flu9 flutot'
        fid.close()


    def checkForAnglePauseOrInterrupt(self,npoints,start,end,step):
        if(self.paused):
            JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
            while(self.paused):
                try:
                    java.lang.Thread.sleep(250)
                except lang.InterruptedException:
                    print 'Stopping angle scan:Writing out data taken'
                    # write the data we have so far and return
                    self.stopDetector()    
                    self.writeSummary(npoints,start,end,step)
                    self.interrupted=Boolean(0)
                    self.paused=Boolean(0)
                    JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
                    print  'Now the nasty bit: throw an exception to stop running'
                    raise lang.InterruptedException()
                    #JythonServerFacade.getInstance().haltCurrentScript()

        if(self.interrupted):
            print 'Stopping angle scan:Writing out data taken'
            # write the data we have so far and return
            self.stopDetector()    
            self.writeSummary(npoints,start,end,step)
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
    def checkForAngleInterrupt(self,npoints,start,end,step,collectionTime):
        #if(self.facade.getScanStatus()==0 and self.facade.getScriptStatus()==0):
        if(self.interrupted):
           print 'Stopping angle scan:Writing out data taken'
           # write the data we have so far and return
           self.stopDetector()	
           self.writeSummary(npoints,start,end,step,collectionTime)
           self.interrupted=Boolean(0)
           self.paused=Boolean(0)
           JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
           print  'Now the nasty bit: throw an exception to stop running'
           raise lang.InterruptedException()
           raise lang.InterruptedException()


    #==================================================
	 #
	 # Checks to see if an angle scan has been paused
	 #
	 #==================================================
    def checkForAnglePause(self,npoints,start,end,step,collectionTime):
        if(self.paused):
           JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
           while(self.paused):
              try:
                 print 'Angle Scan paused - Awaiting resume'
                 java.lang.Thread.sleep(10000)
              except lang.InterruptedException:
                 self.checkForAngleInterrupt(npoints,start,end,step,collectionTime)


    #==================================================
	 #
	 # Checks to see if an angle scan has been paused
	 #
	 #==================================================
    def checkForKScanInterrupt(self,npoints,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting):
        #if(self.facade.getScanStatus()==0 and self.facade.getScriptStatus()==0):
        if(self.interrupted):
           print 'Stopping k scan:Writing out data taken'
           # write the data we have so far and return
           self.stopDetector()	
           self.writeKScanSummary(npoints,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
           self.interrupted=Boolean(0)
           self.paused=Boolean(0)
           JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
           print  'Now the nasty bit: throw an exception to stop running'
           raise lang.InterruptedException()

    #==================================================
	 #
	 # Checks to see if an angle scan has been paused
	 #
	 #==================================================
    def checkForKScanPause(self,npoints,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting):
        if(self.paused):
           JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
           while(self.paused):
              try:
                 print 'K Scan Scan paused - Awaiting resume'
                 java.lang.Thread.sleep(10000)
              except lang.InterruptedException:
                 self.checkForKScanInterrupt(npoints,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)

    def checkForKScanPauseOrInterrupt(self,npoints,start,end,step,edgeEnergy, twoD):
        if(self.paused):
            JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
            while(self.paused):
                try:
                    java.lang.Thread.sleep(250)
                except lang.InterruptedException:
                    print 'Stopping angle scan:Writing out data taken'
                    # write the data we have so far and return
                    self.stopDetector()    
                    self.writeSummary(npoints,start,end,step)
                    self.interrupted=Boolean(0)
                    self.paused=Boolean(0)
                    JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
                    print  'Now the nasty bit: throw an exception to stop running'
                    raise lang.InterruptedException()
                    #JythonServerFacade.getInstance().haltCurrentScript()

        if(self.interrupted):
            print 'Stopping angle scan:Writing out data taken'
            # write the data we have so far and return
            self.stopDetector()    
            self.writeSummary(npoints,start,end,step)
            self.interrupted=Boolean(0)
            self.paused=Boolean(0)
            JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
            print  'Now the nasty bit: throw an exception to stop running'
            raise lang.InterruptedException()    
        
