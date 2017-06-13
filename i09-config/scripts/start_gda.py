# exec file("start_gda.py")

import gda.util.ObjectServer
#obj=gda.util.ObjectServer.createClientImpl("/dls/i03/software/gda/config/xml/client.xml")
obj=gda.util.ObjectServer.createClientImpl()

# standard imports
import java
from java.lang import Thread
from java.lang import Runnable
from java.lang import InterruptedException
from gda.scan import *
from gda.device import *
from gda.jython import JythonServer
from gda.jython import ScriptBase
from gda.device.monitor import BeamMonitor
from gda.device.monitor import EpicsBeamMonitor
from gda.factory import Finder
from gda.device.detector import DetectorBase
from gda.device import Scannable
from gda.device.scannable import ScannableBase
from gda.device.scannable import OEAdapter
from gda.device.scannable import DOFAdapter
from gda.device.scannable import DummyScannable
from gda.device.scannable import PseudoDevice
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import *
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import *
from gda.jython.commands import InputCommands
from gda.jython.commands.InputCommands import *

# persistence
from uk.ac.diamond.daq.persistence.jythonshelf import LocalParameters
from uk.ac.diamond.daq.persistence.jythonshelf import LocalObjectShelfManager

# plotting
from gda.analysis import *
from gda.analysis.utils import *
from gda.analysis.functions import *

# import other interfaces to use with list command
from gda.oe import OE
from gda.oe.dofs import DOF
from gda.device import ScannableMotion
from gda.oe import OE
from gda.device.epicsdevice import IEpicsDevice
from gda.util.converters import IReloadableQuantitiesConverter

# Channel access commands
from gda.epics import CAClient
from gda.epics.CAClient import *
from org.pf.joi import Inspector

# Get the location of the GDA beamline script directory
from gda.configuration.properties import LocalProperties
LocalProperties=LocalProperties
gdaScriptDir = LocalProperties.get("gda.jython.gdaScriptDir")
gdaScriptDir  = gdaScriptDir + "/"
userScriptDir = LocalProperties.get("gda.jython.userScriptDir")
userScriptDir = userScriptDir + "/"
commonScriptDir = LocalProperties.get("gda.jython.commonScriptDir")
commonScriptDir = commonScriptDir + "/"

# we need all OEs and their DOFs to be available in the
# namespace, by wrapping references to them in Adapter objects
finder = Finder.getInstance()
OEs = []
DOFs=[]
OEs = finder.listAllNames("OE");
for fullName in OEs:
	objRef = finder.find(fullName)
	# create an OE adapter object
	exec(fullName + "=OEAdapter(objRef)")
	exec(fullName + ".setName(fullName)")

	# get array of the DOFNames
	exec("tempArray=" + fullName+ ".getDOFNames()");
	for dofName in tempArray: #@UndefinedVariable
		DOFs.append(dofName)
		exec(dofName+ "=DOFAdapter(" + fullName + ",\"" + dofName+ "\")")

# all Scannable objects should be also placed into the
# namespace.

scannables = []
scannables = finder.listAllNames("Scannable")
for fullName in scannables:
	exec(fullName + "=finder.find('"+ fullName + "')");

exec file(gdaScriptDir+"localStation.py")

