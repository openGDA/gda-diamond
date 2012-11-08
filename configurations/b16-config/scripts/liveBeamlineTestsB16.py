from gdascripts.testing.livetest.AllScannablesTestGroup import AllScannablesTestGroup
from gdascripts.testing.livetest.FileAccessPermissionsTestGroup import FileAccessPermissionsTestGroup
from gdascripts.testing.livetest.ExtendedSyntaxCommandTestGroup import ExtendedSyntaxCommandTestGroup

import time


# Header
print "#*"*40
print "liveBeamlineTestsB16"
print "started at: ", time.asctime()
print "#*"*40




esctg = ExtendedSyntaxCommandTestGroup()
esctg.addCommand("newub 'b16_270608'")
esctg.addCommand("setlat 'xtal' 3.8401 3.8401 5.43072")
esctg.addCommand("addref 1 0 1.0628 [5.000 22.790 1.552 22.400 14.255] 12.39842/1.24")
esctg.addCommand("addref 0 1 1.0628 [5.000 22.790 4.575 24.275 101.320] 12.39842/1.24")
esctg.addCommand("checkub")
esctg.test()


################ Test All Scannables ##############


astg=AllScannablesTestGroup(globals())
astg.addNameToSkip('wirescanner')
astg.test()

############### Test file permissions #############


faptg = FileAccessPermissionsTestGroup()

#gda and dls_dasc all permissions to /gda, otherwise rw only..."
BEAMLINE = "b16"
GDAPATH = "/dls_sw/%s/software/gda" % BEAMLINE
CONFIGPATH = "/dls_sw/%s/software/gda/config" % BEAMLINE
VARPATH = "/dls_sw/%s/software/gda/config/var" % BEAMLINE
SOFTWAREPATH = "/dls_sw/%s/software" % BEAMLINE


#faptg.addFaclEntry(GDAPATH,"other::rx")
faptg.addFaclEntry(GDAPATH,"default:user::rwx")
faptg.addFaclEntry(GDAPATH,"default:group::rwx")
faptg.addFaclEntry(GDAPATH,"default:group:dls_dasc:rwx")
faptg.addFaclEntry(GDAPATH,"default:group:gda:rwx")
#faptg.addFaclEntry(GDAPATH,"default:other::rx")

faptg.addFaclEntry(CONFIGPATH,"group:%s_staff:rwx" % BEAMLINE)
faptg.addFaclEntry(CONFIGPATH,"default:group:%s_staff:rwx" % BEAMLINE)

faptg.addFaclEntry(SOFTWAREPATH,"default:group:%s_staff:rwx" % BEAMLINE)


faptg.addFaclEntry(CONFIGPATH +"/scripts/localStation.py","group:%s_staff:rwx" % BEAMLINE)
faptg.addFaclEntry(CONFIGPATH + "/properties/java.properties","group:%s_staff:rwx" % BEAMLINE)
faptg.addFaclEntry("/dls_sw/%s/scripts/localStationUser.py" % BEAMLINE,"# owner: b16user")
faptg.test()

#################### Gda Commands ###################
esctg = ExtendedSyntaxCommandTestGroup()
esctg.addCommand("print 1")
esctg.addCommand("pos x")
esctg.addCommand("x")
esctg.addCommand("scan x 1 3 1")

esctg.test()
