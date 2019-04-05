from gdascripts.scannable.detector.epics.EpicsFirewireCamera import EpicsFirewireCamera
from gda.configuration.properties import LocalProperties
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.pd.dummy_pds import DummyPD
from gdascripts.scannable.detector.dummy.focused_beam_dataset import CreateImageReadingDummyDetector
from gda.util import VisitPath
from gda.device.scannable import PseudoDevice
from time import sleep


datadir = "/dls/i07/data/operation/fleacam/"
#datadir = LocalProperties.getPath("gda.data.scan.datawriter.datadir",None); #@UndefinedVariable
#datadir = VisitPath.getVisitPath() + '/'


#To define the flea camera
USE_DUMMY_DETECTOR = False
if USE_DUMMY_DETECTOR:
	print "Creating dummy detector"
	x = DummyPD("x")
	x.asynchronousMoveTo(430)
	cam1det = CreateImageReadingDummyDetector.create(x)
else:
	print "Creating cam1det, writing to:", datadir
	cam1det = EpicsFirewireCamera('cam1det', 'BL07I-DI-PHDGN-09:CAM:', datadir);
	
print "Creating cam1, peak2d and max2d"
cam1 = ProcessingDetectorWrapper('cam1', cam1det, [], panel_name='Firewire Camera')
peak2d = DetectorDataProcessorWithRoi('peak2d', cam1, [TwodGaussianPeak()])
max2d = DetectorDataProcessorWithRoi('max2d', cam1, [SumMaxPositionAndValue()])

#To define the bimorph mirror;
from Diamond.BimorphVoltageSetter.BimorphVoltageSetter import *; 

print "initialise HFM / VFM bimorph voltage setters"
HFMVoltagePV = "BL07I-OP-KBM-01:HFM:SET-VOUT";
HFMMonitorPV = "BL07I-OP-KBM-01:HFM:GET-VOUT";
VFMVoltagePV = "BL07I-OP-KBM-01:VFM:SET-VOUT"
VFMMonitorPV = "BL07I-OP-KBM-01:VFM:GET-VOUT"
	
bm_hfm = BimorphVoltageDevice('hfm', HFMVoltagePV, HFMMonitorPV, 8, 300);
bm_vfm = BimorphVoltageDevice('vfm', VFMVoltagePV, VFMMonitorPV, 16, 300);

#To define a stopper if beam lost
class ScanAborter(PseudoDevice):
	def __init__(self, qbpm, minValue):
		self.qbpm = qbpm
		self.minValue=minValue
	def rawIsBusy(self):
		if not self.isOK():
			raise RuntimeError("qbpm is < " + `self.minValue`)
		return False
	def getPosition(self):
		return self.qbpm()
	def isOK(self):
		return self.qbpm() > self.minValue
	def asynchronousMoveTo(self, new_energy):
		pass

from gda.device.monitor import EpicsMonitor

beamCurrentMonitor = EpicsMonitor()
beamCurrentMonitor.setPvName("SR21C-DI-DCCT-01:SIGNAL")
beamCurrentMonitor.configure()

# shoudl not be 'test' , should be beamCurrentMonitor
scanAborter = ScanAborter(beamCurrentMonitor, 20)	

def getPositions(initialPos, increment):
#	initialPos=[0,0,0,0,0,0,0,0]
#	increment=50
	positions=[]
	positions.append(initialPos)
	for i in range(1,len(initialPos)+1):
		newPos=[]
		for j in range(len(initialPos)):
			newPos.append(initialPos[j])
		for k in range(i):
			newPos[k]+=increment
		positions.append(newPos)
	return positions

def getData(mirror, increment, 
		slitToScanSize, 
		slitToScanPos,
		slitSize,
		otherSlitSize, 
		otherSlitPos,
		slitStart, slitEnd, slitStep):
	positions = getPositions(mirror.getPosPlusIncrement(0),increment)
	print positions
	pos otherSlitPos 0.
	pos otherSlitSize 10.
	pos slitToScanSize slitSize
	for position in positions:
		print "moving mirror to " + `position`
		mirror.setVoltages(position);
		print "mirror is now at " + `mirror.getVoltages()`;
		while(True):
			while( not scanAborter.isOK()):
				print "waiting for beam to come back"
				sleep(60)
			try:
				print "beam is ok so now start scan"
				scan slitToScanPos slitStart slitEnd slitStep cam1 90 peak2d scanAborter
				break
			except:
				print "scan aborted wait for scanAbort to return OK"

#run "I07BimorphMirrorOptimising"
#pos
#getData(bm_vfm, 50, S3YGAP, S3YCENTRE, 0.1, S3XGAP, S3XCENTRE, -.7, .7, 0.07)
#getData(bm_hfm, 50, S3XGAP, S3XCENTRE, 0.1, S3YGAP, S3YCENTRE, -.7, .7, 0.07 )

#to scan a slit
#scan S3YCENTRE -1. 1. 0.1 cam1 768 peak2d


# awk '{print $1,$6}' /dls/i02/data/2009/cm1843-9/4764.dat
#gdascripts.bimorph.bimorph.runOptimisation()
#/dls/i02/data/2009/cm1843-9/vfm_data/dat
