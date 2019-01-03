'''
Created on 29 Jan 2014

@author: fy65
'''
from time import sleep
from gda.configuration.properties import LocalProperties
from gda.data import NumTracker
scanNumTracker=NumTracker(LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME))
scanNumTracker.incrementNumber()

EXPOSURETIME=120 #seconds
TARGETCOUNT=100000
ONEMINUTECOUNT=1000
DELTAMIN=-15.0
DELTAMAX=77.0
scancount=0
Tolerance=0.1
NUMBEROFSCANS=TARGETCOUNT/ONEMINUTECOUNT*60/EXPOSURETIME
print "Number of scans to do: %d, total time taken: %f" % (NUMBEROFSCANS, NUMBEROFSCANS*EXPOSURETIME)
mythen.configure()  # @UndefinedVariable
mythen.atScanStart()  # @UndefinedVariable
mythen.setCollectionTime(EXPOSURETIME+10)  # @UndefinedVariable
delta.moveTo(DELTAMIN)  # @UndefinedVariable
delta.setSpeed((DELTAMAX-DELTAMIN)/(EXPOSURETIME))  # @UndefinedVariable
target=DELTAMAX
for i in range(NUMBEROFSCANS):
    sleep(5)
    if scancount % 2==0:
        target=DELTAMAX
    else:
        target=DELTAMIN
    startPosition=float(delta.getPosition())  # @UndefinedVariable
    delta.asynchronousMoveTo(target)  # @UndefinedVariable
    mythen.collectData()  # @UndefinedVariable
    sleep(1)
    while mythen.isBusy():  # @UndefinedVariable
        sleep(1)
    currentPosition=float(delta.getPosition())  # @UndefinedVariable
    if currentPosition > (target-Tolerance) and currentPosition < (target+Tolerance):
        scancount= scancount+1
        #mythen.atScanEnd()
    else:
        delta.stop()  # @UndefinedVariable
        print "stop delta motor."
        sleep(3)
        print "move delta to last start position"
        delta.moveTo(startPosition)  # @UndefinedVariable
        print "Number of scans still to do: %d, total time left: %f" % (NUMBEROFSCANS-scancount, (NUMBEROFSCANS-scancount)*EXPOSURETIME)
print "flat field data collection completed."
    
