'''
create detector instances of 'merlin' and 'merlins' with NXProcessingDetectorWrapper for Merlin Detector to support link to HDF file in Nexus data file
Both detectors are configured with detector data processor with ROI to return maximum position and value and summation.

Created on 20 Jul 2023

@author: fy65
'''
from gdaserver import _merlin, _merlin_for_snaps  # @UnresolvedImport
from gda.analysis.io import PilatusTiffLoader
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from scannable.detector.DetectorWithShutter import DetectorWithShutter
from localStationScripts.startup_epics_positioners import X1_DELAY
import gda
from localstation_functions import localStation_exception, localStation_print
import java
from epics.detector.NxProcessingDetectorWrapper import NxProcessingDetectorWrapper
import installation

if installation.isLive():
    from localStationScripts.startup_epics_positioners import x1
else:
    from gda.device.scannable import DummyScannable
    x1=x1_ttl=DummyScannable("x1_ttl", 0)

localStation_print("Configuring merlin")

try:
    merlin = NxProcessingDetectorWrapper('merlin',
                                         _merlin,
                                         None,
                                         _merlin_for_snaps,
                                         [],
                                         panel_name_rcp='Merlin',
                                         iFileLoader=PilatusTiffLoader,
                                         fileLoadTimout=60,
                                         printNfsTimes=False,
                                         returnPathAsImageNumberOnly=True
                                         )
    merlin.disable_operation_outside_scans = False
    merlin.processors=[DetectorDataProcessorWithRoi('max', merlin, [SumMaxPositionAndValue()], False)]
    #As with pil3, we can't just use merlin, we have to wrap a merlins to get the processing to work.
    #please don't expose the next object to users
    _merlins_with_shutter = NxProcessingDetectorWrapper('merlins',
            merlin.detector,
            merlin.hardware_triggered_detector,
            merlin.detector_for_snaps,
            merlin.processors,
            merlin.panel_name,
            merlin.toreplace,
            merlin.replacement,
            merlin.iFileLoader,
            merlin.root_datadir,
            merlin.fileLoadTimout,
            merlin.printNfsTimes,
            merlin.returnPathAsImageNumberOnly,
            merlin.panel_name_rcp,
            merlin.return_performance_metrics,
            merlin.array_monitor_for_hardware_triggering)
    merlins = DetectorWithShutter(_merlins_with_shutter, x1, X1_DELAY, nameSuffix="")
    _merlins_with_shutter.processors = [DetectorDataProcessorWithRoi('max', merlins, [SumMaxPositionAndValue()], False)]

except gda.factory.FactoryException as e:
    localStation_exception("connecting to merlin (FactoryException)", e)
except java.lang.IllegalStateException as e:
    localStation_exception("connecting to merlin (IllegalStateException)", e)
except:
    localStation_exception("connecting to merlin (Other)")
    