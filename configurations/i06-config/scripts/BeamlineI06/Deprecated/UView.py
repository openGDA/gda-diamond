
from Diamond.PseudoDevices.UViewDetector import UViewDetectorClass;
from Diamond.PseudoDevices.UViewDetector import UViewDetectorROIClass;
from Diamond.Utility.PeemImage import PeemImageClass

#Set up the UView Image Detector and ROI
print "Note: Use object name 'uv' for UView Image data access";
uv = UViewDetectorClass("uv");

print "Note: Use roi* for UView Image Region Of Interests access";
roi1 = UViewDetectorROIClass("roi1", "uviewROI1");
roi2 = UViewDetectorROIClass("roi2", "uviewROI2");
roi3 = UViewDetectorROIClass("roi3", "uviewROI3");
roi4 = UViewDetectorROIClass("roi4", "uviewROI4");

#Set up the image analysis scripts

peemImage = PeemImageClass();

#fnx = "/scratch/Dev/gdaDev/gda-config/i07/users/data/operation/Peem/ui00000001.png"
#fny = "/scratch/Dev/gdaDev/gda-config/i07/users/data/operation/Peem/ui00000002.png"

#fnr = "/scratch/Dev/gdaDev/gda-config/i07/users/data/operation/Peem/ui00000001r.png"
#fnt = "/scratch/Dev/gdaDev/gda-config/i07/users/data/operation/Peem/ui00000001t.png"

#peemImage.convert(fnx, fny, fnr, fnt);
