#localStation.py
#For beamline specific initialisation code.
print "===================================================================";
print "Performing Beanline I07 specific client initialisation code (client.py).";
print

#Setup the environment variables
from time import ctime;

from gda.configuration.properties import LocalProperties;

	
# Get the locatation of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.config") + "/scripts/";

# Get the location of the USERS script directory
userScriptDir = "/dls_sw/" + LocalProperties.get("gda.beamline.name") + "/scripts/";
	
try:	
	print
	print "===================================================================";
	clientStartTime=ctime();
	print "The latest client was started at: " + clientStartTime;
	
#	execfile(gdaScriptDir + "BeamlineI07/useMotors.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Client script Error"
	logger.dump("---> ", exceptionType, exception, traceback)
	

try:	
	#Pilatus path update
	print
	print "===================================================================";
	pil1.setFile();
	pil2.setFile();
	pil3.setFile();
	
#	execfile(gdaScriptDir + "BeamlineI07/useMotors.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Client script Error when updating Pilatus image path"
	logger.dump("---> ", exceptionType, exception, traceback)
	

print "==================================================================="; print; print;
