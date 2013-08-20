#!/bin/bash

#!/bin/bash
#Note: this scripts should be executed by user gda from i06-control manually

export BEAMLINE=$1;

echo $BEAMLINE;

. /dls/i06/etc/gda_environment.sh

/dls/$BEAMLINE/software/gda/bin/GDA_StartServers > /dls/$BEAMLINE/var/gda_output.txt 2>&1 &
