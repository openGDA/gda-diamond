from gda.device.scannable import  ScannableMotionBase
import time

class IppdetectorWithEnergySweep(ScannableMotionBase):
	"""
Expose detector ippdet, while energy is swept from energy_start
to energy_end. Provides tools to set/get the dcm crystal speed in
degrees per second, and getMovetime() to return how long the move will take
with the current settings.
	
To view results from last exposure:

	>>>ippws4en
	ippws4en : exp: 0 energy_start: 12000 energy_stop: 20000 speed: 0.38 file: N:/2009/mt1107-1/ippimages\2009-5-21\ipp3.TIF

To set start and stop energies:

	>>>ippws4en.energy_start=12000
	>>>ippws4en.energy_stop = 20000

To set and get speed of dcm motor (degrees/second):

	>>>ippws4en.getSpeed()
	0.38
	>>>ippws4en.setSpeed(.38)

To determine how long the move will take with the current settings:

	>>>ippws4en.getMoveTime()
	20.11400008201599

An example scan with dummy motors x and y:

	>>>scan x 1 2 1 y 3 4 1 ippws4en 20000
	Writing data to file:12491.dat
	x	y	exp	energy_start	energy_stop	speed	file
	1	3	20000	12000	20000	0.38	N:/2009/mt1107-1/ippimages\2009-5-21\ipp4.TIF
	1	4.0000	20000	12000	20000	0.38	N:/2009/mt1107-1/ippimages\2009-5-21\ipp5.TIF
	2.0000	3	20000	12000	20000	0.38	N:/2009/mt1107-1/ippimages\2009-5-21\ipp6.TIF
	2.0000	4.0000	20000	12000	20000	0.38	N:/2009/mt1107-1/ippimages\2009-5-21\ipp7.TIF
	Scan complete.
	"""

	def __init__(self, name, ippdet, energy, dcmspeed):
		self.name = name
		self.ippdet = ippdet
		self.energy = energy
		self.dcmspeed = dcmspeed
		self.setInputNames(['exp'])
		self.setExtraNames(['energy_start', 'energy_stop', 'speed', 'file'])
		self.setOutputFormat(["%.4f","%.4f", "%.4f","%.4f", "%s"])

		self.energy_start = 1000
		self.energy_stop = 2000
		self.last_energy_target = 0	
		self.last_exposure_time = 0

	def setSpeed(self,speed):
		self.dcmspeed.moveTo(speed)

	def getSpeed(self):
		return self.dcmspeed.getPosition()

	def getMoveTime(self):
		if self.last_energy_target ==  self.energy_stop:
			start = self.energy_stop
			stop = self.energy_start
		else:
			start = self.energy_start
			stop = self.energy_stop
		
		self.energy.moveTo(start)
		t = time.time()
		self.energy.moveTo(stop)
		return time.time() - t

	def isBusy(self):
		#return self.theta.isBusy() or self.ttheta.isBusy()
		return False

	def getPosition(self):
		return [self.last_exposure_time, self.energy_start, self.energy_stop, self.getSpeed(), self.ippdet.readout()]

	def asynchronousMoveTo(self,exp):

		if self.last_energy_target ==  self.energy_stop:
			start = self.energy_stop
			stop = self.energy_start
		else:
			start = self.energy_start
			stop = self.energy_stop


		self.energy.moveTo(start)

		self.energy.asynchronousMoveTo(stop)
		self.ippdet.moveTo(exp)

#		t = time.time()
#		too_slow_by = 0
#		while self.energy.isBusy():
#			too_slow_by = time.time() - t
#			time.sleep(.05)
#		if too_slow_by != 0:
#			print "<<< WARNING: After the %fs exposure completed, it took %fs for the energy move to complete" % (exp, too_slow_by)
			
		self.last_exposure_time = exp
		self.last_energy_target = stop
