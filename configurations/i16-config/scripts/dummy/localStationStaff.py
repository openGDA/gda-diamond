# Taken from localStationStaff 2020-10-09
import pd_offset
from gda.configuration.properties import LocalProperties
from gda.jython import InterfaceProvider
from lab84.initialise_offsets import PIL3_CENTRE_I_DEFAULT, PIL3_CENTRE_J_DEFAULT
from localStationScripts.startup_offsets import pil3_centre_i, pil3_centre_j
ci = pil3_centre_i() or PIL3_CENTRE_I_DEFAULT
cj = pil3_centre_j() or PIL3_CENTRE_J_DEFAULT

iw=13; jw=15; roi1params = (int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))
iw=50; jw=50; roi2params = (int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))
maxi=486; maxj=194 #08/10/15
roi3params = (int(ci-1/2.),0,int(ci+1/2.),maxj)
roi4params = (0,int(cj-1/2.),maxi,int(cj+1/2.))

if LocalProperties.get("gda.data.scan.datawriter.dataFormat") == u'NexusScanDataWriter':
	# TODO: Implement an equivalent of roi1-4 initially for pil3, later for merlin and other pilatus detectors
	global pil3_required
	pil3_required.rois()
	pil3_required.roi('roi1', *roi1params)
	pil3_required.roi('roi2', *roi2params)
	pil3_required.roi('roi3', *roi3params)
	pil3_required.roi('roi4', *roi4params)
	pil3_required.active('roi1', True)
	pil3_required.active('roi2', True)
	pil3_required.active('roi3', False)
	pil3_required.active('roi4', False)
	pil3_required.rois()
else:
	from detector_wrappers.pilatus_instances import pil3
	from gdascripts.scannable.detector.DetectorDataProcessor import HardwareTriggerableDetectorDataProcessor
	from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue

	pil3.display_image = False
	roi1 = scroi=HardwareTriggerableDetectorDataProcessor('roi1', pil3, [SumMaxPositionAndValue()])
	roi1.setRoi(*roi1params)
	
	roi2 = lcroi=HardwareTriggerableDetectorDataProcessor('roi2', pil3, [SumMaxPositionAndValue()])
	roi1.setRoi(*roi2params)
	pil3.display_image = True

from gdascripts.scannable.installStandardScannableMetadataCollection import addmeta

addmeta(pil3_centre_i, pil3_centre_j)

if InterfaceProvider.getJythonNamespace().getFromJythonNamespace("USE_DIFFCALC"):
	# Dan's DiffCalc crystal info class
	from i16_gda_functions.CrystalDevice import CrystalInfoDiffCalcName  # @UnresolvedImport
	from diffcalc.ub.ub import ubcalc
	xtlinfo = CrystalInfoDiffCalcName('xtlinfo',ubcalc)
	addmeta(xtlinfo)
