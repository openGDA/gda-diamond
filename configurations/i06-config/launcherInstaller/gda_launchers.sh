#!/bin/sh
# gda_launchers.sh version 4 - more generic
# Create GDA_Launchers link on users' Desktop on user successfully login
# to install this script file in /ect/X11/xinit/xinitrc.d/ 
#
#### This file runs if and only if BEAMLINE environment variable is set and GDA software are installed in /dls_sw/$BEAMLINE/software/ ####
#


##For the screen grabber to eLog:
panel="top_panel"
position="1"
right_stick="true"
#launcher_path="/usr/share/applications/gnome-terminal.desktop"
launcher_path="/dls_sw/i06-1/software/gda/config/Desktop/grab2log.desktop"
launcher_id="grab2elog_launcher"

# Apply the schemas
for schema in $(gconftool-2 --all-entries /schemas/apps/panel/objects | awk -F '=' '{print $1}'); do
    gconftool-2 --apply-schema /schemas/apps/panel/objects/$schema /apps/panel/objects/$launcher_id/$schema
done

# Tweak things
gconftool-2 --set /apps/panel/objects/$launcher_id/object_type -t string launcher-object
gconftool-2 --set /apps/panel/objects/$launcher_id/launcher_location -t string $launcher_path
gconftool-2 --set /apps/panel/objects/$launcher_id/toplevel_id -t string $panel
gconftool-2 --set /apps/panel/objects/$launcher_id/position -t int $position
gconftool-2 --set /apps/panel/objects/$launcher_id/panel_right_stick -t bool $right_stick 

object_id_list=$(gconftool-2 --get /apps/panel/general/object_id_list | sed -e "s|]|, $launcher_id]|" )


### Check beamline GDA installation ###
if [ ! -h "/dls_sw/$BEAMLINE/software/gda" ]; then
	echo "GDA is not installed at /dls_sw/$BEAMLINE/software/gda. " >> $HOME/login.log
else

	## set up GDA desktop launcher on user login
	if [ ! -h "$HOME/Desktop/GDA_Launchers" ]; then
		#update desktop files
		if [ ! -d "/dls_sw/$1/var/Desktop" ]; then
			cp -R /dls_sw/$BEAMLINE/software/gda/config/Desktop /dls_sw/$1/var/Desktop
			if [ -d "/dls_sw/$1/var/Desktop/.svn" ]; then
				rm -rf /dls_sw/$1/var/Desktop/.svn
			fi
		else
			cp -Rf /dls_sw/$BEAMLINE/software/gda/config/Desktop /dls_sw/$1/var/.
			if [ -d "/dls_sw/$1/var/Desktop/.svn" ]; then
				rm -rf /dls_sw/$1/var/Desktop/.svn
			fi
		fi
		# create Desktop Links
		if [ -d "/dls_sw/$1/var/Desktop" ]; then
			cp -Rf /dls_sw/$1/var/Desktop/gda-client-i06.desktop $HOME/Desktop/.
			cp -Rf /dls_sw/$1/var/Desktop/gda-client-i06-1.desktop $HOME/Desktop/.
		elif [ -d "/dls_sw/$BEAMLINE/software/gda/config/Desktop" ]; then
			cp -Rf /dls_sw/$BEAMLINE/software/gda/config/Desktop/gda-client-i06.desktop $HOME/Desktop/.
			cp -Rf /dls_sw/$BEAMLINE/software/gda/config/Desktop/gda-client-i06-1.desktop $HOME/Desktop/.
		fi
		
		#To add the applet once everything has been setup
		gconftool-2 --set /apps/panel/general/object_id_list --type list --list-type string "${object_id_list//[[:blank:]]/}"
	fi

	## setup to remove GDA desktop launchers on user logout
	#Create the logout scripts file $HOME/.logout in home directory and make sure it is executable, i.e.
	if [ ! -d "$HOME/.logout" ]; then
		if [ ! -f "$HOME/.logout" ]; then
			cp -f /dls_sw/$BEAMLINE/software/gda/config/launcherInstaller/logout.sh $HOME/.logout
			chmod 755 $HOME/.logout
		else
			cp -f /dls_sw/$BEAMLINE/software/gda/config/launcherInstaller/logout.sh $HOME/.
			chmod 755 $HOME/logout.sh
			echo '. $HOME/logout.sh' >> $HOME/.logout
		fi
	else
		cp -f /dls_sw/$BEAMLINE/software/gda/config/launcherInstaller/logout.sh $HOME/.logout/gda_launchers_remove.sh
		chmod 755 $HOME/.logout/gda_launchers_remove.sh
	fi

	# setup trap to run logout script on user exit the system
	trap '. $HOME/.logout;exit' 0
fi
