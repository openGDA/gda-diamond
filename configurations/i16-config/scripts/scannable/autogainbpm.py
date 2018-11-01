#beam position monitor
from gdascripts.scannable.epics.PvManager import PvManager
from time import sleep
from gda.device.scannable import ScannableBase

class AutogainBpm(ScannableBase):
    '''
`    Device to read stats from beam position monitor
    Use self.i() to put screen in and self.o() to move screen out manually.
    This is automatic for a scan.
    
    An example detector could be made with:
    
    bpm = SwitchableHardwareTriggerableProcessingDetectorWrapper('bpm',
                            _cam1,
                            None,
                            _cam1_for_snaps,
                            [],
                            panel_name_rcp='Plot 1', 
                            fileLoadTimout=60,
                            printNfsTimes=False,
                            returnPathAsImageNumberOnly=True)

bpm.display_image = True
bpm.processors=[DetectorDataProcessorWithRoi('peak', bpm, [SumMaxPositionAndValue(), TwodGaussianPeakWithCalibration()], False)]

Will return 'maxx','maxy','maxval', 'sum' followed by 'background','peakx_raw','peaky_raw','peakx','peaky','peakx_mm','peaky_mm', 'topx', 'topyy','fwhmx','fwhmy', 'fwhmarea'

    '''
    def __init__(self, name, detector, comchan='BL16I-DI-BPM-01:STATS:', help=None):
        self.name = name        
        self.inputNames = []
        self.extraNames = list(self._det.extraNames)
        self.outputFormat = list(self._det.outputFormat)
        self.level = 9
        self._det = detector
        self.pvs = PvManager(pvroot = comchan)
        self.mm_per_pixel=0.0037
        if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help

    def getPosition(self):
        caput("BL16I-DI-BPM-01:CAM:ExposureAutoAlg", "FitRange")
        caput("BL16I-DI-BPM-01:CAM:ExposureAuto", "Once")
        sleep(0.1)
        while caget('BL16I-DI-BPM-01:CAM:ExposureAuto_RBV') != '0':
            sleep(0.1)
        position = self._det()
        maxx, maxy,maxval, sum, background, peakx_raw, peaky_raw, peakx, peaky, peakx_mm, peaky_mm, topx, topyy, fwhmx, fwhmy, fwhmarea = position
        bpmsum = sum #  float(self.pvs['Total_RBV'].caget())
        bpmx = peakx_mm # float(self.pvs['CentroidX_RBV'].caget())*self.mm_per_pixel/sqrt(2)
        bpmy = float(self.pvs['CentroidY_RBV'].caget())*self.mm_per_pixel
        sigmax = float(self.pvs['SigmaX_RBV'].caget())*self.mm_per_pixel*sqrt(8*log(2))/sqrt(2)
        sigmay = float(self.pvs['SigmaY_RBV'].caget())*self.mm_per_pixel*sqrt(8*log(2))
        exposure = float(caget('BL16I-DI-BPM-01:CAM:AcquireTime_RBV'))
        return [bpmx,bpmy,sigmax,sigmay,bpmsum,exposure]

    def atScanStart(self):
        self.i()

    def atScanEnd(self):
        self.o()

    def isBusy(self):
        return False

    def i(self):
        caput('BL16I-DI-BPM-01:DIAG.VAL',-18)
        print "Screen in"

    def o(self):    
        caput('BL16I-DI-BPM-01:DIAG.VAL',-2)
        print "Screen out"


bp=bpmstats=BpmStats("bpmstats")
#def bpmin():
#    caput('BL16I-DI-BPM-01:DIAG.VAL',-20)
#    print "Screen in (-20)"
#
#def bpmout():
#    caput('BL16I-DI-BPM-01:DIAG.VAL',-2)
#    print "Screen out (-2)"

xlist=[] 
ylist=[]
def bplist():
    global xlist
    global ylist
    bp.i()
    pos w 1
    bpout=bp()
    xlist+=[str(bpout[0])]
    ylist+=[str(bpout[1])]
    bp.o()
    
