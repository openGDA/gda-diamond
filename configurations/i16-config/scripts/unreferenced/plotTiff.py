def plotTiff(image):

    from gda.analysis.io import TIFFImageLoader
    from gda.analysis import Plotter

    img = TIFFImageLoader(image) # e.g. /dls/i16/andortest1.tiff
    hol = img.loadFile()
    data = hol.data
    mydata = data.elementAt(0)
    Plotter.plotImage("Data Vector", mydata)
