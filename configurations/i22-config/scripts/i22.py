import java
import gda.device.scannable.ScannableBase

class I22(gda.device.scannable.PseudoDevice):

	def __init__(self):
		self.name = "i22"
		self.setInputNames(["i22"])
		self.status = "Awake"
		self.AWAKE = "Awake"
		self.SHUTDOWN = "Shutdown"
		self.HFM = "hfm"
		self.VFM = "vfm"
		
	def isBusy(self):
		return self.i22Busy

	def getPosition(self):
		return self.isAwake()

	def asynchronousMoveTo(self,status):
		if ( status != self.AWAKE and status != self.SHUTDOWN):
			print ("Choice are "+self.AWAKE+" or "+ self.SHUTDOWN)
		if ( status == self.AWAKE and self.isAwake() != self.AWAKE):
			self.status = self.AWAKE
			self.wakeUp()
		if ( status == self.SHUTDOWN and self.isAwake() != self.SHUTDOWN):
			self.status = self.SHUTDOWN
			self.shutdown()
		return

	def shutdown(self):
		valves.close()
		mirrorsVoltages.off()
		hotwaxs.off()
		# print positions of the motor in elog

	def wakeUp(self):
		valves.open()
		mirrorsVoltages.on()		
		#hotwaxs.on()

	def isAwake(self):
		status = valves.isAwake() and mirrorsVoltages.isOn(self.VFM) and mirrorsVoltages.isOn(self.HFM) and hotwaxs.isOn()
		if int(status) == 0:
			status = "SHUTDOWN"
			return status
		return "AWAKE"

class Valves():

	def __init__(self):
		v = []
		v.append("BL22I-VA-VALVE-05:CON")
		v.append("BL22I-VA-VALVE-04:CON")
		v.append("BL22I-VA-VALVE-03:CON")
		v.append("BL22I-VA-VALVE-02:CON")
		v.append("BL22I-VA-VALVE-01:CON")
		self.valves = v

	def close(self):
		print "Closing all valves"
		for i in self.valves:
			caput(i , 1)
		print "All valves closed"

	def open(self):
		print "Opening all valves"
		n = 5
		nValves = len(self.valves)
		for i in range (nValves):
			# reset the valves
			caput(self.valves[i],2)
			sleep(1)
			# open the valve
			caput(self.valves[i],0)
			sleep(1)
			print "Valve "+str(n)+" open"
			
			if ( i == 0):
				caput("BL22I-VA-FVALV-01:CON",3)
				sleep(1)
				print "Fast valve armed"
			n = n-1
		print "All valves open"

	def isAwake(self):
		for i in self.valves:
			# If close or reset, return "shutdown"
			if ( caget(i) != 0):
				return "Shutdown"
		return "Awake"

		
class MirrorsVoltages():

	def __init__(self):
		self.directory = "/dls/i22/scripts/voltages/"
		self.HFM = "hfm"
		self.VFM = "vfm"
		self.vfmZeroVoltages = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
		self.hfmZeroVoltages = [0.0,0.0,0.0,0.0,0.0,0.0]

	def save(self , name):
		filename = self.directory+name+".dat"
		file = open(filename,"w") 
		voltages = vfm.getPosition()
		if ( name == self.HFM):
			voltages = hfm.getPosition()
		nVoltages = len(voltages)
		for i in range(nVoltages):
			file.write("%f\n" % (voltages[i]))
		file.close()
		print "Voltages of the "+name+" saved in "+filename

	def read(self, name):
		filename = self.directory+self.VFM+".dat"
		if ( name == self.HFM ):
			filename = self.directory+self.HFM+".dat"
		input=open(filename,'r')
		lines=input.readlines()
		input.close()
		voltages=[]
		for values in lines:
			voltages.append(float(values))
		return voltages

	def set(self, name, voltages):
		if ( name == self.VFM ):
			print "Set voltages of the VFM to", voltages
			pos vfm voltages
			print "vfm: ", vfm.getPosition()
		if ( name == self.HFM):	
			print "Set voltages of the HFM to", voltages
			pos hfm voltages
			print "hfm: ", hfm.getPosition()

	def on(self):
		voltages = self.read(self.VFM)
		self.set(self.VFM , voltages)
		voltages = self.read(self.HFM)
		self.set(self.HFM , voltages)

	def off(self):
		self.save(self.VFM)
		self.save(self.HFM)
		self.set(self.VFM , self.vfmZeroVoltages)
		self.set(self.HFM , self.hfmZeroVoltages)

	def isOn(self , name):
		v = vfm.getPosition()
		if ( name == self.HFM):
			v = hfm.getPosition()
		nVoltages = len(v)
		n = 0
		for i in v:			
			if ( i == 0):
				n = n + 1
		# If all voltages at 0.0, return "shutdown"
		if ( n == nVoltages ):
			return "Shutdown"
		return "Awake"
		
valves = Valves()
mirrorsVoltages = MirrorsVoltages()
i22 = I22()