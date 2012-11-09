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
try:
    del cam1det
    del cam1
    del peak2d
    del max2d
except:
    pass
#datadir = LocalProperties.getPath("gda.data.scan.datawriter.datadir",None) #@UndefinedVariable
datadir = VisitPath.getVisitPath() + '/'
USE_DUMMY_DETECTOR = False
if USE_DUMMY_DETECTOR:
    print "Creating dummy detector"
    x = DummyPD("x")
    x.asynchronousMoveTo(430)
    cam1det = CreateImageReadingDummyDetector.create(x)
else:
    print "Creating cam1det, writing to:", datadir
    cam1det = EpicsFirewireCamera('cam1det', 'BL22I-DI-PHDGN-10:CAM:', datadir)
    
print "Creating cam1, peak2d and max2d"
cam1 = ProcessingDetectorWrapper('cam1', cam1det, [], panel_name='Firewire Camera')
peak2d = DetectorDataProcessorWithRoi('peak2d', cam1, [TwodGaussianPeak()])
max2d = DetectorDataProcessorWithRoi('max2d', cam1, [SumMaxPositionAndValue()])


from gdascripts.bimorph.bimorph import runOptimisation
from uk.ac.gda.beans.bimorph import BimorphParameters
from gdascripts.bimorph import bimorph
from uk.ac.gda.beans import BeansFactory
from gdascripts.bimorph.bimorph_mirror_optimising import SlitScanner, ScanAborter

BeansFactory.setClasses([BimorphParameters])

#scanAborter = ScanAborter("scanAborter",ringcurrent, -10)    

slitscanner = SlitScanner()


run "gdascripts/bimorph/bimorph_mirror_optimising"
run "gdascripts/bimorph/bimorph"
