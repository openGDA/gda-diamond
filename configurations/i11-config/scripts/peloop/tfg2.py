''' filename:tfg.py
This module defines a class for TFG2 configuration and control.
TFG2 configuration implemented use string.Template to substitute livetime, deadtime, number of Frames, number of sequences and number of cycles.
Java tfg object dose not support 'sequence configuration so we cannot use the loadFrameSet() of Tfg.java. Here we bypass these methods in Java. 

Author: Fajin Yuan, created 30 Jan 2012
'''

from gda.device.scannable import ScannableBase
from gda.factory import Finder

class TFG2(ScannableBase):
    def __init__(self, name):
        self.tfg=Finder.getInstance().find("tfg")
        self.daserver=Finder.getInstance().find("daserver")
        # to support showArmed status
        self.tfg.setShowArmed(True) 

    def tfgConfig(self):
        '''create tfg2 configuration script.
        '''
        return 'tfg config "etfg0" tfg2\n'
    
    def trigger(self):
        '''create tfg2 configuration script for trigger output.
            This is used to (re-)synchronise data collection at each data point. 
        '''
        s=''
        s+='tfg setup-groups sequence "trigger"\n'
        s+='1 1.00e-6 0 11 0 0 0\n'
        s+='-1\n'
        return s
    
    def writer(self,writerTime):
        '''create tfg2 configuration script to wait for file writing time in fast ramping mode:
            writerTime - specify the time to wait for data to be written to disk.
        '''
        s=''
        s+='tfg setup-groups sequence "writer"\n'
        s+='1 ' + str(writerTime) + ' 0 0 0 0 0\n'
        s+='-1\n'
        return s
    
    def fastSequences(self, numFrames, deadtime, livetime):
        '''create tfg2 sequence configuration scripts for fast ramping mode:
            numFrames   - specify number of data points to collect
            deadtime    - specify the dead time in each frame
            livetime    - specify the live time in each frame
        '''
        s=''
        for i in range(numFrames):
            s+='tfg setup-groups sequence "seq'+str(i)+'"\n'
            if i != 0:
                s+=str(i) + ' '+str(deadtime)+' 0 0 0 0 0\n'
            s+='1 0 '+str(livetime)+' 0 0 0 0\n'
            if i != numFrames-1:
                s+=str(numFrames-i-1)+' '+str(deadtime)+' 0 0 0 0 0\n'
            s+=str(-1)+'\n'
        return s
        
    def fastCycles(self, numFrames, numSequences, numCycles):
        '''create tfg2 cycles configuration script for fast ramping mode:
            numFrames    - specify number of data points to collect
            numSequences - specify number of gates to collect per frame
            numCycles    - specify number of repetition to do
        '''
        s=''
        s+='tfg setup-groups cycles '+str(numCycles)+'\n'
        for i in range(numFrames):
            s+='1 trigger\n'
            s+=str(numSequences)+' seq'+str(i)+'\n'
            s+='1 writer\n'
        s+=str(-1)+'\n'
        return s
      
    def config_cycle_for_seq(self, seqNumber, numSequences, numCycles):
        '''create tfg2 cycles configuration script for fast ramping mode:
            numFrames    - specify number of data points to collect
            numSequences - specify number of gates to collect per frame
            numCycles    - specify number of repetition to do
        '''
        s=''
        s+='tfg setup-groups cycles '+str(numCycles)+'\n'
        s+='1 trigger\n'
        s+=str(numSequences)+' seq'+str(seqNumber)+'\n'
        s+='1 writer\n'
        s+=str(-1)+'\n'
        print s
        self.daserver.sendCommand(s)
        self.tfg.setFramesLoaded(True) 


    def gdaProcesses(self,duration):
        '''create tfg2 configuration script to provide time for GDA processes post raw data collection in slow ramping mode.
            At slow ramping mode PSD TextClient is used to collect diffraction raw data.
            In this mode, GDA is required to do post process to convert raw data to angle-calibrated data.
            GDA also plots these data.            
        '''
        s=''
        s+='tfg setup-groups sequence "gdaprocess"\n'
        s+='1 ' + str(duration) + ' 0 0 0 0 0\n'
        s+='-1\n'
        return s

    def slowSequence(self,numFrames, deadtime, livetime):
        '''create tfg2 sequence configuration script for slow ramping mode:
            numFrames   - specify number of data points to collect
            deadtime    - specify the dead time in each frame
            livetime    - specify the live time in each frame
        '''
        s=''
        s+='tfg setup-groups sequence "slow"\n'
        s+=str(numFrames) +' '+str(deadtime)+' '+str(livetime)+' 0 0 0 0\n'
        s+=str(-1)+'\n'
        return s
 
    def slowCycle(self,numCycles):
        '''create tfg2 cycles configuration script for fast raming mode:
            numCycles    - specify number of repetition to do
        '''
        s=''
        s+='tfg setup-groups cycles '+ str(numCycles)+'\n'
        s+='1 trigger\n'
        s+='1 slow\n'
        s+='1 gdaprocess\n'
        s+=str(-1)+'\n'
        return s

    def config_fast_no_cycles(self, deadTime, liveTime, numFrames=40, numSequences=1, numCycles=1, writerTime=0.5):
        '''configure tfg2 for fast ramping mode data collection.
            deadTime    - specify the dead time in each frame
            liveTime    - specify the live time in each frame
            numFrames   - specify number of data points to collect
            numSequences - specify number of gates to collect per frame
            numCycles    - specify number of repetition to do
            writerTime - specify the time to wait for data to be written to disk.
        '''
        command=self.tfgConfig()+self.trigger()+self.writer(writerTime)+self.fastSequences(numFrames, deadTime, liveTime)
        print command
        self.daserver.sendCommand(command)
        self.tfg.setFramesLoaded(True) 
          
    def config_fast(self, deadTime, liveTime, numFrames=40, numSequences=1, numCycles=1, writerTime=0.5):
        '''configure tfg2 for fast ramping mode data collection.
            deadTime    - specify the dead time in each frame
            liveTime    - specify the live time in each frame
            numFrames   - specify number of data points to collect
            numSequences - specify number of gates to collect per frame
            numCycles    - specify number of repetition to do
            writerTime - specify the time to wait for data to be written to disk.
        '''
        command=self.tfgConfig()+self.trigger()+self.writer(writerTime)+self.fastSequences(numFrames, deadTime, liveTime)+self.fastCycles(numFrames, numSequences, numCycles)
        print command
        self.daserver.sendCommand(command)
        self.tfg.setFramesLoaded(True) 
    
    def config_slow(self, deadTime, liveTime, numFrames=40, numCycles=1, duration=5):
        '''configure tfg2 for slow ramping mode data collection.
            deadTime    - specify the dead time in each frame
            liveTime    - specify the live time in each frame
            numFrames   - specify number of data points to collect
            numCycles    - specify number of repetition to do
            writerTime - specify the time to wait for data to be written to disk.
        '''
        command=self.tfgConfig()+self.trigger()+self.gdaProcesses(duration)+self.slowSequence(numFrames, deadTime, liveTime)+self.slowCycle(numCycles)
        print command
        self.daserver.sendCommand(command)
        #TODO added this method to Java when upgrade GDA
        self.setFramesLoaded(True) 
        
    def isFramesLoaded(self):
        return self.tfg.isFramesLoaded()
    
    def setFramesLoaded(self, value):
        self.tfg.setFramesLoaded(value)
        
    def fireSingleTrigger(self):
        s=''
        s+='tfg setup-groups cycles 1 \n'
        s+='100 0.09 0.01 0 1 0 0\n'
        s+='-1\n'
        s+='tfg start\n'
        print s
        self.daserver.sendCommand(s)
    
    def fireSingleTriggerOnTTL0Input(self):
        s=''
        s+='tfg setup-trig ttl0 start \n'
        s+='tfg setup-groups cycles 1 \n'
        s+='100 0.09 0.01 0 1 8 0\n'
        s+='-1\n'
        s+='tfg start\n'
        print s
        self.daserver.sendCommand(s)

    def doCollectTest(self, gatesize, numberofgates, numberofframes, delaybefore, writerTime):
        s=''
        s+='tfg setup-trig ttl0 start \n'
        s+='tfg setup-groups cycles '+str(numberofframes)+' \n'
        s+=str(numberofgates)+' '+str(delaybefore)+' '+str(gatesize)+' 0 1 8 0\n'
        s+='1 ' + str(writerTime) + ' 0 0 0 0 0\n'
        s+='-1\n'
        s+='tfg start\n'
        print s
        self.daserver.sendCommand(s)

    def startTimeResolvedExperiment(self, numCycles, numFrames, numGates, gatesize, delaybefore, writerTime):
        s=''
        s+='tfg setup-trig ttl0 start \n'
        s+='tfg setup-groups cycles '+str(numCycles*numFrames)+' \n'
        s+=str(numGates)+' '+str(delaybefore)+' '+str(gatesize)+' 0 1 8 0\n'
        s+='1 ' + str(writerTime) + ' 0 0 0 0 0\n'
        s+='-1\n'
        s+='tfg start\n'
        print s
        self.daserver.sendCommand(s)
        #self.tfg.setFramesLoaded(True) 
        
    def start(self):
        ''' start tfg process - cannot call java tfg object as it checks loaded Frames which we are not used here.
        '''
        #commands="tfg start"
        #print commands
        #self.daserver.sendCommand(commands)
        print "start tfg" 
        self.tfg.start()

    def stop(self):
        #commands="tfg stop"
        #print commands
        #self.daserver.sendCommand(commands) 
        status = int(self.tfg.getStatus())
        if not status == 0:
            self.tfg.stop()
            print "    tfg stopped"
        
    def progress(self):
        '''check tfg process progress - print message to terminal, This method does not implemented in Java tfg object.
        '''
        #commands="tfg read progress"
        #print commands
        #reply = str(self.daserver.sendCommand(commands)) 
        #print reply
        return self.tfg.getProgress()
        
    def status(self):
        #commands="tfg read status"
        #print commands
        #reply = str(self.daserver.sendCommand(commands)) 
        #print reply
        status = int(self.tfg.getStatus())
        if status == 0:
            return "IDLE"
        elif status == 1:
            return "RUNNING"
        elif status == 2:
            return "PAUSED"
        elif status == 5:
            return "ARMED"
        else:
            return "Unknown status"
    
    def getCurrentFrame(self):
        return self.tfg.getCurrentFrame()
    
    def getCurrentCycle(self):
        return self.tfg.getCurrentCycle()
    
    def reset(self):
        self.tfg.stop()
        self.tfg.setFramesLoaded(False)
        
    def releaser(self, numFrames):
        '''create tfg2 configuration script for output to release waiting detector.
        '''
        s='tfg config "etfg0" tfg2\n'
        s+='tfg setup-groups cycles 1\n'
        s+=str(numFrames)+ ' 0.150 5e-3 0 0 0 0\n'
        s+='-1\n'
        s+='tfg start\n'
        print s
        self.daserver.sendCommand(s)
        print "pulses to release waiting detector completed."
        