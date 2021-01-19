from framework.script_utilities import userlog

def compute_gate(run_spec, time_to_velocity=0.5, shutter_delay=0.03, delta_index=0):
		''' 
			Parameters:
				run_spec a RunMetadata object derived from the Collect Request
				time_to_velocity in seconds
				shutter_delay in seconds
				delta_index the index of the oscillation to use, usually 0
			Compute:
				- pre-scan position of scan axis to allow for axis acceleration and shutter delay
				- gate open trigger position to feed to position compare to allow for scan speed and shutter delay
				- gate close trigger position to feed to position compare to allow for above adjustments
			run_spec parameters used:
				- direction
				- range
				- exposure
				- start
				- delta
				- numImages
		'''
		gate = ScanGate()
		gate.configure_gate(run_spec, time_to_velocity, shutter_delay, delta_index)
		return gate


class ScanGate():
	
	def __init__(self):
		self.direction = 1.0 # axis positive
		self.prescan = 0.0
		self.shutter_delay = 0.03 # seconds
		self.shutter_interval = 0.0
		self.shutter_open = 0.0 # position shutter gets open signal
		self.scan_start = 0.0
		self.scan_velocity = 0.0 # usually degrees/second
		self.scan_width = 0.0
		self.scan_exposure = 0.0
		self.axis_travel = 0.0
		self.axis_terminus = 0.0
		self.time_to_velocity = 0.5 # EPICS specifies this instead of acceleration


	def configure_gate(self, run_spec, time_to_velocity=0.5, shutter_delay=0.03, delta_index=0):
		''' 
			Parameters:
				run_spec a RunMetadata object derived from the Collect Request
				time_to_velocity in seconds
				shutter_delay in seconds
			Compute:
				- pre-scan position of scan axis to allow for axis acceleration and shutter delay
				- gate open trigger position to feed to position compare to allow for scan speed and shutter delay
				- gate close trigger position to feed to position compare to allow for above adjustments
		'''
		# calculate direction = math.sign(run_spec.imageRange) or similar # ? assumption or requirement
		self.direction = run_spec.direction()
		self.shutter_delay = shutter_delay
		self.scan_velocity = run_spec.range() / run_spec.exposure() # checked valid as precondition previously
		self.time_to_velocity = time_to_velocity
		# calculate acceleration_prescan = self.scan_velocity / time_to_velocity
		
		ramp_prescan_deg = 0.5 * self.scan_velocity * time_to_velocity
		shtr_prescan_deg = self.scan_velocity * shutter_delay # at constant velocity
		dist_prescan_deg = ramp_prescan_deg + shtr_prescan_deg # total prescan distance
		
		overshoot = max(
			ramp_prescan_deg, 
			ramp_prescan_deg + (self.shutter_delay - self.time_to_velocity) * self.scan_velocity)
		
		self.scan_start = run_spec.start()
		self.scan_width = run_spec.numImages() * run_spec.range()
		self.scan_exposure = run_spec.numImages() * run_spec.exposure()
		
		self.prescan = self.scan_start - self.direction * dist_prescan_deg
		self.shutter_interval = shtr_prescan_deg
		self.shutter_open = self.scan_start - self.direction * shtr_prescan_deg
		self.axis_travel = dist_prescan_deg + self.scan_width + overshoot
		self.axis_terminus = self.prescan + self.direction * self.axis_travel


	def log(self):
		userlog("direction %f" % self.direction)
		userlog("prescan %f" % self.prescan)
		userlog("shutter_delay %f" % self.shutter_delay)
		userlog("shutter_interval %f" % self.shutter_interval)
		userlog("shutter_open %f" % self.shutter_open)
		userlog("scan_start %f" % self.scan_start)
		userlog("scan_velocity %f" % self.scan_velocity)
		userlog("scan_width %f" % self.scan_width)
		userlog("scan_exposure %f" % self.scan_exposure)
		userlog("axis_travel %f" % self.axis_travel)
		userlog("axis_terminus %f" % self.axis_terminus)
		userlog("time_to_velocity %f" % self.time_to_velocity)
