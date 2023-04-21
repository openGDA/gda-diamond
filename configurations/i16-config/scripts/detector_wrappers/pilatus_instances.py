'''
create instances of different wrappers of pilatus detector.

This is extracted from localStation.py to support pyhton import of objects defined here in other modules.

Created on Apr 12, 2023

@author: fy65
'''
#TODO find a better way to switch among different type of detector instance instead of comment in and out

from localstation_functions import localStation_print, localStation_exception
from gda.factory import Finder
from epics.detector.NxProcessingDetectorWrapper import NxProcessingDetectorWrapper
from gda.analysis.io import PilatusTiffLoader
from scannable.detector.DetectorWithShutter import DetectorWithShutter
import installation
from localStationScripts.startup_epics_positioners import X1_DELAY
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from scannable.pilatus import PilatusThreshold, PilatusGain
from gdaserver import pilatus3, pilatus3_for_snaps, kphiZebraPil3  # @UnresolvedImport

if installation.isLive():
    from gdaserver import kthZebraPil3, smargonZebraPil3  # @UnresolvedImport

if installation.isLive():
    from localStationScripts.startup_epics_positioners import x1
else:
    from gda.device.scannable import DummyScannable
    x1=x1_ttl=DummyScannable("x1_ttl", 0)

localStation_print("Configuring pilatus 3 (100k)")

try:
    _pilatus3_counter_monitor = Finder.find("pilatus3_plugins").get('pilatus3_counter_monitor')
    #pil3_100k = SwitchableHardwareTriggerableProcessingDetectorWrapper('pil3_100k',
    pil3_100k = NxProcessingDetectorWrapper('pil3_100k',
        pilatus3,
        kphiZebraPil3, # Switch to kthZebraPil3 if needed
        #kthZebraPil3, # Should normally be kphiZebraPil3
        #smargonZebraPil3, # Should normally be kphiZebraPil3
        pilatus3_for_snaps,
        [],
        panel_name_rcp='Pilatus',
        toreplace=None,
        replacement=None,
        iFileLoader=PilatusTiffLoader,
        fileLoadTimout=60,
        returnPathAsImageNumberOnly=True,
        array_monitor_for_hardware_triggering = _pilatus3_counter_monitor)

    #pil3_100ks = DetectorWithShutter(pil3_100k, x1, X1_DELAY, nameSuffix="")
    # With ^ the Nexus file ends up with a pil3_100ks node but the link writer inside NxProcessingDetectorWrapper fails with
    #   KeyError: "Unable to open object (object 'pil3_100k' doesn't exist)"
    # as pil3_100k has no way to know that it's name is being overridden. Instead clone the NxProcessingDetectorWrapper with
    # it's new name baked in.
    pil3_100ksNPDW = NxProcessingDetectorWrapper('pil3_100ks',
            pil3_100k.detector,
            pil3_100k.hardware_triggered_detector,
            pil3_100k.detector_for_snaps,
            pil3_100k.processors,
            pil3_100k.panel_name,
            pil3_100k.toreplace,
            pil3_100k.replacement,
            pil3_100k.iFileLoader,
            pil3_100k.root_datadir,
            pil3_100k.fileLoadTimout,
            pil3_100k.printNfsTimes,
            pil3_100k.returnPathAsImageNumberOnly,
            pil3_100k.panel_name_rcp,
            pil3_100k.return_performance_metrics,
            pil3_100k.array_monitor_for_hardware_triggering)
    pil3_100ks = DetectorWithShutter(pil3_100ksNPDW, x1, X1_DELAY, nameSuffix="")

    pil3_100k.processors      = [DetectorDataProcessorWithRoi('max', pil3_100k,  [SumMaxPositionAndValue()], False)]
    pil3_100ksNPDW.processors = [DetectorDataProcessorWithRoi('max', pil3_100ks, [SumMaxPositionAndValue()], False)]
    pil3_100k.printNfsTimes      = False
    pil3_100ksNPDW.printNfsTimes = False
    pil3 = pil3_100k
    pil  = pil3_100k
    pil3s = pil3_100ks
    pils  = pil3_100ks

    pil3_100kthresh = PilatusThreshold('pil3_100kthresh', pil3_100k.hardware_triggered_detector.driver.getAdDriverPilatus())
    pil3_100kgain =        PilatusGain('pil3_100kgain',   pil3_100k.hardware_triggered_detector.driver.getAdDriverPilatus())

    # Make sure hdf5 writer isn't still running
    #caput('BL16I-EA-PILAT-03:HDF5:Capture',0)
    # pilatus3.hdfwriter.stop()
except:
    localStation_exception("configuring pilatus 3 (100k)")
