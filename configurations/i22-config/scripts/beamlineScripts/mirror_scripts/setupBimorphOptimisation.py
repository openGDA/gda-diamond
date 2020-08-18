from gdascripts.scannable.detector.epics.EpicsGigECamera import EpicsGigECamera
from gda.configuration.properties import LocalProperties
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.pd.dummy_pds import DummyPD
from gdascripts.scannable.detector.dummy.focused_beam_dataset import CreateImageReadingDummyDetector
from gda.util import VisitPath
from gda.device.scannable import ScannableMotionBase
from time import sleep

from bimorph import runOptimisation
from bimorph_mirror_optimising import SlitScanner, ScanAborter

try:
    del cam1det
    del cam1
    del peak2d
    del max2d
    del bm_topup
    del def_mon
    del defScanAborter
    del scanAborter
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
    print "Creating cam1det"
    cam1det = EpicsGigECamera('cam1det', 'BL22I-DI-PHDGN-08:', None, False)
    
print "Creating cam1, peak2d and max2d"
cam1 = ProcessingDetectorWrapper('cam1', cam1det, [], panel_name='None')
cam1.include_path_in_output=False
cam1.display_image=False


d12fields = {'background': 'CentroidThreshold_RBV',
        'peakx': 'CentroidX_RBV',
        'peaky': 'CentroidY_RBV',
        'topx' : 'MaxX_RBV',
        'topy': 'MaxY_RBV',
        'fwhmx': 'SigmaX_RBV',
        'fwhmy':'SigmaY_RBV'}

d12_base_pv = 'BL22I-DI-PHDGN-12:STAT:'
peak2d = ScannableGroup('peak2d', [DisplayEpicsPVClass('peak2d_'+field, d12_base_pv + pv, '', '%.f') for field, pv in d12fields.items()])
peak2d.configure()

max2d = DetectorDataProcessorWithRoi('max2d', cam1, [SumMaxPositionAndValue()])

slitscanner = SlitScanner()

run "bimorph_mirror_optimising"
run "bimorph"
