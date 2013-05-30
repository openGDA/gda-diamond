from Diamond.Utility.Image import ImageUtility

from gda.analysis.io import JPEGLoader, TIFFImageLoader, ScanFileHolderException, ConvertedTIFFImageLoader, PilatusTiffLoader;

image=ImageUtility("Area Detector", iFileLoader=PilatusTiffLoader);

#demo
#image.open("/dls/i07/data/2010/cm1896-1/demoImages/p686719.tif");