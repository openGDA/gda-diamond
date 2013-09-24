from gda.configuration.properties import LocalProperties
from gda.factory import Finder

from gda.device.scannable import DummyScannable
from gda.device.scannable import TopupScannable
from gda.device.scannable import BeamMonitorWithFeedbackSwitchScannable
from gda.device.scannable import DetectorFillingMonitorScannable
from gda.device.scannable import BeamMonitorScannableForLineRepeat

from gda.data import PathConstructor
from gda.data.fileregistrar import IcatXMLCreator

print "Initialization Started";

finder = Finder.getInstance()

gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

rcpController = finder.find("RCPController")

if (LocalProperties.get("gda.mode") == 'live'):
    print "The initialisation procedure for live mode:"
    archiver = IcatXMLCreator()
    archiver.setDirectory("/dls/bl-misc/dropfiles2/icat/dropZone/i08/i08_")

loggingcontroller = Finder.getInstance().find("XASLoggingScriptController")


test = DummyScannable("test")

gdaRoot = LocalProperties.get("gda.root")
gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

global mapRunning
mapRunning = 0


print "Initialization Complete";
