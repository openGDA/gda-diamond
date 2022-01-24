from datetime import datetime
from commands import getoutput
from os import listdir, path

from gda.configuration.properties import LocalProperties


if LocalProperties.get("gda.mode") == "live":

	visits = ('/dls/i07/data/' + str(datetime.today().year))
	print "Setting i07user permissions for all visits in " + visits
	
	dirs = listdir(visits)
	
	for d in dirs:
		v = visits + "/" + d
		if(d[0:2] != 'cm' and d[0:2] != 'sw' and path.isdir(v) and not path.islink(v)):
			getoutput("setfacl -n -m u:i07user:rx " + v)
			getoutput("setfacl -n -m u:i07user:rx " + v + "/pilatus?")
			getoutput("setfacl -n -m u:i07user:rwx " + v + "/processing")
			getoutput("setfacl -n -m d:u:i07user:rx " + v)
			getoutput("setfacl -n -m d:u:i07user:rx " + v + "/pilatus?")
			getoutput("setfacl -n -m d:u:i07user:rwx " + v + "/processing")
