'''
Module define and create KB Mirror Rastering Control Scannables:
    raster, beamsize, vrastamplitude, hrastamplitude, rastperiod, vraststatus, hraststatus

Fix Issue: I06-620
Created on 5 Mar 2019
#hello
@author: fy65
'''
from gda.device.scannable import PVScannable, ScannableMotionBase,\
    EpicsScannable
from peem.leem_instances import FOV
from scisoftpy.jython.jymaths import nan
from gdaserver import s4ygap  # @UnresolvedImport

print("-"*100)
print("create KB Rastering control scannables: raster, beamsize, vrastamplitude, hrastamplitude, rastperiod, vraststatus, hraststatus")

#Low Level Scannables
vrastamplitude=PVScannable("vrastamplitude","BL06I-EA-SGEN-01:CH1:AMP"); vrastamplitude.configure()
hrastamplitude=PVScannable("hrastamplitude","BL06I-EA-SGEN-01:CH2:AMP"); hrastamplitude.configure()
rastperiod=PVScannable("rastperiod","BL06I-EA-SGEN-01:PERIOD"); rastperiod.configure()
vraststatus=EpicsScannable(); vraststatus.setName("vraststatus"); vraststatus.setHasUnits(False); 
vraststatus.setPvName("BL06I-EA-SGEN-01:CH1:OUT"); vraststatus.setGetAsString(True); 
vraststatus.setUseNameAsInputName(True); vraststatus.configure()
hraststatus=EpicsScannable(); hraststatus.setName("hraststatus"); hraststatus.setHasUnits(False); 
hraststatus.setPvName("BL06I-EA-SGEN-01:CH2:OUT"); hraststatus.setGetAsString(True); 
hraststatus.setUseNameAsInputName(True); hraststatus.configure()
raster=PVScannable("raster","BL06I-OP-KBM-01:RASTER:MODE"); raster.configure()


KEYSIGHT_OUTPUT_STATUS={0:'Off',1:'On'}
KEYSIGHT_OUTPUT_VALUE={'Off':0,'On':1}

vert,horiz,roff,undefined=['vert','horiz','roff','undefined']

class KBMirrorRasteringStateControl(ScannableMotionBase):
    '''
    control Rastering state and direction: vert,horiz,roff,undefined
    '''

    def __init__(self, name, vraststatus, hraststatus, vrastamplitude, hrastamplitude):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%s"])
        self.vraststatus=vraststatus
        self.hraststatus=hraststatus
        self.vrastamplitude=vrastamplitude
        self.hrastamplitude=hrastamplitude
        self.cached_vrastamplitude=0.1
        self.cached_hrastamplitude=0.1
        
    def getPosition(self):
        if self.vrastamplitude.getPosition()>0.001 and self.hrastamplitude.getPosition()<0.002:
            return vert
        elif self.vrastamplitude.getPosition()<0.002 and self.hrastamplitude.getPosition()>0.001:
            return horiz
        elif self.vrastamplitude.getPosition()<0.002 and self.hrastamplitude.getPosition()<0.002:
            return roff
        elif self.vrastamplitude.getPosition()>0.001 and self.hrastamplitude.getPosition()>0.001:
            return undefined
        
    def asynchronousMoveTo(self, newpos):
        try:
            if newpos == vert:
                if not self.getPosition() == roff:
                    self.cached_hrastamplitude=float(self.hrastamplitude.getPosition())
                self.hrastamplitude.asynchronousMoveTo(0.0)
#                 self.hraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['Off'])
                self.vrastamplitude.asynchronousMoveTo(self.cached_vrastamplitude)
#                 self.vraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['On'])
                
            elif newpos == horiz:
                if not self.getPosition() == roff:
                    self.cached_vrastamplitude=float(self.vrastamplitude.getPosition())
                self.vrastamplitude.asynchronousMoveTo(0.0)
#                 self.vraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['Off'])
                self.hrastamplitude.asynchronousMoveTo(self.cached_hrastamplitude)
#                 self.hraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['On'])
            elif newpos == roff:
                if self.getPosition() == horiz:
                    self.cached_hrastamplitude=float(self.hrastamplitude.getPosition())
                if self.getPosition() == vert:
                    self.cached_vrastamplitude=float(self.vrastamplitude.getPosition())
                self.hrastamplitude.asynchronousMoveTo(0.0)
                self.vrastamplitude.asynchronousMoveTo(0.0)
#                 self.vraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['Off'])
#                 self.hraststatus.asynchronousMoveTo(KEYSIGHT_OUTPUT_VALUE['Off'])
            else:
                raise Exception("Input value: %s is not supported" % newpos)
        except:
            raise
    
    def isBusy(self):
        return self.vraststatus.isBusy() or self.hraststatus.isBusy()
    

# raster=KBMirrorRasteringStateControl("raster",vraststatus, hraststatus, vrastamplitude, hrastamplitude)

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
#                 self.raster.asynchronousMoveTo(roff)
                self.s4ygap.asynchronousMoveTo(25.0)
            elif bsize>=6.0 and bsize <= 10.0:
                self.vrastamplitude.asynchronousMoveTo(-0.15+0.025*bsize)
                self.hrastamplitude.asynchronousMoveTo(0)
#                 self.vrastamplitude.asynchronousMoveTo(-0.15+0.025*float(self.fov.getPosition()))
#                 self.raster.asynchronousMoveTo(vert)
                self.s4ygap.asynchronousMoveTo(25.0)
            elif bsize > 10.0:
                self.hrastamplitude.asynchronousMoveTo(-0.17+0.033*bsize)
                self.vrastamplitude.asynchronousMoveTo(0)
#                 self.hrastamplitude.asynchronousMoveTo(-0.17+0.033*float(self.fov.getPosition()))
#                 self.raster.asynchronousMoveTo(horiz)
                self.s4ygap.asynchronousMoveTo(-59.0+8.4*bsize)
#                 self.s4ygap.asynchronousMoveTo(-87+8.4*float(self.fov.getPosition()))
            self.beamsize=bsize
        except:
            raise
        
    def isBusy(self):
        return self.vrastamplitude.isBusy() or self.hrastamplitude.isBusy() or self.raster.isBusy() or self.s4ygap.isBusy()
    
beamsize=BeamSize("beamsize", FOV, vrastamplitude, hrastamplitude, raster, s4ygap)