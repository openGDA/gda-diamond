'''
Created on 13 Jan 2017

@author: fy65
'''

from gdascripts.utils import frange, caget

outputFilename="/dls/i11/data/2017/cm16784-1/ang_20170113.angcal"
output_format="%.5f %d-mythen_1\n"
cl=CAClient()
f=open(outputFilename, "w")
for x in frange(78, -15, -0.1):
    delta.moveTo(x)
    psd 2
    cpos=float(delta.getPosition())
    filenumber=beamline.getFileNumber()
    f.write(output_format % (cpos, filenumber))
    f.flush()
f.close()
