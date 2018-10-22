'''
This script is deprecated, replace by area detector implementation in java
'''
#following  line requires 'uk.ac.gda.devices.peem' plugin
from gda.device.detector.uviewnew import UViewImageDetectorROI as UViewImageDetectorROINew  # @UnresolvedImport
from Peem.UViewDetector import UViewDetectorClassNew;
from gda.analysis.io import TIFFImageLoader
import __main__  # @UnresolvedImport
from peem.usePEEM import ViewerPanelName

#Setup the UView
print "-------------------------------------------------------------------"
print "CONFIGURING TCPIP UVIEW"
__main__.uviewnew.configure()
print "TCPIP UVIEW CONFIGURED!"
print "-------------------------------------------------------------------"

##Create a GDA pseudo device that use the UView detector client
uv = UViewDetectorClassNew("uv", ViewerPanelName, __main__.uviewnew)
uv.setFileFormat('tiff16')
imageLoader=TIFFImageLoader;
uv.setAlive(False)

#Obsoleted UViewImage Region Of Interests support
uviewROI1 = UViewImageDetectorROINew()
uviewROI1.setName("uviewROI1")
uviewROI1.setBaseDetector("uviewnew")
uviewROI1.setBoundaryColor("Red")
uviewROI1.configure()

uviewROI2 = UViewImageDetectorROINew()
uviewROI2.setName("uviewROI2")
uviewROI2.setBaseDetector("uviewnew")
uviewROI2.setBoundaryColor("Green")
uviewROI2.configure()

uviewROI3 = UViewImageDetectorROINew()
uviewROI3.setName("uviewROI3")
uviewROI3.setBaseDetector("uviewnew")
uviewROI3.setBoundaryColor("Blue")
uviewROI3.configure()

uviewROI4 = UViewImageDetectorROINew()
uviewROI4.setName("uviewROI4")
uviewROI4.setBaseDetector("uviewnew")
uviewROI4.setBoundaryColor("Yellow")
uviewROI4.configure()

