#!/bin/bash
. "/dls_sw/i18/etc/i18_profile.sh"
. "/$SOFTWAREFOLDER/$BEAMLINE/software/gda/$BEAMLINE-config/bin/gda_environment.sh"
echo "remote startup from dls_sw"
##/$SOFTWAREFOLDER/$BEAMLINE/software/gda/bin/GDA_StartServers > /dls/i18/var/gda_output.txt 2>&1 &
/$SOFTWAREFOLDER/$BEAMLINE/software/gda/bin/GDA_StartServers_RCP > /dls/i18/var/gda_output.txt 2>&1 &
