from gda.epics import CAClient

ca = CAClient()

basepv = pco_addetector.getAdBase().getBasePVName()
arrpv = pco_addetector.getNdArray().getBasePVName()

# configure plugin chain
camport = ca.get(basepv + "PortName_RBV")
ca.caput(arrpv + "NDArrayPort", camport)

# enable array callbacks
ca.caput(arrpv + "EnableCallbacks", "Enable")

# configure image & trigger mode
ca.caput(basepv + "ImageMode", "Continuous")
ca.caput(basepv + "TriggerMode", "Internal")

# start
ca.caput(basepv + "Acquire", 1)