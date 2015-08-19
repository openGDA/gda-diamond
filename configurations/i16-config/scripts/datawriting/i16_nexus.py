from datawriting.i16_nexus_extender import I16NexusExtender, title, sample

#PDW.returnPathAsImageNumberOnly = True

alias title
alias sample

Energy = en
meta_add Energy

writerMap = Finder.getInstance().getFindablesOfType(gda.data.scan.datawriter.DefaultDataWriterFactory)
ddwf = writerMap.get("DefaultDataWriterFactory")
for dwe in ddwf.getDataWriterExtenders():
    ddwf.removeDataWriterExtender(dwe)
nexusExtender = I16NexusExtender(xtalinfo) #goodbye diffcalc
ddwf.addDataWriterExtender(nexusExtender)

