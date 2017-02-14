import sys

from gdascripts.messages import handle_messages
#localStation.py
#For beamline specific initialisation code.
print "===================================================================";
print "Performing I06 PEEM line specific initialisation code (localStation_i06.py).";
print


# Get the locatation of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.jython.gdaScriptDir") + "/";

# Get the location of the USERS script directory
userScriptDir = LocalProperties.get("gda.jython.userScriptDir") + "/";

#Set up the basic plotting objects
print "-------------------------------------------------------------------"
print "Note: Use image.open('/full/file/name') to plot image on the 'PEEM Image' panel"
#execfile(gdaScriptDir + "BeamlineI06/useImageUtility.py");

# Setup Leem2000 before calling usePeem as leem_fov is needed by it.
try:
    import LEEM2000_tcp
    leem2000=LEEM2000_tcp.leem2000()
    leem_stv=LEEM2000_tcp.leem_scannable("leem_stv","Start voltage", '%.2f' , leem2000)
    leem_obj=LEEM2000_tcp.leem_scannable("leem_obj","Objective", '%.2f' , leem2000)
    leem_objStigmA=LEEM2000_tcp.leem_scannable("leem_objStigmA","Obj.stigm. a", '%.2f' , leem2000)
    leem_objStigmB=LEEM2000_tcp.leem_scannable("leem_objStigmB","Obj.stigm. b", '%.2f' , leem2000)
    leem_fov=LEEM2000_tcp.leem_readonly("leem_fov", "prl", leem2000)
    leem_p2alignx = LEEM2000_tcp.leem_scannable("leem_p2alignx","P2 align.x", '%.8f', leem2000)
    #leem_temp = LEEM2000_tcp.leem_scannable("leem_p2alignx","39", '%.2f', leem2000)
except:
    exceptionType, exception, traceback=sys.exc_info();
    handle_messages.log(None, "Error connecting to LEEM2000 ", exceptionType, exception, traceback, False)

#Setup the PEEM and the UView Camera software
try:
    print "-------------------------------------------------------------------"
    print "Set up the PEEM and UView"
#    execfile(gdaScriptDir + "BeamlineI06/Deprecated/useLeem.py");
#    execfile(gdaScriptDir + "BeamlineI06//Deprecated/useUView.py");

    execfile(gdaScriptDir + "BeamlineI06/usePEEM.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    logger.dump("---> ", exceptionType, exception, traceback)


#try:
#    print "-------------------------------------------------------------------"
#    print "Enable the X-ray Magnetic Dichroism Analysis "
##    execfile(gdaScriptDir + "scisoft/peem_analysis.py");
#    execfile(gdaScriptDir + "BeamlineI06/useMagneticDichroism.py");
#except:
#    exceptionType, exception, traceback=sys.exc_info();
#    print "XXXXXXXXXX:  Magnetic Dichroism Analysis Setting Up Error "
#    logger.dump("---> ", exceptionType, exception, traceback)

try:
    #Enable the laser delay stage functions"
    #print "-------------------------------------------------------------------"
    #print "Enable the laser delay stage functions"
    #execfile(gdaScriptDir + "laserDelayStage.py");
    
    
    #Enable Exit Slits S4 Gap Control s4ygap";
    #print "-------------------------------------------------------------------"
    print "Enable Slits S4 Gap Control s4ygap"
    execfile(gdaScriptDir + "BeamlineI06/useS4.py");
    
    print "-------------------------------------------------------------------"
    #print "Change the default output format to meet the PEEM line requirements"
    execfile(gdaScriptDir + "BeamlineI06/setOutputFormat_i06.py");
    
    #Group the hexapod legs into list
    m1legs = [m1leg1, m1leg2, m1leg3, m1leg4, m1leg5, m1leg6];
    m6legs = [m6leg1, m6leg2, m6leg3, m6leg4, m6leg5, m6leg6];
    m3legs = [m3leg1, m3leg2, m3leg3, m3leg4, m3leg5, m3leg6];

    peemList = [psx, psy]; fileHeader.add(peemList);
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  Errors when running the localstation_i06.py"
    logger.dump("---> ", exceptionType, exception, traceback)

try:
    print "Enable KB Mirrors"
    execfile(gdaScriptDir + "BeamlineI06/KBMirrors.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  Errors when running the BeamlineI06/KBMirrors.py from localstation_i06.py"
    logger.dump("---> ", exceptionType, exception, traceback)


#Setup the diagnostic cameras
try:
    print "-------------------------------------------------------------------"
    print "Set up the diagnostic cameras"
    execfile(gdaScriptDir + "BeamlineI06/useCameras.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    logger.dump("---> ", exceptionType, exception, traceback)


try:
    print "Enable the XEnergy"
    execfile(gdaScriptDir + "BeamlineI06/Users/XEnergy/xenergy.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  Errors when running the BeamlineI06/XEnergy/xenergy.py from localstation_i06.py"
    logger.dump("---> ", exceptionType, exception, traceback)

try:
    print "Enabling the Laser..."
    execfile(gdaScriptDir + "BeamlineI06/useSlap.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  Errors when running the BeamlineI06/useSlap.py from localstation_i06.py"
    logger.dump("---> ", exceptionType, exception, traceback)
