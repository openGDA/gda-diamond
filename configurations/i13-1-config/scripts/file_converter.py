def getFileNames(filepath,detectorName="mpx"):
    from uk.ac.diamond.scisoft.analysis.io import NexusLoader
    nl = NexusLoader(filepath, True)
    dh = nl.loadFile()
    tree = dh.getNexusTree()
    item = tree.getChildNode("entry1", "NXentry").getChildNode(detectorName, "NXdata")
    item1 = item.getChildNode("image_data", "SDS")
    data=item1.getData()
    from gda.data.nexus import FileNameBufToStrings
    return FileNameBufToStrings( data.dimensions, data.getBuffer()).getFilenames()


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
        TIFFSaver(newfilename,False,32).save(dh)
#        dnp.io.save(newfilename, dh, format="tiff")

def sum_edfImages(filepath,outpath):
    """
    reads edf files from scan file and creates a tiff from the sum of the data in it
    filepath: input Nexus filepath
    outpath: output Tiff filepath
    """
    filenames = getFileNames(filepath)
    dh0=dnp.io.load(filenames[0], format="edf")
    ds0=dh0[0]
    summed = dnp.zeros(ds0.shape,dtype=dnp.int64)
    for filename in filenames:
        dh=dnp.io.load(filename, format="edf")
        summed += dh[0]
    
    dnp.io.save(outpath, summed, format="tiff", signed=False, bits=32) 


