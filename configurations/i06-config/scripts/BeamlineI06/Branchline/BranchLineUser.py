#    BranchLineUser.py
#
#    For user specific initialisation code on I06 Branch Line.

print "--->>>Start initalization of user specific code."

userScriptsList=["/dls_sw/i06-1/scripts/hello.py", 
                 "/dls_sw/i06-1/scripts/idivio.py", 
                 "/dls_sw/i06-1/scripts/instruments/light_controller/light_controller.py",
#                 "/dls_sw/i06-1/scripts/branchline/ID_control.py"
#                 "/dls_sw/i06-1/scripts/branchline/xenergy_Class.py",
                 "/dls_sw/i06/scripts/beamline/XEnergy/xenergy.py",
                 
#                Rasor support
#                "/dls_sw/i06-1/scripts/rasor2010/rasormotors_withphi.py",
#                "/dls_sw/i06-1/scripts/rasor2009/Lakeshore_340_3.py",
#                "/dls_sw/i06-1/scripts/rasor2010/startdiff.py",

#                POMS user support
#                "/dls_sw/i06-1/scripts/POMS/PomsSocketDevice_GDA74.py",
#                "/dls_sw/i06-1/scripts/polarimeter/detector.py",
#                "/dls_sw/i06-1/scripts/polarimeter/scripts_pol/idio_pol.py",
#                "/dls_sw/i06-1/scripts/polarimeter/scripts_pol/pola.py",
#                "/dls_sw/i06-1/scripts/polarimeter/scripts_pol/rotationTemperature.py",
#                "/dls_sw/i06-1/scripts/polarimeter/scripts_pol/hexapodAxises4.py",

#                Enable the Classix Camera and Filter Control.
#                gdaScriptDir + "BeamlineI06/Users/ClassixSystem/useClassix.py",
                
#                For the diffcalc
#                "/dls_sw/i06-1/software/gda/config/scripts/BeamlineI06/Users/diffcalc_i07_4circle.py",

                ]

for userScript in userScriptsList:
    print "-------------------------------------------------------------------"
    print "Execution of user script: " + userScript + ">>>>>"
    try:
        execfile(userScript);
    except:
        exceptionType, exception, traceback=sys.exc_info();
        print "XXXXXXXXXX:  User script: " + userScript + " Error"
        logger.dump("---> ", exceptionType, exception, traceback)

print "--->>>Initalization of user specific code done."
