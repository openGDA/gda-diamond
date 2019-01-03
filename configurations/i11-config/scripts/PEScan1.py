'''
Created on 15 Feb 2011

@author: fy65
'''
from peloop.adcchannel import voltage, electrometer
from peloop.eventreceiver import evr
from peloop.functiongenerator import fg
from gda.data import NumTracker, PathConstructor
from gda.jython.commands.GeneralCommands import alias
from gdascripts.scannable.timerelated import _Timer
from gdascripts.utils import frange
from time import sleep
#from localStation import mythen, interruptable

scanNumTracker = NumTracker("tmp");

# default acquisition parameters


def pescan(function=2, frequency=0.1, amplitude=10.0, shift=0.0, symmetry=50.0, number_of_pre_cycles=1,number_of_points_per_cycle=40.0, detector=mythen, ng=1, nf=1):
    #setup function generator
    fg.setFunction(function)
    fg.setFrequency(frequency)
    fg.setAmplitude(amplitude)
    fg.setShift(shift)
    fg.setSymmetry(symmetry)
    sleep(2) 
    #derived parameters for pescan() function inputs
    fg_frequency=fg.getFrequency()
    fg_period=1/fg_frequency
    starttime=number_of_pre_cycles * fg_period
    stoptime=starttime+fg_period
    gatewidth=fg_period/number_of_points_per_cycle
    
    voltage.setNumberOfGates(ng)
    electrometer.setNumberOfGates(ng)
    voltage.addMonitor(1)
    electrometer.addMonitor(1)
    directory=PathConstructor.createFromDefaultProperty()
    scanNumber=scanNumTracker.incrementNumber()
    voltage.setFilename(directory+(str(scanNumber)))
    electrometer.setFilename(directory+(str(scanNumber)))

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
            voltage.setRepetition(collectionNumber)
            electrometer.resetCounter()
            electrometer.setRepetition(collectionNumber)
            print "move event receiver to delay=%s width=%s" % (t1-starttime, gatewidth)
            evr.moveTo([t1-starttime,gatewidth])
            mythen.gated(nf, ng, scanNumber, collectionNumber)
            collectionNumber += 1
            #print "end loop"
            interruptable()
    except:
        raise
    finally:
        print "end loop"
        voltage.removeMonitor()
        electrometer.removeMonitor()

    #stop ramp output
    fg.setOutput(0)
    print "scan completed."

# to support syntax: pescan 20 50 0.1 mythen ng nf
alias("pescan")
