class SingleEpicsPositionerNoIsBusyClass(SingleEpicsPositionerClass):
	def isBusy(self):
		return 0

szasyn=SingleEpicsPositionerNoIsBusyClass('szasyn','BL16I-MO-DIFF-01:SAMPLE:Z.VAL','BL16I-MO-DIFF-01:SAMPLE:Z.RBV','BL16I-MO-DIFF-01:SAMPLE:Z.DMOV','BL16I-MO-DIFF-01:SAMPLE:Z.STOP','mm','%.4f')#
