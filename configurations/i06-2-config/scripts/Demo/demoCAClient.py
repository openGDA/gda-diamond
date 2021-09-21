#Simple Demo about how to use EPICS caput() and caget() method to access PVs directly from GDA

from gda.epics import CAClient

#Create the Client
epicsClient = CAClient()

#Create the PV channels and use the caput and caget method directly
print epicsClient.caget("BL06I-AL-SLITS-01:X:CENTER.RBV")
epicsClient.caput("BL06I-AL-SLITS-01:X:CENTER", -0.55)

#Clear up the channels
epicsClient.clearup();

