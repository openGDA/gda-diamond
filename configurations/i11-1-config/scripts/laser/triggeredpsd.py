'''
Created on 25 Jan 2013

@author: fy65
'''
pos fastshutter "OPEN"
# switch off flat field correct to speed up acquisition
mythen_data_converter.setFlatFieldData(None)
#frange(start, stop, step)
for sp in frange(23.1, 31.1, 0.25):
    # move motor
    tlx.moveTo(sp)
    #make PSD ready to capture multiple frames using one trigger per frame
    #mythen.cmulti(numFrames, delayBeforeFrames, exposureTime)
    print "Please start trigger pulses from Function generator at sample position: %f " % float(tlx.getPosition())
    for i in range(1,11,1):
        mythen.cmulti(100, 0.00004, 0.001)
        sleep(1)
     #start function generator to send pulse
print "All done."
