from gda.device.detector import PseudoDetector

#
# Class for wrapping the Xmap detector to output the data in an ascii file
#
# Important note: this was written in a hurry during beamtime so contains
# lots of hacks and hard-coded paths. Be sure to edit before use!
#
# Jonathan Rawle, 18 January 2018
#
from gda.epics import LazyPVFactory
from gda.data import NumTracker
from time import time
pvroot="ME13C-EA-DET-01:MCA1"
xmnt = NumTracker("xm_nt")

class XMapWrapper(PseudoDetector):

    def __init__(self, name, monitor):
        self.setName(name)
        self.monitor = monitor
        self.lpv = LazyPVFactory.newReadOnlyFloatArrayPV(pvroot)
        self.xmap_filename = ''
        self.counter = 0
        self.isCollecting = 0
        self.starttime = 0

    def collectData(self):
        self.isCollecting = 1
        self.starttime = time()
        self.monitor.collectData()
        self.isCollecting = 0

    def getStatus(self):
        if(time() < (self.starttime + self.getCollectionTime())):
            return 1
        return 0

    def readout(self):
        mcs_readout=self.lpv.get()
        xmfn = xmnt.getCurrentFileNumber()
        self.xmap_filename = '/dls/i07/data/2018/si17042-1/xmap/xmap' + str(xmfn) + '_' + str(self.counter) + '.dat'
        self.counter = self.counter + 1
        file = open(self.xmap_filename, 'w')
        energy = 0
        bin_width = 0.00125
        for i in mcs_readout:
            file.write(str(energy) + "\t" + str(i) + "\n")
            energy = energy + bin_width
        file.close()        
        return str(self.xmap_filename)
        # stuff here to write text file

    def setCollectionTime(self, time):
        self.monitor.setCollectionTime(time)
#        print "Collection time set to " + str(self.monitor.getCollectionTime())

    def getCollectionTime(self):
        return self.monitor.getCollectionTime()

    def getPosition(self):
        self.readout()
        return str(self.xmap_filename)      

    def asynchronousMoveTo(self, time):
        self.monitor.asynchronousMoveTo(time)

    def createsOwnFiles(self):
        return False;

    def toString(self):
        return self.getName() + ": " + str(self.xmap_filename);
