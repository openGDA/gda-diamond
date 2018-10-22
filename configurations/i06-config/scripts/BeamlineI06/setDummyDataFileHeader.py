
from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass

dummyHeader = MetadataHeaderDeviceClass("dummyHeader");
dummyHeader.add([testMotor1, testMotor2])
add_default([dummyHeader]);

dummyHeader.setScanLogger(i06);


