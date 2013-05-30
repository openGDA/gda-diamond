#!/bin/sh
# gda_launchers.sh version 4 - more generic
# Create GDA_Launchers link on users' Desktop on user successfully login
# to install this script file in /ect/X11/xinit/xinitrc.d/ 
#
#### This file runs if and only if BEAMLINE environment variable is set and GDA software are installed in /dls/$BEAMLINE/software/ ####
#

### check BEAMLINE environment variable ###
if [ ! -n "$BEAMLINE" ]; then
	if [ -f "/etc/profile.d/beamline.sh" ]; then
		. /etc/profile.d/beamline.sh
	else
		echo "Error >>>> 'BEAMLINE' environment variable must be set for 'gda_launchers.sh' to work." >> $HOME/login.log
	fi
fi

### Check beamline GDA installation ###
if [ ! -h "/dls/$BEAMLINE/software/gda" ]; then
	echo "GDA is not installed at /dls/$BEAMLINE/software/gda. " >> $HOME/login.log
else

	## set up GDA desktop launcher on user login
	if [ ! -h "$HOME/Desktop/GDA_Launchers" ]; then
		#update desktop files
		if [ ! -d "/var/Desktop" ]; then
			cp -R /dls/$BEAMLINE/software/gda/config/Desktop /var/Desktop
			if [ -d "/var/Desktop/.svn" ]; then
				rm -rf /var/Desktop/.svn
			fi
		else
			cp -Rf /dls/$BEAMLINE/software/gda/config/Desktop /var/.
			if [ -d "/var/Desktop/.svn" ]; then
				rm -rf /var/Desktop/.svn
			fi
		fi
		# create Desktop Links
		if [ -d "/var/Desktop" ]; then
			ln -s /var/Desktop $HOME/Desktop/GDA_Launchers
		elif [ -d "/dls/$BEAMLINE/software/gda/config/Desktop" ]; then
			ln -s /dls/$BEAMLINE/software/gda/config/Desktop $HOME/Desktop/GDA_Launchers
		fi
	fi

	## setup to remove GDA desktop launchers on user logout
	#Create the logout scripts file $HOME/.logout in home directory and make sure it is executable, i.e.
	if [ ! -d "$HOME/.logout" ]; then
		if [ ! -f "$HOME/.logout" ]; then
			cp -f /dls/$BEAMLINE/software/gda/config/launcherInstaller/logout.sh $HOME/.logout
			chmod 755 $HOME/.logout
		else
			cp -f /dls/$BEAMLINE/software/gda/config/launcherInstaller/logout.sh $HOME/.
			chmod 755 $HOME/logout.sh
			echo '. $HOME/logout.sh' >> $HOME/.logout
		fi
	else
		cp -f /dls/$BEAMLINE/software/gda/config/launcherInstaller/logout.sh $HOME/.logout/gda_launchers_remove.sh
		chmod 755 $HOME/.logout/gda_launchers_remove.sh
	fi

	# setup trap to run logout script on user exit the system
	trap '. $HOME/.logout;exit' 0
fi
