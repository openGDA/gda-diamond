#
# Collect vortex mca
#
#
das=finder.find("daserver")
myvortex=xmapMca
myvortex.stop()
myvortex.clearAndStart()
das.sendCommand("tfg init")
command = "tfg setup-groups cycles 1 \n 1 1.0E-7 1.0 0 7 0 0 \n-1 0 0 0 0 0 0 "
das.sendCommand(command)
das.sendCommand("tfg start")
das.sendCommand("tfg wait")
myvortex.stop()


