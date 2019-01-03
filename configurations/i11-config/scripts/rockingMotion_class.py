'''
Created on 24 Jun 2010

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from java.lang import Thread, Runnable
from time import sleep
#from gda.jython import JythonServerFacade, Jython

class RockingMotion(ScannableMotionBase, Runnable):
    '''Create PD for continuous rocking motion of the specified scannable within the limits during scan'''
    def __init__(self, name, pd, lowerlimit, upperlimit):
        self.setName(name)
        self.setInputNames([name])
        self.pd=pd
        self.upperlimit=upperlimit
        self.lowerlimit=lowerlimit
        self.setLevel(5)
        self.runThread=False
        self.thread=None

    def atScanStart(self):
        '''prepare to start scan: start rocking motion thread'''
        self.thread=Thread(self, "Thread: "+self.getName())
        self.runThread=True
        self.thread.start()

    def atScanEnd(self):
        '''clean up after scan finished successfully: stop rocking motion thread'''
        self.runThread=False
        #self.thread.interrupt()
        self.thread=None
        self.pd.stop()

    def start(self):
        '''start rocking'''
        self.rawAsynchronousMoveTo(1.0)

    def stop(self):
        '''stop roking'''
        self.rawAsynchronousMoveTo(0.0)

    def run(self):
        '''rocking motion of the specified pd during scan'''
        moveToUpperLimit=True
        while(self.runThread):
            if not self.rawIsBusy():
                if (moveToUpperLimit):
                    if (abs(float(float(self.getPosition())-float(self.upperlimit)))>0.01):
                        print "move to upper limit " + str(self.upperlimit)
                        moveToUpperLimit=True
                        self.pd.asynchronousMoveTo(self.upperlimit)
                        continue
                    else:
                        print "moving to lower limit"
                        self.pd.asynchronousMoveTo(self.lowerlimit)
                        moveToUpperLimit=False
                        continue

                else:
                    if (abs(float(float(self.getPosition())-float(self.lowerlimit)))>0.01):
                        print "move to lower limit " + str(self.lowerlimit)
                        moveToUpperLimit=False
                        self.pd.asynchronousMoveTo(self.lowerlimit)
                        continue
                    else:
                        print "moving to upper limit"
                        self.pd.asynchronousMoveTo(self.upperlimit)
                        moveToUpperLimit=True
                        continue

    def rawGetPosition(self):
        '''This method not applies for the object, but returns pd position to satisfy framework interface'''
        return self.pd.getPosition()

    def rawAsynchronousMoveTo(self,new_position):
        '''start rocking between two limiting positions, 1 to start rocking, 0 to stop rocking'''
        if (float(new_position) != 1.0):
            if (float(new_position) != 0.0):
                print "must be 0 or 1: 1 to start rocking, 0 to stop rocking."
        if (float(new_position) == 1.0):
            self.thread=Thread(self, "Thread: "+self.getName())
            self.runThread=True
            self.thread.start()
        if (float(new_position) == 0.0):
            self.runThread=False
            self.thread=None
            self.pd.stop()


    def rawIsBusy(self):
        '''always return origianl pd's status'''
        return self.pd.isBusy();


    def toString(self):
        return self.name + " : " + str(self.getPosition())


    def getLowerLimit(self):
        return self.lowerlimit

    def setLowerLimit(self, value):
        self.lowerlimit=value

    def getUpperLimit(self):
        return self.upperlimit

    def setUpperLimit(self, value):
        self.upperlimit=value

from gda.epics import CAClient

class PmacRock(object):
    def __init__(self, pv):
        self._pv = pv
        self._start = CAClient(pv + 'STARTCMD.PROC')
        self._start.configure()
        self._stop = CAClient(pv + 'STOPCMD.PROC')
        self._stop.configure()

        self._start_pos = CAClient(pv + 'START')
        self._start_pos.configure()
        self._start_pos_rbv = CAClient(pv + 'START:RBV')
        self._start_pos_rbv.configure()

        self._end_pos = CAClient(pv + 'END')
        self._end_pos.configure()
        self._end_pos_rbv = CAClient(pv + 'END:RBV')
        self._end_pos_rbv.configure()

        self._current = CAClient(pv + 'CURRENTROCK_RBV')
        self._current.configure()
        self._offset = CAClient(pv + 'OFFSET:RBV')
        self._offset.configure()
        self._speed = CAClient(pv + 'SPEED:RBV')
        self._speed.configure()

    def start(self):
        self._start.caput(1)

    def stop(self):
        self._stop.caput(1)

    def getLowerLimit(self):
        return self._start_pos.caget()

    def setLowerLimit(self, posn):
        self._start_pos.caput(posn)
    lowerLimit = property(getLowerLimit, setLowerLimit)

    def getUpperLimit(self):
        return self._end_pos.caget()

    def setUpperLimit(self, posn):
        self._end_pos.caput(posn)
    upperLimit = property(getUpperLimit, setUpperLimit)

    def getSpeed(self):
        return self._speed.caget()
    def setSpeed(self, speed):
        self._speed.caput(speed)
    speed = property(getSpeed, setSpeed)

    def getCurrent(self):
        return self._current.caget()
    current = property(getCurrent)

    def getOffset(self):
        return self._offset.caget()
    offset = property(getOffset)

    def __enter__(self):
        self.start()

    def __exit__(self, type_, value, traceback):
        self.stop()
    
    def __repr__(self):
        return 'PmacRock: {} -> {}'.format(self.lowerLimit, self.upperLimit)
