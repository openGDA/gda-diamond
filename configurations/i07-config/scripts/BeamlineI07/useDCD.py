
from Diamond.PseudoDevices.ReflectivityDevices import DoubleCrystalDeflectorClass, DoubleCrystalDeflectorMonitorClass, MomentumTransferDeviceClass, ThetaXClass;
from gda.device.scannable import DummyScannable

#Example:
motorWavelength, motorTheta, motorOmega, motorGamma = dcm1lambda, diff1vdelta, dcdomega, diff1vgamma;

#DCD device:
dcdxrot_dummy = DummyScannable('dcdxrot_dummy')
dcdtheta=DoubleCrystalDeflectorClass("dcdtheta", motorWavelength, motorTheta, motorOmega, motorGamma, [diff1vdelta, diff1vgamma]);
sdcdtheta=DoubleCrystalDeflectorClass("sdcdtheta", motorWavelength, motorTheta, motorOmega, motorGamma, [diff1vdelta, diff1vgamma], [dcdxrot_dummy])
#dcdtheta.setLatticePlaneSpaces(3.1355e-10, 1.9201e-10);
dcdtheta.setLatticePlaneSpaces(3.74065e-10, 2.29067e-10);
dcdMonitor=DoubleCrystalDeflectorMonitorClass("dcdMonitor", dcdtheta);

dcdtheta_=DoubleCrystalDeflectorClass("dcdtheta_", motorWavelength, dummyTheta, motorOmega, dummyGamma, None);
#dcdtheta.setLatticePlaneSpaces(3.1355e-10, 1.9201e-10);
dcdtheta_.setLatticePlaneSpaces(3.74065e-10, 2.29067e-10);
#dcdMonitor_=DoubleCrystalDeflectorMonitorClass("dcdMonitor_", dcdtheta_);


#motorWavelength, motorTheta, motorOmega, motorGamma = testMotor1, testMotor4, testMotor5, testMotor6;
testMotor1.moveTo(1.24) #For the energy around 1 keV
dummydcdtheta=DoubleCrystalDeflectorClass("dummydcdtheta", testMotor1, testMotor4, testMotor5, testMotor6, [diff1vomega, diff1vdelta], [dcdxrot_dummy]);
#dummydcdtheta.setLatticePlaneSpaces(3.1355e-10, 1.9201e-10);
dummydcdtheta.setLatticePlaneSpaces(3.74065e-10, 2.29067e-10);


#Reciprocal Space devices in vertical mode:
qv=MomentumTransferDeviceClass("qv", dcm1lambda, diff1vomega, diff1vdelta, [diff1vomega, diff1vdelta]);

#Reciprocal Space devices in horizental mode:
qh=MomentumTransferDeviceClass("qh", dcm1lambda, diff1homega, diff1vgamma, [diff1homega, diff1vgamma]);

#Reciprocal Space devices in DCD mode:
qdcd=MomentumTransferDeviceClass("qdcd", dcm1lambda, dcdtheta, None, [diff1vdelta, diff1vgamma, dcdomega, dcdMonitor]);
qsdcd=MomentumTransferDeviceClass("qsdcd", dcm1lambda, sdcdtheta, None, [diff1vdelta, diff1vgamma, dcdomega, dcdMonitor])
qdcd_=MomentumTransferDeviceClass("qdcd_", dcm1lambda, dcdtheta_, None, [dcdomega, dcdMonitor]);


thetax=ThetaXClass("thetax", dcdtheta, motorGamma, None);
qx=MomentumTransferDeviceClass("qx", dcm1lambda, thetax, None, [diff1vdelta, diff1vgamma]);
