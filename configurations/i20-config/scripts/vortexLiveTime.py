def testVortexWiredCorrectly():
    from gda.device import  DeviceException
    from random import randrange
    import math, time
    print "Testing if Vortex wired correctly by doing a quick collection with ionchambers and Vortex..."
    collecttime = randrange(1,3)
    ionchambers.setCollectionTime(collecttime)
    xmapMca.collectData()
    ionchambers.collectData()
    ionchambers.waitWhileBusy()
    time.sleep(1)
    xmapTime = xmapMca.getRealTime()
    if xmapTime == 0.0:
        print "Vortex not wired correctly: the test showed that the vortex was not run. It is not being triggered by the tfg."
        return
#    print float(collecttime)
#    print float(xmapTime)
    if math.fabs(1-float(collecttime)/float(xmapTime)) > 0.2:
        print "Xmap live time disagrees with ion chambers collection time - is Xmap configured correctly or receiving timing signal correctly?"
        return
    print "Vortex passed test: real collection time matches ionchambers"
