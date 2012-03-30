#!/bin/sh

if [ $# -ne 1 ]; then
	echo 1>&2 Usage: $0 i11
	exit 127
fi

### Check beamline GDA installation ###
if [ ! -h "/$SOFTWAREFOLDER/$1/software/gda" ]; then
	echo "This script requires a valid link '/$SOFTWAREFOLDER/$1/software/gda' pointing to the GDA installation. "
	exit 1
fi

### install BEAMLINE environment variable ###
if [ ! -f "/etc/profile.d/beamline.sh" ]; then
	echo "Install beamline.sh "
	sudo cp -f /$SOFTWAREFOLDER/$1/software/gda/config/launcherInstaller/beamline.sh /etc/profile.d
	sudo chmod 755 /etc/profile.d/beamline.sh
fi

#### xinitrc.d - install gda_launchers ####
if [ ! -f "/etc/X11/xinit/xinitrc.d/gda_launchers.sh" ]; then
	echo "Install GDA launchers"
else 
	echo "Update GDA launchers"
fi
sudo cp -f /$SOFTWAREFOLDER/$1/software/gda/config/launcherInstaller/gda_launchers.sh /etc/X11/xinit/xinitrc.d/gda_launchers.sh
sudo chmod 755 /etc/X11/xinit/xinitrc.d/gda_launchers.sh

#### set up desktop files and menus ####
# check if folder exist 
if [ ! -d "/var/Desktop" ]; then
	sudo mkdir /var/Desktop
fi

# copy files
echo "Install/Update GDA desktop menu"
sudo cp -f /$SOFTWAREFOLDER/$1/software/gda/config/Desktop/*.desktop /var/Desktop
sudo cp -f /$SOFTWAREFOLDER/$1/software/gda/config/Desktop/*.menu /var/Desktop
sudo cp -f /$SOFTWAREFOLDER/$1/software/gda/config/Desktop/*.directory /var/Desktop
sudo cp -f /$SOFTWAREFOLDER/$1/software/gda/config/Desktop/.hidden /var/Desktop

# change permission to avoid the desktop launcher appear with no-entry emblems
sudo chmod -R 777 /var/Desktop

# create desktop links and menu links
sudo ln -sf /var/Desktop/gda-logpanel.desktop /usr/share/applications/gda-logpanel.desktop
sudo ln -sf /var/Desktop/gda-servers.desktop /usr/share/applications/gda-servers.desktop
sudo ln -sf /var/Desktop/gda-client.desktop /usr/share/applications/gda-client.desktop
sudo ln -sf /var/Desktop/gda-user-guide.desktop /usr/share/applications/gda-user-guide.desktop
sudo ln -sf /var/Desktop/gda-startup-guide.desktop /usr/share/applications/gda-startup-guide.desktop
sudo ln -sf /var/Desktop/gda-beamline-manual.desktop /usr/share/applications/gda-beamline-manual.desktop
sudo ln -sf /var/Desktop/gda-logfile.desktop /usr/share/applications/gda-logfile.desktop
sudo ln -sf /var/Desktop/gda-data-backup-2-usb.desktop /usr/share/applications/gda-data-backup-2-usb.desktop
sudo ln -sf /var/Desktop/gda-start-mythen-detector.desktop /usr/share/applications/gda-start-mythen-detector.desktop

sudo ln -sf /var/Desktop/gda.directory /usr/share/desktop-directories/gda.directory
sudo ln -sf /var/Desktop/gda.menu /etc/xdg/menus/applications-merged/gda.menu

#### set up beamline profiles for GDA ####
# check if folder exist
echo
if [ ! -d "/$SOFTWAREFOLDER/$1/etc" ]; then
	echo "Please log into $1-control to create directory /$SOFTWAREFOLDER/$1/etc"
fi
# copy files
cp -f /$SOFTWAREFOLDER/$1/software/gda/config/etc/${1}_profile.sh /dls/$1/etc
ls -l /$SOFTWAREFOLDER/$1/software/gda/config/etc/${1}_profile.sh
echo "Please make sure /$SOFTWAREFOLDER/$1/etc/${1}_profile.sh is EXECUTABLE."
echo
#### set up remote-start-up script ####
ls -l /$SOFTWAREFOLDER/$1/software/gda/config/bin/remotestartupscript.sh
echo "Please make sure /$SOFTWAREFOLDER/$1/software/gda/config/bin/remotestartupscript.sh is EXECUTABLE."
echo
#### set up remote start GDA key ###
if [ ! -r "/$SOFTWAREFOLDER/$1/${1}ssh.key" ]; then
	cp -f /$SOFTWAREFOLDER/$1/software/gda/config/${1}ssh.key /$SOFTWAREFOLDER/$1/
fi
ls -l /$SOFTWAREFOLDER/$1/${1}ssh.key
echo "Please make sure /$SOFTWAREFOLDER/$1/${1}ssh.key file is owned by 'gda:gda'."
echo 
echo "Importent: You need to login to the server to change ownership and mode of files"
echo	
### Message to Installer ###
echo "Now you need to logout then login again for this to take effect, Thank You!"

