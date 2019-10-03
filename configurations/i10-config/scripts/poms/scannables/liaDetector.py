""" #########################################################################################################
Detector for saving lock in amplifier with ADC card, and for reading lia status with rs232
David Burn - 18/10/17
######################################################################################################### """


#from java.lang import Thread, Runnable
#from gda.jython import InterfaceProvider
#from gda.data import NumTracker
#from gda.jython import InterfaceProvider

from other_devices.rs232Device import rs232Device
from gda.device.detector import DetectorBase
from gda.jython import InterfaceProvider
import time

#ca = device()



class liaDetector(DetectorBase):
	def __init__(self, name):
		self.setName(name)
		self.setInputNames([])
		self.setExtraNames([])
		self.setOutputFormat([])
		self.isCollecting = 0 
		self.myData = 0

		self.rs232 = rs232Device(branch, port)
		self.rs232.setOutputTerminator("\r")
		self.rs232.setInputTerminator("\r")

	def collectData(self):     
		newThread = collectDataThread(self)
		t = Thread(newThread)
		t.start()

	def getStatus(self):
		return self.isCollecting

	def readout(self):    
		return True

	def getDataDimensions(self):
		return 1

	def createsOwnFiles(self):
		return False

	def atScanStart(self):
		pass

	def atPointStart(self):
		pass

	def stop(self):
	self.loop = False




	def writeDataToFile(self, data=[]):
		filenumber = NumTracker("i10").getCurrentFileNumber();
		filename = "i10-%06d-%s_%04d.dat"   % (filenumber, self.getName(), self.pointNum)
		print "writing file: " + filename
		waveformfilename=str(InterfaceProvider.getPathConstructor().createFromDefaultProperty())+"anritsu/"+filename
		datafile=open(waveformfilename, 'w')

		data = dnp.array(data,  dtype=dnp.float)
		data = dnp.transpose(data)
		datafile.write(" &END\n")
		datafile.write("freq\ts12\ts21\ts11\ts22"'\n')

		for line in data:
		    s = "".join("%10.5g\t" % x for x in line[0])
		    datafile.write(s+'\n')
		datafile.flush()
		datafile.close()
		return waveformfilename











	def query(self, message):
		self.sock.send(str.encode(message+"\n"))
		return self.sock.recv(2056)

	def write(self, message):
		self.sock.send(str.encode(message+"\n"))


	def setup(self):
		""" display layout settings """
		self.write("CALCulate1:PARameter1:DEFine S11")
		self.write("CALCulate1:PARameter1:FORMat MLOGarithmic")

		self.write("CALCulate1:PARameter2:DEFine S21")
		self.write("CALCulate1:PARameter2:FORMat MLOGarithmic")

		self.write("CALCulate1:PARameter3:DEFine S22")
		self.write("CALCulate1:PARameter3:FORMat MLOGarithmic")

		self.write("CALCulate1:PARameter4:DEFine S12")
		self.write("CALCulate1:PARameter4:FORMat MLOGarithmic")

		self.write("SENSe:HOLD:FUNCtion HOLD")		# single sweep and hold

		""" data transfer settings """
		self.write(":FORMat:DATA REAL")				# ASC, REAL or REAL32
		self.write(":FORMat:BORDer SWAP")			# MSB/LSB: Normal or Swapped


		
		self.setFrequency(0.1,8)
		self.setNumPoints(2048)
		self.setBandwidth(500) 


	def getData(self):
		s11 = self.getTrace(1)	#S11
		s21 = self.getTrace(2)	#S21
		s22 = self.getTrace(3)	#S22
		s12 = self.getTrace(4)	#S12
		return [s12,s21,s11,s22]

 



	def getTrace(self, par):
		# floating point with 8 bytes / 64 bits per number
		#self.write("SYST:ERR:CLE")
		#print self.query("*OPC?")

		#print self.query("SYST:ERR?")				#returns "No Error"

		self.write(":CALC:PAR%1d:DATA:SDAT?" % par)
		#self.write(":CALC:DATA:SDAT?")	#works
		head =  self.sock.recv(2)				# header part 1
		head =  self.sock.recv(int(head[1]))			# header part 2
		MSGLEN = int(head)			# extrace message len from header

		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN:
			chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
			chunks.append(chunk)
			bytes_recd = bytes_recd + len(chunk)
		data = ''.join(chunks)

		extra = self.sock.recv(2048)
		#print len(extra)
		#print chr(extra)

		#print len(data), " bytes, ", len(data)/8, " numbers"

		num = len(data) / 8
		[data,] = struct.unpack('%dd' % num, data),
		
		#return [np.array(data[::2]), np.array(data[1::2]) ]

		return  np.array(data[::2])   + np.array(data[1::2])*1j



	def getFrequency(self):
		self.write("SYST:ERR:CLE")

		self.write(":SENSe:FREQuency:DATA?")
		head =  self.sock.recv(2)				# header part 1
		head =  self.sock.recv(int(head[1]))			# header part 2
		MSGLEN = int(head)			# extrace message len from header

		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN:
			chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
			chunks.append(chunk)
			bytes_recd = bytes_recd + len(chunk)
		data = ''.join(chunks)

		#print len(data), " bytes, ", len(data)/8, " numbers"

		extra = self.sock.recv(2048)

		num = len(data) / 8
		[data,] = struct.unpack('%dd' % num, data),
		return np.array(data)/1e9


	def doSweep(self):
		self.write("SYST:ERR:CLE")
		opc = self.query("*OPC?")
		print "opc ", opc

		self.write("TRIG:SING")
		# there is a wait here until anritsu has finished collecting
		err = self.query("SYST:ERR?")
		print "err ", err



	def setFrequency(self, start, stop):
		""" frequency settings """
		start = start*1.0e9
		stop = stop*1.0e9
		self.write("SENS:FREQ:STAR %d" % start)
		self.write("SENS:FREQ:STOP %d" % stop)



	def setBandwidth(self,bandwidth):
		self.bandwidth = bandwidth
		self.write("SENS:BAND %6d" % bandwidth)				# IFBW Frequency (Hz)

	def setNumPoints(self,num):
		self.write("SENS:SWEEP:POINT %4d" % num)



########################################################################################################
########################################################################################################
########################################################################################################





class collectDataThread(Runnable):
	def __init__(self, theDetector):
		self.myDetector = theDetector
                
	def run(self):
		self.myDetector.isCollecting = 1
        
        	self.doSweep()

		freq = self.getFrequency()
		s12,s21,s11,s22 = self.getTrace()

		self.myDetector.writeDataToFile([freq, s12, s21, s11, s22])



        """
        if self.myDetector.showWaveforms:
            x = dnp.arange(len(wai1))
            dnp.plot.clear(name="Plot 2")
            dnp.plot.line(x,wai1, name="Plot 2")
            dnp.plot.addline(x,wai2, name="Plot 2")
            dnp.plot.addline(x,wai3, name="Plot 2")
            self.myDetector.plotBins()
        
        
        if self.myDetector.showMH:
            dnp.plot.clear()
            dnp.plot.line(wai1,wai2)
	"""
        
      
	self.myDetector.isCollecting = 0






########################################################################################################
########################################################################################################
########################################################################################################





		




