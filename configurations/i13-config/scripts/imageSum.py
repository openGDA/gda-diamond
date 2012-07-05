from gda.util.hdf5 import Hdf5Helper
d1=Hdf5Helper().readDataSet("/scratch/dimax2.h5","entry/instrument/detector","data")
ds=Hdf5Helper().createDataSet(d1,False)
d2=ds.sum(0)
import scisoftpy as dnp
d3=dnp.array(d2)
dnp.plot.image(d3)
dnp.io.save("/scratch/dimax2_sum.tiff", d3, format="tiff", signed=False, bits=32)
del d1
del ds
del d2
del d3
