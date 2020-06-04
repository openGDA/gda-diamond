#localStation_energy_and_diff_only.py

from Jama import Matrix
from constants import *
from gda.configuration.properties import LocalProperties, LocalProperties
from gda.device.epicsdevice import ReturnType
from gda.device.monitor import EpicsMonitor
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from uk.ac.diamond.daq.persistence.jythonshelf import LocalJythonShelfManager
from installation import isEpicsSim
from javashell import *
from math import *
from pd_dummy import dummyClass
from pd_readSingleValueFromVectorScannable import \
	ReadSingleValueFromVectorPDClass
from pd_time import tictoc, showtimeClass, mrwolfClass, showincrementaltimeClass, \
	waittimeClass, TimeScannable
from scannable.MonitorWrapper import MonitorWrapper
from time import sleep
from startup_dataDirFunctions import datadir
import ShelveIO
import installation
import java
import time

from gda.jython.commands.GeneralCommands import alias, run


###############################################################################
# 
#   localStation.py
#
###############################################################################

print "======================================================================"
print "Running I16 specific initialisation code from localStation.py (7.8.x) :"
print "======================================================================"
installation.set(isLive=1)
#installation.set(isEpicsSim=0)
installation.setLoadOldShelf(0)



###############################################################################
###                 Wrap all monitors to make them simply scannable         ###
###############################################################################
toPrint = ''
for objname in dir():
	if isinstance(eval(objname),EpicsMonitor):
		toPrint+= objname + " "
		exec(objname + " = MonitorWrapper(" + objname + ")")
print "Wrapped the monitors: " + toPrint



###############################################################################
###             Generally useful commands, imports and constants            ###
###############################################################################

print "Importing generally useful modules"


#run("pd_readSingleValueFromVectorScannable") #-->ReadSingleValueFromVectorPDClass

print "Importing contants"

print "Creating dummy scannables"

#run("pd_dummy")
dummy = dummyClass('Dummy')
x=dummyClass('x')
y=dummyClass('y')
z=dummyClass('z')
q=dummyClass('q')
qq=dummyClass('qq')
progress=dummyClass('progress')

print "Creating time scannables"
#run("pd_time")

tim = TimeScannable('Time')
showtime=showtimeClass('Showtime')
inctime=showincrementaltimeClass('inctime')
waittime=waittimeClass('Waittime')
w=waittime	#abreviated name
mrwolf=mrwolfClass('mrwolf')




print "Running startup_dataDirFunctions.py"
run('startup_dataDirFunctions')
alias('datadir')
print "  use 'datadir' to read the current directory or 'datadir name' to chnage it"

rc.setOutputFormat(['%.2f'])	#output format for ring current





###############################################################################
###                         Setup shelveIO path                             ###
###############################################################################
print "Configuring ShelveIO system"


shelveIoDir = LocalProperties.get("gda.config")
shelveIoDir  = shelveIoDir + "/var/oldStyleShelveIO/"
ShelveIO.ShelvePath = shelveIoDir
print "  ShelveIO path = ", shelveIoDir



###############################################################################
###                            Offset devices                               ###
###############################################################################
print "Running startup_offsets.py: Starting database system..."
run("startup_offsets")
print "...Database system started"
offsetshelf=LocalJythonShelfManager.open('offsets')
print "  use 'offsetshelf' to see summary of offsets"
delta_axis_offset.pil =-9.5
do=delta_axis_offset


###############################################################################
###############################################################################
###############################################################################
###############################################################################

run("startup_epics_positioners")
run("startup_energy_related")
run("startup_diffractometer_related_DEV")









###############################################################################
###                             Tweak scannables                            ###
###############################################################################
# TODO: Try to move to end. Does anythin later depend on these new names

print "Hacking some scannables' InputName arrays"
eta.setInputNames(['eta'])
chi.setInputNames(['chi'])
phi.setInputNames(['phi'])
psi.setInputNames(['psi'])
psic.setInputNames(['psic'])


print "Changing some scannables' output formats"
eta.setOutputFormat(['%.4f'])
delta.setOutputFormat(['%.4f'])

try:
	finder.find('mu_motor').setSpeed(1.0)
	finder.find('gamma_motor').setSpeed(2.0)
except:
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Could not set speend on mu or gamma - probably disconnected !!!!!!!!!!!!!!"

delta.setOutputFormat(['%.5f'])
gam.setOutputFormat(['%.5f'])
rc.setOutputFormat(['%.4f'])

###############################################################################
###                             Xtalinfo
###############################################################################
run("pd_crystal_info")
xtalinfo=crystalinfo('xtalinfo','A','%7.5f',ub,cr)
print "creating crystal info"
################################

###############################################################################
###                              Set user limits                            ###
###############################################################################
print "Setting user limits (running ConfigureLimits.py)"
run("ConfigureLimits")

###############################################################################
###                           Theta with offset eta                         ###
###############################################################################
print "Creating scannarcbles with offsets(th is eta with offset eta_offset"
run("pd_offsetAxis") #--> OffsetAxisClass
# e.g. th is eta with eta_off as offset
th=OffsetAxisClass('th',eta,eta_offset,help='eta device with offset given by eta_offset. Use pos eta_offset to change offset')






datadir("/dls/i16/data/2009/mt0/run4/")






