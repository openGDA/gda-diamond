#    BranchLineUser.py
#
#    For user specific initialisation code on I06 Branch Line.



#print "Hello! How do you do!"

#Enable Exit Slits S6 Gap Control s6ygap";

execfile("/dls/i06-1/scripts/s6gaps.py");

#print "POMS user support:";
#execfile("/dls/i06-1/scripts/POMS/PomsSocketDevice_GDA74.py");
#execfile("/dls/i06-1/scripts/polarimeter/detector.py");
execfile("/dls/i06-1/scripts/idivio.py");

print "-------------------------------------------------------------------"
