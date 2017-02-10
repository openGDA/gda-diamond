###############################################################################
# This script will be run at the end of the main i15-1 localStation script.   #
#                                                                             #
# Thus it will be run whenever the `reset_namespace` command is run on the    #
# Jython terminal console in GDA, or the gda servers are restarted.           #
#                                                                             #
# CAUTION: Anyone may edit this script.                                       #
#                                                                             #
#          Things you put in here late at night may affect future user runs.  #
#                                                                             #
#          Any errors will prevent subsequent lines in this script being run. #
#                                                                             #
###############################################################################
print "Running /dls_sw/i15-1/scripts/localStationUser.py (user editable)"

##### Define which scan processes take place after each scan ##### 

# scan_processor.processors=[GaussianPeakAndBackgroundP(), GaussianDiscontinuityP(), Lcen(), Rcen()]


#scan_processor.processors=[GaussianEdge(), GaussianDiscontinuityP(),GaussianPeakAndBackground()]
#scan_processor.processors=[MaxPositionAndValue(), MinPositionAndValue(), CentreOfMass(), GaussianPeakAndBackground(), GaussianEdge(), Lcen(), Rcen()]

#######################################+#######################################
###                                   END                                   ###
###############################################################################
print "Completed running /dls_sw/i15-1/scripts/localStationUser.py (user editable)"
