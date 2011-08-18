import os
import math

from gda.configuration.properties import LocalProperties

#print "pdir(object) - pretty print object attributes"
#def pdir(name):
#	pprint(dir(name))

#print "plist(list)  - pretty print a list, or other container"
#def plist(list):
#	for item in list:
#		pprint(item)


#print "datadir        - gets the current data directory"
#print "datadir 'newpath' - changes the current data directory"

def frange(limit1, limit2, increment):
	"""Range function that accepts floats (and integers).
	"""
#		limit1 = float(limit1)
#		limit2 = float(limit2)
	increment = float(increment)
	count = int(math.ceil((limit2 - limit1) / increment))
	result = []
	for n in range(count):
		result.append(limit1 + n * increment)
	return result


#def datadir(newpath=None):
#	if newpath==None:
#		return LocalProperties.getPath("gda.data.scan.datawriter.datadir",None)
#	else:
#		if not os.path.exists(newpath):
#			print "   WARNING: This directory does NOT exist! (pointing to it anyway though)"
#
#		## Set gda datadir ##
#		print "   Setting gda.data.scan.datawriter.datadir preference..."
#		LocalProperties.set("gda.data.scan.datawriter.datadir", newpath)

		## Set IPP datadir ##
#		new_windows_path = newpath.replace("/dls/b16/data", "N:")+"/ippimages"
#		print "   Setting ippws4.outputFolderRoot to: ", new_windows_path
#		global ippws4
#		ippws4.setOutputFolderRoot(new_windows_path)
		
		## Try to set pilatus scannable (it may not exist) ##
#		try:
#			global pil
#			pil.setFilePath(newpath + '/pilatus100k/')
#		except NameError, e:
#			print "   No pilatus (pil) scannable found to modify"
#		
#		return LocalProperties.getPath("gda.data.scan.datawriter.datadir",None)

# def setvisit(visitString=None)
# Should depend on a variable somewhere that stores the visit string

#GeneralCommands.alias("datadir")
