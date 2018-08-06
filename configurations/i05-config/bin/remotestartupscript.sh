#!/bin/bash
# This script is only invoked when user gda2 ssh's to the control machine. It is run by an entry in gda's ~/.ssh/authorized_keys
/dls_sw/i05/software/gda/config/etc/live/remotestartupscript.sh

# the /localhome/gda2/.ssh/authorized_keys on i05-control file needs updating in cf_engine to call the above script directly and then delete this script