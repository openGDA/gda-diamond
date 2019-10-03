'''
file: gatedpixium.py
This module defines a gated pixium class that works with gated theta motion mode. 
In this mode, the data collection is driven by output signal from the pixium detector, which is high when exposing 
and low when writes data out. The theta motor moves when pixium is counting and stops when pixium is writing files.
It collects image data from pixium and position data from rotation motor. 

It maps onto EPICS "Theta gated Motion" screen and captures the rising and falling edge positions of the theta motor as well as enable 
and configure the process. On the 1st falling edge following enable, it must set the motor demand to start the acquisition.
The motor positions must be captured to a data file with corresponding image file name.

Created on 6 Dec 2011 for pixium driven acquisition.

@author: fy65
'''
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from positioncapturer import PositionCapturer
from gatedtheta import GatedTheta
from gda.device.scannable import ScannableMotionBase
from java.io import File
from gdascripts.utils import caget
from time import sleep

class GatedPixium(ScannableMotionBase):
    '''this object requires pixium output signal to drive theta rotation motor and collect images while motor moves
and write images out when motor stops. It takes pixium detector and rotation theta scannable as input.
    '''
    def __init__(self, name, pixium, theta):
        self.setName(name)
        self.setInputNames([])
        self.pixium=pixium
        self.theta=theta
        self.risingedge=PositionCapturer("risingedgecapturer", "BL12I-MO-TAB-02:ST1:PAUSE:RELATCH")
        self.fallingedge=PositionCapturer("fallingedgecapturer","BL12I-MO-TAB-02:ST1:PAUSE:FELATCH")
        self.cyclesdone=PositionCapturer("cyclesdonecapturer","BL12I-MO-TAB-02:ST1:PAUSE:EDGE:COUNTER:RBV")
        self.thetastarter=GatedTheta("thetastarter",pixium,theta,"BL12I-MO-TAB-02:ST1:PAUSE:RUNMODE","BL12I-MO-TAB-02:ST1:PAUSE:NUMPULSES","BL12I-MO-TAB-02:ST1:PAUSE:BUSY","BL12I-MO-TAB-02:ST1:PAUSE:EDGE:RBV")

    def start(self, num=180, startpos=0, endpos=180):
        '''start data collection - configure theta gated motion, start data capture monitor
        On completion, save data to a file using number tracker utility
        '''
        velocity = float(caget("BL12I-MO-TAB-02:ST1:THETA.VELO"))
        exposuretime=float(caget("BL12I-EA-DET-05:PIX:AcquireTime_RBV"))
        acquireperiod = float(caget("BL12I-EA-DET-05:PIX:AcquirePeriod_RBV"))

        avgvelo = velocity * (exposuretime / acquireperiod)

        timeout = (endpos-startpos)/avgvelo

        # add 50% fudge factor timeout
        timeout = 1.5*timeout

        #configure theta gated motion
        self.thetastarter.setMultipleMode()
        self.thetastarter.setNumberOfCycles(num)
    
        scanNumTracker = NumTracker("i12");
        directory=InterfaceProvider.getPathConstructor().createFromDefaultProperty()
        scanNumber=scanNumTracker.getCurrentFileNumber()
        self.risingedge.setFilename(directory+File.separator+(str(scanNumber+1)))
        self.fallingedge.setFilename(directory+File.separator+(str(scanNumber+1)))
        self.cyclesdone.setFilename(directory+File.separator+(str(scanNumber+1)))
    #configure position capturer
        self.risingedge.reset()
        self.risingedge.setNumberOfCycles(num)
        self.risingedge.addMonitor(1)
        self.fallingedge.reset()
        self.fallingedge.setNumberOfCycles(num)
        self.fallingedge.addMonitor(1)
        self.cyclesdone.reset()
        self.cyclesdone.setNumberOfCycles(num)
        self.cyclesdone.addMonitor(1)
        
        self.thetastarter.setTargetPosition(endpos)
        self.thetastarter.addMonitor(1)
        
        print "move ss1_theta to start position %f\n" % (startpos)
        self.thetastarter.moveTo(startpos)
        sleep(5)
        
        #setup file name 
    
        print "starts data collection ..."
        try:
            self.thetastarter.enable(timeout)
        except:
            raise
        finally:
            sleep(float(self.pixium.getAcquirePeriod()))
            self.save(directory+File.separator+(str(scanNumber+1))+"_"+self.getName()+".dat")
            print "collection completed "
            self.risingedge.removeMonitor()        # ensure monitor removed
            self.fallingedge.removeMonitor()        # ensure monitor removed
            self.cyclesdone.removeMonitor()        # ensure monitor removed
            self.thetastarter.removeMonitor()
    
    def save(self, filename):
        print "%s: saving position data to %s" % (self.getName(), filename)
        file=open(filename, "a")
        for counter, rise, fall in zip(self.cyclesdone.getData(), self.risingedge.getData(), self.fallingedge.getData()):
            file.write("%d\t%f\t%f\n"%(counter, rise, fall))
        file.close()
            
    def stop(self):
        '''stop data collection - remove data capturers, stop motor and detector acquisition
        '''
        self.thetastarter.disable()
        self.risingedge.removeMonitor()        # ensure monitor removed
        self.fallingedge.removeMonitor()        # ensure monitor removed
        self.cyclesdone.removeMonitor()        # ensure monitor removed
        self.thetastarter.removeMonitor()
        self.theta.stop() #@UndefinedVariable
        self.pixium.stop() #@UndefinedVariable

gpix=GatedPixium("gpix", pixium, ss1_theta) #@UndefinedVariable