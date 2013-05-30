#!/bin/bash
umask 0002
export BEAMLINE=i07

if [ -f "/etc/profile.d/modules.sh" ]; then
    . /etc/profile.d/modules.sh
fi

if [ -f "/etc/profile.d/modules.sh" ]; then
    . /etc/profile.d/modules.sh
fi

. /dls_sw/$BEAMLINE/etc/gda_environment.sh

/dls_sw/$BEAMLINE/software/gda/bin/GDA_StartServers >> /dls/$BEAMLINE/var/gda_output.txt 2>&1 &
