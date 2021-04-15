'''
Module defines a Struck SIS3820 Scaler class to support extended counting time above 
the 80 seconds limit provided in the simple Scaler mode (constrained by the internal
clock). It uses the MCA mode and can count up to (Dwell time * Number of Bins) second.
The default or maximum number of bins in the Diamond's card is 8192 in EPICS. 

Instance of this class is not configured on instantiation. Configuration and initialisation
of instance of this class will take place on first use either in a scan or any query on it. 
Usage:
    1. create an object:
        Io = LongCountTimeScaler("Io","BL12I-EA-DET-01:SCALER","BL12I-EA-DET-01:MCA-01",17,0.1)
    2. use Io in scan command or interactively on command line.
    3. To use Io alone (not in a scan command), you must initialise it first by running
        Io.setupMCAMode();
        
Created on 4 Nov 2010

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class LongCountTimeScaler(ScannableMotionBase):
    '''
    Jython class definition for a Struck SIS3820 Scaler to support extended counting 
    time above the 80 seconds limit provided in the simple Scaler mode.
    '''
    def __init__(self, name, pv_scaler, pv_mca, channelNumber, dwelltime):
        '''
        Constructor - creates a pseudo device (pd) for  a single change, long counting 
        duration (>80s) scaler.
        inputs:
            1. name of this pseudo device
            2. the scaler PV
            3. the MCA PV
            4. the channel number of the scaler card used
            5. the integration or latch time for each element in the array
        '''
        self.channelNumber = channelNumber
        self.setName(name) 
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5g"])
        self.setLevel(5)
        self.countModeCh = CAClient(pv_scaler + ".CONT")
        self.countControlCh = CAClient(pv_scaler + ".CNT")
        self.mcaStopCh = CAClient(pv_mca + ":StopAll")
        self.mcaNoBins = CAClient(pv_mca + ":NuseAll")
        self.mcaR0LO = CAClient(pv_mca + ":mca" + str(channelNumber)+".R0LO")
        self.mcaR0HI = CAClient(pv_mca + ":mca" + str(channelNumber)+".R0HI")
        self.mcaDwell = CAClient(pv_mca + ":Dwell")
        self.mcaCountTime = CAClient(pv_mca+":PresetReal")
        self.mcaEraseStart= CAClient(pv_mca+":EraseStart")
        self.mcaR0 = CAClient(pv_mca + ":mca" + str(channelNumber)+".R0")
        self.mcaStatus = CAClient(pv_mca + ":Acquiring")
        self.nbins = 0
        self.dwelltime = dwelltime
        self.configured = False
        self.initialsed = False
    
    def configure(self):
        '''
        setup EPICS connections for the scaler.
        '''
        if not self.configured:
            try : 
                if not self.countModeCh.isConfigured():
                    self.countModeCh.configure()
                if not self.countControlCh.isConfigured():
                    self.countControlCh.configure()
                if not self.mcaStopCh.isConfigured():
                    self.mcaStopCh.configure()
                if not self.mcaNoBins.isConfigured():
                    self.mcaNoBins.configure()
                if not self.mcaR0LO.isConfigured():
                    self.mcaR0LO.configure()
                if not self.mcaR0HI.isConfigured():
                    self.mcaR0HI.configure()
                if not self.mcaDwell.isConfigured():
                    self.mcaDwell.configure()
                if not self.mcaCountTime.isConfigured():
                    self.mcaCountTime.configure()
                if not self.mcaEraseStart.isConfigured():
                    self.mcaEraseStart.configure()
                if not self.mcaR0.isConfigured():
                    self.mcaR0.configure()
                if not self.mcaStatus.isConfigured():
                    self.mcaStatus.configure()
                self.configured = True
            except Exception, value:
                print "configure ", self.getName(), " failed:", value
        
    def atScanStart(self):
        if not self.configured:
            self.configure()
        if not self.initialsed:
            self.setupMCAmode()
            
    def setupMCAmode(self):
        '''
        initialise and setup the MCA mode for the scaler.
        '''
        if not self.configured:
            self.configure()
        try: 
            # Stop the simple scaler mode 
            self.countControlCh.caput(0)
            self.countModeCh.caput(0)
            # Stop MCA mode in case it was running
            self.mcaStopCh.caput(1)
            # get the number of bins (i.e. the length of the array)
            self.nbins = float(self.mcaNoBins.caget())
            print "  Max number of bins     = %d"%self.nbins
            # Set the ROI - which part of the array to sum all elements in.
            roi_low  = 0
            roi_high = int(self.nbins-1)
            self.mcaR0LO.caput(roi_low)
            self.mcaR0HI.caput(roi_high)
            print "  ROI high=%d low=%d"%(roi_high, roi_low)
            # Setup the timing: Three parameters need to be setup in a complient fashion:
            #    Dwell time (integration time between each latch)
            #    Count Time (how long to count for overall)
            #    Number of bins (how many elements to use in the array) Default/Max is 8192          
            # Set the 'Dwell Time' in seconds. This is the counting time for each element of the array.
            # As an example we set dwell time = 0.1s
            # With nbins=8192 that means we can count of a total of: 0.1 * 8192 = 819.2s
            self.mcaDwell.caput(self.dwelltime)
            # Just a bit of messages printed for user info and debugging
            print "  Integration/latch time = %.3fs"%self.dwelltime
            
            self.initialsed = True
        except Exception, value:
            print "Failed to setup the MCA mode for",self.getName(), ":",value
    
    def rawGetPosition(self):
        ''' returns the total counts '''
        if not self.configured:
            self.configure()
        if not self.initialsed:
            self.setupMCAmode()
        count=0
        try:
            count = float(self.mcaR0.caget())
        except Exception, value:
            print "Failed to get count value from ",self.getName(), value
        return count
    
    def rawAsynchronousMoveTo(self, countingtime):
        '''set total counting time and start counting '''
        if not self.configured:
            self.configure()
        if not self.initialsed:
            self.setupMCAmode()
        if countingtime > self.getMaxCountingTime():
            print "Counting time %.3fs is greater than MAX allowed %.3fs." %(countingtime, self.getMaxCountingTime())
            return
        try:
            self.mcaCountTime.caput(countingtime)
            self.mcaEraseStart.caput(1)
        except Exception, value:
            print "Failed to set Counting time or start counting on ",self.getName(), value
                    
        
    def isBusy(self):
        if not self.configured:
            self.configure()
        if not self.initialsed:
            self.setupMCAmode()
        busy = 0
        try:
            busy = int(self.mcaStatus.caget())
        except Exception, value:
            print "Failed to get MCA Mode status on ",self.getName(), value
        return busy==1
        
    def getMaxCountingTime(self):
        '''returns the maximum counting time of the object'''
        if not self.configured:
            self.configure()
        if not self.initialsed:
            self.setupMCAmode()
        return self.nbins * self.dwelltime
    
    def setMaxCountingTime(self, timeInSeconds):
        '''sets the maximum counting time of the object'''
        if not self.configured:
            self.configure()
        if not self.initialsed:
            self.setupMCAmode()
        self.dwelltime = timeInSeconds/self.nbins
        try:
            self.mcaDwell.caput(self.dwelltime)
        except Exception, value:
            print "Failed to set Dwell Time on ",self.getName(), value
            
    def getDwellTime(self):
        '''returns the device's integration or latch time'''
        if not self.configured:
            self.configure()
        if not self.initialsed:
            self.setupMCAmode()
        dwell = 0.0
        try:
            dwell = float(self.mcaDwell.caget())
        except Exception, value:
            print "Failed to get Dwell time from ",self.getName(), value
        return dwell
    
    def setDwellTime(self, dwelltime):
        '''sets the device's integration or latch time'''
        if not self.configured:
            self.configure()
        if not self.initialsed:
            self.setupMCAmode()
        self.dwelltime = dwelltime
        try:
            self.mcaDwell.caput(self.dwelltime)
        except Exception, value:
            print "Failed to set Dwell Time on ",self.getName(), value
        
    def getChannelNumber(self):
        return self.channelNumber
    
    def atScanEnd(self):
        pass
    
        