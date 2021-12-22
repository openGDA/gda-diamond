from Diamond.Peem.MagneticDichroism import MagneticDichroismDevice;

#xmd=MagneticDichroismDevice("xmd", imageDetector, energyDevice, polarisationDevice);
#xmd=MagneticDichroismDevice("xmd", dummyCamera, testMotor1, iddpol);
xmd=MagneticDichroismDevice("xmd", uv, pgmenergy, iddpol);

#xmd.xmcd(400, 500, 10, 0.5);
#xmd.xmld(400, 500, 10, 0.5);
#xmd.xmlde(400, 500, 10, 0.5);

def xmcd(startEnergy, endEnergy, numberOfImages, integrationTime):
    try:
        xmd.xmcd(startEnergy, endEnergy, numberOfImages, integrationTime);
    except :
        type, exception, traceback = sys.exc_info();
        logger.fullLog(None, "Error in xmcd", type, exception , traceback, False);        

def xmld(startEnergy, endEnergy, numberOfImages, integrationTime):
    try:
        xmd.xmld(startEnergy, endEnergy, numberOfImages, integrationTime);
    except :
        type, exception, traceback = sys.exc_info();
        logger.fullLog(None, "Error in xmld", type, exception , traceback, False);        

def xmlde(startEnergy, endEnergy, numberOfImages, integrationTime):
    try:
        xmd.xmlde(startEnergy, endEnergy, numberOfImages, integrationTime);
    except :
        type, exception, traceback = sys.exc_info();
        logger.fullLog(None, "Error in xmlde", type, exception , traceback, False);        

alias("xmcd");
alias("xmld");
alias("xmlde");
