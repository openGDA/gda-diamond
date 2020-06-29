#Define some constant used in Beamline I07:

import sys;

from gda.jython.commands.GeneralCommands import alias;
from gda.factory import Finder

#For valve control
Close=CLOSE='Close';
Open=OPEN='Open';
Reset=RESET='Reset';

#For ID polarisation settings
lh=LH='Horizontal';  #linear horizontal polarization"
lv=LV='Vertical';   #linear vertical polarization"
pc=PC='PosCirc';   #positive circular polarization"
nc=NC='NegCirc';   #negative circular polarization"


#For Diffractometer Mode settings
hor=Hor=Horizontal=horizontal=eh1h;  #Horizontal Mode"
ver=Ver=Vertical=vertical=eh1v;   #Vertical Mode"
dummy=Dum=Dummy=2;   #Dummy Mode"
eh2diff=EH2DIFF=eh2   #EH2 Diffractometer

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
	observableSubdirectory=Finder.find("observableSubdirectory");
	observableSubdirectory.deleteIObservers();
	sys.modules.clear();
	reset_namespace();
	print "Reset Done."; print;

alias("clear");
