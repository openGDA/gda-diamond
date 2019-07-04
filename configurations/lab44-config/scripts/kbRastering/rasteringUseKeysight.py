'''
Module define and create KB Mirror Rastering Control Scannables:
    raster, beamsize, vrastamplitude, hrastamplitude, vrastoffset, hrastoffset, rastperiod, vraststatus, hraststatus

Fix Issue: I06-620
Created on 5 Mar 2019

@author: fy65
'''
from gda.device.scannable import PVScannable, ScannableMotionBase,\
    EpicsScannable
from peem.leem_instances import FOV
from scisoftpy.jython.jymaths import nan
from gdaserver import s4ygap

print "-"*100
print "create KB Rastering control scannables: raster, beamsize, vrastamplitude, hrastamplitude, vrastoffset, hrastoffset, rastperiod, vraststatus, hraststatus"

#Low Level Scannables
vrastamplitude=PVScannable("vrastamplitude","BL06I-EA-SGEN-01:CH2:AMP"); vrastamplitude.configure()
hrastamplitude=PVScannable("hrastamplitude","BL06I-EA-SGEN-01:CH1:AMP"); hrastamplitude.configure()
vrastoffset=PVScannable("vrastoffset","BL06I-EA-SGEN-01:CH2:OFF"); vrastoffset.configure()
hrastoffset=PVScannable("hrastoffset","BL06I-EA-SGEN-01:CH1:OFF"); hrastoffset.configure()
rastperiod=PVScannable("rastperiod","BL06I-EA-SGEN-01:PERIOD"); rastperiod.configure()
vraststatus=EpicsScannable(); vraststatus.setName("vraststatus"); vraststatus.setHasUnits(False); 
vraststatus.setPvName("BL06I-EA-SGEN-01:CH2:OUT"); vraststatus.setGetAsString(True); 
vraststatus.setUseNameAsInputName(True); vraststatus.configure()
hraststatus=EpicsScannable(); hraststatus.setName("hraststatus"); hraststatus.setHasUnits(False); 
hraststatus.setPvName("BL06I-EA-SGEN-01:CH1:OUT"); hraststatus.setGetAsString(True); 
hraststatus.setUseNameAsInputName(True); hraststatus.configure()


KEYSIGHT_OUTPUT_STATUS={0:'Off',1:'On'}
KEYSIGHT_OUTPUT_VALUE={'Off':0,'On':1}

vert,horiz,roff,undefined=['vert','horiz','roff','undefined']

class KBMirrorRasteringStateControl(ScannableMotionBase):
    '''
    control Rastering state and direction: vert,horiz,roff,undefined
    '''

    def __init__(self, name, vraststatus, hraststatus):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%s"])
        self.vraststatus=vraststatus
        self.hraststatus=hraststatus
        
    def getPosition(self):
        if self.vraststatus.getPosition()=='On' and self.hraststatus.getPosition()=='Off':
            return vert
        elif self.vraststatus.getPosition()=='Off' and self.hraststatus.getPosition()=='On':
            return horiz
        elif self.vraststatus.getPosition()=='Off' and self.hraststatus.getPosition()=='Off':
            return roff
        elif self.vraststatus.getPosition()=='On' and self.hraststatus.getPosition()=='On':
            return undefined
        
    def asynchronousMoveTo(self, newpos):
        try:
            if newpos == vert:
                self.vraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['On'])
                self.hraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['Off'])
            elif newpos == horiz:
                self.vraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['Off'])
                self.hraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['On'])
            elif newpos == roff:
                self.vraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['Off'])
                self.hraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['Off'])
            else:
                raise "Input value: %s is not supported" % newpos
        except:
            raise
    
    def isBusy(self):
        return self.vraststatus.isBusy() or self.hraststatus.isBusy()
    

raster=KBMirrorRasteringStateControl("raster",vraststatus, hraststatus)

class BeamSize(ScannableMotionBase):
    
    def __init__(self, name, leem_fov, vrastamplitude, hrastamplitude, raster, s4ygap):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%f"])
        self.fov=leem_fov
        self.vrastamplitude=vrastamplitude
        self.hrastamplitude=hrastamplitude
        self.raster=raster
        self.s4ygap=s4ygap
        self.beamsize=nan
    
    def getPosition(self):
        return self.beamsize
    
    def asynchronousMoveTo(self, newpos):
        bsize=float(newpos)
        if bsize<=0.0:
            raise "beam size cannot be 0 or negative!"
        try:
            if bsize < 6.0:
                self.vrastamplitude.asynchronousMoveTo(0)
                self.hrastamplitude.asynchronousMoveTo(0)
                self.raster.asynchronousMoveTo(roff)
                self.s4ygap.asynchronousMoveTo(0.025)
            elif bsize>=6.0 and bsize <= 10.0:
                self.vrastamplitude.asynchronousMoveTo(-0.15+0.025*float(self.fov.getPosition()))
                self.raster.asynchronousMoveTo(vert)
                self.s4ygap.asynchronousMoveTo(0.025)
            elif bsize > 10.0:
                self.hrastamplitude.asynchronousMoveTo(-0.17+0.033*float(self.fov.getPosition()))
                self.raster.asynchronousMoveTo(horiz)
                self.s4ygap.asynchronousMoveTo(-87+8.4*float(self.fov.getPosition()))
            self.beamsize=bsize
        except:
            raise
        
    def isBusy(self):
        return self.vrastamplitude.isBusy() or self.hrastamplitude.isBusy() or self.raster.isBusy() or self.s4ygap.isBusy()
    
beamsize=BeamSize("beamsize", FOV, vrastamplitude, hrastamplitude, raster, s4ygap)