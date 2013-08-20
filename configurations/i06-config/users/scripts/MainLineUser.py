#    MainLineUser.py
#
#    For user specific initialisation code on I06 PEEM Line.


#Set the output format for Current Amplifier
#print "Hello! How do you do!"

#Enable Exit Slits S4 Gap Control s4ygap";

execfile("/dls/i06/scripts/s4gaps.py");
#execfile("/dls/i06/scripts/SetLevel.py");
#execfile("/dls/i06/scripts/id.py");
#execfile("/dls/i06/scripts/id_25_09_2008_to_test.py");
#execfile("/dls/i06/scripts/rp.py");
execfile("/dls/i06/scripts/status.py");
print "-------------------------------------------------------------------"
