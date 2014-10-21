from gda.analysis import RCPPlotter
from org.eclipse.dawnsci.analysis.dataset.impl import DoubleDataset

pp=RCPPlotter()

d=DoubleDataset.arange(10000)
d.shape = [100,100]

pp.imagePlot("Area Detector", d)


pp.scanForImages("Image Explorer", "/dls/i07/data/2010/cm1896-1/demoImages")


