#!/bin/sh

### check BEAMLINE environment variable ###
if [ ! -n "$BEAMLINE" ]; then
	if [ -f "/etc/profile.d/beamline.sh" ]; then
		# set BEAMLINE parameter
		. /etc/profile.d/beamline.sh
	else
		echo "Parameter $BEAMLINE is not set."
		echo "Instal-gda-launchers only available for beamline workstations support client-server deployment."
		echo -n "Is this PC a beamline workstation (y/n)?"
		read input
		echo -n "which beamline (i11/b23)?"
		read beamlinename
		if [ "$input" = "y" ]; then
			echo "Install beamline.sh "
			sudo cp -f /$SOFTWAREFOLDER/$beamlinename/software/gda/config/launcherInstaller/beamline.sh /etc/profile.d/.
			sudo chmod 755 /etc/profile.d/beamline.sh
			. /etc/profile.d/beamline.sh
		else
			exit 1
		fi 
	fi
fi

### Check beamline GDA installation ###
if [ ! -h "/$SOFTWAREFOLDER/$BEAMLINE/software/gda" ]; then
	echo "This script requires a valid link '/$SOFTWAREFOLDER/$BEAMLINE/software/gda' pointing to the GDA installation. "
	exit 1
fi

#### xinitrc.d - install gda_launchers ####
if [ ! -f "/etc/X11/xinit/xinitrc.d/gda_launchers.sh" ]; then
	echo "Install GDA launchers"
else 
	echo "Update GDA launchers"
fi
sudo cp -f /$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/launcherInstaller/gda_launchers.sh /etc/X11/xinit/xinitrc.d/gda_launchers.sh
sudo chmod 755 /etc/X11/xinit/xinitrc.d/gda_launchers.sh

#### set up desktop files and menus ####
# check if folder exist 
if [ ! -d "/var/Desktop" ]; then
	sudo mkdir /var/Desktop
fi

# copy files
echo "Install/Update GDA desktop menu"
sudo cp -f /$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/Desktop/*.desktop /var/Desktop
sudo cp -f /$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/Desktop/*.menu /var/Desktop
sudo cp -f /$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/Desktop/*.directory /var/Desktop
sudo cp -f /$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/Desktop/.hidden /var/Desktop

# change permission to avoid the desktop launcher appear with no-entry emblems
sudo chmod -R 777 /var/Desktop

# create desktop links for Application Menu Items for Data Acquisition
sudo ln -sf /var/Desktop/gda-logpanel.desktop /usr/share/applications/gda-logpanel.desktop
sudo ln -sf /var/Desktop/gda-servers.desktop /usr/share/applications/gda-servers.desktop
sudo ln -sf /var/Desktop/gda-client.desktop /usr/share/applications/gda-client.desktop
sudo ln -sf /var/Desktop/gda-swing.desktop /usr/share/applications/gda-swing.desktop
sudo ln -sf /var/Desktop/gda-user-guide.desktop /usr/share/applications/gda-user-guide.desktop
sudo ln -sf /var/Desktop/gda.desktop /usr/share/applications/gda.desktop
sudo ln -sf /var/Desktop/gdaswing.desktop /usr/share/applications/gdaswing.desktop
sudo ln -sf /var/Desktop/gda-startup-guide.desktop /usr/share/applications/gda-startup-guide.desktop
sudo ln -sf /var/Desktop/gda-beamline-manual.desktop /usr/share/applications/gda-beamline-manual.desktop
sudo ln -sf /var/Desktop/gda-logfile.desktop /usr/share/applications/gda-logfile.desktop
sudo ln -sf /var/Desktop/gda-data-backup-2-usb.desktop /usr/share/applications/gda-data-backup-2-usb.desktop
sudo ln -sf /var/Desktop/gda-start-mythen-detector.desktop /usr/share/applications/gda-start-mythen-detector.desktop
#create menu links to display in Applications Menu
sudo ln -sf /var/Desktop/gda.directory /usr/share/desktop-directories/gda.directory
sudo ln -sf /var/Desktop/gda.menu /etc/xdg/menus/applications-merged/gda.menu

#### set up beamline profiles for GDA ####
# check if folder exist
echo
if [ ! -d "/$SOFTWAREFOLDER/$BEAMLINE/etc" ]; then
	echo "Please log into $BEAMLINE-control to create directory /$SOFTWAREFOLDER/$BEAMLINE/etc"
fi
# copy files
cp -f /$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/etc/${BEAMLINE}_profile.sh /$SOFTWAREFOLDER/$BEAMLINE/etc
ls -l /$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/etc/${BEAMLINE}_profile.sh
echo "Please make sure /$SOFTWAREFOLDER/$BEAMLINE/etc/${BEAMLINE}_profile.sh is EXECUTABLE."
echo
#### set up remote-start-up script ####
ls -l /$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/bin/remotestartupscript.sh
echo "Please make sure /$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/bin/remotestartupscript.sh is EXECUTABLE."
echo
#### set up remote start GDA key ###
if [ ! -r "/$SOFTWAREFOLDER/$BEAMLINE/${BEAMLINE}ssh.key" ]; then
	cp -f /$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/keys/${BEAMLINE}ssh.key /$SOFTWAREFOLDER/$BEAMLINE/software/gda_versions/var/
fi
ls -l /$SOFTWAREFOLDER/$BEAMLINE/software/gda_versions/var/${BEAMLINE}ssh.key
echo "Please make sure /$SOFTWAREFOLDER/$BEAMLINE/${BEAMLINE}ssh.key file is owned by 'gda:gda'."
echo 
echo "Importent: You need to login to the server to change ownership and mode of files"
echo	
### Message to Installer ###
echo "Now you need to logout then login again for this to take effect, Thank You!"

