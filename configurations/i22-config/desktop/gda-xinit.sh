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

if [ ! -f "$HOME/.config/autostart/launcherStatus.py.desktop" ]; then
mkdir -p $HOME/.config/autostart/
cat <<EOF >  $HOME/.config/autostart/launcherStatus.py.desktop
[Desktop Entry]
Type=Application
Exec=/dls_sw/prod/etc/Launcher/launcherStatus.py
Hidden=false
X-GNOME-Autostart-enabled=true
Name=Diamond Launcher
Comment=Put a Diamond Launcher in your Notification Area
EOF
fi

