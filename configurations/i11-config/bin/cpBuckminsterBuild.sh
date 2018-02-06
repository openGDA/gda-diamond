zenity --title "Are you sure?" --question --text "Are you sure you want to replace the GDA client?" --window-icon=question
SURE=$?
if [ $SURE == 1 ]; then
  exit
fi

cd /dls_sw/i09/software/gda
echo "rm old client"
rm -rf ./client
#mv client client_old
echo "chmod o+w new client"
chmod -R o+w /tmp/uk.ac.gda.beamline.i11.site/output/uk.ac.gda.beamline.i11.site_1.0.0-eclipse.feature/i11.gtk.linux.x86_64
echo "cp new client"
cp -r /tmp/uk.ac.gda.beamline.i11.site/output/uk.ac.gda.beamline.i11.site_1.0.0-eclipse.feature/i11.gtk.linux.x86_64 ./client
echo "done"
