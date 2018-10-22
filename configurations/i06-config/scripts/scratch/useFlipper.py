#Usage:
from Diamond.PseudoDevices.FlippingDevice import FlippingDeviceClass, Algorism01Processor;

scannerName = "testMotor1";
flipperName = "testMotor2";
detectorNames = ["dummyCounter", "dummyCounter1"]
integrationTime = 0.5
f1 = FlippingDeviceClass('f1', scannerName, flipperName, [-20, 20], detectorNames, integrationTime, [Algorism01Processor()]);

f2 = FlippingDeviceClass('f2', scannerName, flipperName, [-20, 20], detectorNames, integrationTime, [Algorism01Processor()]);
f2.setScanner("testMotor2");
f2.setFlipper("testMotor1", [-5,0,1.2,3.3,5.1, 5]);
f2.setDetectors(['dummyCounter','dummyCounter1', 'dummyCounter2'], integrationTime=0.1);

#scan f1 0 10 0.5


