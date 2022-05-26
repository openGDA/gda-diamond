from datawriting.i16_nexus_extender2 import I16NexusExtender, title, sample, set_diffcalc_instance, use_cryo
from gda.configuration.properties import LocalProperties

set_diffcalc_instance(diffcalc if USE_DIFFCALC else None)
use_cryo(USE_CRYO_GEOMETRY)

#PDW.returnPathAsImageNumberOnly = True

alias title
alias sample

Energy = en

if LocalProperties.get("gda.data.scan.datawriter.dataFormat") == u'NexusDataWriter':
	writerMap = Finder.getFindablesOfType(gda.data.scan.datawriter.DefaultDataWriterFactory)
	ddwf = writerMap.get("DefaultDataWriterFactory")
	for dwe in ddwf.getDataWriterExtenders():
		ddwf.removeDataWriterExtender(dwe)

	nexusExtender = I16NexusExtender([
		"/dls_sw/i16/scripts/pilatus_calibration/geometry.xml",
		"/dls_sw/i16/scripts/pilatus_calibration/geometry_merlin.xml"])
	"""
	nexusExtender = I16NexusExtender([
		"/dls_sw/i16/scripts/calibration/geometry_pilatus.xml",
		"/dls_sw/i16/scripts/calibration/geometry_merlin.xml"])
	"""
	ddwf.addDataWriterExtender(nexusExtender)
