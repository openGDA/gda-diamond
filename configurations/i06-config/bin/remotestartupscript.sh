#!/bin/bash
#Note: this scripts should be executed by user gda from i06-control
#So after new installation, this file should be in /dls/i06_sw/software/gda/bin/remotestartupscript.sh

CMD="$SSH_ORIGINAL_COMMAND"
: ${CMD:="$*"}

case "$CMD" in
'i06-1') export BEAMLINE=i06-1;;
*) export BEAMLINE=i06;;
esac

if [ -f "/etc/profile.d/modules.sh" ]; then
    . /etc/profile.d/modules.sh
fi

. /dls_sw/$BEAMLINE/etc/gda_environment.sh

/dls_sw/$BEAMLINE/software/gda/bin/GDA_StartServers > /dls/$BEAMLINE/var/gda_output.txt 2>&1 &

