from gdascripts.pd.epics_pds import SingleEpicsPositionerNoStatusClassDeadband

#m4fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m4fpitch', 'BL10I-OP-FOCS-01:FPITCH:DMD:AO', 'BL10I-OP-FOCS-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)

class SingleEpicsPositionerNoStatusClassDeadbandOrStop(SingleEpicsPositionerNoStatusClassDeadband):
    'EPICS device that obtains a status from a deadband without a stop PV'
    def __init__(self, name, pvinstring, pvoutstring, unitstring, formatstring, deadband):
        self.deadband = deadband
        SingleEpicsPositionerNoStatusClassDeadband.__init__(self, name, pvinstring, pvoutstring, None, None, unitstring, formatstring, deadband)

    def stop(self):
        print "stopping by demanding current position"
        try:
            self.new_position=self()    # need this attribute for some other classes
            if self.incli.isConfigured():
                self.incli.caput(self.new_position)
            else:
                self.incli.configure()
                self.incli.caput(self.new_position)
        except:
            print "error stopping"
