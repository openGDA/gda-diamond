from datawriting.i16_nexus_extender2 import I16NexusExtender, title, sample, set_diffcalc_instance, use_cryo

set_diffcalc_instance(diffcalc if USE_DIFFCALC else None)
use_cryo(USE_CRYO_GEOMETRY)

#PDW.returnPathAsImageNumberOnly = True

alias title
alias sample

Energy = en
if USE_NEXUS_METADATA_COMMANDS:
	meta_add(Energy)
else:
	meta.add(Energy)

writerMap = Finder.getFindablesOfType(gda.data.scan.datawriter.DefaultDataWriterFactory)
ddwf = writerMap.get("DefaultDataWriterFactory")
for dwe in ddwf.getDataWriterExtenders():
    ddwf.removeDataWriterExtender(dwe)

nexusExtender = I16NexusExtender("/dls_sw/i16/scripts/pilatus_calibration/geometry.xml")
# Comment this out if using gda.data.scan.datawriter.dataFormat = NexusScanDataWriter 
ddwf.addDataWriterExtender(nexusExtender)
