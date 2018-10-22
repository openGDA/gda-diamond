import sys
from rasor.init_scan_commands_and_processing import * 
scan_processor.rootNamespaceDict=globals()
print "excecuting rasor scripts"
diffcalcDir = LocalProperties.get("gda.diffcalc.path") + "/"
sys.path.append(diffcalcDir)
execfile(diffcalcDir + "example/startup/i10fourcircle.py")
#execfile(gdaDevScriptDir+"scan/createAndAliasSpecscans.py")
#print "running rasor position wrappers and SaveandReload"
execfile("/dls/i10/software/gda/config/scripts/rasor/positionWrapper.py")
#execfile("/dls/i10/software/gda/config/scripts/rasor/saveAndReload.py")
##setup metadata for the file
run("rasor/pd_metadata.py")
rmotors=MetaDataPD("rmotors", [tth,th,chi,eta,ttp, thp, py,pz, dsu, dsd, difx, alpha, lgm, lgf, lgb, rpenergy, iddpol, s6ygap])
add_default rmotors
run("rasor/pd_wait.py")
wait = WaitPD("wait", 0.1)
add_default wait
run ("rasor/pd_CollectionTime.py")
collectTime=CollectionTimePD("collectTime", [ca61sr,ca62sr,ca64sr])
add_default collectTime
print "==================================================================="; print; print;
