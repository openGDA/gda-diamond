print "running the wire scan script"

# set up some things first
from gda.data import NumTracker
from gda.jython import InterfaceProvider
import scisoftpy as dnp
i22NumTracker = NumTracker("i22");

for z in dnp.arange (-40, 40, 2):
	pos mfstage_z z
	rscan mfstage_x -0.15 0.15 0.001 topup d10d2 
	go edge
	
	size = edge.result.fwhm
	edge_pos = edge.result.pos	
	
	filenum = str(i22NumTracker.getCurrentFileNumber())
	file = open("/mfstage_wirescans_"+time.strftime("%Y-%m-%d")+".dat","a")
	file.write(filenum+" , %f , %f , %f\n" % (z, edge_pos, size))
	file.close()
	
print "all done"