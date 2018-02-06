'''
file: adccontrol.py
This module defines ADC Control class that provides methods for setting ADC parameters for data collection.
To instantiate you must name the object as "adc2" or "adc1"

Created on 15 Feb 2011
updated on 22 June 2011
Created on 2 Feb 2012

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from gda.factory import FactoryException
from gov.aps.jca import CAException
import sys

#EPICS PVs for control of ADC settings
adcmodepv="BL11I-EA-ADC-02:MODE"
adcclockratepv="BL11I-EA-ADC-02:CLOCKRATE"
adcextclockpv="BL11I-EA-ADC-02:EXTCLOCK"
adcenablepv="BL11I-EA-ADC-02:ENABLE"
adcreenablepv="BL11I-EA-ADC-02:REENABLE"
adcsofttrigpv="BL11I-EA-ADC-02:SOFTTRIGGER.VAL"
adcsamplespv="BL11I-EA-ADC-02:SAMPLES:OUT"
adcoffsetpv="BL11I-EA-ADC-02:OFFSET:OUT"
adcaveragepv="BL11I-EA-ADC-02:AVERAGE:OUT"
#EPICS key-value enum setting
adcmode={ 0:"Continuous",1:"Trigger",2:"Gate"}
adcclockrate={"1 Hz":0, "2 Hz":1,"5 Hz":2,"10 Hz":3, "20 Hz":4,"50 Hz":5,"100 Hz":6, "200 Hz":7,"500 Hz":8, "1 kHz":9, "2 kHz":10,"5 kHz":11, "10 kHz":12, "20 kHz":13,"50 kHz":14,"110 kHz":15}
adcextclock={"Internal":0, "External":1}
adcenable={"Disabled":0,"Enabled":1}
adcreenable={ "Manual":0,"Auto":1}
adcsofttrig={"Done":0,"Busy":1}


class AdcControl(ScannableMotionBase):
    
    def __init__(self, name):
        self.setName(name)
        num = int(name[-1])
        #EPICS PVs
        mode="BL11I-EA-ADC-0%d:MODE" % num
        rate="BL11I-EA-ADC-0%d:CLOCKRATE" % num
        enable="BL11I-EA-ADC-0%d:ENABLE" % num
        samples="BL11I-EA-ADC-0%d:SAMPLES:OUT" % num
        clock="BL11I-EA-ADC-0%d:EXTCLOCK" % num
        reenable="BL11I-EA-ADC-0%d:REENABLE" % num
        offset="BL11I-EA-ADC-0%d:OFFSET:OUT" % num
        average="BL11I-EA-ADC-0%d:AVERAGE:OUT" % num
        softtrig="BL11I-EA-ADC-0%d:SOFTTRIGGER.VAL" % num

        self.setInputNames(["ADC Mode","Clock Rate","Enable","Samples"])
        self.setExtraNames([])
        self.setOutputFormat(["%s","%s","%s","%d"])
        self.mode=CAClient(mode)
        self.rate=CAClient(rate)
        self.enableField=CAClient(enable)
        self.samples=CAClient(samples)
        self.clock=CAClient(clock)
        self.reenable=CAClient(reenable)
        self.adcoffset=CAClient(offset)
        self.average=CAClient(average)
        self.softtrig=CAClient(softtrig)
        
    def continuousMode(self):
        try:
            if not self.mode.isConfigured():
                self.mode.configure()
            self.mode.caput(0)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.mode.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.mode.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def triggerMode(self):
        try:
            if not self.mode.isConfigured():
                self.mode.configure()
            self.mode.caput(1)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.mode.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.mode.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def gateMode(self):
        try:
            if not self.mode.isConfigured():
                self.mode.configure()
            self.mode.caput(2)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.mode.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.mode.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setMode(self, name):
        try:
            if not self.mode.isConfigured():
                self.mode.configure()
            self.mode.caput([key for key, value in adcmode.iteritems() if value==name][0])
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.mode.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.mode.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getMode(self):
        try:
            if not self.mode.isConfigured():
                self.mode.configure()
            return adcmode[int(self.mode.caget())]
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.mode.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.mode.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setClockRate(self, rate):
        try:
            if not self.rate.isConfigured():
                self.rate.configure()
            self.rate.caput(adcclockrate[rate])
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.rate.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.rate.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getClockRate(self):
        try:
            if not self.rate.isConfigured():
                self.rate.configure()
            return [key for key, value in adcclockrate.iteritems() if value==int(self.rate.caget())][0]
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.rate.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.rate.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def enable(self):
        try:
            if not self.enableField.isConfigured():
                self.enableField.configure()
            self.enableField.caput(adcenable["Enabled"])
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.enableField.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.enableField.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        
    def disable(self):
        try:
            if not self.enableField.isConfigured():
                self.enableField.configure()
            self.enableField.caput(adcenable["Disabled"])
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.enableField.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.enableField.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    
    def setState(self, name):
        try:
            if not self.enableField.isConfigured():
                self.enableField.configure()
            self.enableField.caput(adcenable[name])
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.enableField.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.enableField.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getState(self):
        try:
            if not self.enableField.isConfigured():
                self.enableField.configure()
            return [key for key, value in adcenable.iteritems() if value==int(self.enableField.caget())][0]
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.enableField.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.enableField.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        
    def getSamples(self):
        try:
            if not self.samples.isConfigured():
                self.samples.configure()
            return int(self.samples.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.samples.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.samples.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    
    def setSamples(self, num):
        try:
            if not self.samples.isConfigured():
                self.samples.configure()
            self.samples.caput(num)
        except FactoryException, e:
            print "create channel error: %s" % (self.samples.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.samples.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise

    def getAdcOffset(self):
        try:
            if not self.adcoffset.isConfigured():
                self.adcoffset.configure()
            return int(self.adcoffset.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.adcoffset.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.adcoffset.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    
    def setAdcOffset(self, num):
        try:
            if not self.adcoffset.isConfigured():
                self.adcoffset.configure()
            self.adcoffset.caput(num)
        except FactoryException, e:
            print "create channel error: %s" % (self.adcoffset.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.adcoffset.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise

    def getAverage(self):
        try:
            if not self.average.isConfigured():
                self.average.configure()
            return int(self.average.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.average.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.average.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    
    def setAverage(self, num):
        try:
            if not self.average.isConfigured():
                self.average.configure()
            self.average.caput(num)
        except FactoryException, e:
            print "create channel error: %s" % (self.average.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.average.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise

    def internalClock(self):
        try:
            if not self.clock.isConfigured():
                self.clock.configure()
            self.clock.caput(adcextclock["Internal"])
        except FactoryException, e:
            print "create channel error: %s" % (self.clock.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.clock.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise
        
    def externalClock(self):
        try:
            if not self.clock.isConfigured():
                self.clock.configure()
            self.clock.caput(adcextclock["External"])
        except FactoryException, e:
            print "create channel error: %s" % (self.clock.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.clock.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise

    def manual(self):
        try:
            if not self.reenable.isConfigured():
                self.reenable.configure()
            self.reenable.caput(adcreenable["Manual"])
        except FactoryException, e:
            print "create channel error: %s" % (self.reenable.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.reenable.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise
        
    def auto(self):
        try:
            if not self.reenable.isConfigured():
                self.reenable.configure()
            self.reenable.caput(adcreenable["Auto"])
        except FactoryException, e:
            print "create channel error: %s" % (self.reenable.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.reenable.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise

    def softStart(self):
        try:
            if not self.softtrig.isConfigured():
                self.softtrig.configure()
            self.softtrig.caput(1)
        except FactoryException, e:
            print "create channel error: %s" % (self.softtrig.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.softtrig.getChannel().getName(),e)
        except:
            print "Unexpected error (%s):", sys.exc_info()[0]
            raise
        
    def atScanStart(self):
        '''enableField ADC data collection at scan start'''
        self.enableField() 
    
    def atScanEnd(self):
        '''disable ADC data collection at scan end'''
        self.disable()
    
    def getPosition(self):
        try:
            return self.getMode(),self.getClockRate(), self.getState(),self.getSamples()
        except:
            print "failed to get tuple data: ", sys.exc_info()[0]
            raise

    def asynchronousMoveTo(self,new_position):
        try:
            self.setMode(new_position[0])
            self.setClockRate(new_position[1])
            self.setState(new_position[2])
            self.setSamples(new_position[3])
        except:
            print "error ADC acquisition (%s): %f" % (sys.exc_info()[0], new_position)
            raise

    def isBusy(self):
        return (adcenable[self.getState()] == adcenable["Enabled"])
    
    def stop(self):
        '''disable ADC data collection at scan end'''
        #self.disable()
        pass

#    def toString(self):
#        return self.name + " : (" + str(self.getPosition()[0]), str(self.getPosition()[1]), str(self.getPosition()[2]), str(self.getPosition()[3])+")"

