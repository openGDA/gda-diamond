#GDA Demos

#============================ GDA Objects ==================================
# When the GDA is started, all the devices are accessible in the Jython interpreter
# Jython objects have been created which represent the devices

# Optical Elements (OEs) are groups of motors belonging to a particular part of the beamline
# to list them:

list OE

# And to see all detectors:
list Detector

# and to see all countertimers (which are a sub-type of detectors):
list CounterTimer

# All OEs have various degrees of freedom (DOFs) associated with them.
# To list all the DOFs for an object:
dofs Mi_JackingTable

# array(['RearLeftJack', 'FrontJack', 'RearRightJack'], java.lang.String)

# To access one of these DOFs, a variable has automatically been created which has 
# the same name, but in lowercase!!
print frontjack

# this is to make typing faster and easier.  This means that all DOFs on a beamline
# must have a unique name.

# Objects which represent DOFs and devices in the Jython environments are known
# as "scannables" (er, because they can participate in scans)

# all scannables have a common set of methods which you can call:

print frontjack.getPosition()
frontjack.moveTo(10)
print frontjack.getPosition()
frontjack.moveBy(5)
print frontjack.getPosition()

# to make typing faster for these most common commands, the GDA has a special
# extended syntax for Jython.

# so the above commands would be:
print frontjack
pos frontjack 10
inc frontjack 5

# these commands are not 'real' Jython, but they can be used in the GDA environment
# if required,  beamline-specific commands can be created  for frequent repeated commands

# to find the full list of extended syntax commands, type:
help

#=====================GDA Scanning=========================================
#  The scanning mechanism does not currently include continuous scanning, but this will be 
#  added in the future.

#  Scans are defined using the GDA Jython syntax.  They are not performed using pure Jython.
# A scan has a list of objects which are operated during the scan, and a list of detectors which are read out at each point in the scan
# Only Scannable objects may be controlled in a scan.  Scannables include the DOFs which make up Optical Elements (OEs)

# for example, to raise a sample vertically and collect data at each point:
scan samplevertical 5 10 1 countertimer01
# this will collect data at heights 5,6,7,8,9,10  (start, stop, step)

# you can operate more than one scannable in a scan
scan samplevertical 5 10 1 sampleyaw 20 1 countertimer01
#this is set the sample rotation to 20 degrees initialy and move it by 1 degree when the sample hieght is moved  (start, step)

# whereas:
scan samplevertical 5 10 1 sampleyaw 20 countertimer01
# will set the sample rotation to 20 initially and not move it again (start)

# and:
scan samplevertical 5 10 1 sampleyaw countertimer01
# will senot move the sample rotation, but will record its current position in the output data

# to perform a 2D scan, give the other scannable three arguments:
scan samplevertical 5 10 1 sampleyaw 20 30 1 countertimer01
# so this will collect data at all points in the range 5 to 10 in height and 20 to 30 in rotation



#default objects:

# to include a detector or a scannable in every scan, without having to type it in the command-line, there is a list of default object
list defaults

# to have the same detector called in every scan:
add default countertimer01
#now you will not have to type the detector name every time (if you did it would not matter)

#to remove an object from the list of defaults:
remove default countertimer01


# Other types of scans will become available, such as peak finding scans, or when specific hardware is available, continuous scans
#  These will also be controlled via a similar syntax.


#
#  Scanning
#

# These operate the chi, phi and theta arms of the diffractometer and use an eight channel countertimer named 't'

# Have values of chi, phi and theta display and update in the Terminal window:
watch chi phi theta

# Find out about chi
chi

# Move chi to 50
pos chi 50

# Move chi back by 1
inc chi -1

# Obtain full position of all Scannables:
list Scannable

# Set 't' to be implicitly used in every scan:  (if you don't do this, then add 't' to the end of the other commands below)
add default t

# Scan over chi
scan chi 10 12 1

# Same scan but include current position of phi in every print out
scan chi 10 12 1 phi

# Same scan, but ensure phi is at 20
scan chi 10 12 1 phi 20

# This time start phi at 20, but move it by 1 every step
scan chi 10 12 1 phi 20 1

# Grid scan, where every point of phi and chi from 10 to 12 are operated:
scan chi 10 12 1 phi 10 12 1



# In fact it is easy for users to write their own Scannables (like VM's in JCLAM or Pseudo Motors in SPEC).  To do this, a minimum of only three methods need to be written - so its quick to write them.
# Scannables have levels so they are operated in order during a scan.
# Scannables can be set to be 'default'  (see the add default above) so they are implicitly operated in every scan.
#The data points from each scan will be shown in the display.  To have each scan plot to a brand new graph, then check the tick box at the bottom of the plotting area on the Terminal tab

#==================== Using Java from Jython ==========================================
#import Java packages as needed
import java.lang as lang

#Invoke the Java static method:
lang.System.out.println("Hello Jython from Java");

#Create Java instance the same way as create Python object, without using the Java new keyword
myStr = lang.String("Zot");

#The Java method can be invoked in two way:
#1. bounded way
print myStr.startsWith("Z")

#2. Unbounded way
print lang.String.startsWith(myStr, "Z");
  
#jarrays
import jarray
x=jarray.zeros(200,"i");
print x;

import java.lang.Math
y=java.lang.Math.sqrt(256);
print y;

#=================GDA Track Number (Scan Number)=============================================
from gda.data import NumTracker

nt = NumTracker("tmp")

#get current scan number
nt.getCurrentFileNumber()

#set new scan number
#nt.setFileNumber(2000)

del nt


#=====================Using EPICS caget() and caput to access PVs =========================================
from gda.epics import CAClient

#Create the Client
epicsClient = CAClient()

#Create the PV channels and use the caput and caget method directly
print epicsClient.caget("BL06I-AL-SLITS-01:X:CENTER.RBV")
epicsClient.caput("BL06I-AL-SLITS-01:X:CENTER", -0.55)

#Clear up the channels
epicsClient.clearup();

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================

#==============================================================
