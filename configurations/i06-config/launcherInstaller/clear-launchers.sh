#!/bin/sh

if [ $# -ne 1 ]; then
	echo 1>&2 Usage: $0 i11
	exit 127
fi

sudo rm -f /etc/X11/xinit/xinitrc.d/gda_launchers.sh

sudo rm -f -R /var/Desktop

sudo rm -f /usr/share/applications/gda-client.desktop
sudo rm -f /usr/share/applications/gda-servers.desktop
sudo rm -f /usr/share/applications/gda-logpanel.desktop
sudo rm -f /usr/share/applications/gda-logfile.desktop
sudo rm -f /usr/share/applications/gda-user-guide.desktop
sudo rm -f /usr/share/applications/gda-wiki.desktop

sudo rm -f /usr/share/desktop-directories/gda.directory
sudo rm -f /etc/xdg/menus/applications-merged/gda.menu



### Message to Installer ###
echo "All gda launchers deleted. Need to run the install-launchers.sh to install all launchers"
