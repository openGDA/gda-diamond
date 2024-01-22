from uk.ac.gda.arpes.calculator import IResolutionCalculatorConfiguration

def estimateResolution(AnalyserSlit=200):
    """ Script to calculate APPROXIMATE beamline and analyser resolutions
    
    estimateResolution((optional)AnalyserSlit)  - print out all resolutions 
    """
    # pull relevant PVs
    try:
        HRExitSlit      = exit_slit.getPosition()
        HRPhotonEnergy  = pgm_energy.getPosition()
        HRPassEnergy    = analyser.getPassEnergy()
        Grating         = pgm_linedensity.getPosition()
        calculatorConfig =  Finder.findSingleton(IResolutionCalculatorConfiguration)
    except Exception as e:
        print e
        print " Pulling PVs for resolution estimation failed"
        return 
    finally:
        print " Exit Slit value: ", HRExitSlit, " mm"
        print " Photon Energy value: ", HRPhotonEnergy, " eV"
        print "Grating ", Grating, " l/mm"
        print "Pass Energy ", HRPassEnergy, " eV"
        print "Analyser slit ", AnalyserSlit, " micron"
        print "CalculatorConfig ", calculatorConfig
        
    #Check values are reasonable
    if (HRExitSlit<-10.0) or (HRExitSlit>10) or (not isinstance(HRExitSlit,float)):
        print " Exit slit value is not in [-10 10] interval or not float"
        return
    
    if (HRPhotonEnergy<=0.0) or (HRPhotonEnergy>1000) or (not isinstance(HRPhotonEnergy,float)):
        print " Photon Energy value is not in [0 1000] interval or not float"
        return
    
    beamlineResolutionParameters = calculatorConfig.getParametersFromFile(calculatorConfig.getBlResolutionParamsFilePath());
    
    blResolvingPower = calculatorConfig.calculateResolvingPower(HRExitSlit*1000, Grating, beamlineResolutionParameters);
    HRBeamlineResolution = calculatorConfig.calculateBeamlineResolution(HRPhotonEnergy, blResolvingPower);
    print "  HR BEAMLINE resolution is approx.  %.2f meV" % HRBeamlineResolution
    
    # analyser resolution
    HRAnalyserResolution = calculatorConfig.calculateAnalyserResolution(HRPassEnergy, AnalyserSlit); #meV
    print "  HR ANALYSER resolution is approx. %.2f meV " % HRAnalyserResolution
    
    # combined
    HRResolutionTotal=calculatorConfig.calculateTotalResolution(HRBeamlineResolution, HRAnalyserResolution);
    print "  HR COMBINED resolution is approx. %.2f meV" % HRResolutionTotal
    