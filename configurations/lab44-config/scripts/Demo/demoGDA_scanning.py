#
#  Scanning
#

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
