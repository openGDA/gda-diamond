#Define some constant used on Beamline I06:

import sys;

from gda.configuration.properties import LocalProperties
from gda.jython.commands.GeneralCommands import run, alias
from gda.scan import ConcurrentScan


#For valve control
Close=CLOSE=cls='Close';
Open=OPEN=opn='Open';
Reset=RESET='Reset';

#For ID polarisation settings
lh=LH='Horizontal'; #linear horizontal polarization"
lv=LV='Vertical';   #linear vertical polarization"
pc=PC='PosCirc';    #positive circular polarization"
nc=NC='NegCirc';    #negative circular polarization"
la=LA='LA';         #linear arbitrary/angle"

vertical=ver='Vertical'
horizontal=hor='Horizontal'

#For ID harmonic settings
#The Harmonic value should be: "First" (1), "Third" (3) or "Fifth" (5)
First=FIRST="First";
Third=THIRD="Third";
Fifth=FIFTH="Fifth";

#For the Superconducting Magnet mode:
UNIAXIAL_X, UNIAXIAL_Y, UNIAXIAL_Z, SPHERICAL, PLANAR_XZ, QUADRANT_XY, CUBIC = range(7);
uniaxialx, uniaxialy, uniaxialz, spherical, planar_xz, quadrant_xy, cubic = range(7);

#For fast energy scan (zac scan) ID mode
fixid, cvid, slaveid = range(3);


#To define the useful beamline alias commands:

#posall command is used to print all the current beamline motor positions and beam position monitor readings 
def posall():
	print;
	print "==================== Beamline Motor Positions ===================="
	psg(ALL_MOTORS);
	print;
	print "==================== Beamline QBPM Readings ===================="
	psg(ALL_QBPMS);
	print; print;
	
alias("posall");

def clear():
	print;
	print "To Reset the namespace and reload all modules ..."
	sys.modules.clear();
	reset_namespace();
	print "Reset Done."; print;

alias("clear");



def reset_peem():
#    execfile( LocalProperties.get("gda.jython.gdaScriptDir") + "/BeamlineI06/resetPEEM.py");
	run("BeamlineI06/resetPEEM.py");

def peeminit():
	reset_peem();

def closebeam():
	gv11i.moveTo(Close);

def openbeam():
	gv11i.moveTo(Open);

def closeprep():
	gv13i.moveTo(Close);

def openprep():
	gv13i.moveTo(Open)

alias("reset_peem")
alias("peeminit")

alias("closebeam")
alias("openbeam")
alias("closebrep")
alias("openprep")






####################
#Notes: More alias from top three addition-commands for picture, closebeam and openbeam



