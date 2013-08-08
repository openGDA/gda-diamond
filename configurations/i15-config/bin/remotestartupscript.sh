#!/bin/bash

. /usr/share/Modules/init/bash
. /dls_sw/i15/etc/i15_profile.sh

CMD="$SSH_ORIGINAL_COMMAND"
: ${CMD:="$*"}

SOFTWAREFOLDER=dls_sw; export SOFTWAREFOLDER
OBJECT_SERVER_STARTUP_FILE=/$SOFTWAREFOLDER/$BEAMLINE/software/gda_versions/var/object_server_startup_server_main
rm -f $OBJECT_SERVER_STARTUP_FILE

/dls_sw/i15/software/gda/config/bin/GDA_StartServers $CMD

# look for the output file which will tell us when the servers have started

/$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/bin/lookForFile $OBJECT_SERVER_STARTUP_FILE
