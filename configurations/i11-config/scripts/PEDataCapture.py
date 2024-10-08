'''
file: PEDataCapture.py
This module defines functions for collecting PSD and PE data at specified High Voltage ramp frequency during PE Loop experiments.
At slow ramping rate (i.e. period >= 8sec, frequency <= 0.125Hz), each ramp cycle provide 40 data points;
At fast ramping rate acquisition may need to spread over multiple ramp cycles in order to archive useful diffraction pattern by setting number of gates greater than 1.

Created on 2 Dec 2011 for TFG2 driven experiment

@author: fy65
'''
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.jython.commands.GeneralCommands import alias
from peloop.adc import ADC
from peloop.functiongenerator import FunctionGenerator
from time import sleep, time
#from localStation import mythen

peobject=ADC("peobject")
fg2=FunctionGenerator("fg2")
scanNumTracker = NumTracker("tmp");

#bm.off()

def peloop(frequency=0.03,numberofgates=1,amplitude=5.0):
    '''convenient method that only permits setting of 2 args: ramp frequency and number of gates.
    When frequency is less than 0.125Hz, only the default 1 gate required.
    when frequency is greater than 2Hz, multiple gates (>1) will be required.
    Between 0.125 and 2 Hz, number of gates will depend on the sample diffraction properties.
    '''
    pescan(freq=frequency, ng=numberofgates, amp=amplitude)

def pescan(func=2,freq=0.125,amp=5.0,shift=0.0,symmetry=50.0,trig=1,bmode=0,bncycle=1,bstate=1,
           nprecycles=1,nptspercycle=40, det=mythen,
           ng=1, nf=40):

    #setup func generator 2
    fg2.setFunction(func)       # 2 - ramp
    fg2.setAmplitude(amp)
    fg2.setShift(shift)
    fg2.setSymmetry(symmetry)
    fg2.setTriggerSource(trig)
    fg2.setBurstState(bstate)   # switch on burst mode
    fg2.setBurstMode(bmode)
    fg2.setOutput(1)

    fg2.setFrequency(freq)
    fg2.setBurstNCycle(ng)

    sleep(1)

    #setup ADC to capture PE data
    peobject.addMonitors()
    peobject.setFirstData(True)
    peobject.setNumberOfGates(ng)

    #setup file name
    directory=InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    scanNumber=scanNumTracker.incrementNumber()
    peobject.setFilename(directory+(str(scanNumber)))

    #collection
    collectionNumber=1
    numberToCollect=0
    try:
        peobject.reset()                          # reset the gate counter
        print "open fast shutter %d" % time()
        pos fastshutter "OPEN"
        if freq <= 0.03:
            print "GDA is ready for data collection, you need now to start TFG please. "
            mythen.gated(nf, ng, scanNumber, collectionNumber)  # block until all frames and gates are collected
        else:
            print "Please start PSD collection from QT window client"
            sleep(5)
            while (peobject.getCollectionNumber() <= nf):
                if numberToCollect != peobject.getCollectionNumber():
                    numberToCollect=peobject.getCollectionNumber()
                    print "ready to collect frame %d, please wait..." % numberToCollect
        pos fastshutter "CLOSE"
        #peobject.save(collectionNumber)
        collectionNumber += 1
    except:
        raise
    finally:
        print "collection completed at %d" % time()
        peobject.removeMonitors()        # ensure monitor removed
        #pestop()

def pestop():
    #stop ramp output
    fg2.setOutput(0)

# to support syntax: pescan 20 50 0.1 mythen ng nf
alias("pescan")
alias("peloop")
