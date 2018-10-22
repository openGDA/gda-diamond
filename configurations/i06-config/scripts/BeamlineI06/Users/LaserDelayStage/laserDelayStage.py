
from time import sleep
import math;

from gda.epics import CAClient 
from gda.device.scannable import PseudoDevice

class LaserMotorClass(PseudoDevice):
	'''Create PD for single EPICS positioner which respond only to set and get'''
	def __init__(self, name, pvinstring, pvoutstring, unitstring, formatstring,help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)
		self.incli=CAClient(pvinstring)
		self.incli.configure()
		self.outcli=CAClient(pvoutstring)
		self.outcli.configure()
		
	def getPosition(self):
		self.incli.caput('TP')
		sleep(0.5)
		s=self.outcli.caget()
		#print "getPos: " + s
		c=299792548;
		a=250*pow(12.0/28.0,4);
		counts = float(s[s.find(':')+1:len(s)])
		time = -1000*counts*2*a/c
		return time

	def asynchronousMoveTo(self,time):
		c=299792548;
		a=250*pow(12.0/28.0,4);
		counts= -round(c*time/(2*a)*0.001);
		temp=str(int(counts));
		temp2="MA" + temp;
		#print temp2
		self.incli.caput(temp2)
		sleep(0.5)

	def isBusy(self):
		self.incli.caput('TE')
		sleep(0.5)
		s=self.outcli.caget()
		#print "isBusy: " + s
		sleep(0.5)
		return abs(float(s[s.find(':')+1:len(s)])) > 150

	def zero(self):
		self.incli.caput('DH') 

print "Laser Delay Stage 'lasmot' created" 
lasmot=LaserMotorClass('lasmot','BL06I-EA-USER-01:ASYN1.AOUT','BL06I-EA-USER-01:ASYN1.TINP','%','%.0f',help='GDA control of Laser motor')
 

print "Enable the I06 delay stage timing control by using scannable lastim";
#dgap = CorrespondentDeviceClass("dgap", 0.0, 1000.0, "testMotor1","s4_x_ygap", "s4_ygap_x");
lastim = CorrespondentDeviceClass("lastim", -200.0, 200.0, "lasmot","stepToTime", "timeToStep");

a = 250.0 * (12.0/28.0)**4;
c = 299792456.0;
#Calculate the delay time in pico second from the motor steps
#input: motor steps
#output: time delay in pico second
def stepToTime(step):
	t = 2.0*a*step*1000/c;
	return t;

#Calculate the motor steps from the delay time required
#input: time delay in pico second
#output: motor steps
def timeToStep(t):
	step = (t*c)/(2.0*a*1000);
	return step;
