#!/bin/sh
# gda_launchers.sh version 4 - more generic
# Create GDA_Launchers link on users' Desktop on user successfully login
# to install this script file in /etc/X11/xinit/xinitrc.d/
#
#### This file runs if and only if BEAMLINE environment variable is set and GDA software are installed in /dls/$BEAMLINE/software/ ####
#

### check BEAMLINE environment variable ###
if [ ! -n "$BEAMLINE" ]; then
        if [ -f "/etc/profile.d/beamline.sh" ]; then
                . /etc/profile.d/beamline.sh
        else
                exit 0
        fi
fi

### Check beamline GDA installation ###
if [ ! -d "/dls_sw/$BEAMLINE/software/gda/config/." ]; then
        echo "This script requires a valid installation in '/dls_sw/$BEAMLINE/software/gda'"
        exit 0
fi

#rsync -a "/dls_sw/$BEAMLINE/software/gda/config/desktop/launchers/" "/var/tmp/$USER-$BEAMLINE-LAUNCHERS"
rsync -a --del "/dls_sw/$BEAMLINE/software/gda/config/desktop/launchers/" "/var/tmp/$USER-$BEAMLINE-LAUNCHERS/"

mkdir "$HOME/Desktop" > /dev/null 2>&1 || true
ln -nsf "/var/tmp/$USER-$BEAMLINE-LAUNCHERS" "$HOME/Desktop/$BEAMLINE Launchers"
