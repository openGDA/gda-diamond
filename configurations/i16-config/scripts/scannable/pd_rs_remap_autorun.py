from gda.device.scannable import ScannableMotionBase
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.util.logging.LoggingUtils import logSince
from java.time import Instant #@UnresolvedImport
from org.slf4j import LoggerFactory
import subprocess, threading

class RSRemapAutorun(ScannableMotionBase):
	'''Class for reciprocal space remapping '''
	def __init__(self, name):
		self.setName(name)
		self.setInputNames([name])
		self.Units=['Units']
		self.setOutputFormat(['%6.4f'])
		self.setLevel(100)
		self.miller_step = 0.002
		self.numTracker = NumTracker("scanbase_numtracker")
		self.logger = LoggerFactory.getLogger("RSRemapAutorun:%s" % name)

	def getCurrentFileName(self):
		file = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
		file = file + "/" + `numTracker.getCurrentFileNumber()`+".nxs"
		return(file)

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,new_position):
		self.miller_step = float(new_position)

	def getPosition(self):
		return self.miller_step

	def atScanEnd(self):
		message="Reciprocal space remapping has been requested, submitting job to cluster"
		command = "/dls_sw/i16/scripts/AutoProc/run_rs_map.sh %s %f" % (self.getCurrentFileName(), self.miller_step)
		self.logger.trace("{} with command '{}'", message, command)
		start_time = Instant.now()
		threading.Thread(target=self.submitRsRemapJobRequest, name=command, args=(self.logger, start_time, message, command)).start()
		logSince(self.logger, "Job request process started, taking", start_time)

	def submitRsRemapJobRequest(self, logger, start_time, message, command):
		logSince(self.logger, "Job request running, taking", start_time)
		print(message)
		print("Command which will be run is '%s'" % command)
		print(subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read())
		logSince(self.logger, "Job request submitted, taking", start_time)
		print("Submission complete")

try:
	del(rs_remap)
except:
	pass
rs_remap = RSRemapAutorun('rs_remap')
