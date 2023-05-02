# Taken from localStationStaff 2020-10-09
import pd_offset
from gda.jython import InterfaceProvider
from detector_wrappers.pilatus_instances import pil3

pil3_centre_i = pd_offset.Offset('pil3_centre_i')
pil3_centre_j = pd_offset.Offset('pil3_centre_j')
ci = pil3_centre_i()
cj = pil3_centre_j()

from gdascripts.scannable.detector.DetectorDataProcessor import HardwareTriggerableDetectorDataProcessor
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue

pil3.display_image = False
roi1 = scroi=HardwareTriggerableDetectorDataProcessor('roi1', pil3, [SumMaxPositionAndValue()])
iw=13; jw=15; roi1.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))

roi2 = lcroi=HardwareTriggerableDetectorDataProcessor('roi2', pil3, [SumMaxPositionAndValue()])
iw=50; jw=50; roi2.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))
pil3.display_image = True

from gdascripts.scannable.installStandardScannableMetadataCollection import addmeta

addmeta(pil3_centre_i, pil3_centre_j)

if InterfaceProvider.getJythonNamespace().getFromJythonNamespace("USE_DIFFCALC"):

    # Dan's DiffCalc crystal info class
    from i16_gda_functions.CrystalDevice import CrystalInfoDiffCalcName  # @UnresolvedImport
    from diffcalc.ub.ub import ubcalc
    xtlinfo = CrystalInfoDiffCalcName('xtlinfo',ubcalc)
    addmeta(xtlinfo)
    


