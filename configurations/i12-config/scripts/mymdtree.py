from gda.analysis.io import *
from gda.data.nexus.tree import *
from uk.ac.diamond.scisoft.analysis.plotserver import *
from gda.analysis import ScanFileHolder
from gda.factory import Finder

st = NexusTreeNodeSelection.createTreeForAllData() # default does not load data
s = ScanFileHolder()
#s.load(CBFLoader("../images/myoglobin.cbf"))
#s.load(NexusLoader("../images/base-12.nxs"))
#s.load(NexusLoader("/dls/tmp/1.nxs", st, st, None))
#s.load(NexusLoader("/home/zjt21856/nexus.nxs", st, st, None))
s.load(NexusLoader("/dls/i12/data/2009/ee2214-1/749.nxs", st, st, None))

s.info()
n = s.getNexusTree()
d = DataBean()
d.addNexusTree(n)
a = Finder.find("plot_server")

a.setData("nexusTreeViewer", d)


