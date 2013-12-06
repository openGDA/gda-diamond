from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
from gda.factory import Finder

print "Initialization Started";

finder = Finder.getInstance()

test = DummyScannable("test")

print "Initialization Complete";
