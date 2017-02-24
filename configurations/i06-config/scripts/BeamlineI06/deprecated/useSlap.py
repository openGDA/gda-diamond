from Diamond.Slap.SlapWebServiceClient import SlapClass, JavaSlapClass, LaserPhaseDeviceClass, LaserDelayDeviceClass, LaserLockingStateDeviceClass


#I06 Sony Laptop
#LabViewWebServiceURL = 'http://diamrl5098.diamond.ac.uk:8080/SlapWebServices'

#I06 rack mounted Windows server i06-ws011
LabViewWebServiceURL = 'http://i06-ws011.diamond.ac.uk:8080/SlapWebServices'

#The value readback service for testing: http://diamrl5098.diamond.ac.uk:8080/SlapWebServices/ReadOnlyService

#laser=SlapClass(LabViewWebServiceURL);
laser=JavaSlapClass(LabViewWebServiceURL);
#laser.setHost("172.23.106.76");
laser.setOffset(20000);
#laser.setMaxStep(100):


laserphase=LaserPhaseDeviceClass("laserphase", laser)
laserdelay=LaserDelayDeviceClass("laserdelay", laser)
laserlocking=LaserLockingStateDeviceClass("laserlocking", laser)

#laserURL='http://diamrl5098.diamond.ac.uk:8080/SlapWebServices/ReadOnlyService'
