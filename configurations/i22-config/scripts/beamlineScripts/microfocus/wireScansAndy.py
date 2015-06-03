print "running the wire scan script"

# set up some things first
from gda.data import NumTracker
from gda.data import PathConstructor
import scisoftpy as dnp
i22NumTracker = NumTracker("i22");

for mfs_z in dnp.arange (-44, -24, 2):
	pos mfstage_z mfs_z
	rscan mfstage_x -0.3 0.3 0.002 topup d10d1 
	go edge
	
	size = edge.result.fwhm
	edge_pos = edge.result.pos	
	
	filenum = str(i22NumTracker.getCurrentFileNumber())
	file = open(PathConstructor.createFromDefaultProperty()+"mfstage_wirescans_"+time.strftime("%Y-%m-%d")+".dat","a")
	file.write(filenum+" , %f , %f , %f\n" % (mfs_z, size, edge_pos))
	file.close()
	
print "all done"