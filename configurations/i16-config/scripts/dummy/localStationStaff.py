# Taken from localStationStaff 2020-10-09
from gda.jython import InterfaceProvider
from dummy.initialise_offsets import PIL3_CENTRE_I_DEFAULT, PIL3_CENTRE_J_DEFAULT
from localStationScripts.startup_offsets import pil3_centre_i, pil3_centre_j
ci = pil3_centre_i() or PIL3_CENTRE_I_DEFAULT
cj = pil3_centre_j() or PIL3_CENTRE_J_DEFAULT

iw=13; jw=15; roi1params = (int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))
iw=50; jw=50; roi2params = (int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))
maxi=486; maxj=194 #08/10/15
roi3params = (int(ci-1/2.),0,int(ci+1/2.),maxj)
roi4params = (0,int(cj-1/2.),maxi,int(cj+1/2.))

from gdascripts.scannable.installStandardScannableMetadataCollection import addmeta

addmeta(pil3_centre_i, pil3_centre_j)

if InterfaceProvider.getJythonNamespace().getFromJythonNamespace("USE_DIFFCALC"):
	# Dan's DiffCalc crystal info class
	from i16_gda_functions.CrystalDevice import CrystalInfoDiffCalcName  # @UnresolvedImport
	from diffcalc.ub.ub import ubcalc
	xtlinfo = CrystalInfoDiffCalcName('xtlinfo',ubcalc)
	addmeta(xtlinfo)
