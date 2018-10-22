#! /usr/bin/env jython

import socket;
import sys;
#run this script from the Pilatus script directory. ie: gdaBeamlineConfigDir/scripts/Diamond/Pilatus/
sys.path.append("./../../../scripts");

from PilatusInfo import PilatusInfo;
from PilatusCamserverSim import CamServerSimClass;

#sys.path.append("/home/xr56/Dev/gdaDev/gda-config-local/localBase/scripts/Diamond/Pilatus");

#execfile("/home/xr56/Dev/gdaDev/gda-config-local/localBase/scripts/Diamond/Pilatus/PilatusCamserverSim.py");
#execfile("./PilatusCamserverSim.py");



hostName = socket.gethostname();
#hostName = '172.23.243.157'
portNumber = 41234;


camserver=CamServerSimClass(hostName, portNumber, PilatusInfo.PILATUS_MODEL_100K);

camserver.setout();

