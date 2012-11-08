from gdascripts.scannable.detector.ScalerSubsetScannable import ScalerSubsetScannable
from gda.epics import CAClient

class ScalerChannelAssigner(object):

    def __init__(self, namespace, scalerDetector, struckRootPv=None): # struckRootPv must end just before '.NM'
        self.namespace = namespace
        self.scaler = scalerDetector
        self.struckRootPv = struckRootPv

    def assign(self, channelNo, namelist):
        if isinstance(namelist, str):
            namelist = [namelist]
        allNames = ''
        for name in namelist:
            self.namespace[name] = ScalerSubsetScannable(name,self.scaler,[channelNo])
            allNames += name + '/'
        allNames = allNames[:-1]
    
        print "ch%i: %s" % (channelNo, allNames)
        if self.struckRootPv:
            pv = self.struckRootPv+'.NM%i' % channelNo
            print "caput %s %s"%(pv,allNames)
            cac = CAClient(pv)
            cac.configure()
            cac.caput(allNames)
            cac.clearup()