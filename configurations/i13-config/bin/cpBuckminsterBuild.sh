zenity --title "Are you sure?" --question --text "Are you sure you want to replace the GDA client?" --window-icon=question
SURE=$?
if [ $SURE == 1 ]; then
  exit
fi

cd /dls_sw/i13/software/gda
echo "rm old client"
rm -rf ./client
echo "chgrp dls_dasc client"
chgrp -R dls_dasc /tmp/uk.ac.gda.beamline.i13i.site/output/uk.ac.gda.beamline.i13i.site_1.0.0-eclipse.feature/i13i.gtk.linux.x86_64
echo "cp new client"
cp -r /tmp/uk.ac.gda.beamline.i13i.site/output/uk.ac.gda.beamline.i13i.site_1.0.0-eclipse.feature/i13i.gtk.linux.x86_64 ./client
cp config/gda-i13i.ini client/
echo "done"
