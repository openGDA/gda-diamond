'''
file: peloop.py
This module defines functions for collecting PSD and PE data at specified High Voltage ramp frequency during PE Loop experiments.
At slow ramping rate (i.e. period >= 8sec, frequency <= 0.125Hz), each ramp cycle provide 40 data points;
At fast ramping rate acquisition may need to spread over multiple ramp cycles in order to archive useful diffraction pattern by setting number of gates greater than 1.
 
Created on 15 Feb 2011
updated on 22 june 2011

@author: fy65
'''
from peloop.adc import ADC
from peloop.eventreceiver import EventReceiver
from peloop.functiongenerator import FunctionGenerator
from gda.data import NumTracker, PathConstructor
from gda.jython.commands.GeneralCommands import alias
from gdascripts.scannable.timerelated import _Timer
from gdascripts.utils import frange
from time import sleep, time
import thread
#from localStation import mythen, interruptable

peobject=ADC("peobject")
fg1=FunctionGenerator("fg1")
fg2=FunctionGenerator("fg2")
evr=EventReceiver("evr")
scanNumTracker = NumTracker("tmp");

#bm.off()

def peloop(frequency=0.125,numberofgates=1):
    '''convenient method that only permits setting of 2 args: ramp frequency and number of gates.
    When frequency is less than 0.125Hz, only the default 1 gate required. 
    when frequency is greater than 2Hz, multiple gates (>1) will be required.
    Between 0.125 and 2 Hz, number of gates will depend on the sample diffraction properties.
    '''
    pescan(freq=frequency, ng=numberofgates)

def pescan(func=2,freq=0.125,amp=5.0,shift=0.0,symmetry=50.0,trig=1,bmode=0,bncycle=1,bstate=0,
           nprecycles=1,nptspercycle=40, det=mythen, ng=1, nf=1):

    #setup func generator 2
    fg2.setFunction(1)          # square wave
    fg2.setAmplitude(5.0)
    fg2.setShift(2.5)
    fg2.setDutyCycle(50.0)
    fg2.setTriggerSource(trig)
    fg2.setBurstState(0)        # switch off burst mode before change burst parameters
    if (freq<=0.125):              # slow HV ramping
        fg2.setFrequency(freq*nptspercycle)
        fg2.setBurstNCycle(nptspercycle)
    else:                       # fast HV ramping
        fg2.setFrequency(freq)
        fg2.setBurstNCycle(1)
    fg2.setBurstMode(bmode)
    fg2.setBurstState(1)        #switch on burst mode
    
    sleep(1)

    #setup func generator 1
    fg1.setFunction(func)       # 2 - ramp
    fg1.setFrequency(freq)
    fg1.setAmplitude(amp)
    fg1.setShift(shift)
    fg1.setSymmetry(symmetry)
    fg1.setTriggerSource(trig)
    fg1.setBurstState(bstate)   # switch off burst mode
    fg1.setBurstMode(bmode)
    fg1.setBurstNCycle(bncycle)
    
    sleep(1)

    #calculate acquisition parameters 
    fg1_frequency=fg1.getFrequency()
    fg1_period=1/fg1_frequency
    starttime=nprecycles * fg1_period
    stoptime=starttime+fg1_period       # only one cycle
    gatewidth=fg1_period/nptspercycle    # no need to minus file writing time as FIFO can buffer 4 frames
    
    #setup ADC to capture PE data
    peobject.addMonitor(1)
    peobject.setFirstData(True)
    
    #setup file name 
    directory=PathConstructor.createFromDefaultProperty()
    scanNumber=scanNumTracker.incrementNumber()
    peobject.setFilename(directory+(str(scanNumber)))

    #pre-conditioning
    evr.disable()
    timer=_Timer()
    timer.start()
    fg2.setOutput(1)
    fg1.setOutput(1)
    print "sample pre-conditioning cycles, please wait for %s" % starttime
    while(not timer.hasElapsed(starttime)):
        sleep(0.01)
    
    #collection
    collectionNumber=0    
    evr.enableField()
    try:
        if (freq<=0.125):               # 8sec period, 200ms per point
            peobject.reset()
            peobject.setFastMode(False)
            evr.moveTo([0.0,gatewidth-0.15])    #150 ms writing to disk allowed
            print "move event receiver to delay=%s width=%s" % (evr.getDelay(), evr.getWidth())
            print "start mythen %d" % time()
            pos fastshutter "OPEN"
            mythen.gated(nptspercycle, ng, scanNumber)
            pos fastshutter "CLOSE"
            peobject.save()       
        else:
            peobject.setFastMode(True)
            for t1 in frange(starttime, stoptime, gatewidth)[:-1]:
                #print t1
                peobject.reset()                             # reset the gate counter
                print "move event receiver to delay=%s width=%s" % (t1-starttime, gatewidth)
                evr.moveTo([t1-starttime,gatewidth])
                print "start mythen %d" % time()
                pos fastshutter "OPEN"
                mythen.gated(nf, ng, scanNumber, collectionNumber)  # block until all frames and gates are collected
                pos fastshutter "CLOSE"
                collectionNumber += 1
                peobject.save(collectionNumber)
                interruptable()                                     # allow "StopAll" to work
    except:
        raise
    finally:
        print "collection completed at %d" % time()
        peobject.removeMonitor()        # ensure monitor removed
        pestop()
 
    #stop ramp output
    fg2.setOutput(0)
    fg1.setOutput(0)
    
def pestop():
    #stop ramp output
    fg2.setOutput(0)
    fg1.setOutput(0)
   
# to support syntax: pescan 20 50 0.1 mythen ng nf
alias("pescan")
alias("peloop")
