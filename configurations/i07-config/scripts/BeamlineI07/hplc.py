from gdascripts.scannable.epics.PvManager import PvManager
import threading
import time

class Hplc:
    def __init__(self, pvBase):
        pumps_demand_list = ['PUMP:%s' % _l for _l in ['A', 'B', 'C', 'D']]
        pumps_rbv_list = ['PUMP:%s:RBV' % _l for _l in ['A', 'B', 'C', 'D']]
        self.pumps_demand = dict( zip(['A', 'B', 'C', 'D'], pumps_demand_list) )
        self.pumps_rbv = dict( zip(['A', 'B', 'C', 'D'], pumps_rbv_list) )

        pvs = pumps_demand_list + pumps_rbv_list + ['PUMP:STREAM', 'PUMP:FLOW:GO.PROC', 'PUMP:STOP', 'PUMP:RUNNING', 'PUMP:FLOW', 'PUMP:RAMPTIME', 'PUMP:FLOW:RBV', 'VALVE:POSMENU', 'VALVE:GETPOSITION']
        self.pvs = PvManager(pvs, pvBase)
        self.pvs.configure()

    def set_input(self, a, b, c, d):
        self.pvs[self.pumps_demand['A']].caput(a)
        self.pvs[self.pumps_demand['B']].caput(b)
        self.pvs[self.pumps_demand['C']].caput(c)
        self.pvs[self.pumps_demand['D']].caput(d)

    def get_input(self):
        return (self.pvs[self.pumps_demand['A']].caget(),
                self.pvs[self.pumps_demand['B']].caget(),
                self.pvs[self.pumps_demand['C']].caget(),
                self.pvs[self.pumps_demand['D']].caget())

    def set_output(self, outvalve):
        self.pvs['VALVE:POSMENU'].caput(str(outvalve))

    def get_output(self):
        #add 1 because this is an enum, where 0 maps to 1 and 1 maps to 2, etc
        return int(self.pvs['VALVE:POSMENU'].caget()) + 1

    def set_rate(self, rate):
        self.pvs['PUMP:FLOW'].caput(rate)

    def get_rate(self):
        return self.pvs['PUMP:FLOW'].caget()

    def set_ramp(self, ramp):
        self.pvs['PUMP:RAMPTIME'].caput(ramp)

    def get_ramp(self, ramp):
        return self.pvs['PUMP:RAMPTIME'].caget()

    def is_running(self):
        return float(self.pvs['PUMP:RUNNING'].caget()) == 1.

    def isBusy(self):
        return is_running

    def start(self):
        self.pvs['PUMP:FLOW:GO.PROC'].caput(1)

    def stop(self):
        self.stop_thread = True
        self.pvs['PUMP:STOP'].caput(1)
        if self.run_thread != None:
            self.run_thread.join(5.)
            if self.run_thread.isAlive():
                print "hplc thread to manage pump is still running"

    def useA(self):
        self.pvs[self.pumps_demand['A']].caput(100)
        self.pvs[self.pumps_demand['B']].caput(0)
        self.pvs[self.pumps_demand['C']].caput(0)
        self.pvs[self.pumps_demand['D']].caput(0)
        self.pvs['PUMP:STREAM'].caput('A')

    def useB(self):
        self.pvs[self.pumps_demand['A']].caput(0)
        self.pvs[self.pumps_demand['B']].caput(100)
        self.pvs[self.pumps_demand['C']].caput(0)
        self.pvs[self.pumps_demand['D']].caput(0)
        self.pvs['PUMP:STREAM'].caput('B')

    def useC(self):
        self.pvs[self.pumps_demand['A']].caput(0)
        self.pvs[self.pumps_demand['B']].caput(0)
        self.pvs[self.pumps_demand['C']].caput(100)
        self.pvs[self.pumps_demand['D']].caput(0)
        self.pvs['PUMP:STREAM'].caput('C')

    def useD(self):
        self.pvs[self.pumps_demand['A']].caput(0)
        self.pvs[self.pumps_demand['B']].caput(0)
        self.pvs[self.pumps_demand['C']].caput(0)
        self.pvs[self.pumps_demand['D']].caput(100)
        self.pvs['PUMP:STREAM'].caput('D')

    def run_for_time(self, duration):
        self.stop_thread = False
        self.run_thread = threading.Thread(None, self.run_for_time_sync, None, (duration,))
        self.run_thread.start()

    def run_for_time_sync(self, duration):
        try:
            start_time = time.clock()
            self.start()
            while time.clock() < (start_time + duration) and not self.stop_thread:
                time.sleep(0.05)
        finally:
            self.pvs['PUMP:STOP'].caput(1)

