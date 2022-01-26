#@PydevCodeAnalysisIgnore
from uk.ac.gda.client.microfocus.scan.datawriter import MicroFocusWriterExtender
from uk.ac.gda.util.beans.xml import XMLHelpers
from gda.factory import Finder
from gda.exafs.scan import BeanGroup
from java.io import File
from java.lang import System
from gda.configuration.properties import LocalProperties
from jarray import array
from gda.jython import InterfaceProvider
from gda.data.scan.datawriter import XasAsciiDataWriter
from gda.data.scan.datawriter import NexusDataWriter
#import rastermap.rastermap
#import microfocus.microfocus_elements

def mapscan (scanFileName, detectorFileName, folderName=None, scanNumber= -1, validation=True):
    #print globals()
    """
    main map data collection command. 
    usage:-
    
    map scanFileName detectorFileName [experiment name (_script)] [scan index (1)] [validation required (True)]
    
    """
    print detectorFileName
    
    if True:# Turn on debugging here
        print "Values sent to script:"
        print "scanFileName", scanFileName
        print "detectorFileName", detectorFileName
        print "folderName", folderName
        print "scanNumber", scanNumber
        print "validation", validation

    # Create the beans from the file names        
    scanBean     = XMLHelpers.getBeanObject(MicroFocusEnvironment().getScriptFolder(), scanFileName)
    detectorBean = XMLHelpers.getBeanObject(MicroFocusEnvironment().getScriptFolder(), detectorFileName)
     
    # give the beans to the xasdatawriter class to help define the folders/filenames 
    beanGroup = BeanGroup()
    beanGroup.setController(Finder.find("ExafsScriptObserver"))
    beanGroup.setScriptFolder(MicroFocusEnvironment().getScriptFolder())
    beanGroup.setScannable(globals()[scanBean.getXScannableName()]) #TODO
    beanGroup.setExperimentFolderName(folderName)
    beanGroup.setScanNumber(scanNumber)
    beanGroup.setDetector(detectorBean)
    beanGroup.setValidate(validation)
    beanGroup.setScan(scanBean)
    XasAsciiDataWriter.setBeanGroup(beanGroup)
      
    # add detector object to this list
    xmap_name = detectorBean.getDetectorGroups()[0].getDetector()[0] # WRONG
    xmap_name = 'xmap'
    detectorList = [Finder.find(xmap_name)]
    
    # extract any signal parameters to add to the scan command
    dataWriter = NexusDataWriter()
    nx = abs(scanBean.getXEnd() - scanBean.getXStart()) / scanBean.getXStepSize()
    ny = abs(scanBean.getYEnd() - scanBean.getYStart()) / scanBean.getYStepSize()
    
  
    print "number of x points is ", str(nx)
    print "number of y points is ", str(ny)
    # Determine no of points
    nx = int(round(nx + 1.0))
    ny = int(round(ny + 1.0))
    print "number of x points is ", str(nx)
    print "number of y points is ", str(ny)
    energyList = [scanBean.getEnergy()]
    zScannablePos = scanBean.getZValue()
    for energy in energyList:
        mfd = MicroFocusWriterExtender(nx, ny, scanBean.getXStepSize(), scanBean.getYStepSize())
        zScannable = globals()[scanBean.getZScannableName()]
    
        ##put the data writer in the globals to retreive the plot and spectrum info later from the gui
        globals()["microfocusScanWriter"] = mfd
        mfd.setPlotName("MapPlot")
        print " the detector is " 
        print detectorList
    
        #should get the bean file name from detector parametrs
        if(folderName != None):
            detectorBeanFileName =MicroFocusEnvironment().getScriptFolder()+File.separator +folderName +File.separator+detectorBean.getFluorescenceParameters().getConfigFileName()
        else:
            detectorBeanFileName =MicroFocusEnvironment().getScriptFolder()+detectorBean.getFluorescenceParameters().getConfigFileName()
        print detectorBeanFileName
        elements = showElementsList(detectorBeanFileName)
        selectedElement = elements[0]
        mfd.setRoiNames(array(elements, java.lang.String))
        mfd.setDetectorBeanFileName(detectorBeanFileName)
        bean = XMLHelpers.getBean(File(detectorBeanFileName))   
        detector = globals()[bean.getDetectorName()]   
        mfd.setDetectors(array(detectorList, gda.device.Detector))     
        mfd.setSelectedElement(selectedElement)
        mfd.getWindowsfromBean()
            
        mfd.setEnergyValue(energy)
        if(zScannablePos == None):
            mfd.setZValue(zScannable.getPosition())
        else:
            mfd.setZValue(zScannablePos)
        dataWriter.addDataWriterExtender(mfd)
        
        xScannable = globals()[scanBean.getXScannableName()]
        yScannable = globals()[scanBean.getYScannableName()]
        useFrames = LocalProperties.check("gda.microfocus.scans.useFrames")
        print "using frames ", str(useFrames)
        energyScannable = globals()[scanBean.getEnergyScannableName()]
        
        print "energy is ", str(energy)
        print "energy scannable is " 
        print energyScannable  
        print detectorList
        energyScannable.moveTo(energy) 
        # TODO add extra scannables here
        args=[yScannable, scanBean.getYStart(), scanBean.getYEnd(),  scanBean.getYStepSize(),  xScannable, scanBean.getXStart(), scanBean.getXEnd(),  scanBean.getXStepSize(),energyScannable, zScannable]
        
        for detector in detectorList:
            args.append(detector)              
            args.append(scanBean.getCollectionTime())
        print args
        try:
            myscan = ConcurrentScan(args)
            myscan.setDataWriter(dataWriter);
            myscan.runScan()
        finally:
            dataWriter.removeDataWriterExtender(mfd)
              
              
class MicroFocusEnvironment:
    testScriptFolder=None
    def getScriptFolder(self):
        if MicroFocusEnvironment.testScriptFolder != None:
            return MicroFocusEnvironment.testScriptFolder
        dataDirectory = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
        return dataDirectory + "/xml/"

    testScannable=None
    def getScannable(self):
        if MicroFocusEnvironment.testScannable != None:
            return MicroFocusEnvironment.testScannable
        # The scannable name is defined in the XML when not in testing mode.
        # Therefore the scannable argument is omitted from the bean
  
        return None
