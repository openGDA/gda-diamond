from gda.epics import CAClient
from java.lang import *
#from gda.jython.scannable import ScannableBase
#from gda.jython.scannable import Scannable
from gda.device.scannable import ScannableBase
from gda.device import Scannable

from org.python.modules.math import *
from time import sleep
from gda.analysis import *
import os
import jarray
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

class I18VortexStepMapClass:
    def __init__(self, datafileNo="default"):
        self.scannableNamesVector=Vector()
        self.scannableNamesVector.add("MicroFocusSampleX")
        self.scannableNamesVector.add("MicroFocusSampleY")
        self.detectorNamesVector=Vector()
        self.detectorNamesVector.add("counterTimer01")
        self.detectorNamesVector.add("counterTimer02")
        # Find the script controller 
        self.controller = finder.find("MicroFocusController")    
        self.xmotor=MicroFocusSampleX
        self.ymotor=MicroFocusSampleY
        #self.das=finder.find("daserver")
        self.ionchambers=DummySlaveCounterTimer()
        #self.vortex=vortex_mca
        self.vortex = xmapMca
        self.ionchamberData=[]
        if(datafileNo == "default"):
            self.runs=NumTracker("tmp")
            self.fileno=self.runs.getCurrentFileNumber()+1
            self.runs.incrementNumber()
        else:
            self.fileno = datafileNo
        self.runext='.dat'
        self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
        self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
        self.rgbdatafilename=self.datadir+'/'+str(self.fileno)+".rgb"
        
        self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
        self.mcarootname=self.mcadir+str(self.fileno)
        
        if not os.path.isdir(self.mcadir):
            os.mkdir(self.mcadir)
            
        self.fluData=[]
        self.createFile()
        self.createRGBFile()
         # Set default windows
        self.windowValues=[]
        self.windowName=[]
        self.windowArrays=[]
        self.setWindows('/home/nv23/workspace/trunk_i18config/vortexdefault.scas')




    def stepmapscan(self,xstart,xend,xstep,ystart,yend,ystep,collectionTime):
        nx=abs(xend-xstart)/xstep
        ny=abs(yend-ystart)/ystep
        nx=int(round(nx+0.5))
        ny=int(round(ny+0.5))
        xcurrent=xstart
        ycurrent=ystart
        # Move to start
        self.xmotor.moveTo(xcurrent)
        self.ymotor.moveTo(ycurrent)
        self.ionchambers.setCollectionTime(collectionTime)
        #self.vortex.setCollectionTime(collectionTime/1000.0)
        #self.vortex.stop()
        # Create the dataset
        self.fluData=DataSet([nx,ny])
        self.vortex.stop()
        for i in range(ny):
            #
            # Prepare detector for row
            # 
            self.ionchamberData=[]
            self.prepareTFGForRow(nx,collectionTime)
            for j in range(nx):
                # Check beam is running
               # while(BeamMonitor.beamOn()==0):
                #    print 'Beam lost : Pausing until resumed'
                #    try:
                #        sleep(60)
                #    except:
                #        print 'Trying to stop during sleep'

                #
                # topup test
                #
               # while(BeamMonitor.collectBeforeTopupTime(collectionTime/1000.0)==1):
                #    print 'Top up coming : Pausing until resumed'
                #    try:
                #        sleep(1)
                 #   except:
                 #       self.interrupted=1    
                #self.checkForInterrupt()
                # Ready the ion chambers and vortex
                #self.vortex.stopEraseAndStart()
                self.vortex.clearAndStart()
                self.ionchambers.clearAndPrepare()
                # 
                #self.das.sendCommand("tfg cont")
                #self.das.sendCommand("tfg wait timebar")
                ###sleep to wait for the collectiontime 
                ##not needed in real scans as the vortex will be triggered by the tfg
                #sleep(collectionTime/1000.0)
                self.vortex.stop()
                while(self.ionchambers.isBusy()==1):
                    sleep(0.05)
                    pass
                # Update the vortex status
                #self.vortex.updateStatus()
                sleep(0.1)
                ionChambers=self.ionchambers.collectData()
                vortexdata=self.vortex.getROIsSum()
                vortexSpectrum = self.vortex.getData()
                #self.vortex.stop()
                print xcurrent,ycurrent,ionChambers[0],ionChambers[1],ionChambers[2],vortexdata
                #self.fluData.set(vortexdata,[j,i])
                # update the motor position
                self.writeSummary(xcurrent,ycurrent,j,i,ionChambers,collectionTime,vortexdata, vortexSpectrum)
                self.writeToRGB(i,j,ionChambers[0],ionChambers[1],ionChambers[2],vortexdata)
                xcurrent=xcurrent+xstep
                self.xmotor.moveTo(xcurrent)    
                # tell the tfg to continue
            print 'Finished row',i
            # Now update the plot
            #self.plot()
            self.stopTFG()
            #
            # increment y
            #
            ycurrent=ycurrent+ystep
            self.ymotor.moveTo(ycurrent)    
            #
            # return x to its start point
            # 
            xcurrent=xstart
            self.xmotor.moveTo(xcurrent)
        # Tell the GUI the script has stopped
        self.controller.update(None, "STOP")
        print 'Scan complete'


    
    def prepareTFGForRow(self,noOfFrames,collectionTime):
        #self.das.sendCommand("tfg init")
        #self.das.sendCommand("tfg setup-groups cycles 1 ")
        command = "%d 0.01 %f 0 3 1 0 "  %(noOfFrames,collectionTime/1000.0)
        #self.das.sendCommand(command)
        #self.das.sendCommand("-1 0 0 0 0 0 0 ")
        #self.das.sendCommand("tfg start")

            

    def writeSummary(self,currentx,currenty,xindex,yindex,ionChambers,collectionTime,vortexdata, vortexSpectrum):
        fid = open(self.datafilename,'a')
        ##spectrum file
        filename = "%s_yindex_%d_xindex_%d.xsp" % (self.mcarootname, yindex, xindex)
        print >>fid,str(currentx),str(currenty),str(collectionTime),str(ionChambers[0]),str(ionChambers[1]),str(ionChambers[2]),filename
        fid.close()
        fid.close()
        
        print filename
        
        print str(len(vortexSpectrum))
        for data in vortexSpectrum:
            datacounter = 0
            datalen = len(data)
            line =''
            sfid = open(filename, 'a')
            for j in data:
                datacounter = datacounter + 1
                
                if( datacounter  == datalen):
                    #print 'writing new line', str(datacounter)
                    line =line + str(j) 
                else:
                    line = line + str(j) + ' '
            #print line
            print >>sfid, line
            sfid.close()
                    
        
                
        # SDP Stuff
        detectorVector = Vector()
        detectorVector.add(ionChambers)
        vortexVector = Vector()
        vortexVector.add(vortexdata)
        vortexVector.add(filename)
        detectorVector.add(vortexVector)
        positionVector = Vector()
        positionVector.add(str(currentx))
        positionVector.add(str(currenty))
        #sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,positionVector,detectorVector,"Panel Name","I18 Custom SDP","Header String",files[0])
        sdp = ScanDataPoint("MicroFocus VortexStepMap", self.scannableNamesVector, self.detectorNamesVector, None, None, None, None, positionVector, detectorVector, None, "Panel Name", "I18 Custom SDP", "Header String", self.datafilename, 0)
        self.controller.update(None, sdp)


    # Stop the tfg and disable the detector
    #
    def stopTFG(self):
        #self.das.sendCommand("tfg init")
        pass


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

    def plot(self):
        newdata=self.getNorm(self.fluData)
        Plotter.plotImage("Data Vector",newdata)

    def createRGBFile(self):
        fid=open(self.rgbdatafilename,'w')
        mystr='row  column  i0  it  id  vortex'
        print >> fid,mystr
        fid.close()

    def writeToRGB(self,nx,ny,i0,it,id,flu):
        fid=open(self.rgbdatafilename,'a')
        print >> fid,nx,ny,str(i0).strip(),str(it).strip(),str(id).strip(),flu
        fid.close()


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

