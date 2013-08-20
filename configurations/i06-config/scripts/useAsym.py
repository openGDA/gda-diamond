from time import sleep;
from gda.epics import CAClient

def getAsymmetry01():
	sleep(2);
	return 0.123456;

def getAsymmetry():
	
	t=CAClient()
	#import math
	
	pos iddpol pc
	pos rpenergy 640.83
	
	signal_c1_E1_P2=0
	for average_readout in range(3):
	
		t.caput("BL06I-DI-8512-02:STARTCOUNT", 1)
		sleep(2)
		c1=t.caget("BL06J-EA-USER-01:SC1-RAW")
		signal_c1_E1_P2=signal_c1_E1_P2+float(c1)
		print c1
	
	pos rpenergy 630
	
	signal_c1_E0_P2=0
	for average_readout in range(3):
	
		t.caput("BL06I-DI-8512-02:STARTCOUNT", 1)
		sleep(2)
		c1=t.caget("BL06J-EA-USER-01:SC1-RAW") 
		signal_c1_E0_P2=signal_c1_E0_P2+float(c1)
		print c1
	
	pos iddpol nc
	pos rpenergy 630
	
	signal_c1_E0_P3=0
	for average_readout in range(3):
	
		t.caput("BL06I-DI-8512-02:STARTCOUNT", 1)
		sleep(2)
		c1=t.caget("BL06J-EA-USER-01:SC1-RAW")
		signal_c1_E0_P3=signal_c1_E0_P3+float(c1)
		print c1
	
	pos rpenergy 640.83
	
	signal_c1_E1_P3=0
	for average_readout in range(3):
	
		t.caput("BL06I-DI-8512-02:STARTCOUNT", 1)
		sleep(2)
		c1=t.caget("BL06J-EA-USER-01:SC1-RAW")
		signal_c1_E1_P3=signal_c1_E1_P3+float(c1)
		print c1
	
	pos iddpol pc
	
	asymmetry=(signal_c1_E1_P2/(signal_c1_E0_P2+1)-signal_c1_E1_P3/(signal_c1_E0_P3+1))/(signal_c1_E1_P2/(signal_c1_E0_P2+1)+signal_c1_E1_P3/(signal_c1_E0_P3+1)) 
	#/(signal_c1_E1_P2/(signal_c1_E0_P2+1)+signal_c1_E1_P3/(signal_c1_#E0_P3+1))
	
	print 'asymmetry=', asymmetry
	
	return asymmetry;


#Usage:
from Diamond.PseudoDevices.AsymmetryDevices import TemperatureControllerClass;
from Diamond.PseudoDevices.AsymmetryDevices import AsymmetryDeviceClass;

pvTempSetReadBack = 'BL06J-EA-ITC-01:READ:S_TEMP'
pvTempSet='BL06J-EA-ITC-01:SET:TEMP';
pvTemp1='BL06J-EA-ITC-01:READ:TEMP1';
pvTemp2 = 'BL06J-EA-ITC-01:READ:TEMP2';

tc=TemperatureControllerClass('tc', pvTempSet, pvTempSetReadBack, pvTemp1, pvTemp2);
asym1=AsymmetryDeviceClass('asym1', 'getAsymmetry');

tc.setDelay(10);
tc.setError(1);
