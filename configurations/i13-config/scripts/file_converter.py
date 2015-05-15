def getFileNames(filepath,detectorName="mpx"):
    from uk.ac.diamond.scisoft.analysis.io import NexusLoader
    nl = NexusLoader(filepath, True)
    dh = nl.loadFile()
    tree = dh.getNexusTree()
    item = tree.getChildNode("entry1", "NXentry").getChildNode(detectorName, "NXdata")
    item1 = item.getChildNode("image_data", "SDS")
    data=item1.getData()
    return data.getBuffer()

def getData(filepath,detectorName, itemName):
    from uk.ac.diamond.scisoft.analysis.io import NexusLoader
    nl = NexusLoader(filepath, True)
    dh = nl.loadFile()
    tree = dh.getNexusTree()
    item = tree.getChildNode("entry1", "NXentry").getChildNode(detectorName, "NXdata")
    item1 = item.getChildNode(itemName, "SDS")
    data=item1.getData()
    return data.getBuffer()

from scisoftpy.jython.jyio import TIFFSaver
import scisoftpy as dnp
def create_tiffs(filepath):
    """
    reads edf files from scan file and creates a tiff from the data in it
    """
    filenames = getFileNames(filepath)
    for filename in filenames:
        dh=dnp.io.load(filename, format="edf")
        newfilename=filename.replace(".edf",".tiff")
        print "Creating %s from %s " % (newfilename,filename)
#       print dh.__class__
        TIFFSaver(newfilename,32).save(dh)
#        dnp.io.save(newfilename, dh, format="tiff")
