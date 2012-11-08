from gdascripts.testing.livetest.AllScannablesTestGroup import AllScannablesTestGroup
from gdascripts.testing.livetest.FileAccessPermissionsTestGroup import FileAccessPermissionsTestGroup
from gdascripts.testing.livetest.ExtendedSyntaxCommandTestGroup import ExtendedSyntaxCommandTestGroup

import time


# Header
print "#*"*40
print "liveBeamlineTestsB16"
print "started at: ", time.asctime()
print "#*"*40

################ Test All Scannables ##############

astg=AllScannablesTestGroup(globals())
astg.addNameToSkip('checkbeam')
astg.addNameToSkip('checkbeamcurrent')

astg.test()
# NOTE: use astg.writeCSV(path) to save results

############## Test file permissions #############


faptg = FileAccessPermissionsTestGroup()

#gda and dls_dasc all permissions to /gda, otherwise rw only..."
BEAMLINE = "i16"
GDAPATH = "/dls_sw/%s/software/gda" % BEAMLINE
CONFIGPATH = "/dls_sw/%s/software/gda/config" % BEAMLINE
VARPATH = "/dls_sw/%s/software/gda/config/var" % BEAMLINE
SOFTWAREPATH = "/dls_sw/%s/software" % BEAMLINE

# TODO: should be checked recursively
faptg.addFaclEntry(GDAPATH,"user::rwx")
faptg.addFaclEntry(GDAPATH,"group::rwx")
faptg.addFaclEntry(GDAPATH,"group:dls_dasc:rwx")
faptg.addFaclEntry(GDAPATH,"group:gda:rwx")
#faptg.addFaclEntry(GDAPATH,"other::rx")
faptg.addFaclEntry(GDAPATH,"default:user::rwx")
faptg.addFaclEntry(GDAPATH,"default:group::rwx")
faptg.addFaclEntry(GDAPATH,"default:group:dls_dasc:rwx")
faptg.addFaclEntry(GDAPATH,"default:group:gda:rwx")
#faptg.addFaclEntry(GDAPATH,"default:other::rx")

faptg.addFaclEntry(CONFIGPATH,"group:%s_staff:rwx" % BEAMLINE)
faptg.addFaclEntry(CONFIGPATH,"default:group:%s_staff:rwx" % BEAMLINE)

faptg.addFaclEntry(VARPATH,"other::rwx")
#faptg.addFaclEntry(VARPATH,"default:other::rwx")

faptg.addFaclEntry(SOFTWAREPATH,"default:group:%s_staff:rwx" % BEAMLINE)

# i16 specific:
faptg.addFaclEntry(CONFIGPATH,"user:%suser:rwx" % BEAMLINE)
faptg.addFaclEntry(CONFIGPATH,"default:user:%suser:rwx" % BEAMLINE)
# check these especially as we can't check facl's recursively (it takes ages to do so)
faptg.addFaclEntry(CONFIGPATH,"default:user:%suser:rwx" % BEAMLINE)
faptg.addFaclEntry(CONFIGPATH +"/scripts/localStation.py","user:%suser:rwx" % BEAMLINE)
faptg.addFaclEntry(CONFIGPATH + "/properties/java.properties","user:%suser:rwx" % BEAMLINE)
faptg.addFaclEntry(CONFIGPATH + "/xml/I16_Server.xml","user:%suser:rwx" % BEAMLINE)
# check tempscript (used for compiling scripts run via the 'run' command into)
faptg.addFaclEntry(VARPATH+"/.tempScript2", "group:gda:rwx")
faptg.test()

#################### Gda Commands ###################
esctg = ExtendedSyntaxCommandTestGroup()
esctg.addCommand("print 1")
esctg.addCommand("print 1/0")
esctg.addCommand("pos x")
esctg.addCommand("scan x 1 3 1 z")
esctg.addCommand("scan x 1 3 1 y 1 3 1 z")
esctg.addCommand("ascan x 1 3 13")
esctg.addCommand("dscan x -1 1 13")
esctg.addCommand("scancn .1 10")
esctg.addCommand("")
esctg.test()
