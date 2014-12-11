#New version of magnet control

from Diamond.PseudoDevices.SuperconductingMagnet import SuperconductingMagnetClass, ModeMagnetClass;
from Diamond.PseudoDevices.SuperconductingMagnet import CartesianMagnetClass, SphericalMagnetClass, SingleAxisMagnetClass;
from Diamond.PseudoDevices.Flipper import FlipperClass, DichroicFlipperClass
from gda.jython.commands.GeneralCommands import alias

#The root EPICS PV for the superconducting magnet
magRootPV = 'BL06J-EA-MAG-01';

print "Note: Use object name 'scm' for the Superconducting Magenet control";
scm = SuperconductingMagnetClass('scm', magRootPV);

print "Note: Use Pseudo device name 'magmode' for the Superconducting Magenet mode control";
magmode = ModeMagnetClass('magmode', 'scm');

print "Note: Use Pseudo device name 'magcartesian' for the Superconducting Magenet control in Cartesian coordinate";
magcartesian = CartesianMagnetClass('magcartesian', 'scm');

print "Note: Use Pseudo device name 'magspherical' for the Superconducting Magenet control in Spherical coordinate";
magspherical = SphericalMagnetClass('magspherical', 'scm');

print "Note: Use Pseudo device name 'magx, magy, magz, magrho, magth, magphi' for the Superconducting Magenet uniaxial control";
magx = SingleAxisMagnetClass('magx', 'scm', SingleAxisMagnetClass.X);
magy = SingleAxisMagnetClass('magy', 'scm', SingleAxisMagnetClass.Y);
magz = SingleAxisMagnetClass('magz', 'scm', SingleAxisMagnetClass.Z);
magrho = SingleAxisMagnetClass('magrho', 'scm', SingleAxisMagnetClass.RHO);
magth  = SingleAxisMagnetClass('magth',  'scm', SingleAxisMagnetClass.THETA);
magphi = SingleAxisMagnetClass('magphi', 'scm', SingleAxisMagnetClass.PHI);
magdelay=scm.delay
magtolerance=scm.tolerance
magdelay(0.1)    # Tests suggest that with magtolerance set up, only a very short delay is needed.
magtolerance(6.) # Given that the magnet goes +-6T mag moves will always return the demand position after magdelay.

print "Note: Use object name 'hyst2' for the hysteresis measurement with flipping magnet";
print "Usage: scan hyst2 -1 1 0.1";
print "To change magnet device : hyst2.setMagnet(magnetName='magz')";
print "To change energy setting: hyst2.setEnergy(energyName='rpenergy', startEnergy=700, endEnergy=750)"
print "To change detector:       hyst2.setCounters(counterName1='ca61sr', counterName2='ca62sr', counterName3='ca63sr', integrationTime=1)"


hyst2 = FlipperClass('hyst2', 'magz', 'denergy', 700, 750, 'ca61sr', 'ca62sr', 'ca63sr', 1);
hyst2.setMagnet(magnetName='magz');
hyst2.setEnergy(energyName='denergy', startEnergy=700, endEnergy=750);
hyst2.setCounters(counterName1='ca61sr', counterName2='ca62sr', counterName3='ca63sr', integrationTime=1);


print "Note: Use object name 'dhyst' for the hysteresis measurement with dichroitic flipping magnet";
dhyst = DichroicFlipperClass('dhyst', 'magz', 'denergy', 770, 777, 'iddpol', 'PosCirc', 'NegCirc' , 'ca61sr', 'ca62sr', 'ca63sr', 1);
#dhyst.setMagnet('magnet.magz');
#dhyst.setEnergy('denergy', startEnergy=700, endEnergy=750);
#dhyst.setCounters(counterName1='ca61sr', counterName2='ca62sr', counterName3='ca63sr', integrationTime=1);
#dhyst.setPolarisation('iddpol', pol1='PosCirc', pol2='NegCirc');


#dhyst = DichroicFlipperClass('dhyst2', 'dummyMotor1', 'dummyMotor2', 700, 750, 'dummyPol', 'PosCirc', 'NegCirc' , 'ca61sr', 'ca62sr', 'ca63sr', 1);



