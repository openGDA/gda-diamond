
#scannable/laser_experiment.py
from gda.factory import Finder
from gda.device.scannable import ScannableMotionBase
daserver = Finder.find('daserver')


ALLOFF = 0
OUT0 = 1
OUT1 = 2
OUT2 = 4
OUT3 = 8
OUT4 = 16
OUT5 = 32
OUT6 = 64
OUT7 = 128

class DummyDAServer(object):
    
    def sendCommand(self, s):
        print s + ' --> ' + `0`
        return 0
    
    
class TfgGroupsScannable(ScannableMotionBase):
    """Assumes that da.server has been configured with:
          tfg config "etfg0" tfg2
          
          
        Outputs:

        OUT0 - laser lamp
        OUT3 - laser switch trigger
        OUT4 - shutter
        
        Timefames:
        
        1. lamp --> ON
           for t_switch s (.2 to .3 ms)
           
        2. switch, lamp --> ON
           for t_laser
           
        3. all OFF
           for t_delay
         
        4. shutter ON
           for t_shutter
        
        5. all OFF
           for t_wait - t_switch

    """
    def __init__(self, name, daserver):
        self.name = name
        self.inputNames = ['n_cycles']
        self.outputFormat = ['%i']
        self.daserver = daserver
        self._ncycles = -1
        self.groups = [] # tuples of parameters
        
    def asynchronousMoveTo(self, ncycles):
        self._ncycles = int(ncycles)
        self._uploadGroups()
        self._start()
    
    def getPosition(self):
        return self._getCurrentCycle()
    
    def isBusy(self):
        return self._getStatus() != 'IDLE'

    def stop(self):
        self._stop()
###       
    def clearGroups(self):
        self.groups = []
        
    def addGroup(self, num_frames=1, dead_time=0.,live_time=0., dead_port=ALLOFF,
                 live_port=ALLOFF, dead_pause=0, live_pause=0):
        self.groups.append((num_frames, dead_time, live_time, dead_port,
                 live_port, dead_pause, live_pause))
###        
    def _send(self, cmd_str):
        return self.daserver.sendCommand(cmd_str)
    
    def _uploadGroups(self):
        self._send("tfg setup-groups cycles %s" % self._ncycles)
        for group in self.groups:
            print "group = ", group
            self._send("%i %f %f %i %i %i %i" % group)
        self._send("-1 0 0 0 0 0 0")
        
    def _start(self):
        self._send("tfg start")
    
    def _stop(self):
        self._send("tfg stop")

    def _getStatus(self):
        """Returns status string; one of IDLE, RUNNING, PAUSED.
        """
        return str(self._send("tfg read status"))
    
    
    def _getCurrentCycle(self):
        return int(self._send("tfg read lap"))


class LaserShutterPulseController(TfgGroupsScannable):
    
    def __init__(self, name, daserver):
        TfgGroupsScannable.__init__(self, name, daserver)
        self.inputNames = ['n_cycle', 't_laser', 't_delay', 't_shutter', 't_wait']
        self.extraNames = ['cycle']
        self.outputFormat = ['%i', '%f', '%f', '%f', '%f', '%i']
        self._ncycles = -1
        self._tlaser = 0.
        self._tdelay = 0.
        self._tshutter = 0.
        self._twait = 0.
        self.t_switch = .0003 #s

    def asynchronousMoveTo(self, position):
        self.cfg()
        self._start()
        print self.name + " started tfg"

    def cfg(self, position):
        self._ncycles, self._tlaser, self._tdelay, self._tshutter, self._twait \
         = tuple(position)
        self._configureGroups()
        print self.name + " uploading groups to tfg"
        self._uploadGroups()
        print "Setting all outputs to 50ohm series impedance"
        self._send('tfg setup-port 0 255')
        
        
    def go(self):
        self._start()
        print self.name + " started tfg"

    def _configureGroups(self):
        # OUT0 - laser lamp
        # OUT3 - laser switch trigger
        # OUT4 - shutter


        self.clearGroups()
        
        # 1. lamp --> ON, for t_switch s (.2 to .3 ms)
        self.addGroup(live_time=self.t_switch, live_port=OUT0)

        # 2. switch, lamp --> ON, for t_laser
        self.addGroup(live_time=self._tlaser, live_port=OUT0+OUT3)

        # 3. all OFF, for t_delay
        self.addGroup(live_time=self._tdelay)

        # 4. shutter ON, for t_shutter
        self.addGroup(live_time=self._tshutter, live_port=OUT4)

        # 5. all OFF, for t_wait - t_switch
        self.addGroup(live_time=self._twait-self.t_switch)
        
        print "Total cycle time: " + str(self.t_switch + self._tlaser + self._tdelay + self._tshutter + (self._twait-self.t_switch)) + "s"
        
        
    def getPosition(self):
        cycle = self._getCurrentCycle()
        return self._ncycles, self._tlaser, self._tdelay, self._tshutter, self._twait, cycle


if __name__ == '__main__':
    dummyda = DummyDAServer()
    #tfggroups = TfgGroupsScannable('tfggroups', dummyda)
    lspc = LaserShutterPulseController('lspc', dummyda)