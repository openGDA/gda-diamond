#copied from /dls/b16/scripts as i12_Topup_pause 
#modified to have a hard topup pause time: self.minTopupTime 
from gda.device.scannable import ScannableMotionBase 
#from gda.util import * 
from gdascripts.utils import caget 
from time import sleep 
 
# class to pause during the topup 
class TopupPause(ScannableMotionBase):  
    def __init__(self,name): 
        self.minTopupTime = 4 #minimum topup time, at which this scannable will pause 
        self.stabilitytime = 2 
        self.name = name 
        self.setInputNames([]) 
        self.setExtraNames(["Topup"]) 
        self.setOutputFormat(["%5.5g"]) 
        self.result = 0; 
        self.countdownName="SR-CS-FILL-01:COUNTDOWN"
        self.shutterName="FE12I-PS-SHTR-02:STA"
        #self.shutterName="BL12I-EA-DIO-01:OUT:00"
        self.stopcalled = 0
        self.busy1 = False
        
        # set up the passed in parameters 
    def asynchronousMoveTo(self, position): 
        self.busy1 = True
        self.stopcalled=0
        # dosent need to do anything 
        self.minTopupTime = position 
         
        # here is where we would need to pause if the beam curent is zero. 
        try :
            self.timeLeft = float(caget(self.countdownName))
        except :
            self.timeLeft = 0; 
        # set a flag to trigger if the topup is about to be proformed 
        self.hasPaused = 0 
        # the while loop is overcautious, just in case something takes slightly longer then expected. 
        counter = -1 
         
        try :
            self.shutter = int(caget(self.shutterName)) 
        except :
            self.shutter = 0
            
        while ((self.timeLeft < self.minTopupTime) or (self.shutter > 2 )) : 
            if(self.stopcalled == 1) :
                return
            counter += 1 
            if (counter%10)==0: 
                if (self.shutter > 2) : 
                    print "pausing as main shutter closed" 
                    sleep(10) 
                else : 
                    print "Pausing for Topup"     #print out a message every 1 sec or so 
                    sleep(self.timeLeft+1.1) 
                     
            # set the flag so that the output can be set up correctly 
            self.hasPaused = 1 
            
            # get the next point, so we can exit the loop 
            try:
                self.timeLeft = float(caget(self.countdownName)) 
                self.shutter = int(caget(self.shutterName)) 
            except :
                self.timeLeft = 0
                self.shutter = 0
 
        if(self.hasPaused == 0) : 
 
            # if there was no pause then just return 0, all is well 
            self.result = [self.timeLeft] 
        else: 
            print "Topup Complete, pausing for stability" 
             
            sleep(self.stabilitytime) 
 
            print "Beam stable, continuing scan" 
            # Continue with the scan, but show a topup has occured 
            self.result = [-1.0] 
        self.busy1 = False
         
    def isBusy(self): 
        return self.busy1  
     
    def getPosition(self): 
        return self.result 
    
    def stop(self):
        self.stopcalled=1
        self.busy = False
        
