#!/bin/bash
# This script is only invoked when user gda2 ssh's to the control machine. It is run by an entry in gda's ~/.ssh/authorized_keys
$GDA_INSTANCE_CONFIG/etc/live/remotestartupscript.sh

# the /localhome/gda2/.ssh/authorized_keys on i08-control file needs updating in cf_engine to call the above script directly and then delete this script