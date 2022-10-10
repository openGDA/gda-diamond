from uk.ac.gda.util.beans.xml import XMLHelpers
import scisoftpy as dnp
from java.io import File
from uk.ac.gda.beans.xspress import XspressDeadTimeParameters, XspressParameters
from gda.device.detector.xspress.xspress2data import Xspress2DeadtimeTools
"""
    Some functions to process the raw scaler data from Xspress2/3X/4 detectors and
    calculated the deadtime correction (DTC) factors and DTC corrected in window counts
    imh 4/10/2022
"""


def load_raw_in_window_data(filename, detectorName):
    print("Reading raw in-window counts data in %s from /entry1/%s"%(filename, detectorName))
    xspdata = dnp.io.load(filename)
    return xspdata['entry1'][detectorName]['raw scaler in-window'][...]

# Load data from Nexus file (make sure it's not already open somewhere else!)
def load_raw_scaler_data(filename, detectorName):
    """
    Load scaler data from Nexus file. This will fail if the data isn't present in the
    file, or the file is already open somewhere else.
    Input :
        filename - full path to nexus file
        detectorName - name of Nexus group in /entry1/ containing the data
    Output :
        list of raw scaler data arrays (data shape = [num points in scan x num detector channels]) :
        i,e. 'raw scaler total', 'tfg resets', 'tfg clock cycles' datasets read from /entry1/detectorName/
    """
    print("Reading scaler data in %s from /entry1/%s"%(filename, detectorName))
    xspdata = dnp.io.load(filename)
    
    ## Check detector Nexus group is present
    assert xspdata['entry1'].keys().count(detectorName) == 1 , "Could not find "+detectorName+" dataset in /entry1/ of "+filename
    
    # Get the detector data
    detdata=xspdata['entry1'][detectorName]
    
    # Get arrays of the raw scaler values :
    # Seem to need underscores rather than spaces...
    required_dataset_names=["raw_scaler_total", "tfg_resets", "tfg_clock_cycles"]
    raw_scaler_data = []
    for name in required_dataset_names :
        ## Check the data group is present
        assert detdata.keys().count(name) == 1 , "Could not find dataset "+name+" in /entry1/"+detectorName+" of "+filename
        raw_scaler_data.append(detdata[name][...])

    return raw_scaler_data

def assemble_values(rawScalerTotal, resets, tfgCounts):
    """
 Assemble raw scaler values for all channels into single array,
 in format suitable for Xspress2DeadtimeTools.calculateDeadtimeCorrectionFactors
 Input : 
       rawScalerTotal, resets, tfgCounts
       arrays with scaler values for each channel
 Output : 
    4 scaler values for each channel, concatenated into single array:
        raw scaler total, reset counts, in window counts (not used), tfg clock cycles
    """

    arrayVals = []
    assert len(rawScalerTotal) == len(resets) == len(tfgCounts) , "Number of raw scaler values do not all match"
    numChannels = len(rawScalerTotal)
    for i in range(numChannels) :
        arrayVals.append(long(rawScalerTotal[i]))
        arrayVals.append(long(resets[i]))
        arrayVals.append(0L) ## not used, but required!
        arrayVals.append(long(tfgCounts[i]))
    return arrayVals

# Path to template data and detector files
templateDir="/dls_sw/b18/software/gda_versions/gda_9_26/workspace_git/gda-dls-beamlines-xas.git/b18/templates/"
dtcParamFile="Xspress3X_DTC_params_ME7.xml"
detSettingsFile="Xspress3X_Parameters_ME7.xml"
dtcEnergyKev = 10.0

# Read the DTC parameters file
dtcParametersBean = XMLHelpers.readBean(File(templateDir+dtcParamFile), XspressDeadTimeParameters)

# Read the detector settings file (only used by calculateDeadtimeCorrectionFactors to get num of detector channels
detSettingsBean = XMLHelpers.readBean(File(templateDir+detSettingsFile), XspressParameters)


def calculate_dtc_vals(filename, detName=None) :
    """
    Calculate deadtime correction factors from raw scaler data stored in Nexus file
    Input : 
        filename = name of nexus file
        detName = name of detector. Detector data will be loaded from Nexus group :  /entry1/detName/...
    Output :
        List of list of of deadtime correction factors, array of values for each channel of detector, 
        for each frame in the scan.
    """
    numChannels = detSettingsBean.getDetectorList().size()
    if detName == None : 
        detName=detSettingsBean.getDetectorName()

    raw_scaler_data = load_raw_scaler_data(filename, detName)
    raw_scalers_total = raw_scaler_data[0]
    tfg_resets = raw_scaler_data[1]
    tfg_clockcycles = raw_scaler_data[2]

    deadtimeTools = Xspress2DeadtimeTools()
    numFrames = len(raw_scalers_total) 
    # Process each frame in the scan and calculate the DTC factor for each channel
    print("Calculating DTC factors : %d channels, %d frames of data"%(numChannels, numFrames))
    allDtcVals=[]
    for i in range(numFrames) :
        scalerValues = assemble_values(raw_scalers_total[i], tfg_resets[i], tfg_clockcycles[i])
        #print vals
        dtcVals = deadtimeTools.calculateDeadtimeCorrectionFactors(scalerValues, numChannels, detSettingsBean, dtcParametersBean, dtcEnergyKev)
        allDtcVals.append(dtcVals)

    return allDtcVals


def calculate_corrected_window_counts(filename, detName=None) :
    """
    Calculate the deadtime corrected in-window counts
    using calculate_dtc_vals.
    i.e. For each step in scan, DTC factor for each channel multiplied
    by raw in-window counts for channel.
    
    """
    if detName == None : 
        detName=detSettingsBean.getDetectorName()

    dtc_factors = calculate_dtc_vals(filename, detName)
    raw_in_window_counts = load_raw_in_window_data(filename, detName)
    assert len(dtc_factors) == len(raw_in_window_counts) , "Length of DTC factors and raw in-window counts data do not match"
    corrected_counts=[]
    print("Calculating DTC corrected in-window counts")
    for i in range(len(dtc_factors)) :
        dtc=dtc_factors[i]
        counts=raw_in_window_counts[i]
        assert len(dtc) == len(counts) , "Number of channels of DTC and in-window counts data for frame "+str(i)+" is not correct"
        corrected = [dtc[j]*counts[j] for j in range(len(dtc))]
        corrected_counts.append(corrected)

    return corrected_counts

def write_data(data_array,  path, header=None,) :
    """
    Write 2d array of data to Ascii text file.
    
    Inputs :
        data_array - 2d array of data (list of lists)
        path - string path of output ascii file to be created
        header - header string to be placed at start of file (optional)
    """
    print("Writing data to file : %s"%(path))
    numRows = len(data_array)
    print("Data array length : %d"%(numRows))
    
    ## Convert each row of data to formatted string
    linestrings=[]
    for i in range(numRows) :
        strVals = [str(i) for i in data_array[i]]
        linestrings.append("\t".join(strVals)+"\n")

    # Write to ascii file with optional header
    with open(path, "w") as f :
        if header != None :
            f.write(header+"\n")
            
        for row in linestrings :
            f.write(row)

def example() :
    ## Calculate the DTC factors
    dtc_factors = calculate_dtc_vals("/dls/b18/data/2022/cm31142-4/nexus/554162_b18.nxs", "xspress3X")
    ## Calculated the in-window corrected counts
    corrected_vals = calculate_corrected_window_counts("/dls/b18/data/2022/cm31142-4/nexus/554162_b18.nxs", "xspress3X")
    
    ## Write some data to Ascii filex
    write_data(dtc_factors, "/scratch/test_dtc_factors.txt","# DTC factors")
    write_data(corrected_vals, "/scratch/test_counts.txt","# Corrected in-window counts")
    return corrected_vals

def example2(nexus_path, out_dir) :
    nexus_name = nexus_path.rpartition("/")
    ascii_output = nexus_name[ len(nexus_name)-1].replace(".nxs","_dtc_window_counts.txt")
    out_path=out_dir+"/"+ascii_output
    corrected_vals = calculate_corrected_window_counts(nexus_path, "xspress3X")
    write_data(corrected_vals, out_path,"# header")

def example3() :
    ## get path to the Nexus file from last scan that was run 
    nexus_path=lastScanDataPoint().getCurrentFilename()
    out_dir = "/dls/b18/data/2022/cm31142-4/processing/"
    example2(nexus_path, out_dir)

