from Diamond.Utility.Image import ImageUtility

from gda.analysis.io import JPEGLoader, TIFFImageLoader, ScanFileHolderException, ConvertedTIFFImageLoader, PilatusTiffLoader;

image=ImageUtility("PEEM Image", iFileLoader=JPEGLoader);

#demo
#image.open("/dls/i06/data/2010/cm1895-1/demoImages/LEEM_palladium_on_tungsten.png");