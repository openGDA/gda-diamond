'''
Created on 15 Feb 2011

@author: fy65
'''
from peloop.adcchannel import voltage, electrometer
from peloop.eventreceiver import EventReceiver
from peloop.functiongenerator import FunctionGenerator
from gda.data import NumTracker, PathConstructor
from gda.jython.commands.GeneralCommands import alias
from gdascripts.scannable.timerelated import _Timer
from gdascripts.utils import frange
from time import sleep
from localStation import mythen, interruptable

fg=FunctionGenerator("fg")
evr=EventReceiver("evr")
scanNumTracker = NumTracker("tmp");

# default acquisition parameters
number_of_pre_cycles=1
fg.setFunction(2)
fg.setFrequency(0.1)
fg.setAmplitude(10.0)
fg.setShift(0.0)
fg.setSymmetry(50.0)
number_of_points_per_cycle=40.0
number_gates=1
number_frames=1

#derived parameters for pescan() function inputs
fg_frequency=fg.getFrequency()
fg_period=1/fg_frequency
pre_condition_time=number_of_pre_cycles * fg_period
stop_time=pre_condition_time+fg_period
gate_width=fg_period/number_of_points_per_cycle

def pescan(starttime=pre_condition_time, stoptime=stop_time, gatewidth=gate_width, mythen1=mythen, ng=number_gates, nf=number_frames):
    #setup
    voltage.setNumberOfGates(ng)
    electrometer.setNumberOfGates(ng)
    voltage.addMonitor(1)
    electrometer.addMonitor(1)
    directory=PathConstructor.createFromDefaultProperty()
    scanNumber=scanNumTracker.incrementNumber()
    voltage.setFilename(directory+("/")+(str(scanNumber)))
    electrometer.setFilename(directory+("/")+(str(scanNumber)))

    #pre-conditioning
    fg.setOutput(1)
    timer=_Timer()
    timer.start()
    print "sample pre-conditioning cycles, please wait for %s" % starttime
    while(not timer.hasElapsed(starttime)):
        sleep(1)

    #collection
    collectionNumber=0
    try:
        for t1 in frange(starttime, stoptime, gatewidth):
            #print t1
            voltage.resetCounter()
            voltage.setCollectionNumber(collectionNumber)
            electrometer.resetCounter()
            electrometer.setCollectionNumber(collectionNumber)
            print "move event receiver to delay=%s width=%s" % (t1-starttime, gatewidth)
            evr.moveTo([t1-starttime,gatewidth])
            mythen.gated(nf, ng, scanNumber, mythen.getDataDirectory(),collectionNumber)
            collectionNumber += 1
            #print "end loop"
            interruptable()
    except:
        raise
    finally:
        print "end loop"
        voltage.removeMonitor()
        electrometer.removeMonitor()
    #clearup
    #voltage.removeMonitor()
    #electrometer.removeMonitor()
    #stop ramp output
    fg.setOutput(0)
    print "scan completed."

# to support syntax: pescan 20 50 0.1 mythen ng nf
alias("pescan")
