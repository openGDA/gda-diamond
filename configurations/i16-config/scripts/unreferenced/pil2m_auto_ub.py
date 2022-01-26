from uk.ac.diamond.scisoft.analysis.io import CBFLoader, PilatusTiffLoader
from gdascripts.utils import caput

BASE_PV = 'BL16I-EA-PILAT-02:cam1:'

def set_mx(**args):
    for key in args:
        caput(BASE_PV + key, args[key])

def write_cbf(pdw):
    pdw.iFileLoader = CBFLoader
    pdw.det.fileTemplate = '%s%s%d.cbf'

def write_tif(pdw):
    pdw.iFileLoader = PilatusTiffLoader
    pdw.det.fileTemplate = '%s%s%d.tif'



#################################################################
# setup

write_cbf(pil2m)
#DetDist in mm, BeamX and BeamY in pixels
set_mx(Wavelength=1.093, OscillAxis='omega', DetDist=208+17.5, BeamX=760, BeamY=1033) 

#################################################################
# scan
pil2m.returnPathAsImageNumberOnly = False
pil2m.root_datadir = datadir() + '/'

start = -90
stop = 270
#step = 1
step = 0.5 #after 242124

set_mx(StartAngle=start, AngleIncr=step)
pos pil2m 1 # to clear any wierdness
pos kphi start
#242116
#trajscan kphi start stop step pil2m 1
#242118
#pos atten 50 # 11.6%
#trajscan kphi start stop step pil2m .2

#Si crystal (was 50A germanate)
#pos atten 0
#242121
#trajscan kphi start stop step pil2m .2

#pos atten 100
#242122
#trajscan kphi start stop step pil2m .2

#pos atten 100
#step = .1
#242125
#trajscan kphi start stop step pil2m .2

#step=0.1 crashed
#0.2 did not run
#0.5 OK?
#java.lang.InterruptedException: Scan halted: DeviceException during doing collection: Problem setting number of elements in Epics

pos atten 200
#242125 start 18:30 waiting for beam 250 mA
note('Si step=0.5 20 scans')
for ii in range(20):
	pos checkbeam
	trajscan kphi start stop step pil2m .2
note('no note')
pos shutter 0
#last scan #242168