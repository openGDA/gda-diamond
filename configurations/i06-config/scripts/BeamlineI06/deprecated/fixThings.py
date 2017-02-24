from Diamond.Objects.EpicsPv import EpicsButtonClass
from Diamond.Objects.EpicsPv import EpicsPvClass

from time import sleep;

#For fixing the Hexapod

#Click the "Copy readback to setpoint Button of Hexapod to fix it"
def hexinit():
	logger.simpleLog( "------ To fix the I06 Hexapods by pressing the EPICS STOP and COPY STOP buttons ------");
	pvCopyButtonM1 = 'BL06I-OP-COLM-01:TCPUP.PROC';
	pvCopyButtonM3 = 'BL06I-OP-FCMIR-01:TCPUP.PROC';
	pvCopyButtonM6 = 'BL06I-OP-SWMIR-01:TCPUP.PROC';
	pvCopyButtonM7 = 'BL06J-OP-FCMIR-01:TCPUP.PROC';
	
	m1CopyButton = EpicsButtonClass(pvCopyButtonM1);
	m3CopyButton = EpicsButtonClass(pvCopyButtonM3);
	m6CopyButton = EpicsButtonClass(pvCopyButtonM6);
	m7CopyButton = EpicsButtonClass(pvCopyButtonM7);
	
	pvStopButtonM1 = 'BL06I-OP-COLM-01:SCAN.WAIT';
	pvStopButtonM3 = 'BL06I-OP-FCMIR-01:SCAN.WAIT';
	pvStopButtonM6 = 'BL06I-OP-SWMIR-01:SCAN.WAIT';
	pvStopButtonM7 = 'BL06J-OP-FCMIR-01:SCAN.WAIT';
	
	m1StopButton = EpicsButtonClass(pvStopButtonM1);
	m3StopButton = EpicsButtonClass(pvStopButtonM3);
	m6StopButton = EpicsButtonClass(pvStopButtonM6);
	m7StopButton = EpicsButtonClass(pvStopButtonM7);

	m1StopButton.press(); m1CopyButton.press();
	m3StopButton.press(); m3CopyButton.press();
	m6StopButton.press(); m6CopyButton.press();
	m7StopButton.press(); m7CopyButton.press();

	sleep(1);
	print "Done."

#For fixing the PGM motors when they get stuck in a busy state
def pgminit():
	logger.simpleLog( "------ To fix the I06 PGM ------");
	pgmMirror = EpicsPvClass("BL06I-OP-PGM-01:PITCH:MIR.SPMG");
	pgmGratting= EpicsPvClass("BL06I-OP-PGM-01:PITCH:GRT.SPMG");
	pgmEnergy= EpicsPvClass("BL06I-OP-PGM-01:ENERGY.SPMG");

	logger.simpleLog( "------ To stop its motors first ------");
	pgmMirror.caput(0); #puts it into stop mode
	pgmGratting.caput(0); #puts it into stop mode
	pgmEnergy.caput(0); #puts it into stop mode

	sleep(2);
	logger.simpleLog( "------ Then to start its motors ------");
	pgmMirror.caput(3); #puts it into go mode
	pgmGratting.caput(3); #puts it into go mode
	pgmEnergy.caput(3); #puts it into go mode

	sleep(1);
	print "Done. Should be OK now"

#For fixing the PGM motors when they get stuck in a busy state
def iddinit():
	try:
		logger.simpleLog( "---------- Initialising Down Stream ID ----------");
		print " ... Move iddgap to 28";
		iddgap.moveTo(28);
		
		print " ... Move iddtrp to 22";
		iddtrp.moveTo(22);
		
		print " ... Move iddbrp to 22";
		iddbrp.moveTo(22);
	
		print " ... Move pgmenergy to 400 eV";
		pgmenergy.moveTo(400);
	
		print " ... Move iddenergy to 400 eV";
		iddenergy.moveTo(400);
	
		print " ... Move iddrpenergy";
		iddrpenergy.moveTo(400);
		
		print " ... Move iddpgmenergy";
		iddpgmenergy.moveTo(400);
		
		print " ... Change the polarisation to 'Positive Circular' mode"
		iddpol.moveTo(pc);
		
		print " ... Tweak the denergy to confirm the moving"
		denergy.moveTo(401);
		print " ... Current denergy: " + str(denergy.getPosition());
		sleep(2);
		
		denergy.moveTo(400);
		print "Current energy values:";
		print Energy;
		print pgmenergy;
		print iddpol;
		print;
		print "---------- Done! Downstream ID initialised successfully ----------";
	except:
		type, exception, traceback = sys.exc_info();
		logger.fullLog(None,"localStation error -  " , type, exception, traceback, False);



alias("hexinit");
#setAlias("hexinit", "hexinit()");

alias("pgminit");
#setAlias("pgminit", "pgminit()");
alias("iddinit");
	
