from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase
from time import sleep

class DelayLineClass(ScannableMotionBase):
    '''Create PD for single EPICS positioner which respond only to set and get'''
    def __init__(self, name, pvinstring, pvoutstring, pvieos, unitstring, formatstring, hlp=None):
        self.setName(name);
        if hlp is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+hlp
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(5)
        self.incli=CAClient(pvinstring)
        self.incli.configure()
        self.outcli=CAClient(pvoutstring)
        self.outcli.configure()
        self.pvieos=pvieos
        self.verbose = False

    def getPosition(self):
        t=CAClient()
        t.caput(self.pvieos,"\r\n")
        sleep(1)
        self.incli.caput('DEL?');
        sleep(1);
        s=self.outcli.caget();
        if self.verbose:
            print "Return: " + s; print;
        
        counts = float( s.lstrip("?DEL\\n\\r") );
        return counts;

    def asynchronousMoveTo(self,time):
        t3=CAClient()
        t3.caput(self.pvieos,"\n")
        sleep(1)
        temp2="DEL " + str(time);
        if self.verbose:
            print temp2;
        self.incli.caput(temp2)
        sleep(1)
        
    def isBusy(self):
        sleep(1)
        return False;

#print "Colby delay line Stage delay created" 
#exec("delay=None")
#delay=DelayLineClass('delay', 'BL06J-EA-USER-01:ASYN3.AOUT',
#    'BL06J-EA-USER-01:ASYN3.TINP', "BL06J-EA-USER-01:ASYN3.IEOS",
#    '%', '%.15f', 'GDA read of ITC T2')