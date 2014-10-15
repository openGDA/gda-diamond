#>>> run "startup_trajscan.py"

from gda.device.detector.hardwaretriggerable import DummyHardwareTriggerableDetector
from gda.scan import ConcurrentScan
from scannable.scaler import McsController, McsChannelScannable
# TODO: Move to using mtscripts.scannable.waveform_channel
from misc_functions import caput
from gdascripts.scan.scanListener import ScanListener
from gdascripts.scannable.preloadedArray import PreloadedArray
from gdascripts.scan.process.ScanDataProcessorResult import determineScannableContainingField
from gdascripts.scan.process.ScanDataProcessor import loadScanFile
from gdascripts.scan.trajscans import setDefaultScannables
from time import sleep

PERFORM_SECOND_SCAN_TO_SHOW_ACTUAL_POSITIONS = True

class ActualTrajectoryPositionScannable(object): # new interface required
	"""Generates an actual position and error for every motor and a list of demand positions for those explicitely moved"""
	def __init__(self, group):
		self.group = group
		
	def atScanStart(self):
		self.initial_position = self.group()
		self.ready = False
		self.lastscan_names = []
		self.lastscan_formats = []
		self.lastscan_positions = []
		
	def getPositions(self):
		if not self.ready:
			self.makeReady()
		return self.lastscan_positions
	
	def getNames(self):
		if not self.ready:
			self.makeReady()
		return self.lastscan_names
	
	def getFormats(self):
		if not self.ready:
			self.makeReady()
		return self.lastscan_formats
	
	
	def makeReady(self):
		print "Reading actual motor positions from EPICS"
		print "Sleeping for 2 seconds to work around known Epics problem: (https://trac.diamond.ac.uk/beam/ticket/6942)"
		sleep(2)
		self.group.getContinuousMoveController()
		self.demand_points = list(self.group.getContinuousMoveController().getPointsList())
		self.actual_points = list(self.group.getContinuousMoveController().readActualPositionsFromHardware())
		
		# names and formats
		for i, name, format in zip(range(len(self.group.inputNames)), self.group.inputNames, self.group.outputFormat):
			if self.demand_points[0][i] is not None:
				self.lastscan_names.append(name + '_dmd')
				self.lastscan_formats.append(format)
			self.lastscan_names.append(name + '_actual')
			self.lastscan_formats.append(format)
			self.lastscan_names.append(name + '_delta')
			self.lastscan_formats.append(format)
		
		# positions		
		for demand_point, actual_point in zip(self.demand_points, self.actual_points):
			position = []
			for i, demand, actual in zip(range(len(demand_point)), demand_point, actual_point):
				if demand is not None:
					position.append(demand)
				position.append(actual)
				if demand is not None:
					position.append(actual - demand)
				else:
					position.append(actual - self.initial_position[i])
			self.lastscan_positions.append(position)
		assert len(self.lastscan_names) == len(self.lastscan_positions[0]) == len(self.lastscan_formats)
		self.ready = True
		

class TrajectoryControllerHelper(ScanListener):
	
	def __init__(self, controller, group):
		self.controller = controller
		self.group = group
		self.actual_group = ActualTrajectoryPositionScannable(group)

	def prepareForScan(self):
		print "Manually making sure that BL16I-MO-DIFF-01:TRAJ1:MoveMode is absolute"
		caput("BL16I-MO-DIFF-01:TRAJ1:MoveMode", 1)
		self.actual_group.atScanStart()
	
	def update(self, scanObject):
		if PERFORM_SECOND_SCAN_TO_SHOW_ACTUAL_POSITIONS:
			# TODO: Won't work for x scannables with multiple input fields yet
			# get x scannable
			xfieldname = scanObject.getScanPlotSettings().getXAxisName()
			xscannable = determineScannableContainingField(xfieldname, scanObject.getUserListedScannables())
			
			# get x positions
			all_detectors_and_scannables = list(scanObject.getAllScannables()) + list(scanObject.getDetectors())
			sfh = loadScanFile(scanObject, [xfieldname], all_detectors_and_scannables)
			self.x_values = list(sfh.getDataset(xfieldname))
			
			column_names = [xfieldname] + list(self.actual_group.getNames())
			formats = [xscannable.outputFormat[0]] + list(self.actual_group.getFormats())
			
			self.pa = PreloadedArray('kappa_positions', column_names, formats, True)
			for x, line in zip(self.x_values, self.actual_group.getPositions()):
				self.pa.append([x] + list(line))
			try:
				original_default_scannables = setDefaultScannables([])
				s = ConcurrentScan([self.pa, 0, self.pa.getLength()-1, 1])
			finally:
				setDefaultScannables(original_default_scannables)
			s.runScan()


st = DummyHardwareTriggerableDetector('st')
st.setHardwareTriggerProvider(sixckappa.getContinuousMoveController()) #@UndefinedVariable
xps_controller = sixckappa.getContinuousMoveController() #@UndefinedVariable
trajectory_controller_helper = TrajectoryControllerHelper(xps_controller, sixckappa) #@UndefinedVariable



mcs_controller = McsController("BL16I-EA-DET-01:MCA-01:")
mcs1 = McsChannelScannable('mcs1', mcs_controller, "BL16I-EA-DET-01:MCA-01:", 1)
mcs1.setHardwareTriggerProvider(sixckappa.getContinuousMoveController()) #@UndefinedVariable
mcs2 = McsChannelScannable('mcs2', mcs_controller, "BL16I-EA-DET-01:MCA-01:", 2)
mcs2.setHardwareTriggerProvider(sixckappa.getContinuousMoveController()) #@UndefinedVariable
mcs3 = McsChannelScannable('mcs3', mcs_controller, "BL16I-EA-DET-01:MCA-01:", 3)
mcs3.setHardwareTriggerProvider(sixckappa.getContinuousMoveController()) #@UndefinedVariable
mcs4 = McsChannelScannable('mcs4', mcs_controller, "BL16I-EA-DET-01:MCA-01:", 4)
mcs4.setHardwareTriggerProvider(sixckappa.getContinuousMoveController()) #@UndefinedVariable



		
		
		

# An example scan
#tsl=TrajectoryScanLine([kphi, 0, 10, 1, mcs1, 1, mcs2]);tsl.setScanDataPointQueueLength(10000);tsl.setPositionCallableThreadPoolSize(1);tsl.runScan()

# Note that the arg list in []s are those of any regular gda scan as long as they contain only one line. 

# Detectors must be only the above mcs detectors : these are channels 1-4 on the struck card (where the first is wired internally to 50Mhz clock). Make more as needed.

# Scannables to move or read must be any of sixc (kphi, kap, kth, kmu, kdelta, kgam), euler (chi, phi, eta, delta, mu, gamma), hkl (h, k, l). Remove all defaults for now please.

# All Scannable positions in data files are demand positions for now.


#def trajscan(*args):
#	print "Manually making sure that BL16I-MO-DIFF-01:TRAJ1:MoveMode is absolute"
#	caput("BL16I-MO-DIFF-01:TRAJ1:MoveMode", 1)
#	command_server = Finder.getInstance().find("command_server")
#	default_scannables_to_remove = list(command_server.getDefaultScannables())
#	try:
#		default_scannables_to_remove.remove(meta) #@UndefinedVariable
#		print "Leaving in default scannable: meta"
#	except ValueError:
#		print "No meta default scannable set"
#	print "Removing defaults: " + ', '.join([scn.name for scn in default_scannables_to_remove])
#	for scn in default_scannables_to_remove:
#		command_server.removeDefault(scn)
#	try:
#		tsl=TrajectoryScanLine(list(args))
#		tsl.setScanDataPointQueueLength(10000)
#		tsl.setPositionCallableThreadPoolSize(1)
#		tsl.runScan()
#	finally:
#		print "Restoring defaults: "  + ', '.join([scn.name for scn in default_scannables_to_remove])
#		for scn in default_scannables_to_remove:
#			command_server.addDefault(scn)
#alias('trajscan')

from gdascripts.scan import trajscans

print "Creating gda trajscan commands:"
trajascan=trajscans.TrajAscan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
trajcscan=trajscans.TrajCscan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
trajdscan=trajscans.TrajDscan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
trajrscan=trajscans.TrajRscan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
trajscan=trajscans.TrajScan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
trajscancn=trajscans.TrajScancn([scan_processor, trajectory_controller_helper]) #@UndefinedVariable

def extractScanDocline(scanobj, scanname):
	return [line.strip() for line in scanobj.__doc__.split('\n') if line.strip().startswith(scanname)][0]

alias('trajascan');print extractScanDocline(trajascan, 'trajascan') #@UndefinedVariable
alias('trajcscan');print extractScanDocline(trajcscan, 'trajcscan') #@UndefinedVariable
alias('trajdscan');print extractScanDocline(trajdscan, 'trajdscan') #@UndefinedVariable
alias('trajrscan');print extractScanDocline(trajrscan, 'trajrscan') #@UndefinedVariable
alias('trajscan');print extractScanDocline(trajscan, 'trajscan') #@UndefinedVariable
alias('trajscancn');print extractScanDocline(trajscancn, 'trajscancn') #@UndefinedVariable

trajscans.DEFAULT_SCANNABLES_FOR_TRAJSCANS = [meta] #@UndefinedVariable
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()  #@UndefinedVariable
