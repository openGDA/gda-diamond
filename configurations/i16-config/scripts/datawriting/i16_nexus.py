from datawriting.i16_nexus_extender2 import I16NexusExtender, set_diffcalc_instance
from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import DefaultDataWriterFactory, NexusDataWriterConfiguration
from gda.factory import Finder

set_diffcalc_instance(diffcalc if USE_DIFFCALC else None)

#PDW.returnPathAsImageNumberOnly = True

Energy = en

if LocalProperties.get("gda.data.scan.datawriter.dataFormat") == u'NexusDataWriter':
	# Clear default Nexus templates and data writer extenders
	ndwc = Finder.getFindablesOfType(NexusDataWriterConfiguration).get("nexusDataWriterConfiguration")
	ddwf = Finder.getFindablesOfType(DefaultDataWriterFactory).get("DefaultDataWriterFactory")
	ndwc.getNexusTemplateFiles().clear()
	# ddwf.getDataWriterExtenders().clear()

	if len(ddwf.getDataWriterExtenders()) > 1:
		ddwf.removeDataWriterExtender(ddwf.getDataWriterExtenders()[1])  # remove old diffcalc instance

	nexusExtender = I16NexusExtender([
		"/dls_sw/i16/scripts/detector_calibration/geometry_pil3_100k.xml",
		"/dls_sw/i16/scripts/detector_calibration/geometry_merlin.xml"])

	ddwf.addDataWriterExtender(nexusExtender)
