from gda.analysis import ScanFileHolder, RCPPlotter, DataSet
from gda.data import PathConstructor,NumTracker
from gda.data.nexus.tree import NexusTreeNodeSelection
from uk.ac.diamond.scisoft.analysis.io import NexusLoader

st = NexusTreeNodeSelection.createTreeForAllData() # default does not load data

def plotAll(point) :
	s = ScanFileHolder()

	# create the location of the last file
	filename = "%s/%d.nxs" % (PathConstructor.createFromDefaultProperty(), NumTracker("i12").getCurrentFileNumber())
	s.load(NexusLoader(filename, st, st, None))

	plots = []

	# build the array
	for i in range(23) :
		name = "EDXD_Element_%02d"% (i)
		print name
		ds = s.getAxis(name)[point,:]
		ds.setName(name)
		plots.append(ds)
		

	RCPPlotter.plot("Plot 1",DataSet.arange(plots[0].getDimensions()[0]), plots)


def plotOne(Number) :
	s = ScanFileHolder()

	# create the location of the last file
	filename = "%s/%d.nxs" % (PathConstructor.createFromDefaultProperty(), NumTracker("i12").getCurrentFileNumber())
	s.load(NexusLoader(filename, st, st, None))

	name = "EDXD_Element_%02d"% (Number)
	print name
	data = s.getAxis(name)

	plots = []

	print "building the array"
	# build the array	
	for i in range(data.getDimensions()[0]) :
		ds = s.getAxis(name)[i,:]
		ds.setName(str(i))
		plots.append(ds)		

	RCPPlotter.plot("Plot 1",DataSet.arange(plots[0].getDimensions()[0]), plots)

