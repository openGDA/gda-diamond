import file_converter
import scisoftpy as dnp
from  gda.analysis.io import SRSLoader
from uk.ac.diamond.scisoft.analysis.io import DataHolder

from gda.analysis.io import NexusLoader


def integrate(filepath="/dls/i13-1/data/2011/mt5659-1/709.nxs", motor="energyThreshold"):
    """
    Produces a srs file with threshold against total counts
    """
    #load file, extract 'motor values
    nl = NexusLoader(filepath, True)
    dh = nl.loadFile()
    motorDS = dh.getDataset(motor)
    
    
    #get edf filenames
    filenames=file_converter.getFileNames(filepath)

    #create total counts dataset
    y1vals = []
    index=0
    for filename in filenames:
        dh=dnp.io.load(filename, format="edf")
        total = dh[0].sum()
        y1vals.append(total)
        print "Index: %d TotalCounts:%d" %(index, total)
        index +=1
        
    y1_ds = dnp.asarray(y1vals)

    
    #create dataset holder and save
    dh = DataHolder()
    dh.addDataset(motor, motorDS)
    dh.addDataset("TotalCounts", y1_ds)
    return dh

def integrate_save_plot(filepath="/dls/i13-1/data/2011/mt5659-1/709.nxs", motor="energyThreshold", plotname="Plot 2",
                        outputFile=""):
    dh= integrate( filepath, motor);
    if outputFile=="":
        outputFile=filepath.replace(".nxs","_TotalCounts_vs_" + motor + ".dat")
    SRSLoader(outputFile).saveFile(dh)
    dnp.plot.setdefname(plotname)
    dnp.plot.line(dh.getDataset(0), dh.getDataset(1))
    return outputFile
