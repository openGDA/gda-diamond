from datetime import datetime, timedelta
from Diamond.energyScannableBase import EnergyScannableBase 
from gda.device.scannable import ScannableMotionBase, ScannableMotor
from org.slf4j import LoggerFactory
from time import sleep
import threading

class FollowerThread(threading.Thread):

    def __init__(self, parent):
        super(FollowerThread, self).__init__()
        self.parent = parent
        self._movelog_time = datetime.now()
        self.running = True

    def moveTo(self, energy_eV):
        idPosition = self.parent.follower_scannable.getIdPosition(energy_eV)
        if self.parent.verbose:
            if self.parent.follower_scannable.energyMode:
                msg = "Moving %s to %f (%r)" % (self.parent.follower_scannable.name, energy_eV, idPosition.gap)
                self.parent.logger.info(msg)
            else:
                msg = "Moving %s to %f (%r)" % (self.parent.follower_scannable.name, energy_eV, idPosition.jawphase)
                self.parent.logger.info(msg)
        if self.parent.follower_scannable.energyMode:
            self.parent.follower_scannable.id_gap.moveTo(idPosition.gap)
            #self.parent.follower_scannable.id_rowphase1.moveTo(idPosition.rowphase1)
            #self.parent.follower_scannable.id_rowphase2.moveTo(idPosition.rowphase2)
            #self.parent.follower_scannable.id_rowphase3.moveTo(idPosition.rowphase3)
            #self.parent.follower_scannable.id_rowphase4.moveTo(idPosition.rowphase4)
        else:
            self.parent.follower_scannable.id_jawphase.moveTo(idPosition.jawphase)
        self.parent.follower_scannable.last_energy_eV = energy_eV

    def run(self):
        if self.parent.verbose:
            self.parent.logger.info("Running...")
        while (self.running):
            followed = self.parent.followed_scannable.getPosition()
            follower = self.parent.follower_scannable.getPosition()[0]
            diff = abs(followed-follower) 
            if (diff > abs(self.parent.follower_tolerance)):
                self.moveTo(followed)
            if self.parent.verbose and (datetime.now() - self._movelog_time) > timedelta(seconds=5):
                self.parent.logger.info("%s following %s with a tolerance of %r (diff=%r)" % (self.parent.follower_scannable.name, self.parent.followed_scannable.name, self.parent.follower_tolerance, diff))
                self.parent.logger.info("Use 'pos %s 0' to stop it following" % (self.parent.name))
                self._movelog_time = datetime.now()
            if not self.running:
                break
            sleep(0.1)
                

        self.parent.logger.info("Stopped.")

class FollowerScannable(ScannableMotionBase):

    def __init__(self, name, followed_scannable, follower_scannable):
        self.logger = LoggerFactory.getLogger("FollowerScannable:%s" % name)
        self.followed_scannable=ScannableMotionBase()
        self.follower_scannable=ScannableMotionBase()
        
        assert len(followed_scannable.getInputNames())==1 and len(followed_scannable.getExtraNames())==0 and len(followed_scannable.getOutputFormat())==1
        #assert len(follower_scannable.getInputNames())==1 and len(follower_scannable.getExtraNames())==0 and len(follower_scannable.getOutputFormat())==1
        assert(issubclass(type(follower_scannable), EnergyScannableBase))
        assert(issubclass(type(followed_scannable), ScannableMotor))
        self.followed_scannable = followed_scannable
        self.follower_scannable = follower_scannable
        self.follower_tolerance = 0
        
        self.setName(name)
        self.inputNames = [name]
        self.extraNames = self.getExtraNames()
        self.outputFormat = self.getOutputFormat()
        self.setLevel(5)
        self.thread = None
        self.verbose = True

    def atScanStart(self):
        if self.thread and self.thread.running:
            self.stop()
        self.thread=FollowerThread(self)
        self.follower_tolerance=-1
        self.thread.start()
        self.logger.info("%s now following %s with a tolerance of %r ..." % (self.follower_scannable.name, self.followed_scannable.name, self.follower_tolerance))

    def stop(self):
        if self.thread and self.thread.running:
            self.logger.info("FollowerThread running, stopping thread...")
            self.thread.running = False
            self.follower_scannable.stop()
            self.thread.join()
            self.logger.info("...FollowerThread stopped.")
        else:
            self.logger.info("FollowerThread %r not running." % self.thread)

    def atScanEnd(self):
        self.stop()
        self.thread.join()
        #self.follower_scannable.moveTo(self.thread.centre)

    def getExtraNames(self): 
        return list(self.follower_scannable.getInputNames()) + list(self.follower_scannable.getExtraNames())

    def getOutputFormat(self):
        return ['%f'] + list(self.follower_scannable.getOutputFormat())

    def getPosition(self):
        follower = self.follower_scannable.getPosition()
        return [self.follower_tolerance] + list(follower) 

    def asynchronousMoveTo(self, position):
        self.follower_tolerance = position
        if position == 0:
            self.stop()
        elif self.thread and self.thread.running:
            self.logger.info("%s following %s now with a tolerance of %r ..." % (self.follower_scannable.name, self.followed_scannable.name, self.follower_tolerance))
        else:
            self.thread=FollowerThread(self)
            self.thread.start()
            self.logger.info("%s now following %s with a tolerance of %r ..." % (self.follower_scannable.name, self.followed_scannable.name, self.follower_tolerance))

    def isBusy(self):
        # If we have started the follower and we are before the first point in a scan then we are busy if the followed scannable is busy
        # This allows the scan mechanism to sync the move to the start positions for both follower and followed scannables.
        if self.thread and self.thread.running and self.follower_tolerance < 0:
            return self.followed_scannable.isBusy() and self.follower_scannable.isBusy()
        return False

""" This is a zie scannable (zero input and extra names) which allows the following mechanism to be turned on at the start of a
    continuous scan and off at the end. In this variant the tolerance must be set outside of a scan.
"""
class SilentFollowerScannable(FollowerScannable):

    def __init__(self, name, followed_scannable, follower_scannable, follower_tolerance):
        self.logger = LoggerFactory.getLogger("SilentFollowerScannable:%s" % name)
        FollowerScannable.__init__(self, name, followed_scannable, follower_scannable)
        
        self.follower_tolerance = follower_tolerance
        
        self.inputNames = []
        self.setLevel(5)
        self.verbose = True

    def atScanStart(self):
        if self.thread and self.thread.running:
            self.stop()
        self.thread=FollowerThread(self)
        self.thread.start()
        self.logger.info("%s now following %s with a tolerance of %r ..." % (self.follower_scannable.name, self.followed_scannable.name, self.follower_tolerance))

    def getExtraNames(self): 
        return []

    def getOutputFormat(self):
        return []

    def getPosition(self):
        return None
