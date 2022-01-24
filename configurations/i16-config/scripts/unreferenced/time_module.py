import time

class time_module:
	def __init__(self):
		self.start=time.time()

	def __repr__(self):
		return str((time.time()-self.start))

	def reset(self):
		self.start=time.time()


#	def getCPUclocks(self):
#		return (time.clock()-self.start)/time.time()
