''' file: tfg_peloop.py
This module implements PE loop experiment control and data collection logics and strategy. 
Experiment and data collection control are triggered use TFG2 signals acting as master.
X-ray diffraction patterns are collected from PSD detector using gated control and 
PE data across the sample are captured continuously using EPICS ADC at 50kHz (update at about 1 second, i.e. every 50000 samples)
along with the gate signal to identify the positions at which diffraction patterns are collected.
It support the following requirements:
1. It must collect maximum 40 data points over a whole PE Loop cycle, - input
2. The voltage range at which an X-ray diffraction is taken is limited to 1 volt - fixed,
3. settable PSD counting/exposure time, depending on samples - input - to TFG
4. settable voltage amplitude - input - to function generator
5. settable ramping cycle frequency - input - to function generator
6. allow for pre-cycles to be selected
At slow ramping rate (frequency <= 0.1Hz), only one cycle is required to produce 40 data points at 0.5 second exposure time 
as there is sufficient time for both counting and data saving;
At fast ramping rate a single diffraction pattern must be collected over multiple ramp cycles gated at exactly the same voltage level
 in the PELoop in order to produce sufficient counting (at 0.5 secodn exposure time) and 
 the diffraction pattern is saved only at end of the cycles.
For longer exposure time multiple frames collection are required and the data are summed together post the data collection.
Created on 27 Jan 2012 for TFG2 driven experiment
@author: fy65 '''
from gda.data import NumTracker, PathConstructor
from gda.device.scannable import ScannableBase
from gda.factory import Finder
from gda.jython.commands import GeneralCommands
from gda.jython.commands.Input import requestInput
from threading import Thread
from time import sleep, time
import math
import sys
import subprocess

scanNumTracker = NumTracker("tmp");
MYTHENREADOUTTIME=0.150
MINIMUMEXPOSURETIME=0.005
NOMINALEXPOSURETIME=0.5
WRITERTIME=0.5
GDAPROCESSTIME=1.0
TIME_FUDGE_FACTOR_IN_SECONDS=1
class PELoop(ScannableBase):
    def __init__(self, name, tfg, fg, adc, pe, detector):
        self.name=name
        self.tfg=tfg
        self.fg=fg
        self.adc=adc
        self.pedata=pe
        self.detector=detector
        self.fastshutter=Finder.getInstance().find("fastshutter")
        self.numGates=1
        self.numCycles=1
        self.numFrames=1
        self.livetime=0.0
        self.deadtime=0.0
        self.boundaryFrequency=0.1
        self.func = 2
        self.bncycle=1
        self.freq=0.1
        self.adcStreamerCompleted=True
        self.gateDetectorCompleted=True
        self.numDefinedSequency=1
        self.filename=""
        self.directory=""
        self.scanNumber=0
        self.preConditioning=True
        self.startCycleNumber=0
        self.startSeqNumber=0
    def isSampleConditioning(self):
        return self.preConditioning
    def setSampleConditioning(self, value):
        self.preConditioning=value
    def setStartCycleNumber(self, value):
        self.startCycleNumber=value
    def getStartCycleNumber(self):
        return self.startCycleNumber
    def setStartSeqNumber(self, value):
        self.startSeqNumber=value
    def getStartSeqNumber(self):
        return self.startSeqNumber
    def setupFG(self,freq=0.125,amp=5.0,bncycle=1,func=2,shift=0.0,symmetry=50.0,trig=1,bmode=0,bstate=1):
        '''prime the function generator ready for PELoop experiment'''
        print "\nsetup fuction generator for experiment"
        self.fg.setAmplitude(amp)       # amplitude value -5.0
        #self.fg.setShift(shift)         # offset value - 0.0
        self.fg.setSymmetry(symmetry)   # cycle symmetry value - 50%
        self.fg.setTriggerSource(trig)  # select external source - IMM=0, EXT=1, BUS=2
        self.fg.setBurstState(bstate)   # switch on burst mode - On=1, Off=0
        self.fg.setBurstMode(bmode)     # burst mode - Trig=0, Gate=1
        self.fg.setFrequency(freq)      # set cycle frequency
        self.fg.setOutput(1)            # enableField output - On=1, Off=0
        self.func = func
        self.bncycle=bncycle
        print "function generator is ready: frequency=%f, amplitude=%f" % (self.fg.getFrequency(), self.fg.getAmplitude())
    def setupADC2(self):
        print "\nsetup ADC control for gated acquisition at 50kHz sampling rate"
        self.adc.gateMode()
        self.adc.setClockRate("5 kHz")
        self.adc.internalClock()
        self.adc.auto()
        self.adc.setSamples(5000)
        self.adc.setAdcOffset(0)
        self.adc.setAverage(1)
        self.adc.enable()
        print "ADC is ready: mode=%s, rate=%s, state=%s, samples=%d " % (self.adc.getMode(), self.adc.getClockRate(), self.adc.getState(), self.adc.getSamples())
    def configADC(self, samples, rate):
        print "\nconfigure ADC control for triggered acqisition at specified sampling rate and for specified number of samples. "
        self.adc.disable()
        self.adc.triggerMode()
        self.adc.setClockRate(rate)
        self.adc.internalClock()
        self.adc.auto()
        self.adc.setSamples(samples)
        self.adc.setAdcOffset(0)
        self.adc.setAverage(1)
        print "ADC is ready: mode=%s, rate=%s, state=%s, samples=%d " % (self.adc.getMode(), self.adc.getClockRate(), self.adc.getState(), self.adc.getSamples())
    def setupDataCapturer(self, filename, numGates):
        self.pedata.setFilename(filename)
        self.pedata.setNumberOfGates(numGates)
        self.pedata.addMonitors()
        self.pedata.reset()
    def calculateExperimentParameters(self, frequency=0.1, exposure=0.5, numPoints=40):
        print "\nsetup PELoop Experiment parameters"
        self.boundaryFrequency=1/(numPoints*(MYTHENREADOUTTIME+MINIMUMEXPOSURETIME))
        self.freq=frequency
        if frequency <= self.boundaryFrequency:
            self.numGates=1
            self.numCycles=math.ceil(exposure/((1/frequency/numPoints)-MYTHENREADOUTTIME))
            self.numFrames=numPoints
            self.numDefinedSequency=1
            self.livetime=exposure/self.numCycles
            self.deadtime=1/frequency/numPoints-self.livetime
            totaltime=((self.livetime+self.deadtime)*self.numFrames*self.numGates*self.numDefinedSequency+GDAPROCESSTIME)*self.numCycles
        else:
            self.numGates=int(NOMINALEXPOSURETIME/(1/frequency/numPoints))
            self.numCycles=math.ceil(exposure/(1/frequency/numPoints)/self.numGates)
            self.numFrames=1
            self.numDefinedSequency=numPoints
            self.livetime=1/frequency/numPoints
            self.deadtime=self.livetime
            totaltime=(self.livetime*numPoints*self.numFrames*self.numGates+WRITERTIME)*self.numDefinedSequency*self.numCycles
        numPSDFiles=self.numFrames*self.numCycles*self.numDefinedSequency
        numADCFiles=numPSDFiles #self.numCycles*self.numDefinedSequency
        print "number of PSD data files to collect: %d" % numPSDFiles
        print "number of PE and gate data files to collect: %d" % numADCFiles
        print "calculated total data collection time in seconds for your request is: %f" % totaltime
        print "tfg2 configuration parameters:"
        print "        number of cycles = %d " % self.numCycles
        print "        number of gates  = %d "% self.numGates
        print "        number of Frames = %d " % (self.numFrames*self.numDefinedSequency)
        print "        size of gate (s) = %f " % self.livetime
        print "        exposure time (s)= %f " % (self.livetime*self.numGates)
    def gateDetector(self, *args):
        self.gateDetectorCompleted=False
        print "start PSD detector"
        self.detector.gated(args[0], args[1], args[2], args[3])  # block until all frames and gates are collected
        print "PSD collection number %d completed." % (args[3])
        self.gateDetectorCompleted=True
    def startDetector(self, frequency, scanNumber, collectionNumber):
        print "\ncollecting %d frames, %d gates per frame, Scan number %d, Collection number %d" % (self.numFrames*self.numDefinedSequency, self.numGates, scanNumber, collectionNumber)
        if frequency <= self.boundaryFrequency:
            Thread(target=self.gateDetector, name="MythenGatedCollection", args=(self.numFrames, self.numGates, scanNumber, collectionNumber), kwargs={}).start()
            sleep(1)
        else:
            print "\nPlease start PSD collection from Mythen QT client ..."
            print "select 'Gated' option in the 'Runs' box first"
            print "then set 'Acquisition time' to %d, 'Repetitions' to %d" % (self.numGates, self.numFrames * self.numDefinedSequency*self.numCycles)
            print "set 'Output Directory' to %s, 'File name root' to %d, 'Start index' to %d" % (self.directory, self.scanNumber, 0)
            target = requestInput("Is PSD ready, Yes or No?")
            print str(target)
            if str(target)!="Yes":
                sys.exit()
    def epicsDataStreamer(self, *args):
        print "start PE and gate data streamer"
        self.adcStreamerCompleted=False
        subprocess.call(args[0])
        print "PE & gate signal collection completed."
        self.adcStreamerCompleted=True
    def startPEDataStreamer(self, filename, duration):
            print "\ncollecting PE and gate data to file %s for %d seconds..." % (filename, int(math.ceil(duration)))
            Thread(target=self.epicsDataStreamer, name="EpicsDataStreamer", args=(["/dls/i11/software/i11_rebin/monitor_ADC.py", filename, str(int(math.ceil(duration)))],), kwargs={}).start()
            sleep(1)
    def sampleConditioning(self, func, bncycle):
        print "\nstart sample conditioning before data collection cycles"
        self.fg.setFunction(func)       # Arb or USER function - 6
        self.fg.setBurstNCycle(bncycle)
        self.fg.setOutput(1)
        self.tfg.fireSingleTrigger()
        print "wait %f seconds for sample conditioning..." % (1/self.freq)
        sleep(1/self.freq)
        print "sample conditioning completed."
        self.fg.setFunction(self.func)
        self.fg.setBurstNCycle(self.bncycle)
    def configTFG(self, frequency):
        if frequency <= self.boundaryFrequency:
            print "\nConfigure tfg2 for slow ramping mode data collection ... "
            self.tfg.config_slow(self.deadtime, self.livetime, self.numFrames, 1, GDAPROCESSTIME)
        else:
            print "\nConfigure tfg2 for fast ramping mode data collection ..."
            self.tfg.config_fast_no_cycles(self.deadtime, self.livetime, self.numDefinedSequency, self.numGates, 1, WRITERTIME)
        while not self.tfg.isFramesLoaded():
            sleep(0.1)
        print "TFG frames configuration completed!"
    def pescan(self, frequency=0.1,exposure=0.5,amplitude=5.0,numPoints=40, function=2, bncycle=1):
        self.directory=PathConstructor.createFromDefaultProperty()
        self.scanNumber=scanNumTracker.incrementNumber()
        self.filename=self.directory+(str(self.scanNumber))
        print self.filename
        if self.adc.getMode()=="Gate":
            self.setupADC2()
        elif self.adc.getMode()=="Trigger":
            self.configADC(200, self.adcClockRate(frequency))
        self.calculateExperimentParameters(frequency, exposure, numPoints)
        self.setupFG(freq=frequency,amp=amplitude,bncycle=self.numGates, func=function)
        # must in following order
        if self.isSampleConditioning():
            self.sampleConditioning(func=6, bncycle=1)
        self.configTFG(frequency)
        self.setupDataCapturer(self.filename, self.numGates)
        print "open fast shutter %d" % time()
        self.fastshutter.moveTo("OPEN")
        try:
            if frequency <= self.boundaryFrequency:
                for i in range(self.numCycles):
                    GeneralCommands.pause()
                    self.pedata.reset()
                    self.pedata.setCollectionNumber(i)
                    print "\ncollecting %d frames, %d gates per frame, Scan number %d, Collection number %d" % (self.numFrames*self.numDefinedSequency, self.numGates, self.scanNumber, i)
                    Thread(target=self.gateDetector, name="MythenGatedCollection", args=(self.numFrames, self.numGates, self.scanNumber, i), kwargs={}).start()
                    sleep(1)
                    #self.startDetector(frequency, self.scanNumber, i)
                    if self.adc.getMode()=="Trigger":
                        print "enable adc sampling"
                        self.adc.enable()
                    #elif self.adc.getMode()=="Continuous":
                    self.startPEDataStreamer(self.filename+"_pe_"+str(i)+".h5", 1/frequency+TIME_FUDGE_FACTOR_IN_SECONDS)
                    self.tfg.start()
                    sleep(1/frequency+GDAPROCESSTIME)
            else:
                finder=Finder.getInstance()
                print "\nPlease start PSD collection from Mythen QT client ..."
                print "    1. select 'Gated' option in the 'Runs' box first"
                print "    2. then set 'Acquisition time' to %d, 'Repetitions' to %d" % (self.numGates, self.numFrames * self.numDefinedSequency*self.numCycles)
                print "    3. set 'Output Directory' to subdirector %s under 'processing' directory, 'File name root' to %d, 'Start index' to %d" % (finder.find("GDAMetadata").getMetadataValue("subdirectory"), self.scanNumber, 0)
                target = requestInput("Is PSD ready, Yes or No?")
                print str(target)
                if str(target)!="Yes":
                    raise "Exiting program"
                for j in range(self.startCycleNumber,self.numCycles):
                    self.pedata.reset()
                    self.pedata.setCollectionNumber(j)
                    #self.startDetector(frequency, self.scanNumber, j)
                    for i in range(self.startSeqNumber, self.numDefinedSequency):
                        GeneralCommands.pause()
                        sleep(4.0)
                        self.tfg.config_cycle_for_seq(i, self.numGates, 1)
                        sleep(4.0)
                        if self.adc.getMode()=="Trigger":
                            print "enable adc sampling"
                            self.adc.enable()
                        #elif self.adc.getMode()=="Continuous":
                        self.startPEDataStreamer(self.filename+"_pe_"+str(i)+".h5", 1/frequency*self.numGates+TIME_FUDGE_FACTOR_IN_SECONDS)
                        self.tfg.start()
                        sleep(1/frequency*self.numGates+GDAPROCESSTIME)
        except:
            self.stop()
            raise
        finally:
            print "close fast shutter %d" % time()
            self.fastshutter.moveTo("CLOSE")
            self.pedata.removeMonitors()
            print "collection completed at %d" % time()
    def recollect(self, startCycleNumber,startSeqNumber,frequency, numGates,numDefinedSequency,numCycles, filename):
        self.fastshutter.moveTo("OPEN")
        self.pedata.removeMonitors()
        self.setupDataCapturer(filename, numGates)
        for j in range(startCycleNumber,numCycles):
                    self.pedata.reset()
                    self.pedata.setCollectionNumber(j)
                    #self.startDetector(frequency, self.scanNumber, j)
                    for i in range(startSeqNumber, numDefinedSequency):
                        GeneralCommands.pause()
                        sleep(4.0)
                        self.tfg.config_cycle_for_seq(i, numGates, 1)
                        sleep(4.0)
                        if self.adc.getMode()=="Trigger":
                            print "enable adc sampling"
                            self.adc.enable()
                        #elif self.adc.getMode()=="Continuous":
                        self.startPEDataStreamer(filename+"_pe_"+str(i)+".h5", 1/frequency*self.numGates+TIME_FUDGE_FACTOR_IN_SECONDS)
                        self.tfg.start()
                        sleep(1/frequency*self.numGates+GDAPROCESSTIME)
        self.pedata.removeMonitors()
    def collect(self,gateNumber,frequency, numGates, filename):
        self.fastshutter.moveTo("OPEN")
        self.pedata.removeMonitors()
        self.setupDataCapturer(filename, numGates)
        self.pedata.reset()
        self.pedata.setCollectionNumber(0)
        self.tfg.config_cycle_for_seq(gateNumber, numGates, 1)
        self.startPEDataStreamer(filename+"_pe_"+str(gateNumber)+".h5", 1/frequency*self.numGates+TIME_FUDGE_FACTOR_IN_SECONDS)
        self.tfg.start()
        sleep(1/frequency*numGates+GDAPROCESSTIME)
        self.pedata.removeMonitors()
 
    def stop(self): 
        if self.isBusy():
            print "    %s: stop called at %d" % (self.getName(),time())
            GeneralCommands.pause()
            self.pedata.removeMonitors()        # ensure monitor removed
            self.tfg.stop()
            #self.fg.stop()
            #self.adc.stop()
            self.detector.stop()
            #self.resetDetector()
            self.gateDetectorCompleted=True
            self.adcStreamerCompleted=True
            
    def resetDetector(self):
        if self.numFrames != None:
            self.tfg.releaser(self.numFrames*self.numCycles*self.numGates)
    def config(self,frequency,exposure,amplitude,numPoints):
        self.freq=frequency
        if self.adc.getMode()=="Continuous":
            self.setupADC2()
        elif self.adc.getMode()=="Trigger":
            self.configADC(200, self.adcClockRate(frequency))
        self.calculateExperimentParameters(frequency, exposure, numPoints)
        self.setupFG(freq=frequency,amp=amplitude,bncycle=self.numGates)
        self.configTFG(frequency)
        self.sampleConditioning()
    def atScanStart(self):
        self.collectionNumber=0
        self.directory=PathConstructor.createFromDefaultProperty()
        self.scanNumber=scanNumTracker.getCurrentFileNumber()
        self.filename=self.directory+(str(self.scanNumber))
    def atPointStart(self):
        self.startDetector(self.frequency, self.scanNumber, self.collectionNumber)
        sleep(1.0)
        self.sampleConditioning(func=6, bncycle=1)
        print "open fast shutter %d" % time()
        self.fastshutter.moveTo("OPEN")
        self.setupDataCapturer()
        self.adc.enableField()
    def atPointEnd(self):
        self.adc.disable()
        self.pedata.removeMonitors()
        self.fastshutter.moveTo("CLOSE")
        self.pedata.save(self.filename, self.collectionNumber)
        self.collectionNumber += 1
    def rawGetPosition(self):
        pass
    def rawAsynchronousMoveTo(self,new_position):
        try:
            self.tfg.start()
        except:
            raise "PELoop error (%s): %f" % (sys.exc_info()[0], new_position)
    def isBusy(self):
        return (self.adc.getState()== "Enabled" or self.tfg.status() != "IDLE")
    def adcClockRate(self, frequency):
        if frequency == 0.01:
            return "2 Hz"
        elif frequency >0.01 and frequency <=0.02:
            return "5 Hz"
        elif frequency >0.02 and frequency <=0.04:
            return "10 Hz"
        elif frequency >0.04 and frequency <=0.07:
            return "20 Hz"
        elif frequency >0.07 and frequency <=0.3:
            return "50 Hz"
        elif frequency >0.3 and frequency <=0.6:
            return "100 Hz"
        elif frequency >0.6 and frequency <=1.0:
            return "200 Hz"
        elif frequency >1.0 and frequency <=3.0:
            return "500 Hz"
        elif frequency >3.0 and frequency <=6.0:
            return "1 kHz"
        elif frequency >6.0 and frequency <=12.0:
            return "2 kHz"
        elif frequency >12.0 and frequency <=31.0:
            return "5 kHz"
        elif frequency >31.0 and frequency <=62.0:
            return "10 kHz"
        elif frequency >62.0 and frequency <=100.0:
            return "20 kHz"
        else:
            raise "Frequency is out of the range supported!"
        
