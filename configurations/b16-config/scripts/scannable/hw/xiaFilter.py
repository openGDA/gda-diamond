from scannable.epics.setBinaryPvAndWaitForFeadbackViaStatePV import SetBinaryPvAndWaitForFeadbackViaStatePV

class XiaFilter(SetBinaryPvAndWaitForFeadbackViaStatePV):
	def __init__(self, name, pvBase, number, timeout):
		SetBinaryPvAndWaitForFeadbackViaStatePV.__init__(self, name, pvBase + ':F%dTRIGGER'%number, pvBase + ':F%dSTATE'%number, timeout)
