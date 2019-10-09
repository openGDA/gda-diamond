
################
# Cryocooler
################

cryolevel=DisplayEpicsPVClass('N2level','BL16I-CG-CRYO-01:MNLEV','%','%.2f')
cryopressure=DisplayEpicsPVClass('N2buffpressure','BL16I-CG-CRYO-01:NBUFF','%','%.3f')
n2fill=DisplayEpicsPVClass('N2solenoide','BL16I-CG-CRYO-01:ST12','%','%.0f')
#cryolevel.setInputNames(['cryolevel'])

cryo_pump_speed=SingleEpicsPositionerSetAndGetOnlyClass('pump_speed','BL16I-CG-CRYO-01:PSET','BL16I-CG-CRYO-01:PSET','Hz','%.0f',help='Crypump speed - do not change unless you are sure!!')

buffer_pressure=SingleEpicsPositionerSetAndGetOnlyClass('buffer_pressure','BL16I-CG-CRYO-01:TPBUF','BL16I-CG-CRYO-01:TPBUF','PSI','%.1f',help='LN high pressure circuit pressure - do not change unless you are sure!!')

vessel_startfill=SingleEpicsPositionerSetAndGetOnlyClass('vessel_startfill','BL16I-CG-CRYO-01:LP1L','BL16I-CG-CRYO-01:LP1L','%','%.1f',help='Cryocooler vessel start fill level - do not change unless you are sure!!')

vessel_stopfill=SingleEpicsPositionerSetAndGetOnlyClass('vessel_stopfill','BL16I-CG-CRYO-01:LP1H','BL16I-CG-CRYO-01:LP1H','%','%.1f',help='Cryocooler vessel stop fill level - do not change unless you are sure!!')




def checkcryolevel():
	if cryolevel < 64 or cryolevel > 54.5:
		return 1
	else:
		return 0

def waitcryoready():
	while n2fill()==0:
		sleep(60)
	return	

def dofill():
	current_startfill=vessel_startfill()
	vessel_startfill(vessel_stopfill())
	sleep(1)
	vessel_startfill(current_startfill)

def fill_if_needed():
	if cryolevel()<60:
		dofill()
		print '=== Filling Cryocooler vessel'
		sleep(2)


#alias dofill

#State=1 if ready, 0 if moving
#need to stop motors on error; get propper State 
