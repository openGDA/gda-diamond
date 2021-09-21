from gda.device.detector.uview import UViewImageDetectorROI
from Diamond.Peem.LeemModule import LeemFieldOfViewClass;
from Diamond.Peem.UViewDetector import UViewDetectorClass;
from gda.analysis.io import TIFFImageLoader
from gda.factory import Finder

global logger
global uview, ViewerPanelName

print "-------------------------------------------------------------------"
print "To set up the PEEM Corba Bridge Connection"

try:
    peemBridge = Finder.find("peemBridge");
    msImpl=peemBridge.connect()
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "Connection to the CORBA Bridge failed. Please check!"
    logger.dump("---> ", exceptionType, exception, traceback);

if not peemBridge.isConnected():
    print "Connection to the CORBA Bridge failed. Please check!"
    logger.dump("Connection to the CORBA Bridge failed. Please check!");
    raise IOError("CORBA Bridge Error");
#    return;

fov = LeemFieldOfViewClass("fov", msImpl);

#Setup the UView
print "-------------------------------------------------------------------"
#PEEM UViewImage Detector
#uview = Finder.find("uview")
print "CONFIGURING CORBA UVIEW\n"
uview.configure()
print "CORBA UVIEW CONFIGURED!"

print "-------------------------------------------------------------------"

##Create a GDA pseudo device that use the UView detector client
uv = UViewDetectorClass("uv", ViewerPanelName, uview);
#uv.setFileFormat('png', 2); imageLoader=PNGLoader;
uv.setFileFormat('tif')
imageLoader=TIFFImageLoader;
uv.setAlive(False);

#Obsoleted UViewImage Region Of Interests support
uviewROI1 = UViewImageDetectorROI()
uviewROI1.setName("uviewROI1")
uviewROI1.setBaseDetector("uview")
uviewROI1.setBoundaryColor("Red")
uviewROI1.configure()

uviewROI2 = UViewImageDetectorROI()
uviewROI2.setName("uviewROI2")
uviewROI2.setBaseDetector("uview")
uviewROI2.setBoundaryColor("Green")
uviewROI2.configure()

uviewROI3 = UViewImageDetectorROI()
uviewROI3.setName("uviewROI3")
uviewROI3.setBaseDetector("uview")
uviewROI3.setBoundaryColor("Blue")
uviewROI3.configure()

uviewROI4 = UViewImageDetectorROI()
uviewROI4.setName("uviewROI4")
uviewROI4.setBaseDetector("uview")
uviewROI4.setBoundaryColor("Yellow")
uviewROI4.configure()
