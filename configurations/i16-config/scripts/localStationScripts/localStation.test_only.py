print "In localStation.testonly.py"



raise Exception("Manually INTERRUPTING localStation.testonly.py")

if USE_DIFFCALC:
    energy = dummy_energy

class Wavelength(ScannableMotionBase):
    
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

class Energy(ScannableMotionBase):
    
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

#wl = Wavelength('wl')
energy = Energy('energy')
energy.asynchronousMoveTo(12.39842)


        


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




from gdascripts.scannable.detector.epics.EpicsPilatus import EpicsPilatus

from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessor, DetectorDataProcessorWithRoi
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gda.analysis.io import PilatusLoader, PilatusTiffLoader, TIFFImageLoader

pil100k = SwitchableHardwareTriggerableProcessingDetectorWrapper('pil100k',
                                                                pilatus1,
                                                                pilatus1_hardware_triggered,
                                                                pilatus1_for_snaps,
                                                                [],
                                                                panel_name_rcp='Plot 1',
                                                                toreplace=None,
                                                                replacement=None,
                                                                iFileLoader=PilatusTiffLoader,
                                                                fileLoadTimout=60,
                                                                returnPathAsImageNumberOnly=False)
pil100k.processors=[DetectorDataProcessorWithRoi('max', pil100k, [SumMaxPositionAndValue()], False)]
pil100k.printNfsTimes = False
pil100ks = DetectorWithShutter(pil100k, x1)
pil = pil100k
pils = pil100ks
#pil100kvrf=SingleEpicsPositionerSetAndGetOnlyClass('P100k_VRF','BL16I-EA-PILAT-01:VRF','BL16I-EA-PILAT-01:VRF','V','%.3f',help='set VRF (gain) for pilatus\nReturns set value rather than true readback\n-0.05=very high\n-0.15=high\n-0.2=med\n-0.3=low')
#pil100kvcmp=SingleEpicsPositionerSetAndGetOnlyClass('P100k_VCMP','BL16I-EA-PILAT-01:VCMP','BL16I-EA-PILAT-01:VCMP','V','%.3f',help='set VCMP (threshold) for pilatus\nReturns set value rather than true readback\n0-1 V')
#pil100kgain=SingleEpicsPositionerSetAndGetOnlyClass('P100k_gain','BL16I-EA-PILAT-01:Gain','BL16I-EA-PILAT-01:Gain','','%.3f',help='set gain for pilatus\nReturns set value rather than true readback\n3=very high\n2=high\n1=med\n0=low')
#pil100kthresh=SingleEpicsPositionerSetAndGetOnlyClass('P100k_threshold','BL16I-EA-PILAT-01:ThresholdEnergy','BL16I-EA-PILAT-01:ThresholdEnergy','','%.0f',help='set energy threshold for pilatus (eV)\nReturns set value rather than true readback')

from scannable.pilatus import PilatusThreshold, PilatusGain
pil100kthresh = PilatusThreshold('pil100kthresh', pilatus1_hardware_triggered.getCollectionStrategy().getAdDriverPilatus())
pil100kgain = PilatusGain('pil100kgain', pilatus1_hardware_triggered.getCollectionStrategy().getAdDriverPilatus())
