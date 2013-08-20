
from Diamond.PseudoDevices.PEEMModule import PEEMModuleClass;

#Set up the PEEM
print "Note: Use object name 'pm' for LEEM2000 control"

pm = finder.find("leem");

print "      Use object name 'ca71' for PEEM drain current monitoring";
ca71 = PEEMModuleClass("ca71", 42);

print "      Use object name 'startVoltage' for Start Voltage control";
startVoltage = PEEMModuleClass("startVoltage", 38);

print "      Use object name 'objective' for Objective control";
objective = PEEMModuleClass("objective", 11);
