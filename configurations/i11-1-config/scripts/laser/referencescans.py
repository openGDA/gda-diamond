'''
Created on 25 Jan 2013

@author: tni13765
'''

pos fastshutter "OPEN"
# switch off flat field correct to speed up acquisition
mythen_data_converter.setFlatFieldData(None)
#frange(start, stop, step)
for sp in frange(23.1, 31.1, 0.25):
    # move motor
    tlx.moveTo(sp)
    # perform 1 exposure 
    psd 20
    print sp
print "All done."