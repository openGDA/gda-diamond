from gdascripts.pd.epics_pds import SingleEpicsPositionerNoStatusClassDeadband

# m4fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m4fpitch', 'BL10I-OP-FOCS-01:FPITCH:DMD:AO', 'BL10I-OP-FOCS-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
from gov.aps.jca.event import MonitorListener  # @UnresolvedImport


class SingleEpicsPositionerNoStatusClassDeadbandOrStop(SingleEpicsPositionerNoStatusClassDeadband, MonitorListener):
    'EPICS device that obtains a status from a deadband without a stop PV'

    def __init__(self, name, pvinstring, pvoutstring, unitstring, formatstring, deadband):
        self.deadband = deadband
        self.monitor = None
        SingleEpicsPositionerNoStatusClassDeadband.__init__(self, name, pvinstring, pvoutstring, None, None, unitstring, formatstring, deadband)

    def stop(self):
        print "stopping by demanding current position"
        try:
            self.new_position = self()  # need this attribute for some other classes
            if self.incli.isConfigured():
                self.incli.caput(self.new_position)
            else:
                self.incli.configure()
                self.incli.caput(self.new_position)
        except:
            print "error stopping"

    def monitorChanged(self, mevent):
        self.current = float(mevent.getDBR().getDoubleValue()[0])
        self.notifyIObservers(self, self.current)
        
    def addIObserver(self, ob):
        if not self.outcli.isConfigured():
            self.outcli.configure()
        self.monitor = self.outcli.camonitor(self)
        super(SingleEpicsPositionerNoStatusClassDeadbandOrStop, self).addIObserver(ob)
        
    def deleteIObserver(self, ob):
        if not self.outcli.isConfigured():
            self.outcli.configure()
        if self.monitor:
            self.outcli.removeMonitor(self)
        super(SingleEpicsPositionerNoStatusClassDeadbandOrStop, self).deleteIObserver(ob)