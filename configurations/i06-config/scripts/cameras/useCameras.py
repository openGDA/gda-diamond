# new PVs for the device involved in PEEM Refocusing work!
# camc1: BL06I-DI-PHDGN-98
# camc2: BL06I-Di-GIGE-01
# X-axis: BL06I-EA-USER-03:MTR1: 
# Y axis: BL06I-EA-USER-03:MTR2:
# Z axis: BL06I-EA-USER-03:MTR3:
# screen Z axis: BL06I-EA-USER-03:MTR4: 

from Diamond.AreaDetector.ADDetectorDevice import ADDetectorDeviceClass

print("Use camerac2 for the GIGE1 camera C2")
camerac2 = ADDetectorDeviceClass('camerac2', camc2_addetector, "Plot 2");  # @UndefinedVariable
camerac2.setFile('CamC2Image', 'camerac2');
camerac2.setStats(True);
camerac2.delay=2;

print("Use camerac1 for the Flea camera C1 on PEEM")
camerac1 = ADDetectorDeviceClass('camerac1', camc1_addetector, "Plot 1");  # @UndefinedVariable
camerac1.setFile('CamC1Image', 'camerac1');
camerac1.setStats(True);


