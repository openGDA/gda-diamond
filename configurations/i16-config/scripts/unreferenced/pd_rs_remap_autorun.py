from gda.device.scannable import PseudoDevice
from gda.data import NumTracker
from gda.data import PathConstructor
import subprocess

class RSRemapAutorun(PseudoDevice):
	'''Class for reciprocal space remapping '''
	def __init__(self, name):
		self.setName(name)
		self.setInputNames([name])
		self.Units=['Units']
		self.setOutputFormat(['%6.4f'])
		self.setLevel(100)
		self.miller_step = 0.002
		self.numTracker = NumTracker("scanbase_numtracker")

	def getCurrentFileName(self):
		file = PathConstructor.createFromDefaultProperty()
		file = file + "/" + `numTracker.getCurrentFileNumber()`+".nxs"
		return(file)

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,new_position):
		self.miller_step = float(new_position)

	def getPosition(self):
		return self.miller_step

	def atScanEnd(self):
		print("Reciprocal space remapping has been requested, submitting job to cluster")
		command = "/dls_sw/i16/scripts/AutoProc/run_rs_remap.sh %s %f" % (self.getCurrentFileName(), self.miller_step)
		print("Command which will be run is '%s'" % command)
		print(subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read())
		print("Submission complete")
try:
	del(rs_remap)
except:
	pass
rs_remap = RSRemapAutorun('rs_remap')
