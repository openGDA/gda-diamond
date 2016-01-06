from datawriting.i16_nexus_extender2 import I16NexusExtender, title, sample, set_diffcalc_instance, use_cryo

set_diffcalc_instance(hkl._diffcalc if USE_DIFFCALC else None)
use_cryo(USE_CRYO_GEOMETRY)

#PDW.returnPathAsImageNumberOnly = True

alias title
alias sample

Energy = en
meta_add Energy

writerMap = Finder.getInstance().getFindablesOfType(gda.data.scan.datawriter.DefaultDataWriterFactory)
ddwf = writerMap.get("DefaultDataWriterFactory")
for dwe in ddwf.getDataWriterExtenders():
    ddwf.removeDataWriterExtender(dwe)
nexusExtender = I16NexusExtender("/dls_sw/i16/software/gda/workspace_git/gda-mt.git/configurations/i16-config/pythonscripts/gda_external/geometry.xml")
ddwf.addDataWriterExtender(nexusExtender)

