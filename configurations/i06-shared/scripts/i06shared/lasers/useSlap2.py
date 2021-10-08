from Diamond.Slap.SlapWebServiceClient import SlapClass, JavaSlapClass, LaserPhaseDeviceClass, LaserDelayDeviceClass, LaserLockingStateDeviceClass

#I06 rack mounted Windows server i06-ws014
LabViewWebService2URL = 'http://i06-ws021.diamond.ac.uk:8080/SlapWebServices'

#laser2=SlapClass(LabViewWebServiceURL);
laser2=JavaSlapClass(LabViewWebService2URL);
laser2.phase2delay_ce=[-23.9209961982287, 0.142095153813483, -2.32220343219571E-05, 3.20115386459306E-09, -2.14561959061541E-13, 7.62576731446377E-18, 1.35627681022786E-22, 9.97611012094939E-28, 4.20630921302906E-34, -2.84482027189109E-38]
laser2.delay2phase_ce=[250.936271279245, 13.6034842059384, 0.000656983157377759, -2.08799828953862E-06, 7.56552965866636E-10, -1.38088907300248E-13, 1.45660372818405E-17, -8.96012702104993E-22, 2.98195847300446E-26, -4.14229055816086E-31]
laser2.setHost("i06-ws021.diamond.ac.uk");
laser2.setOffset(20000);
#laser2.setMaxStep(100):


laser2phase=LaserPhaseDeviceClass("laser2phase", laser2)
laser2delay=LaserDelayDeviceClass("laser2delay", laser2)
laser2locking=LaserLockingStateDeviceClass("laser2locking", laser2)

#To Test, open a browser from any beamline workstation, type the following address in LOcation field.
#laser2URL='http://i06-ws021.diamond.ac.uk:8080/SlapWebServices/ReadOnlyService'
