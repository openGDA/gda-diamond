cd /dls_sw/i13/software/gda
echo "rm old client"
rm -rf ./client
echo "chmod o+w new client"
chmod -R o+w /tmp/uk.ac.gda.beamline.i13i.site/output/uk.ac.gda.beamline.i13i.site_1.0.0-eclipse.feature/i13i.gtk.linux.x86_64
echo "cp new client"
cp -r /tmp/uk.ac.gda.beamline.i13i.site/output/uk.ac.gda.beamline.i13i.site_1.0.0-eclipse.feature/i13i.gtk.linux.x86_64 ./client
echo "done"
