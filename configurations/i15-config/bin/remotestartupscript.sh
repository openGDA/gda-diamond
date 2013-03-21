#!/bin/bash

LOGDIR=/dls_sw/i15/var
LOGNAME=gda_output
export LOGFILE=$LOGDIR/$LOGNAME/$LOGNAME_`date +%F-%T`.txt
touch $LOGFILE
rm $LOGDIR/$LOGNAME.txt
ln -s $LOGFILE $LOGDIR/$LOGNAME.txt

. /dls_sw/i15/etc/i15_profile.sh

CMD="$SSH_ORIGINAL_COMMAND"
: ${CMD:="$*"}

SOFTWAREFOLDER=dls_sw; export SOFTWAREFOLDER
OBJECT_SERVER_STARTUP_FILE=/$SOFTWAREFOLDER/$BEAMLINE/var/object_server_startup_i15server
rm -f $OBJECT_SERVER_STARTUP_FILE

echo  /dls_sw/i15/software/gda/i15-config/bin/GDA_StartServers $CMD to $LOGFILE
nohup /dls_sw/i15/software/gda/i15-config/bin/GDA_StartServers $CMD >  $LOGFILE 2>&1&

#
# look for the output file which will tell us when the servers have started
#

/$SOFTWAREFOLDER/$BEAMLINE/software/gda/i15-config/bin/lookForFile $OBJECT_SERVER_STARTUP_FILE
