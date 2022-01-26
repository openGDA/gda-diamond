def ccdon():
	caput('BL16I-EA-USER-02:BO1','ON')

def ccdoff():
	caput('BL16I-EA-USER-02:BO1','OFF')

def ccdstatus():
	return caget('BL16I-EA-USER-02:BO1')
