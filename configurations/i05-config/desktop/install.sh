#! /bin/sh

# create/update dataaqc.menu

for host in `host -l diamond.ac.uk |awk '/^'$BEAMLINE'-ws[0-9][0-9][0-9]/ {print $1}'` ; do

ssh $host "SUDO_ASKPASS=/usr/libexec/openssh/ssh-askpass sudo -A ln -sf /dls_sw/$BEAMLINE/software/gda/config/desktop/gda-xinit.sh /etc/X11/xinit/xinitrc.d/gda-xinit.sh"

done
