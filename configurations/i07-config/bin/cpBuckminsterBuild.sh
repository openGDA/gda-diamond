cd /dls_sw/i07/software/gda/client
echo "rm old i07.gtk.linux.x86_64"
rm -rf ./i07.gtk.linux.x86_64
echo "chmod o+w new client"
chmod -R o+w /tmp/uk.ac.gda.beamline.i07.site/output/uk.ac.gda.beamline.i07.site_1.0.0-eclipse.feature/i07.gtk.linux.x86_64
echo "cp new client"
cp -r /tmp/uk.ac.gda.beamline.i07.site/output/uk.ac.gda.beamline.i07.site_1.0.0-eclipse.feature/i07.gtk.linux.x86_64 .
echo "done"