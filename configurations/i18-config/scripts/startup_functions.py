import os
from gda.configuration.properties import LocalProperties
from gda.data import PathConstructor
print "pdir(object) - pretty print object attributes"
def pdir(name):
	pprint(dir(name))

print "plist(list)  - pretty print a list, or other container"
def plist(list):
	for item in list:
		pprint(item)


print "datadir        - gets the current data directory"
print "datadir 'newpath' - changes the current data directory"

def datadir(newpath=None):
	if newpath==None:
		#return LocalProperties.getPath("gda.data.scan.datawriter.datadir",None)
		return PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
	else:
		if not os.path.exists(newpath):
			print "WARNING: This directory does NOT exist! (pointing to it anyway though)"
		LocalProperties.set("gda.data.scan.datawriter.datadir", newpath)
		#return LocalProperties.getPath("gda.data.scan.datawriter.datadir",None)
		return PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")


GeneralCommands.alias("datadir")