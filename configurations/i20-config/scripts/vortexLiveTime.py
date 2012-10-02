
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
#    print float(collecttime)
#    print float(xmapTime)
    if math.fabs(1-float(collecttime)/float(xmapTime)) > 0.2:
        raise DeviceException("Xmap live time disagrees with ion chambers collection time - is Xmap configured correctly or receiving timing signal correctly?")
    print "Vortex passed test: real collection time matches ionchambers"
