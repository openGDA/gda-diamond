print "running the wire scan script"

# set up some things first
from gda.data import NumTracker
from gda.data import PathConstructor
import scisoftpy as dnp
i22NumTracker = NumTracker("i22");

for z in dnp.arange (-55, 0, 1):
	pos mfstage_z z
	rscan mfstage_x -0.2 0.2 0.005 topup d10d2 
	go edge
	
	size = edge.result.fwhm
	edge_pos = edge.result.pos	
	
	filenum = str(i22NumTracker.getCurrentFileNumber())
	file = open(PathConstructor.createFromDefaultProperty()+"mfstage_wirescans_"+time.strftime("%Y-%m-%d")+".dat","a")
	file.write(filenum+" , %f , %f , %f\n" % (z, size, edge_pos))
	file.close()
	
print "all done"