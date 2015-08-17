print "<<< Entering: startup_diffractometer_related_DEV.py ..."

#from gda.configuration.properties import LocalProperties
#import sys
#diffcalc_path = LocalProperties.getPath('gda.config',None)
#print "Adding path: ", diffcalc_path
#sys.path.append(diffcalc_path)

from pd_offsetAxis import OffsetAxisClass
from diffractometer.scannable.CoordinatedMotionGroup import CoordinatedMotionGroup
#from diffractometer.scannable.DeferredMotionGroup import DeferredMotionGroup
from gda.device.scannable import DOFAdapterWithStationaryRelativeLimits


### Rename OE and DOFs ###
rawsixc = sixc; rawkphi = kphi; rawkap = kap; rawkth = kth; rawkmu = mu; rawkdelta = delta; rawkgam = gam
del sixc, kphi, kap, kth, mu, delta, gam
#rawkphi = dummyClass('rawkphi')
#rawkap = dummyClass('rawkap')
#rawkth = dummyClass('rawkth')
#rawkmu = dummyClass('rawkmu')
#rawkdelta = dummyClass('rawkdelta')
#delta = dummyClass('delta')
#rawkgam = dummyClass('rawkgam')


### Install relative limits ###
exec("rawkth=DOFAdapterWithStationaryRelativeLimits(rawkth.getOE(), rawkth.getDofname())")
exec("rawkdelta=DOFAdapterWithStationaryRelativeLimits(rawkdelta.getOE(), rawkdelta.getDofname())")
exec("rawkgam=DOFAdapterWithStationaryRelativeLimits(rawkgam.getOE(), rawkgam.getDofname())")
exec("rawkmu=DOFAdapterWithStationaryRelativeLimits(rawkmu.getOE(), rawkmu.getDofname())")
# Note: the limits are actually set in ConfigureLimits.py

### Add offset to rawdelta ###
rawkdelta_no_offset=rawkdelta; del rawkdelta
rawkdelta_no_offset.setName('rawkdelta_no_offset')
rawkdelta_no_offset.setInputNames(['rawkdelta_no_offset'])
rawkdelta=OffsetAxisClass('rawkdelta', rawkdelta_no_offset, delta_axis_offset, help='rawkdelta device with offset given by delta_axis_offset. Use pos delta_axis_offset to change offset')
for scn in [rawkphi, rawkap, rawkth, rawkmu, rawkdelta, rawkgam ]:
	scn.setOutputFormat(['% 5.5f'])

### Build MotionGroup from raw diffractometer axes ###
sixc = CoordinatedMotionGroup('sixc',(rawkphi,rawkap,rawkth,rawkmu,rawkdelta,rawkgam), ('kphi','kap','kth','kmu','kdelta','kgam'))
#sixc = DeferredMotionGroup('sixc',(rawkphi,rawkap,rawkth,rawkmu,rawkdelta,rawkgam),('kphi','kap','kth','kmu','kdelta','kgam'), xps2_defer)
kphi = sixc.kphi; kap =sixc.kap; kth = sixc.kth; kmu = sixc.kmu; kdelta = sixc.kdelta; kgam= sixc.kgam





#
######
from EulerianKconversionModes import EulerianKconversionModes
EKCM = EulerianKconversionModes()
mode e2k 1

from diffractometer.scannable.EulerKappa import EulerKappa
euler = EulerKappa('euler',sixc)
phi = euler.phi; chi = euler.chi; eta = euler.eta; mu  = euler.mu; delta= euler.delta; gam = euler.gam



##############################################################################
###                         Diffraction Calculator                          ###
###############################################################################

print "Running DiffractTopClass.py"
run("DiffractTopClass")
# Now override the settings made by DiffractTopClass to beamline_objects
import beamline_objects as BLobjects
BLobjects.my_kphi = sixc.kphi
BLobjects.my_kap = sixc.kap
BLobjects.my_kth = sixc.kth
BLobjects.my_mu = sixc.kmu
BLobjects.my_delta = sixc.kdelta
BLobjects.my_gam = sixc.kgam

###############################################################################
###                        Eulerian axes from Kappa                         ###
###############################################################################


print "Euler-K Conversion modules imported"
print "   creating BLobjects"
import beamline_objects as BLobjects



###############################################################################
###                               HKL devices                               ###
###############################################################################
#create the hkl pd
import DiffractometerInfo as EDi

print "Creating HKL scannables"
from diffractometer.scannable import HklEuler 
reload(HklEuler) 
hkl = HklEuler.HklEuler("hkl",euler,rs,CA,EDi,az) 
print "   creating hkl, h, k and l" 
h = hkl.h; k = hkl.k; l = hkl.l 

#print "   creating  scannable (from hklPseudoDevice_Borrman): hkl_0"
#import hklPseudoDevice_Borrman
#reload(hklPseudoDevice_Borrman)
#hkl_0=hklPseudoDevice_Borrman.hklPseudoDevice_Borrman("hkl_B",euler,delta,rs,CA,EDi,delta_virtual,gam,az,delta)
#



print "   creating hkl calculator: hkl_calc"
import hklPseudoDevice_no_move
reload(hklPseudoDevice_no_move)
hkl_calc = hklPseudoDevice_no_move.hklPseudoDevice("hkl_calc",euler,delta,rs,CA,EDi)

#print "Creating thetatth pseudo device..."
#import thetatth as thetatthClass
#reload(thetatthClass)
#thetatth = thetatthClass.thetatth("thetatth",eta)

###############################################################################
###                          Four circle scannable                          ###
###############################################################################

print "Creating fourcircle scannable"
import fourCirclePseudoDevice
reload(fourCirclePseudoDevice)
fourcircle = fourCirclePseudoDevice.fourCirclePseudoDevice("fourcircle",euler)


###############################################################################
###                        Scattering plane scannable                       ###
###############################################################################
print "Creating scattering plane scannable: tth"
tth = BLobjects.getTth()                       #[Will be either delta or gamma]


###############################################################################
###                            Psi scannables                               ###
###############################################################################
print "Creating psi scannables: psi & psic"
import PsiPseudoDevice
reload(PsiPseudoDevice)
import PsicPseudoDevice
reload(PsicPseudoDevice)
psi = PsiPseudoDevice.PsiPseudoDevice("psi",euler,az,CA,hkl)
psic = PsicPseudoDevice.PsicPseudoDevice("psic",az)


###############################################################################
###                         Two-theta scannable                            ###
###############################################################################
if installation.isLive():
	print "setting up th2th and thp2thp scannables"
	run("pd_thetatth")

	th2th=thetatth("th2th",eta,delta,eta_offset,delta_offset,help="Example scan: scan th2th [0.1 0.2] [0.2 0.4] [0.01 0.02] t 0.1\n Can offset angles using eta_offset,delta_offset")
	thp2thp=thetatth("thp2thp",thp,tthp,thp_offset,tthp_offset)
	phi_gam=thetatth("phi_gam",phi,gam,phi_offset,gam_offset,help="Example scan: scan th2th [-0.1 0.2] [-0.2 0.4] [-0.01 0.02] t 0.1 \n Remember Phi and Gam move in opposite directions"); phi_gam.setInputNames(["phi","gam"]); #remember phi  and gam move in opposite directions


###############################################################################
###                            Diffractometer base                          ###
###############################################################################
print "Creating diffractometer base scannable"
run("pd_diffractometerbase") #--> DiffoBaseClass
print '!!! using TEMPORARY DiffBaseClass !!!'
basez1=SingleEpicsPositionerClass('basez1','BL16I-MO-DIFF-01:BASE:Y1.VAL','BL16I-MO-DIFF-01:BASE:Y1.RBV','BL16I-MO-DIFF-01:BASE:Y1.DMOV','BL16I-MO-DIFF-01:BASE:Y1.STOP','mm','%4f',command=None)
basez2=SingleEpicsPositionerClass('basez2','BL16I-MO-DIFF-01:BASE:Y2.VAL','BL16I-MO-DIFF-01:BASE:Y2.RBV','BL16I-MO-DIFF-01:BASE:Y2.DMOV','BL16I-MO-DIFF-01:BASE:Y2.STOP','mm','%4f',command=None)
basez3=SingleEpicsPositionerClass('basez3','BL16I-MO-DIFF-01:BASE:Y3.VAL','BL16I-MO-DIFF-01:BASE:Y3.RBV','BL16I-MO-DIFF-01:BASE:Y3.DMOV','BL16I-MO-DIFF-01:BASE:Y3.STOP','mm','%4f',command=None)
base_z= TemporaryDiffoBaseClass([1.52,-0.37,0.]) #measured 28/11/07

print "... Leaving: startup_diffractometer_related_DEV.py >>>"
