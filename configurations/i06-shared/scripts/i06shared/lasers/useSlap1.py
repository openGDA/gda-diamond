from Diamond.Slap.SlapWebServiceClient import SlapClass, JavaSlapClass, LaserPhaseDeviceClass, LaserDelayDeviceClass, LaserLockingStateDeviceClass

#I06 rack mounted Windows server i06-ws011
LabViewWebServiceURL = 'http://i06-ws020.diamond.ac.uk:8080/SlapWebServices'

#laser=SlapClass(LabViewWebServiceURL);
laser1=JavaSlapClass(LabViewWebServiceURL);
laser1.phase2delay_ce=[-0.0058976070255, 1.31253880142145E-4, -2.26326432895618E-8, 3.53663784002266E-12, -2.63010486113614E-16, 1.04042843159956E-20, -2.16666613588553E-25, 2.26190976227321E-30, -9.58629545249244E-36, 2.90678349766489E-42]
laser1.delay2phase_ce=[-88.36914666723533, 12855.32380237554, 824.10592216745135, -1946.0535305088042, 664.20982780807435, -115.31870988361487, 11.61543948306145, -0.68333494362544, 0.02173576685147, -2.87621826209067E-4]
laser1.setHost("i06-ws020.diamond.ac.uk");
laser1.setOffset(20000);
#laser1.setMaxStep(100):


laser1phase=LaserPhaseDeviceClass("laser1phase", laser1)
laser1delay=LaserDelayDeviceClass("laser1delay", laser1)
laser1locking=LaserLockingStateDeviceClass("laser1locking", laser1)

#The value readback service for testing: http://i06-ws020.diamond.ac.uk:8080/SlapWebServices/ReadOnlyService
