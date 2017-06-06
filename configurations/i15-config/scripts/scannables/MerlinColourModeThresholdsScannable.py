from gda.device.scannable import ScannableBase
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.scannable.epics.PvManager import PvManager

class MerlinColourModeThresholdsScannable(ScannableBase):
    def __init__(self, name, pvManager):
        self.name = name
        self.pvManager = PvManager() # Just to get PyDev completion
        self.pvManager = pvManager
        
        self.setName(name);
        self.setInputNames(['OperatingEnergy', 'ThresholdEnergy0', 'ThresholdEnergy1', 'ThresholdEnergy2', 'ThresholdEnergy3',
                                               'ThresholdEnergy4', 'ThresholdEnergy5', 'ThresholdEnergy6', 'ThresholdEnergy7'])
        self.setExtraNames([]);
        self.setOutputFormat(['%6.3f'] * (len(self.getInputNames()) + len(self.getExtraNames())))
        self.setLevel(1)
        
        self.verbose = False
        self.requestedEnergies = [0.0] * len(self.getInputNames())
        
        self.TIMEOUT=5

    def __repr__(self):
        return "%s(name=%r, pvManager=%r)" % (self.__class__.__name__, self.name, self.pvManager)

    # Either getPosition or rawGetPosition is required for default implementation of __str__():
    def getPosition(self):
        return [float(self.pvManager[self.inputNames[0]+'_RBV'].caget())
               ,float(self.pvManager[self.inputNames[1]+'_RBV'].caget())
               ,float(self.pvManager[self.inputNames[2]+'_RBV'].caget())
               ,float(self.pvManager[self.inputNames[3]+'_RBV'].caget())
               ,float(self.pvManager[self.inputNames[4]+'_RBV'].caget())
               ,float(self.pvManager[self.inputNames[5]+'_RBV'].caget())
               ,float(self.pvManager[self.inputNames[6]+'_RBV'].caget())
               ,float(self.pvManager[self.inputNames[7]+'_RBV'].caget())
               ,float(self.pvManager[self.inputNames[8]+'_RBV'].caget())
               ]

    def asynchronousMoveTo(self, new_energies):
        if len(new_energies) != len(self.requestedEnergies):
            raise ValueError("Invalid arguments: new_energies must be %d elements long: %r" %
                             (len(self.requestedEnergies), new_energies))

        if any(map(lambda x: x<0 and x != None, new_energies)):
            raise ValueError("Invalid arguments: new_energies must be positive or None: %r" % (new_energies))

        for i in xrange(len(self.requestedEnergies)):
            if new_energies[i] != None:
                self.pvManager[self.inputNames[i]].caput(self.TIMEOUT, float(new_energies[i]))
                self.requestedEnergies[i] = float(new_energies[i])

    def atScanStart(self):
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))

    def atScanEnd(self):
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))

    def atCommandFailure(self):
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))
        self.requestedEnergies = self.getPosition()

    def stop(self): # This is required because Interrupt Scan Gracefully calls stop, but not atCommandFailure
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))
        self.requestedEnergies = self.getPosition()

    def isBusy(self):
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))
        positions = map(lambda x,y: abs(x-y)>0.001, self.requestedEnergies, self.getPosition())
        if self.verbose:
            simpleLog("requested=%r ; current=%r ; positions=%r ; any=%r" % (self.requestedEnergies, self.getPosition(), positions, any(positions)))
        return any(positions)

    def pfuncname(self):
        import traceback
        return "%s" % traceback.extract_stack()[-2][2]

# mcts=scannables.MerlinColourModeThresholdsScannable.MerlinColourModeThresholdsScannable('mcts',
#    PvManager(pvroot='BL15I-EA-DET-18:Merlin1:'))
