#!/bin/bash
# This file used by remove server to start GDA servers and forward all messages to gda_output.txt. It must source the beamline profile.


umask 002

export BEAMLINE=i09-2


. /dls_sw/$BEAMLINE/etc/${BEAMLINE}_profile.sh

# when remote server restart on a different date, a new gda_out file is logged, 
# i.e. GDA session logs (for the same date restart a single log file is used)
export LOGFILE=/dls_sw/$BEAMLINE/logs/gda_output_`date +%F-%T`.txt
echo Running /dls_sw/$BEAMLINE/software/gda/config/bin/GDA_StartServers to output to $LOGFILE
touch $LOGFILE
rm /dls_sw/$BEAMLINE/logs/gda_output.txt
ln -s $LOGFILE /dls_sw/$BEAMLINE/logs/gda_output.txt

/dls_sw/$BEAMLINE/software/gda/config/bin/GDA_StartServers >> /dls_sw/$BEAMLINE/logs/gda_output.txt 2>&1 &
