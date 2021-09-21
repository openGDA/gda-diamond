
from gda.jython.commands.GeneralCommands import run, alias
from gda.factory import Finder

pdl=['ca71', 'startVoltage','stv', 'objective', 'obj', 'objStigmA', 'objStigmB', 'fov', 'uv', 'uvroi', 'uviewROI1', 'uviewROI2', 'uviewROI3', 'uviewROI4', 'roi1', 'roi2', 'roi3', 'roi4']
i06.removeDevices( pdl );

print "-------------------------------------------------------------------"
print "To shutdown the PEEM Corba Bridge Connection"

peemBridge = Finder.find("peemBridge");
peemBridge.disconnect()

run("BeamlineI06/usePEEM")

