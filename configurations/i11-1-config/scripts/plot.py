'''
A module provides convenient or wrapper method for plot existing data on specified plot panel. 
It supports plotting of 3 types of data: MAC, SRS, PSD, and the selection of plotting destination. 
You may also choose to plot over existing plots on the graph or not. 

This method is development to use Swing DataVector plotting facility in GDA.

Created on 22 Sep 2009
updateed to add "DataPlot" panel, 06 Dec 2010

@author: fy65
'''
from gda.analysis import ScanFileHolder, Plotter
from gda.analysis.io import MACLoader, SRSLoader, ScanFileHolderException
from gda.data import NumTracker, PathConstructor
from gda.jython.commands.GeneralCommands import alias
from java.io import IOException, File #@UnresolvedImport
import java #@UnresolvedImport
import re
from gda.configuration.properties import LocalProperties
import os
from uk.ac.diamond.scisoft.analysis import SDAPlotter
from uk.ac.diamond.scisoft.analysis.dataset import DoubleDataset

INT_RE = re.compile(r"^[-]?\d+$")
def representsInt(s):
    return INT_RE.match(str(s)) is not None

MAC=0
SRS=1
PSD=2
RAW=3

def plot(datatype, filename, panelname="DataPlot"):
    ''' Plot collected data in the Graph,  erase existing lines on the graph.
        command syntax:
            plot datatype filename [panelname]
        function syntax:
            plot(datatype, filename, [panelname])
        where:
            datatype can be MAC or PSD (in capitals)
            filename must be file name string in quote or absolute file path or URL to the data file (must be quoted)
    '''
    plotdata(filename, datatype, panelname, False)

def plotover(datatype, filename, panelname="DataPlot"):
    ''' Plot collected data on top of existing lines in the Graph.
        command syntax:
            plotover datatype filename [panelname]
        function syntax:
            plotover(datatype, filename, [panelname])
        where:
            datatype can be MAC or PSD (in capitals)
            filename must be file name string in quote or absolute file path or URL to the data file (must be quoted)
    '''
    plotdata(filename, datatype, panelname, True)

alias("plot")   
alias("plotover")   

def plotdata(filename, dataType=MAC, plotPane="DataPlot", Overlay=True):
    '''Plot existing data on "MAC, PSD", or "SRS" (if any) Panel, the default is MAC data on DataPlot panel and overlay is True.
       
       syntax:
               plotdata(filename,[MAC|SRS|PSD],["MAC"|"Mythen"|"DataPlot"],[True|False])
       
               where:
                    filename: the filename string in quote. 
                
                    dataType: the input data types or formats available
		                MAC - plot MAC data on MAC panel
		                PSD - plot PSD data on Mythen panel
		                SRS - plot SRS data on SRS panel
		            
		            plotPane: the graph panel to display the plot
		        
		            Overlay:
                        'True': plot over the exist data on the graph (Default) 
                        'False': clear existing plot data from the graph before plotting new data
                         
    '''
    print("Data plotting to " + plotPane + " panel, please wait ...")
    if dataType == MAC:
        sfh = loadMacData(filename)
        dataset=sfh.getAxis(1)
        dataset.setName(filename)
        if Overlay:
            Plotter.plotOver(plotPane, sfh.getAxis(0), dataset)
        else:
            Plotter.plot(plotPane, sfh.getAxis(0), dataset)
    elif dataType == SRS:
        sfh = loadSRSData(filename)
        if Overlay:
            Plotter.plotOver(plotPane, sfh.getAxis(0), sfh.getAxis(1))
        else:
            Plotter.plot(plotPane, sfh.getAxis(0), sfh.getAxis(1))
    elif dataType == PSD:
        if not str(filename).find("mythen") == -1:
            # mythen data file
            dataset = loadMythenData(filename)
            data=dataset.getCountDataSet()
            data.setName(filename)
            if Overlay:
                Plotter.plotOver(plotPane, dataset.getAngleDataSet(), data)
            else:
                Plotter.plot(plotPane, dataset.getAngleDataSet(), data)
        else:
            parts = str(filename).split(File.separator)
            name=parts[-1]
            names=str(name).split(".")
            if representsInt(names[0]):
                # Mythen SRS file
                for each in loadMythenSRSFile(filename):
                    dataset = loadMythenData(str(each) + ".dat")
                    data=dataset.getCountDataSet()
                    data.setName(each)
                    if Overlay:
                        Plotter.plotOver(plotPane, dataset.getAngleDataSet(), data)
                    else:
                        Plotter.plot(plotPane, dataset.getAngleDataSet(), data)
            else:
                dataset = loadMythenData(filename)
                data=dataset.getCountDataSet()
                data.setName(filename)
                if Overlay:
                    Plotter.plotOver(plotPane, dataset.getAngleDataSet(), data)
                else:
                    Plotter.plot(plotPane, dataset.getAngleDataSet(), data)
    elif dataType == RAW:
            # mythen raw data file
            dataset = loadMythenRawData(filename)
            data=DoubleDataset(dataset.getCountArray(), dataset.getCountArray().length)
            channeldata=DoubleDataset(dataset.getChannelArray(),dataset.getChannelArray().length)
            data.setName(filename)
            if Overlay:
                Plotter.plotOver(plotPane, channeldata, data)
                SDAPlotter.addPlot(plotPane, "", channeldata, data, "delta", "counts")
            else:
                Plotter.plot(plotPane, channeldata, data)
                SDAPlotter.plot(plotPane, "", channeldata, data, "delta", "counts")
    else:
        print "Data Type is not recognised or supported."
    print "Plotting completed."

def loadMacData(filename):
    '''Load MAC data file into a ScanFileHolder object, 
    supporting relative loading with respect to the current collected data (0)'''
    sfh = ScanFileHolder()
    try:
        if filename == None:
            #current file
            sfh.load(MACLoader(0))
        elif representsInt(filename):
            #past file - relative path
            sfh.load(MACLoader(int(filename)))
        else:
            #absolute file path or filename with extension MACLoader will prepend the directory
            sfh.load(MACLoader(filename))
    except ScanFileHolderException, err:
        print "File loader failed", err
    return sfh

def loadSRSData(filename):
    '''Load SRS data file into a ScanFileHolder object, 
    supporting relative loading with respect to the current collected data (0)'''
    sfh = ScanFileHolder()
    try:
        if filename == None:
            #current file
            sfh.load(SRSLoader(_getCurrentFileName(0)))
        elif representsInt(filename):
            #past file - relative path
            sfh.load(SRSLoader(_getCurrentFileName(int(filename))))
        elif not filename.startswith(File.separator):
            #filename with extension
            sfh.load(SRSLoader(os.path.join(PathConstructor.createFromDefaultProperty(),filename)))
        else:
            #absolute file path
            sfh.load(SRSLoader(filename))
    except ScanFileHolderException, err:
        print "File loader failed. " + err
    return sfh

def loadMythenSRSFile(filename):
    '''load MythenSRSFile, supporting relative file number with respect to the current one (0).'''
    from gda.device.detector.mythen.data import MythenSrsFileLoader
    filenamelist=[]
    try:
        if filename == None:
            #current file
            filenamelist=MythenSrsFileLoader().load(_getCurrentFileName(0))
        elif representsInt(filename):
            #past file - relative path
            filenamelist=MythenSrsFileLoader().load(_getCurrentFileName(int(filename)))
        elif not str(filename).startswith(File.separator):
            #filename with extension
            filenamelist=MythenSrsFileLoader().load(os.path.join(PathConstructor.createFromDefaultProperty(),filename))
        else:
            #absolute file path
            filenamelist=MythenSrsFileLoader().load(filename)
    except IOException, err:
        print "MythenSrsFileLoader failed. " , err
    return filenamelist
  
def loadMythenRawData(filename):
    '''load the mythen frame data.'''
    from gda.device.detector.mythen.data import MythenRawDataset
    
    if str(filename).startswith(File.separator):
        try:
            dataset = MythenRawDataset(java.io.File(filename))
        except:
            print "Fail to load data file: "+filename
        return dataset
    try:
        dataset = MythenRawDataset(java.io.File(os.path.join(PathConstructor.createFromDefaultProperty(),str(filename))))
    except:
        print "Fail to load data file: "+filename
    return dataset

def loadMythenData(filename):
    '''load the mythen frame data.'''
    from gda.device.detector.mythen.data import MythenProcessedDataset, MythenMergedDataset
    
    if str(filename).startswith(File.separator):
        try:
            dataset = MythenProcessedDataset(java.io.File(filename))
        except:
            dataset = MythenMergedDataset(java.io.File(filename))
        return dataset
    if str(filename).find("merged") == -1:
        if str(filename).find("summed") == -1:
            #Not merged file or it is mythen data file
            try:
                dataset = MythenProcessedDataset(java.io.File(os.path.join(PathConstructor.createFromDefaultProperty(),str(filename))))
            except:
                dataset = MythenMergedDataset(java.io.File(os.path.join(PathConstructor.createFromDefaultProperty(),str(filename))))
        else:
            dataset = MythenMergedDataset(java.io.File(os.path.join(PathConstructor.createFromDefaultProperty(),str(filename))))
        return dataset
    else:
        #externally merged file in 'processing' sub-folder
        dataset = MythenMergedDataset(java.io.File(os.path.join(PathConstructor.createFromDefaultProperty(),str(filename))))
        return dataset

def _getCurrentFileName(filenumber):
    ''' convert relative file number to its absolute path to the file with file extension as ".dat"'''
    filename = str(filenumber)
    if long(filenumber) < 0:
        filename = os.path.join(PathConstructor.createFromDefaultProperty(),str(int(NumTracker(LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME)).getCurrentFileNumber()+int(filenumber)))+".dat")
    else:
        filename = os.path.join(PathConstructor.createFromDefaultProperty(),str(filenumber)+ ".dat")
    return filename
