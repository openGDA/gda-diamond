
#cvscan d4dx -100 -50 50 1

scannableMotor, startPosition, stopPosition,scanTime, pointTime = d4dx, -100, -50, 50, 1;

#fastController = FastScanControlClass("fastController", scannableMotor);
fastController = EpicsPositionComparationDeviceClass("fastController", scannableMotor, pcPV);
fastData = EpicsMCADataDeviceClass("fastData", mcaPV, numberOfMCA);
fastMotion = FastMotionDeviceClass("fastMotion", fastController, fastData);

#fastController.setAcceleration(0.2);
#fastController.setMotorSpeed(6);
fastController.setAcceleration(1);
fastController.setMotorSpeed(10);

#    fastController.setDof(dofName);
fastController.setScanRange(startPosition, stopPosition);
fastController.setTime(scanTime, pointTime);

fastData.setTime(scanTime+2.0*pointTime, pointTime);
numPoint = fastController.getNumberOfPoint();

fastController.setVelocity(velocity=None);
positions1=fastController.getEstimatedPositions();

step=fastController.getStep();

pscan([fastMotion,0,1,numPoint,fastData,0,1]);
positions2=fastController.getRealPositions();
