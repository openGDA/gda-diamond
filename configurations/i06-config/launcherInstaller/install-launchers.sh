#!/bin/sh

if [ $# -ne 1 ]; then
	echo 1>&2 Usage: $0 i11
	exit 127
fi

### Check beamline GDA installation ###
if [ ! -h "/dls_sw/$1/software/gda" ]; then
	echo "This script requires a valid link '/dls_sw/$1/software/gda' pointing to the GDA installation. "
	exit 1
fi

#### xinitrc.d - install gda_launchers ####
if [ ! -f "/etc/X11/xinit/xinitrc.d/gda_launchers.sh" ]; then
	echo "Install GDA launchers"
else 
	echo "Update GDA launchers"
fi

sudo cp -f /dls_sw/$1/software/gda/config/launcherInstaller/gda_launchers.sh /etc/X11/xinit/xinitrc.d/gda_launchers.sh
sudo chmod 755 /etc/X11/xinit/xinitrc.d/gda_launchers.sh

#### set up desktop files and menus ####
# check if folder exist 
if [ ! -d "/dls_sw/$1/var/Desktop" ]; then
	sudo mkdir /dls_sw/$1/var/Desktop
fi

# copy files
echo "Install/Update GDA desktop menu"
sudo cp -f /dls_sw/$1/software/gda/config/Desktop/*.desktop /dls_sw/$1/var/Desktop
sudo cp -f /dls_sw/$1/software/gda/config/Desktop/*.menu /dls_sw/$1/var/Desktop
sudo cp -f /dls_sw/$1/software/gda/config/Desktop/*.directory /dls_sw/$1/var/Desktop
sudo cp -f /dls_sw/$1/software/gda/config/Desktop/.hidden /dls_sw/$1/var/Desktop

# change permission to avoid the desktop launcher appear with no-entry emblems
sudo chmod -R 777 /dls_sw/$1/var/Desktop

# create desktop links and menu links
sudo ln -sf /dls_sw/$1/var/Desktop/gda-client.desktop /usr/share/applications/gda-client.desktop
sudo ln -sf /dls_sw/$1/var/Desktop/gda-client-i06-1.desktop /usr/share/applications/gda-client-i06-1.desktop
#sudo ln -sf /dls_sw/$1/var/Desktop/gda-servers.desktop /usr/share/applications/gda-servers.desktop
#sudo ln -sf /dls_sw/$1/var/Desktop/gda-logpanel.desktop /usr/share/applications/gda-logpanel.desktop
#sudo ln -sf /dls_sw/$1/var/Desktop/gda-logfile.desktop /usr/share/applications/gda-logfile.desktop
#sudo ln -sf /dls_sw/$1/var/Desktop/grab2log.desktop /usr/share/applications/grab2log.desktop

sudo ln -sf /dls_sw/$1/var/Desktop/gda.directory /usr/share/desktop-directories/gda.directory
sudo ln -sf /dls_sw/$1/var/Desktop/gda.menu /etc/xdg/menus/applications-merged/gda.menu

#### set up beamline profiles for GDA ####
# check if folder exist
echo
if [ ! -d "/dls_sw/$1/etc" ]; then
	echo "Please log into $1-control to create directory /dls_sw/$1/etc"
fi
### Message to Installer ###
echo "Now you need to logout then login again for this to take effect, Thank You!"

