print "<<< Entering: startup_energy_related.py ..."

# depends on bragg, perp, and at least M1y (then gave up looking for dependencies)


# The following replaced with idgap --> ID.GAP -->  SR16I-MO-SERVC-01:BLGAPMTR

#from pd_epics import SingleEpicsPositionerNoStatusClass2, SingleEpicsPositionerClass
#run("pd_idgap")	#--> IDGapFromPVClass
#id_gap=SingleEpicsPositionerNoStatusClass2('ID_gap','SR16I-MO-SERVC-01:BLGSET','SR16I-MO-SERVC-01:CURRGAPD','SR16I-MO-SERVC-01:ALLMOVE','SR16I-MO-SERVC-01:ESTOP','mm','%.4f'); 
#id_gap.deadband=0.005
#print "   creating idgap scannable"
#idgap=IDGapFromPVClass('IDgap',5,'SR16I-MO-SERVC-01:BLGSET','SR16I-MO-SERVC-01:CURRGAPD','SR16I-MO-SERVC-01:BLGSETP','SR16I-MO-SERVC-01:ALLMOVE','SR16I-MO-SERVC-01:ESTOP','mm','%.3f')
id_gap = idgap


print "creating BLi"
import beamline_info as BLi 
# 1. works with module data energy and wavelength or provides a persistant dummy value
#    if AllBeamlineObjects.isDummySimulation() or BLobjects.isSimulation() from
#    the shelf BLI

print "   creating energy scannables to control dcm"
run("pd_dcm")
en=EnergyFromBraggPD('en',BLi) # NOT USED
#enf=EnergyFromBraggFixedoffsetPD('energy',BLi)
en=EnergyFromBraggwithHarmonicPD('en',BLi,dcmharmonic)  #dcmharmonic is a persistant number from offset shelf
enf = EnergyFromBraggFixedoffsetwithHarmonicPD('enf',BLi,dcmharmonic) # GLOBALS: bragg, perp FOR THE REAL DCM, TH F IS for fixed beam height


### Undulator
print "Setting up undulator"
run("pd_undulator")
id = Undulator2('Undulator',uharmonic,idgap,idgap_offset,en,GBHfile='/dls_sw/i16/var/U27_GBH.dat')
#u27 = Undulator('U27-I16',idgap,idgap_offset,'/dls_sw/i16/var/U27_GBH.dat')
#uenergy = EnergyFromUndulator('Undulator Energy',u27)
uenergy = EnergyFromUndulator2('Uenergy',id)
energy2 = EnergyFromIDandDCM('energy2',uenergy,enf) # could rename

def calcgap(energy=None,H=None):
	return id.calcGap(energy,H)

def ucalibrate(newenergy=None,H=None):
	'''
	Calibrate ID gap offset
	Do this after a large energy change or change of harmonic
	The nominal value is around 0.54 mm
	If you get lost then type:  pos idgap_offset 0.54 and start again
	'''
	id.calibrate(newenergy,H)

### Mono
print "Creating ChanCutMono scannable: cc/energy"
run("pd_ChannelCutMono") #--> ChanCutMonoClass
cc=ChanCutMonoClass('energy')
energy=cc
enf.fixedoffsetmode=0


energy.getPosition() ### DANGER: Required because energy is cached somewhere in here
print "... Leaving: startup_energy_related.py >>>"
