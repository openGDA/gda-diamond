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