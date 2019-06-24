from Diamond.PseudoDevices.EpicsMotors import EpicsCallbackMotorClass

print "Polarisation analyser 2theta rotation motor"
pv="ME01D-MO-POLAN-01:TWOTHETA"
ttp = EpicsCallbackMotorClass('ttp',pv, '%.4f');


print "Polarisation analyser theta rotation motor";
pv="ME01D-MO-POLAN-01:THETA"
thp = EpicsCallbackMotorClass('thp',pv, '%.4f');


print "Polarisation analyser y translation motor"
pv="ME01D-MO-POLAN-01:Y"
py = EpicsCallbackMotorClass('py',pv, '%.4f');

print "Polarisation analyser z translation motor"
pv="ME01D-MO-POLAN-01:Z"
pz = EpicsCallbackMotorClass('pz',pv, '%.4f');

print "Polarisation analyser eta rotation motor"
pv="ME01D-MO-POLAN-01:ETA"
eta = EpicsCallbackMotorClass('eta',pv, '%.4f');

print "Upstream detector aperture translation motor"
pv="ME01D-MO-APTR-01:TRANS"
dsu = EpicsCallbackMotorClass('dsu',pv, '%.4f');
#	
print "Downstream detector aperture translation motor"
pv="ME01D-MO-APTR-02:TRANS"
dsd = EpicsCallbackMotorClass('dsd',pv, '%.4f');

print "Diffractometer 2theta rotation motor" 
pv="ME01D-MO-DIFF-01:TWOTHETA"
tth = EpicsCallbackMotorClass('tth',pv, '%.4f');
#
print "Diffractometer theta rotation motor" 
pv="ME01D-MO-DIFF-01:THETA" 
th = EpicsCallbackMotorClass('th',pv, '%.4f');

print "Diffractometer chi rotation motor" 
pv="ME01D-MO-DIFF-01:CHI" 
chi = EpicsCallbackMotorClass('chi',pv, '%.4f');

print "Diffractometer chamber alpha rotation motor" 
pv="ME01D-MO-DIFF-01:ALPHA" 
alpha = EpicsCallbackMotorClass('alpha',pv, '%.4f');

print "Diffractometer chamber x translation motor" 
pv="ME01D-MO-DIFF-01:X" 
difx = EpicsCallbackMotorClass('difx',pv, '%.4f');

print "Front/upstream table leg motor" 
pv="ME01D-MO-TABLE-01:LEG1" 
lgf = EpicsCallbackMotorClass('lgf',pv, '%.4f');

print "Middle table leg motor" 
pv="ME01D-MO-TABLE-01:LEG2" 
lgm = EpicsCallbackMotorClass('lgm',pv, '%.4f');

print "Back/downstream table leg motor" 
pv="ME01D-MO-TABLE-01:LEG3" 
lgb = EpicsCallbackMotorClass('lgb',pv, '%.4f');

print "Cryostat x translation motor"
pv="ME01D-MO-CRYO-01:X" 
sx = EpicsCallbackMotorClass('sx',pv, '%.4f');

print "Cryostat y translation motor" 
pv="ME01D-MO-CRYO-01:Y" 
sy = EpicsCallbackMotorClass('sy',pv, '%.4f');

print "Cryostat z translation motor" 
pv="ME01D-MO-CRYO-01:Z" 
sz = EpicsCallbackMotorClass('sz',pv, '%.4f');

print "Table height or y translation compound motor" 
pv="ME01D-MO-TABLE-01:Y" 
tabley= EpicsCallbackMotorClass('tabley',pv, '%.4f');

print "Table pitch compound motor" 
pv="ME01D-MO-TABLE-01:PITCH"
tablep = EpicsCallbackMotorClass('tablep',pv, '%.4f');

print "Table roll compound motor" 
pv="ME01D-MO-TABLE-01:ROLL"
tabler = EpicsCallbackMotorClass('tabler',pv, '%.4f');

#print "Diffractometer phi rotation motor" 
#pv="ME01D-MO-DIFF-01:PHI"
#phi = EpicsCallbackMotorClass('phi',pv, '%.4f');


