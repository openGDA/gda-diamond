from Diamond.Utility.Image import ImageUtility

from gda.analysis.io import JPEGLoader, TIFFImageLoader, PilatusTiffLoader;
from org.eclipse.dawnsci.analysis.api.io import ScanFileHolderException

image=ImageUtility("Area Detector", iFileLoader=PilatusTiffLoader);

#demo
#image.open("/dls/i07/data/2010/cm1896-1/demoImages/p686719.tif");