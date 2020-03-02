from datetime import datetime, timedelta
from gda.device.scannable import ScannableMotionBase
from gdascripts.messages.handle_messages import simpleLog
import threading

class RockerThread(threading.Thread):

    def __init__(self, name, scannable, centre, delta, rockCount, parent):
        super(RockerThread, self).__init__()
        self.name = name
        self.scannable = scannable
        self.centre = centre
        self.delta = delta
        self.rockCount = rockCount
        self.running = True
        self.parent = parent
        self.movelog_time = datetime.now()

    def moveTo(self, position):
        help_stop_me = ", to stop rocking run 'pos %s [%f 0]'" % (self.parent.name, self.centre)
        if self.parent.verbose:
            msg = self.name + ": Moving " + self.scannable.name + " to %f (%d)" % (position, self.rockCount) + help_stop_me
            simpleLog(msg)
        elif (datetime.now() - self.movelog_time) > timedelta(seconds=30):
            simpleLog("Continuously rocking" + help_stop_me)
            self.movelog_time = datetime.now()
        self.scannable.moveTo(position)

    def run(self):
        if self.parent.verbose:
            simpleLog(self.name + ": Running...")
        while (self.running):
            self.moveTo(self.centre-self.delta)
            self.rockCount+=1
            if not self.running or self.delta == 0:
                break
            self.moveTo(self.centre+self.delta)
            self.rockCount+=1
        simpleLog(self.name + ": Stopped.")

class ContinuouslyRockingScannable(ScannableMotionBase):

    def __init__(self, name, scannable):
        self.scannable=ScannableMotionBase()
        self.setName(name)
        assert len(scannable.getInputNames())==1
        assert len(scannable.getExtraNames())==0
        assert len(scannable.getOutputFormat())==1
        self.setInputNames(["centre", "delta"])
        self.setExtraNames(["rocks"])
        self.setOutputFormat([scannable.getOutputFormat()[0], "%3.3f", "%d"])
        self.scannable = scannable
        self.setLevel(5)
        self.rockCount = 0
        self.thread=None
        self.runningAtStart = False
        self.verbose=False

    def atScanStart(self):
        self.runningAtStart = self.thread and self.thread.running
        self.rockCount = 0
        if self.verbose:
            simpleLog("atScanStart() %s (%s), runningAtStart = %r" % (self.name, self.scannable.name, self.runningAtStart))

    def stop(self):
        if self.thread:
            self.thread.running=False
        self.scannable.stop()
        if self.verbose:
            simpleLog("stop() %s (%s), runningAtStart = %r" % (self.name, self.scannable.name, self.runningAtStart))

    def atScanEnd(self):
        if self.verbose:
            simpleLog("atScanEnd() %s (%s), runningAtStart = %r" % (self.name, self.scannable.name, self.runningAtStart))
        if not self.runningAtStart:
            self.stop()
            self.thread.join()
            self.scannable.moveTo(self.thread.centre)

    def getPosition(self):
        if self.thread and self.thread.running:
            return [ self.thread.centre, self.thread.delta, self.thread.rockCount ]
        return [ self.scannable.getPosition(), 0, self.rockCount ]

    def asynchronousMoveTo(self, position):
        assert(len(position)==2)
        if self.verbose:
            simpleLog("asynchronousMoveTo(%r) %s (%s), runningAtStart = %r" % (position, self.name, self.scannable.name, self.runningAtStart))
        if self.thread and self.thread.running:
            if   (abs(self.thread.centre-position[0]) < 0.00001 and
                   abs(self.thread.delta-position[1]) < 0.00001):
                simpleLog(self.name + ": New positions (%r) same as old." % (position))
                return
            self.stop()
            self.thread.join()

        self.thread=RockerThread(self.name, self.scannable, position[0], position[1], self.rockCount, self)
        simpleLog(self.name + ": Starting RockerThread...")
        self.thread.start()

    def isBusy(self):
        return False

#    def __str__(self):
#        if self.thread and self.thread.running:
#            print ScannableMotionBase.__str__(self) + " (rocking, %d rocks)" % self.rockCount
#        else:
#            print ScannableMotionBase.__str__(self) + " (not rocking, %d rocks)" % self.rockCount
