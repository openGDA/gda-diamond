def getFileNames(filepath,detectorName="mpx"):
    from uk.ac.diamond.scisoft.analysis.io import NexusLoader
    nl = NexusLoader(filepath, True)
    dh = nl.loadFile()
    tree = dh.getNexusTree()
    item = tree.getChildNode("entry1", "NXentry").getChildNode(detectorName, "NXdata")
    item1 = item.getChildNode("image_data", "SDS")
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
        TIFFSaver(newfilename,False,32).save(dh)
#        dnp.io.save(newfilename, dh, format="tiff")

def sum_edfImages(filepath,outpath=None):
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
    if outpath is not None:
        dnp.io.save(outpath, summed, format="tiff", signed=False, bits=32)
    return summed; 

def getImagesAs3D(filepath):
    """
    Reads all images in filepath and returns a 3d data object with first dimension being image number
    """
    filenames = getFileNames(filepath)
    dh0=dnp.io.load(filenames[0], format="edf")
    ds0=dh0[0]
    numberOfImages = len(filenames)
    data = dnp.zeros([numberOfImages,ds0.shape[0],ds0.shape[1]] ,dtype=dnp.int64)
    for i in range(numberOfImages):
        dh=dnp.io.load(filenames[i], format="edf")
        image=dh[0]
        data[i,:,:]=image
    return data




