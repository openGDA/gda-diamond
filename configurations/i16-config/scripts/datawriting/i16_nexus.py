from datawriting.i16_nexus_extender2 import I16NexusExtender, title, sample, set_diffcalc_instance, use_cryo
from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import DefaultDataWriterFactory, NexusDataWriterConfiguration

set_diffcalc_instance(diffcalc if USE_DIFFCALC else None)
use_cryo(USE_CRYO_GEOMETRY)

#PDW.returnPathAsImageNumberOnly = True

alias title
alias sample

Energy = en

if LocalProperties.get("gda.data.scan.datawriter.dataFormat") == u'NexusDataWriter':
	# Clear default Nexus templates and data writer extenders
	ndwc = Finder.getFindablesOfType(NexusDataWriterConfiguration).get("nexusDataWriterConfiguration")
	ddwf = Finder.getFindablesOfType(DefaultDataWriterFactory).get("DefaultDataWriterFactory")
	ndwc.getNexusTemplateFiles().clear()
	ddwf.getDataWriterExtenders().clear()

	nexusExtender = I16NexusExtender([
		"/dls_sw/i16/scripts/pilatus_calibration/geometry.xml",
		"/dls_sw/i16/scripts/pilatus_calibration/geometry_merlin.xml"])
	"""
	nexusExtender = I16NexusExtender([
		"/dls_sw/i16/scripts/calibration/geometry_pilatus.xml",
		"/dls_sw/i16/scripts/calibration/geometry_merlin.xml"])
	"""
	ddwf.addDataWriterExtender(nexusExtender)
