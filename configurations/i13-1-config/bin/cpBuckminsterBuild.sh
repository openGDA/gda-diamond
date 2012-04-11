cd /dls_sw/i13-1/software/gda
echo "rm old client"
rm -rf ./client 
echo "chmod o+w new client"
chmod -R o+w /tmp/uk.ac.gda.beamline.i13j.site/output/uk.ac.gda.beamline.i13j.site_1.0.0-eclipse.feature/i13j.gtk.linux.x86_64
echo "cp new client"
cp -r /tmp/uk.ac.gda.beamline.i13j.site/output/uk.ac.gda.beamline.i13j.site_1.0.0-eclipse.feature/i13j.gtk.linux.x86_64 ./client
echo "done"
