from gda.device.scannable import PVScannable

print "Adding centroid scannables for D10 (d10_centroid_y, d10_centroid_x, d10_total) "

d10_centroid_y=PVScannable()
d10_centroid_y.setPvName("BL20J-DI-PHDGN-10:STAT:CentroidY_RBV")
d10_centroid_y.setName("d10_centroid_y")
d10_centroid_y.setOutputFormat(["%.4f"])
d10_centroid_y.configure()

d10_centroid_x=PVScannable()
d10_centroid_x.setPvName("BL20J-DI-PHDGN-10:STAT:CentroidX_RBV")
d10_centroid_x.setName("d10_centroid_x")
d10_centroid_x.setOutputFormat(["%.4f"])
d10_centroid_x.configure()

d10_total=PVScannable()
d10_total.setPvName("BL20J-DI-PHDGN-10:STAT:Total_RBV")
d10_total.setName("d10_total")
d10_total.setOutputFormat(["%.4f"])
d10_total.configure()