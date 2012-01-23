from gda.epics import CAClient 
def fixEpicsTrajectoryStatus():
    trajReadStatus = CAClient("BL18I-MO-TABLE-01:TRAJ1:Readback")
    trajReadStatus.configure()
    trajReadStatus.caput(0)
    