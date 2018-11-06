""" #########################################################################################################
Scannable to control the SR 830 lock in amplifier

David Burn - 23/10/17

######################################################################################################### """


"""
Sensitivity
7: 500 nV/fA
8: 1 uV/pA
9: 2 uV/pA
10: 5 uV/pA
11: 10 uV/pA

Time Constant
10: 1s
11: 3s
12: 10s


Need to make sure RS232 is selected under the setup menu onj the instrument
"""



from gda.device.scannable import ScannableBase
from other_devices.rs232Device import rs232Device



class liaSensitivityScannable(ScannableBase):
	def __init__(self, rs232):
		self.name = "liaSens"
		self.setInputNames(["liaSens"])
		self.setOutputFormat(["%02d"])
		self.iambusy = 0 
		self.rs232 = rs232
		self.lookup = [2e-15, 5e-15, 10e-15, 20e-15, 50e-15,100e-15, 200e-15, 500e-15, 1e-12, 2e-12, 5e-12,
					10e-12, 20e-12, 50e-12, 100e-12, 200e-12, 500e-12, 1e-9, 2e-9, 5e-9, 10e-9, 20e-9, 50e-9,
					100e-9, 200e-9, 500e-9, 1e-6] # Lookup for current
		
		#self.lookup = [2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, 1e-6, 2e-6, 5e-6, 10e-6,
		#			20e-6, 50e-6, 100e-6, 200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 
		#			200e-3, 500e-3, 1] # Lookup for voltage

	def getPosition(self):
		return self.lookup[int(self.rs232.query("SENS?"))]

	def asynchronousMoveTo(self, value):
		self.iambusy = 1
		self.rs232.write("SENS %2d" % self.lookup.index(value))
		self.iambusy = 0

	def isBusy(self):
		return self.iambusy
	
	

class liaInputScannable(ScannableBase):
	def __init__(self, rs232):
		self.rs232 = rs232
		self.name = "liaInput"
		self.setInputNames(["liaInput"])
		self.setOutputFormat(["%1d"])
		self.iambusy = 0 
	
	def getPosition(self):
		return self.rs232.query("ISRC?")
	
	def asynchronousMoveTo(self, newPos):
		self.iambusy = 1
		self.rs232.write("ISRC %1d" % newPos)
		self.iambusy = 0

	def isBusy(self):
		return self.iambusy
	
	
	
class liaPhaseScannable(ScannableBase):
	def __init__(self, rs232):
		self.rs232 = rs232
		self.name = "liaPhase"
		self.setInputNames(["liaPhase"])
		self.setOutputFormat(["%3d"])
		self.iambusy = 0 
	
	def getPosition(self):
		return float(self.rs232.query("PHAS?"))
	
	def asynchronousMoveTo(self, newPos):
		self.iambusy = 1
		self.rs232.write("PHAS %3d" % newPos)
		self.iambusy = 0

	def isBusy(self):
		return self.iambusy

class liaFreqScannable(ScannableBase):
	def __init__(self, rs232):
		self.rs232 = rs232
		self.name = "liaFreq"
		self.setInputNames(["liaFreq"])
		self.setOutputFormat(["%3d"])
		self.iambusy = 0 
	
	def getPosition(self):
		return float(self.rs232.query("FREQ?"))
	
	def asynchronousMoveTo(self, newPos):
		self.iambusy = 1
		self.rs232.write("FREQ %3d" % newPos)
		self.iambusy = 0

	def isBusy(self):
		return self.iambusy










class sr830LIAScannable(ScannableBase):
	def __init__(self, name, branch, port):
		self.name = name
		self.setInputNames(["lia_sensitivity", "lia_time_constant", "lia_offset_x", "lia_offset_y"])
		self.setExtraNames([])
		self.setOutputFormat(["%02d","%02d", "%0.2f", "%0.2f"])
		self.iambusy = 0 

		self.rs232 = rs232Device(branch, port)
		self.rs232.setOutputTerminator("\r")
		self.rs232.setInputTerminator("\r")
		#9600 baud

		#self.setup()

	def getPosition(self):
		s = self.rs232.query("SENS?")		# sensitivity
		tc = self.rs232.query("OFLT?")		# time constant: 10=1s
		ox = self.rs232.query("OEXP? 1")		# X offset voltage
		ox = ox.split(',')[0]
		oy = self.rs232.query("OEXP? 2")		# Y offset voltage
		oy = oy.split(',')[0]
		return [s, tc, ox, oy]
		#return [0,0,0,0]
	
	def asynchronousMoveTo(self, values):
		self.iambusy = 1
		self.rs232.write("SENS %2d" % values[0])	# sensitivity
		self.rs232.write("OFLT %2d" % values[1])	# time constant: 10=1s
		self.rs232.write("OEXP 1, %0.2f, 0" % values[2])	# X offset voltage
		self.rs232.write("OEXP 2, %0.2f, 0" % values[3])	# Y offset voltage
		self.iambusy = 0

	def isBusy(self):
		return self.iambusy




	def setup(self):
		self.rs232.write("FMOD 1")			# use internal frequency
		self.rs232.write("FREQ %0.2f" % 700)		# set frequency

		self.rs232.write("HARM %1d" % 1)		# harmonic detection
		self.rs232.write("ISRC %1d" % 3)		# current mode with 10^8
		self.rs232.write("IGND %1d" % 0)		# input shield grounding: 0=float, 1=ground 
		self.rs232.write("ICPL %1d" % 0)		# input coupling: 0=AC, 1=DC 
		self.rs232.write("ILIN %1d" % 1)		# input line notch: 0=none, 1=1x, 2=2x, 3=both 

		self.rs232.write("SENS %2d" % 18)		# sensitivity
		self.rs232.write("RMOD %1d" % 0)		# reserve: 0=high, 1=normal, 2=minimum
		self.rs232.write("OFLT %2d" % 10)		# time constant: 10=1s
		self.rs232.write("OFSL %1d" % 3)		# low pass filter slope: 0=6dB/oct, 1=12dB/oct, 2=18dB/oct, 3=24dB/oct
		self.rs232.write("SYNC %1d" % 0)		# synchronous filtering: 0=off, 1=on

		self.rs232.write("DDEF 1,0,0")			# ch1 display X
		self.rs232.write("DDEF 2,0,0")			# ch1 display X

		self.rs232.write("FPOP 1,1")			# ch1 output X
		self.rs232.write("FPOP 2,1")			# ch1 output Y

		self.rs232.write("PHAS %02f" % -63.45)		# phase
