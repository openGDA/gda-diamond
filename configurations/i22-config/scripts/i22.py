import java
import gda.device.scannable.ScannableBase

class I22(gda.device.scannable.PseudoDevice):

	def __init__(self):
		self.name = "i22"
		self.setInputNames(["i22"])
		self.i22Busy = 0
		self.status = "Awake"
		self.vfmZeroVoltages = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
		self.hfmZeroVoltages = [0.0,0.0,0.0,0.0,0.0,0.0]
		self.AWAKE = "Awake"
		self.SHUTDOWN = "Shutdown"
		self.directory = "/dls/i22/scripts/voltages/"
		self.HFM = "hfm"
		self.VFM = "vfm"
		
	def isBusy(self):
		return self.i22Busy

	def getPosition(self):
		return self.isAwake()

	def asynchronousMoveTo(self,status):
		if ( status != self.AWAKE and status != self.SHUTDOWN):
			raise DeviceException("Choice are "+self.AWAKE+" or "+ self.SHUTDOWN)
		self.i22Busy = 1
		if ( status == self.AWAKE and self.isAwake() != self.AWAKE):
			self.status = self.AWAKE
			self.wakeUp()
		if ( status == self.SHUTDOWN and self.isAwake() != self.SHUTDOWN):
			self.status = self.SHUTDOWN
			self.shutdown()
		self.i22Busy = 0	
		return

	def shutdown(self):
		valves.close()
		mirrorsVoltages.off()
		self.setHotwaxsOff()
		# print positions of the motor in elog

	def wakeUp(self):
		valves.open()
		vfmVoltages = mirrorsVoltages.on()
		
		self.setHotwaxsOn()

	def isAwake(self):
		valvesAwake = valves.isAwake()
		vfmAwake = mirrorsVolates.isOn(self.VFM)
		hfmAwake = mirrorsVolates.isOn(self.HFM)
		
		nAwake = 0
		if ( caget("BL22I-VA-VALVE-05:CON") == 0):
			nAwake = nAwake+1
			nDevices = nDevices + 1
		if ( caget("BL22I-VA-VALVE-04:CON") == 0):
			nAwake = nAwake+1
			nDevices = nDevices + 1 
		if ( caget("BL22I-VA-VALVE-03:CON") == 0):
			nAwake = nAwake+1
			nDevices = nDevices + 1
		if ( caget("BL22I-VA-VALVE-02:CON") == 0):
			nAwake = nAwake+1
			nDevices = nDevices + 1
		if ( caget("BL22I-VA-VALVE-01:CON") == 0):
			nAwake = nAwake+1
			nDevices = nDevices + 1

		voltages = vfm.getPosition()
		nVoltages = len(voltages)
		for i in range(nVoltages):
			if ( voltages[i] != 0.0)
				nAwake=nAwake+1
			nDevices = nDevices + 1
			
		voltages = hfm.getPosition()
		nVoltages = len(voltages)
		for i in range(nVoltages):
			if ( voltages[i] != 0.0)
				nAwake=nAwake+1
			nDevices = nDevices + 1
			
		if ( caget("BL22I-EA-ISEG-04:HWAX1:V1_ACTUAL") != 0.0):
			nAwake = nAwake+1
			nDevices = nDevices + 1
		if ( caget("BL22I-EA-ISEG-04:HWAX1:V2_ACTUAL") != 0.0):
			nAwake = nAwake+1
			nDevices = nDevices + 1
		if ( caget("BL22I-EA-ISEG-05:HWAX1:V1_ACTUAL") != 0.0):
			nAwake = nAwake+1
			nDevices = nDevices + 1
		if ( caget("BL22I-EA-ISEG-05:HWAX1:V2_ACTUAL") != 0.0):
			nAwake = nAwake+1
			nDevices = nDevices + 1
		
		ratio = nAwake/nDevices
		if ( ratio == 1 ):
			return self.AWAKE
		if ( ratio == 0 ):
			return self.SHUTDOWN
		return "Drowsy"

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
			caput(self.valves[i] , 1)
		print "All valves closed"

	def open(self):
		print "Opening all valves"
		for i in self.valves:
			# reset the valves
			caput(self.valves[i],2)
			# open the valve
			caput(self.valves[i],0)
			sleep(2)
			print "Valve "+str(5-i)+" open"
			
			if ( i == self.valves[0]):
				caput("BL22I-VA-FVALV-01:CON",3)
				sleep(2)
				print "Fast valve armed"

		print "All valves open"

	def isAwake(self):
		for i in self.valves:
			# If close or reset, return "shutdown"
			if ( caget(self.valves) != 0):
				return "Shutdown"
		return "Awake"

		
class MirrorsVoltages():

	def init(self):	
		self.directory = "/dls/i22/scripts/voltages/"
		self.HFM = "hfm"
		self.VFM = "vfm"

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
			print "Set voltages of the VFM to", vfmVoltages
			pos vfm vfmVoltages
			print "vfm: ", vfm.getPosition()
		if ( name == self.HFM):	
			print "Set voltages of the HFM to", hfmVoltages
			pos hfm hfmVoltages
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
			if ( v[i] == 0):
				n = n + 1
		# If all voltages at 0.0, return "shutdown"
		if ( n == nVoltages ):
			return "Shutdown"
		return "Awake"
		
class Hotwaxs():

	def init(self):	
		self.cathodes = "BL22I-EA-HV-01:"
		self.cathodesRBV = "BL22I-EA-HV-01:STAT0:RBV"
		self.windowRBV = "BL22I-EA-HV-01:STAT1:RBV"
		self.sideRBV = "BL22I-EA-HV-01:STAT2:RBV"
		self.driftRBV = "BL22I-EA-HV-01:STAT3:RBV"
		
	def on(self):
		print "Set HOTWAXS high voltages ON"
		if ( self.cathodes+"STAT0:RBV"
		caput(self.cathodes, 200 )
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V2_DEMAND", 600 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V1_DEMAND", 600 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V2_DEMAND", 1200 )
		caput("BL22I-EA-ISEG-04:HWAX1:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-04:HWAX1:V2_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V2_START" , "ON" )
		sleep(15)
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V1_DEMAND", 400 )
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V2_DEMAND", 1200 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V1_DEMAND", 1200 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V2_DEMAND", 2400 )
		caput("BL22I-EA-ISEG-04:HWAX1:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-04:HWAX1:V2_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V2_START" , "ON" )
		sleep(15)
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V1_DEMAND", 470 )
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V2_DEMAND", 1500 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V1_DEMAND", 1500 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V2_DEMAND", 3000 )
		caput("BL22I-EA-ISEG-04:HWAX1:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-04:HWAX1:V2_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V2_START" , "ON" )
		sleep(15)
	
	def setCathodes(self , voltage):		
		pvSet = self.cathodes+"VSET0"
		pvRBV = self.cathodes+"STAT0:RBV"
		if ( caget(pvRBV+".BA") == 1 ):
			print "Power supply OFF"
		caput(pvSet , voltage)
		print "Cathodes: "+str(voltage)+"V"
		
	def setHotwaxsOff(self):
		print "Set HOTWAXS high voltages OFF"
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V1_DEMAND", 400 )
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V2_DEMAND", 1200 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V1_DEMAND", 1200 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V2_DEMAND", 2400 )
		caput("BL22I-EA-ISEG-04:HWAX1:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-04:HWAX1:V2_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V2_START" , "ON" )
		sleep(15)
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V1_DEMAND", 200 )
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V2_DEMAND", 600 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V1_DEMAND", 600 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V2_DEMAND", 1200 )
		caput("BL22I-EA-ISEG-04:HWAX1:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-04:HWAX1:V2_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V2_START" , "ON" )
		sleep(15)
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V1_DEMAND", 0 )
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V2_DEMAND", 0 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V1_DEMAND", 0 )
		caput("BL22I-EA-ISEG-05:HWAX2:SET_V2_DEMAND", 0 )
		caput("BL22I-EA-ISEG-04:HWAX1:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-04:HWAX1:V2_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V1_START" , "ON" )
		caput("BL22I-EA-ISEG-05:HWAX2:V2_START" , "ON" )
		sleep(15)
		
class HotWaxsVoltages(gda.device.scannable.PseudoDevice):
	
	def init(self , name):	
		self.pvName = name
		self.pvSet = self.pvName+"VSET0"
		self.pvEnabled = self.pvName+"STAT0:RBV.BA"
		self.readout = self.pvName+"VMONO:RBV"
		self.rampUp = self.pvName+"STAT0:RBV.1"
		self.rampDown = self.pvName+"STAT0:RBV.2"

	def isBusy(self):
		return self.bragg.isBusy()

	def getPosition(self):
		""" Return the keV value"""
		X=float(self.bragg.getPosition())
		exp = X / self.coefficient 
		return 12.3985/(6.2712*sin(exp*3.14159265/180)) 

	def asynchronousMoveTo(self,X):
		""" Moves to the keV value supplied """
		self.bragg.asynchronousMoveTo(180/3.14159265*asin(12.3985/(X*6.2712))*self.coefficient)

valves = Valves()
mirrorsVoltages = MirrorsVoltages()
i22 = I22()