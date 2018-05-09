import scisoftpy as dnp
d1=dnp.io.load("/scratch/dimax2.h5")["entry/instrument/detector/data"][...]
d2=d1.sum(0)
d3=dnp.array(d2)
dnp.plot.image(d3)
dnp.io.save("/scratch/dimax2_sum.tiff", d3, format="tiff", signed=False, bits=32)
del d1
del ds
del d2
del d3
