print "In localStation.testonly.py"

class Wavelength(PseudoDevice):
    
    def __init__(self, name):
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%f']
        
    def isBusy(self):
        return False
    
    def getPosition(self):
        return BLi.getWavelength()

    def asynchronousMoveTo(self, wl):
        BLi.setWavelength(float(wl))

class Energy(PseudoDevice):
    
    def __init__(self, name):
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%f']
        
    def isBusy(self):
        return False
    
    def getPosition(self):
        return BLi.getEnergy()

    def asynchronousMoveTo(self, en):
        BLi.setEnergy(float(en))   

wl = Wavelength('wl')
energy = Energy('energy')
        


#print """
#
#newub 'cubic'                   <-->  reffile('cubic) 
#setlat 'cubic' 1 1 1 90 90 90   <-->  latt([1,1,1,90,90,90])
#pos wl 1                        <-->  BLi.setWavelength(1)
#                                <-->  c2th([0,0,1]) --> 60
#pos sixc [0 60 0 30 1 1]        <-->  pos euler [1 1 30 0 60 0]
#addref 1 0 0                    <-->  saveref('100',[1, 0, 0])
#pos chi 91                      <-->  
#addref 0 0 1                    <-->  saveref('001',[0, 0, 1]) ; showref()
#                                      ubm('100','001')
#                                      ubm() -> array('d', [0.9996954135095477, -0.01745240643728364, -0.017449748351250637, 0.01744974835125045, 0.9998476951563913, -0.0003045864904520898, 0.017452406437283505, -1.1135499981271473e-16, 0.9998476951563912])
#
#checkub                         <-->  
#ub                              <-->  
#hklmode                         <-->  
#
#
#"""




#from gdascripts.scannable.detector.epics.EpicsPilatus import EpicsPilatus
#
#from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
#from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessor, DetectorDataProcessorWithRoi
#from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
#from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
#from gda.analysis.io import PilatusLoader, PilatusTiffLoader, TIFFImageLoader
#
#
#
#
#try:
#    pil2mdet = EpicsPilatus('pil2mdet', 'BL16I-EA-PILAT-02:','/dls/i16/detectors/im/','test','%s%s%d.tif')
#    pil2m = ProcessingDetectorWrapper('pil2m', pil2mdet, processors=[], panel_name='Pilatus2M', toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, root_datadir=None, fileLoadTimout=None, printNfsTimes=False, returnPathAsImageNumberOnly=True)
#    pil2m.processors=[DetectorDataProcessorWithRoi('max', pil2m, [SumMaxPositionAndValue()], False)]
#    pil2m.printNfsTimes = True
#    pil2m.display_image = True
#except gda.factory.FactoryException:
#    print " *** Could not connect to pilatus (FactoryException)"
#except     java.lang.IllegalStateException:
#    print " *** Could not connect to pilatus (IllegalStateException)"


