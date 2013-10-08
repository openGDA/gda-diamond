#!/bin/bash

. /usr/share/Modules/init/bash
. /dls_sw/i10/etc/i10_profile.sh

CMD="$SSH_ORIGINAL_COMMAND"
: ${CMD:="$*"}

SOFTWAREFOLDER=dls_sw; export SOFTWAREFOLDER
OBJECT_SERVER_STARTUP_FILE=/$SOFTWAREFOLDER/$BEAMLINE/var/object_server_startup_I10-main
rm -f $OBJECT_SERVER_STARTUP_FILE

/dls_sw/i10/software/gda/workspace_git/gda-mt.git/configurations/$BEAMLINE-config/bin/GDA_StartServers $CMD

# look for the output file which will tell us when the servers have started

/$SOFTWAREFOLDER/$BEAMLINE/software/gda/workspace_git/gda-mt.git/configurations/$BEAMLINE-config/bin/lookForFile $OBJECT_SERVER_STARTUP_FILE
