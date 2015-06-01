def getIntensity():
	"""
	Constructs and returns a relative intensity from the QBPM.
	"""
	QBPM1A = beamline.getValue(None,"Top","-DI-QBPM-01:A")				#Current readout of QBPM1 A
	QBPM1B = beamline.getValue(None,"Top","-DI-QBPM-01:B")				#Current readout of QBPM1 B
	QBPM1C = beamline.getValue(None,"Top","-DI-QBPM-01:C")				#Current readout of QBPM1 C
	QBPM1D = beamline.getValue(None,"Top","-DI-QBPM-01:D")				#Current readout of QBPM1 D
	intensity = QBPM1A + QBPM1B + QBPM1C + QBPM1D	#Construct relative beam intensity
	return intensity
