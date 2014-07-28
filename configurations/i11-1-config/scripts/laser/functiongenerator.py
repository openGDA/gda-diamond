'''
file: functiongenerator.py

This module defines class that enables controls of agilent33220A function generator via EPICS.
To instantiate you must name the object in the format of "name" plus a number such as "tfg1" or "tfg2".
The number must map onto TFG device available in EPICS IOCs.

Created on 15 Feb 2011
updated on 22 June 2011
updated on 28 Feb 2012 - make doc clearer

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from gda.factory import FactoryException
from gov.aps.jca import CAException
import sys

class FunctionGenerator(ScannableMotionBase):
    
    def __init__(self, name):
        self.setName(name)
        num = int(name[-1])
        #EPICS PVs
        func="BL11I-EA-FGEN-0%d:FUNC" % num
        output="BL11I-EA-FGEN-0%d:OUT" % num
        freq="BL11I-EA-FGEN-0%d:FREQ" % num
        freqrbv="BL11I-EA-FGEN-0%d:FREQ:RBV" % num
        amp="BL11I-EA-FGEN-0%d:AMP" % num
        amprbv="BL11I-EA-FGEN-0%d:AMP:RBV" % num
        offset="BL11I-EA-FGEN-0%d:OFF" % num
        offsetrbv="BL11I-EA-FGEN-0%d:OFF:RBV" % num
        sym="BL11I-EA-FGEN-0%d:SYMM" % num
        symrbv="BL11I-EA-FGEN-0%d:SYMM:RBV" % num
        
        dutycyc="BL11I-EA-FGEN-0%d:DCYC" % num
        dutycycrbv="BL11I-EA-FGEN-0%d:DCYC:RBV" % num
        trigger="BL11I-EA-FGEN-0%d:TRIGSRC" % num
        burstmode="BL11I-EA-FGEN-0%d:BURSTMODE" % num
        burstncyc="BL11I-EA-FGEN-0%d:BURSTNCYC" % num
        burstncycrbv="BL11I-EA-FGEN-0%d:BURSTNCYC:RBV" % num
        burststate="BL11I-EA-FGEN-0%d:BURST" % num
        disable="BL11I-EA-FGEN-0%d:DISABLE" % num        
        
        self.setInputNames(["frequency","amplitude","shift","symmetry"])
        self.setExtraNames([])
        self.function=CAClient(func)
        self.output=CAClient(output)
        self.frequency=CAClient(freq)
        self.frequencyrbv=CAClient(freqrbv)
        self.amplitude=CAClient(amp)
        self.amplituderbv=CAClient(amprbv)
        self.shiftcli=CAClient(offset)
        self.shiftrbv=CAClient(offsetrbv)
        self.symmetry=CAClient(sym)
        self.symmetryrbv=CAClient(symrbv)
        self.dutycycle=CAClient(dutycyc)
        self.dutycyclerbv=CAClient(dutycycrbv)
        self.triggersrc=CAClient(trigger)
        self.burstmode=CAClient(burstmode)
        self.burstncyc=CAClient(burstncyc)
        self.burstncycrbv=CAClient(burstncycrbv)
        self.burststate=CAClient(burststate)
        self.disable=CAClient(disable)
        
    # function generator controls
    def setFunction(self, function):
        try:
            if not self.function.isConfigured():
                self.function.configure()
            self.function.caputWait(function)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.function.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.function.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getFunction(self):
        try:
            if not self.function.isConfigured():
                self.function.configure()
            return float(self.function.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.function.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.function.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setOutput(self, output):
        try:
            if not self.output.isConfigured():
                self.output.configure()
            self.output.caputWait(output)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.output.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.output.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getOutput(self):
        try:
            if not self.output.isConfigured():
                self.output.configure()
            return float(self.output.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.output.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.output.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setFrequency(self, frequency):
        try:
            if not self.frequency.isConfigured():
                self.frequency.configure()
            self.frequency.caputWait(frequency)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.frequency.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.frequency.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getFrequency(self):
        try:
            if not self.frequencyrbv.isConfigured():
                self.frequencyrbv.configure()
            return float(self.frequencyrbv.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.frequencyrbv.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.frequencyrbv.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setAmplitude(self, amplitude):
        try:
            if not self.amplitude.isConfigured():
                self.amplitude.configure()
            self.amplitude.caputWait(amplitude)
        except FactoryException, e:
            print "create channel error: %s" % (self.amplitude.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.amplitude.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise

    def getAmplitude(self):
        try:
            if not self.amplituderbv.isConfigured():
                self.amplituderbv.configure()
            return float(self.amplituderbv.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.amplituderbv.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.amplituderbv.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        
    def setShift(self, amplitude):
        try:
            if not self.shiftcli.isConfigured():
                self.shiftcli.configure()
            self.shiftcli.caputWait(amplitude)
        except FactoryException, e:
            print "create channel error: %s" % (self.shiftcli.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.shiftcli.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise

    def getShift(self):
        try:
            if not self.shiftrbv.isConfigured():
                self.shiftrbv.configure()
            return float(self.shiftrbv.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.shiftrbv.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.shiftrbv.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

       
    def setSymmetry(self, value):
        try:
            if not self.symmetry.isConfigured():
                self.symmetry.configure()
            self.symmetry.caputWait(value)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.symmetry.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.symmetry.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getSymmetry(self):
        try:
            if not self.symmetryrbv.isConfigured():
                self.symmetryrbv.configure()
            return float(self.symmetryrbv.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.symmetryrbv.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.symmetryrbv.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
   
    def setDutyCycle(self, value):
        try:
            if not self.dutycycle.isConfigured():
                self.dutycycle.configure()
            self.dutycycle.caputWait(value)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.dutycycle.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.dutycycle.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getDutyCycle(self):
        try:
            if not self.dutycyclerbv.isConfigured():
                self.dutycyclerbv.configure()
            return float(self.dutycyclerbv.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.dutycyclerbv.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.dutycyclerbv.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setTriggerSource(self, src):
        ''' set the trigger source for the function generator:
        0 - IMM, 1 - EXT, 2 - BUS.
        '''
        try:
            if not self.triggersrc.isConfigured():
                self.triggersrc.configure()
            self.triggersrc.caputWait(src)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.triggersrc.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.triggersrc.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getTriggerSource(self):
        ''' get the trigger source for the function generator:
        0 - IMM, 1 - EXT, 2 - BUS.
        '''
        try:
            if not self.triggersrc.isConfigured():
                self.triggersrc.configure()
            return float(self.triggersrc.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.triggersrc.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.triggersrc.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setBurstMode(self, mode):
        ''' set the burst mode for the function generator:
        0 - TRIG, 1 - GAT.
        '''
        try:
            if not self.burstmode.isConfigured():
                self.burstmode.configure()
            self.burstmode.caputWait(mode)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.burstmode.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.burstmode.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getBurstMode(self):
        ''' get the trigger source for the function generator:
        0 - TRIG, 1 - GAT.
        '''
        try:
            if not self.burstmode.isConfigured():
                self.burstmode.configure()
            return float(self.burstmode.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.burstmode.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.burstmode.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setBurstState(self, state):
        ''' set the burst state for the function generator:
        0 - OFF, 1 - ON.
        '''
        try:
            if not self.burststate.isConfigured():
                self.burststate.configure()
            self.burststate.caputWait(state)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.burststate.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.burststate.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getBurstState(self):
        ''' get the trigger source for the function generator:
        0 - OFF, 1 - ON.
        '''
        try:
            if not self.burststate.isConfigured():
                self.burststate.configure()
            return float(self.burststate.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.burststate.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.burststate.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setBurstNCycle(self, value):
        try:
            if not self.burstncyc.isConfigured():
                self.burstncyc.configure()
            self.burstncyc.caputWait(value)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.burstncyc.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.burstncyc.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getBurstNCycle(self):
        try:
            if not self.burstncycrbv.isConfigured():
                self.burstncycrbv.configure()
            return float(self.burstncycrbv.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.burstncycrbv.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.burstncycrbv.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getTargetPosition(self):
        freq=0.0
        ampl=0.0
        off=0.0
        sym=0.0
        try:
            if not self.frequency.isConfigured():
                self.frequency.configure()
            freq=float(self.frequency.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.frequency.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.frequency.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        try:
            if not self.amplitude.isConfigured():
                self.amplitude.configure()
            ampl=float(self.amplitude.caget())
        except FactoryException, e:
            print "create channel error: %s" % (self.amplitude.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.amplitude.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise
        try:
            if not self.shiftcli.isConfigured():
                self.shiftcli.configure()
            off=float(self.shiftcli.caget())
        except FactoryException, e:
            print "create channel error: %s" % (self.shiftcli.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.shiftcli.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise
        try:
            if not self.symmetry.isConfigured():
                self.symmetry.configure()
            sym=float(self.symmetry.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.symmetry.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.symmetry.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        return freq,ampl,off,sym

    def atScanStart(self):
        '''switch on output'''
        self.setOutput(1) 
    
    def atScanEnd(self):
        '''switch off output'''
        self.setOutput(0)
    
    def getPosition(self):
        try:
            return self.getFrequency(),self.getAmplitude(), self.getShift(),self.getSymmetry()
        except:
            print "failed to get tuple data: ", sys.exc_info()[0]
            raise

    def asynchronousMoveTo(self,new_position):
        try:
            self.setFrequency(new_position[0])
            self.setAmplitude(new_position[1])
            self.setShift(new_position[2])
            self.setSymmetry(new_position[3])
        except:
            print "error moving shiftcli to position (%s): %f" % (sys.exc_info()[0], new_position)
            raise

    def isBusy(self):
        return (self.getPosition() != self.getTargetPosition())
    
    def stop(self):
        '''switch off output'''
        #self.setOutput(0)
        pass

#    def toString(self):
#        return self.name + " : (" + str(self.getPosition()[0]), str(self.getPosition()[1]), str(self.getPosition()[2]), str(self.getPosition()[3])+")"

