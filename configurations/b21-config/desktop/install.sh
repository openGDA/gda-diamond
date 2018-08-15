#! /bin/sh

# create/update dataaqc.menu

cat > /dls_sw/$BEAMLINE/software/gda/config/desktop/dataacq.menu <<EOF
<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN" "http://www.freedesktop.org/standards/menu-spec/1.0/menu.dtd">
<!-- warning this is a generated file -- do not edit -->
<Menu>
	<Name>Applications</Name>
	<Menu>
		<Name>Data Acquisition</Name>
`for i in /dls_sw/$BEAMLINE/software/gda/config/desktop/launchers/*.desktop ; do 
echo '		<Include> <Filename>'$i'</Filename> </Include>'
done`
	</Menu>
</Menu>
EOF

for host in `host -l diamond.ac.uk |awk '/^'$BEAMLINE'-ws[0-9][0-9][0-9]/ {print $1}'` ; do

ssh $host "SUDO_ASKPASS=/usr/libexec/openssh/ssh-askpass sudo -A ln -sf /dls_sw/$BEAMLINE/software/gda/config/desktop/dataacq.directory /usr/share/desktop-directories/data-acquisition.directory ; sudo -A ln -sf /dls_sw/$BEAMLINE/software/gda/config/desktop/dataacq.menu /etc/xdg/menus/applications-merged/data-acquisition.menu ; sudo -A ln -sf /dls_sw/$BEAMLINE/software/gda/config/desktop/gda-xinit.sh /etc/X11/xinit/xinitrc.d/gda-xinit.sh"

done
