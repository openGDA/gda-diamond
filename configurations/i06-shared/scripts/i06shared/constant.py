#Define some constant used:
print "-"*100
print "Setup constants in Jython namespace for beamline"
#For valve control
Close=CLOSE=cls='Close';
Open=OPEN=opn='Open';
Reset=RESET='Reset';

#For ID polarisation settings
#commented out as these are defined in mode_polarisation_energy_instances.py now for the new system.
# lh=LH='Horizontal'; #linear horizontal polarization"
# lv=LV='Vertical';   #linear vertical polarization"
# pc=PC='PosCirc';    #positive circular polarization"
# nc=NC='NegCirc';    #negative circular polarization"
# la=LA='LA';         #linear arbitrary/angle"

vertical=ver='Vertical'
horizontal=hor='Horizontal'

#For ID harmonic settings
#The Harmonic value should be: "First" (1), "Third" (3) or "Fifth" (5)
First=FIRST="First";
Third=THIRD="Third";
Fifth=FIFTH="Fifth";

#For the Superconducting Magnet mode:
UNIAXIAL_X, UNIAXIAL_Y, UNIAXIAL_Z, SPHERICAL, PLANAR_XZ, QUADRANT_XY, CUBIC = range(7);
uniaxialx, uniaxialy, uniaxialz, spherical, planar_xz, quadrant_xy, cubic = range(7);

#For fast energy scan (zac scan) ID mode
fixid, cvid, slaveid = range(3);
