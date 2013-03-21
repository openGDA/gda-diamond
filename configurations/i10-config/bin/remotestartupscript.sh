#!/bin/bash
. "/dls_sw/i10/etc/i10_profile.sh"
echo "Remote startup from dls_sw"

echo /$SOFTWAREFOLDER/$BEAMLINE/software/gda/i10-config/bin/GDA_StartServers
     /$SOFTWAREFOLDER/$BEAMLINE/software/gda/i10-config/bin/GDA_StartServers
