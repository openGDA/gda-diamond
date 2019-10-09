import installation
print "<<< Entering: startup_diffractometer_hkl.py ..."

from diffractometer.calc import DiffractometerInfo as EDi

print "Running localStationScripts/DiffractTopClass.py"
run("localStationScripts/DiffractTopClass.py")

print "Creating coordianted HKL scannable"
from diffractometer.scannable import HklEuler 
reload(HklEuler) 
hkl = HklEuler.HklEuler("hkl",euler,rs,CA,EDi,az) 
print "   creating hkl, h, k and l" 
h = hkl.h; k = hkl.k; l = hkl.l 



print "   creating  scannable (from hklPseudoDevice_Borrman): hkl_0"
from diffractometer.calc import hklPseudoDevice_Borrman
reload(hklPseudoDevice_Borrman)
hkl_0=hklPseudoDevice_Borrman.hklPseudoDevice_Borrman("hkl_B",euler,delta,rs,CA,EDi,delta_virtual,gam,az,delta)

print "   creating hkl scannable with eta offset: hkl_0"
from diffractometer.calc import hklPseudoDevice_offset
reload(hklPseudoDevice_offset)
hkl_etao=hklPseudoDevice_offset.hklPseudoDevice_offset("hkl_etao",euler,delta,rs,CA,EDi,delta,gam,az,eta_offset,1)

#import qPseudoDevice
#reload(qPseudoDevice)
#q = qPseudoDevice.qPseudoDevice("q",euler,delta,rs,CA,EDi,delta,gam,az)
#import qxyzPseudoDevice
#reload(qxyzPseudoDevice)
#qx = qxyzPseudoDevice.qxyzPseudoDevice("qx",q)
#qy = qxyzPseudoDevice.qxyzPseudoDevice("qy",q)
#qz = qxyzPseudoDevice.qxyzPseudoDevice("qz",q)

print "   creating hkl calculator: hkl_calc"
from diffractometer.calc import hklPseudoDevice_no_move
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
from diffractometer.calc import fourCirclePseudoDevice
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
from diffractometer.calc import PsiPseudoDevice
reload(PsiPseudoDevice)
from diffractometer.calc import PsicPseudoDevice
reload(PsicPseudoDevice)
psi = PsiPseudoDevice.PsiPseudoDevice("psi",euler,az,CA,hkl)
psic = PsicPseudoDevice.PsicPseudoDevice("psic",az)


if installation.isDummy():
    raise Exception("Manually bailing out of startup_diffractometer_hkl.py before entering the unknown (as this is a test installation)")
###############################################################################
###                         Two-theta scannable                            ###
###############################################################################
print "setting up th2th and thp2thp scannables"
run("localStationScripts/pd_thetatth")

th2th=thetatth("th2th",eta,delta,eta_offset,delta_offset,help="Example scan: scan th2th [0.1 0.2] [0.2 0.4] [0.01 0.02] t 0.1")
thp2thp=thetatth("thp2thp",thp,tthp,thp_offset,tthp_offset)
phi_gam=thetatth("phi_gam",phi,gam,phi_offset,gam_offset,help="Example scan: scan th2th [-0.1 0.2] [-0.2 0.4] [-0.01 0.02] t 0.1 \n Remember Phi and Gam move in opposite directions"); phi_gam.setInputNames(["phi","gam"]); #remember phi  and gam move in opposite directions


###############################################################################
###                            PD from function	(alpha, beta)	            ###
###############################################################################
run('localStationScripts/PDFromFunctionClass')
###############################################################################
###############################################################################
###                             Xtalinfo
###############################################################################
run("localStationScripts/pd_crystal_info")

xtalinfo=crystalinfo('xtalinfo','A','%7.5f',ub,cr)

print "creating crystal info"

print "... Leaving: startup_diffractometer_hkl.py >>>"