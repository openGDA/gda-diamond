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
		self.closeValves()
		self.saveVoltages()
		self.setVoltages( self.vfmZeroVoltages, self.hfmZeroVoltages)
		self.setHotwaxsOff()
		# print positions of the motor in elog

	def wakeUp(self):
		self.openValves()
		vfmVoltages = self.readVoltages( self.VFM)
		hfmVoltages = self.readVoltages( self.HFM)
		self.setVoltages( vfmVoltages, hfmVoltages)
		self.setHotwaxsOn()
		
	def closeValves(self):
		print "Closing all valves"
		caput("BL22I-VA-VALVE-05:CON" , 1)
		caput("BL22I-VA-VALVE-04:CON" , 1)
		caput("BL22I-VA-VALVE-03:CON" , 1)
		caput("BL22I-VA-VALVE-02:CON" , 1)
		caput("BL22I-VA-VALVE-01:CON" , 1)
		print "All valves closed"

	def openValves(self):
		print "Opening all valves"
		caput("BL22I-VA-VALVE-05:CON",0)
		sleep(2)
		print "Valve 5 open"

		caput("BL22I-VA-FVALV-01:CON",3)
		sleep(2)
		print "Fast valve armed"
		
		caput("BL22I-VA-VALVE-04:CON",2)
		sleep(2)
		print "Interlocks reset for valve 4"
		caput("BL22I-VA-VALVE-04:CON",0)
		print "Valve 4 open"
		
		caput("BL22I-VA-VALVE-03:CON",0)
		print "Valve 3 open"

		caput("BL22I-VA-VALVE-02:CON",0)
		print "Valve 2 open"

		caput("BL22I-VA-VALVE-01:CON",0)
		print "Valve 1 open"
		print "All valves open"

	def saveVoltages(self):
		filename = self.directory+self.VFM+".dat"
		file = open(filename,"w")
		vfmVoltages = [] 
		vfmVoltages = vfm.getPosition()
		nVoltages = len(vfmVoltages)
		for i in range(nVoltages):
			file.write("%f\n" % (vfmVoltages[i]))
		file.close()
		print "Voltages of the VFM saved in "+filename
		filename = self.directory+self.HFM+".dat"

		file = open(filename,"w")
		hfmVoltages = [] 
		hfmVoltages = hfm.getPosition()
		nVoltages = len(hfmVoltages)
		for i in range(nVoltages):
			file.write("%f\n" % ( hfmVoltages[i]) )
		file.close()
		print "Voltages of the HFM saved in "+filename

	def readVoltages(self, type):
		filename = self.directory+self.VFM+".dat"
		if ( type == self.HFM ):
			filename = self.directory+self.HFM+".dat"
		input=open(filename,'r')
		lines=input.readlines()
		input.close()
		voltages=[]
		for values in lines:
			voltages.append(float(values))
		return voltages

	def setVoltages(self, vfmVoltages, hfmVoltages):
		print "Set voltages of the VFM to", vfmVoltages
		pos vfm vfmVoltages
		print "vfm: ", vfm.getPosition()
		#print "done for VFM"
		print "Set voltages of the HFM to", hfmVoltages
		pos hfm hfmVoltages
		print "hfm: ", hfm.getPosition()
		#print "done for HFM"

	def setHotwaxsOn(self):
		print "Set HOTWAXS high voltages ON"
		caput("BL22I-EA-ISEG-04:HWAX1:SET_V1_DEMAND", 200 )
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
		
	def isAwake(self):
		nDevices = 0
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
	
i22 = I22()