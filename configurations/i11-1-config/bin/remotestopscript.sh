#!/bin/bash
umask 002
export BEAMLINE=i11

. /dls_sw/$BEAMLINE/etc/${BEAMLINE}_profile.sh
#put stop messages to the same gda output log file as it is started with.
/dls_sw/$BEAMLINE/software/gda/config/bin/GDA_StopServers >> /dls_sw/$BEAMLINE/logs/gda_output.txt 2>&1 &
