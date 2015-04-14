###############################################################################
# This script will be run at the end of the main i15 localStation script.     #
#                                                                             #
# Thus it will be run whenever the `reset_namespace` command is run on the    #
# Jython terminal console in GDA, or the gda servers are restarted.           #
#                                                                             #
# CAUTION: Anyone may edit this script.                                       #
#                                                                             #
#          Things you put in here late at night may affect future user runs.  #
#                                                                             #
#          Any errors will prevent any future lines in this script being run. #
#                                                                             #
###############################################################################
print "Running /dls/i15/scripts/localStationUser.py (user editable)"

#######################################+#######################################
###                     Other scripts and configuration                     ###
###############################################################################
#                                                                             #
###############################################################################

### Loading math for tuple definition of non-equidistant E scanning
import scisoftpy as dnp

### Standard options


### Special purpose options


### Visit specific options

add_default(thermo1)
add_default(pt100_1)
add_default(d1sum)

#######################################+#######################################
###                                   END                                   ###
###############################################################################
print "Completed running /dls/i15/scripts/localStationUser.py (user editable)"
