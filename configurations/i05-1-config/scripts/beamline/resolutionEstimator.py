from uk.ac.gda.arpes.calculator import IResolutionCalculatorConfiguration

def estimateResolution():
    """ Script to calculate APPROXIMATE beamline and analyser resolutions
    
    Usage: estimateResolution()  - print out all resolutions 
    """
    
    try:
        nanoExitSlit        = exit_slit.getPosition()
        nanoPhotonEnergy    = pgm_energy.getPosition()
        nanoPassEnergy      = analyser.getPassEnergy()
        Grating             = pgm_linedensity.getPosition()
        calculatorConfig    = Finder.findSingleton(IResolutionCalculatorConfiguration)
    except Exception as e:
        print e
        print " Pulling PVs for resolution estimation failed"
        return
    finally:
        print "Exit slit ", nanoExitSlit, " mm"
        print "Photon energy ", nanoPhotonEnergy, " eV"
        print "Pass Energy ", nanoPassEnergy, " eV"
        print "Grating ", Grating, " l/mm"
        print "calculatorConfig ", calculatorConfig
        
    #Check values are reasonable
    if (nanoExitSlit<-10.0) or (nanoExitSlit>10.0) or (not isinstance(nanoExitSlit,float)):
        print " Exit slit value is not in [-1000 1000] interval or not float"
        return
    
    if (nanoPhotonEnergy<=0.0) or (nanoPhotonEnergy>1000) or (not isinstance(nanoPhotonEnergy,float)):
        print " Photon Energy value is not in [0 1000] interval or not float"
        return
    
    # beamline resolution
    beamlineResolutionParameters = calculatorConfig.getParametersFromFile(calculatorConfig.getBlResolutionParamsFilePath());
    blResolvingPower = calculatorConfig.calculateResolvingPower(nanoExitSlit*1000, Grating, beamlineResolutionParameters);
    nanoBeamlineResolution = calculatorConfig.calculateBeamlineResolution(nanoPhotonEnergy, blResolvingPower);
    print '  NANO BEAMLINE resolution is approx.  %.2f meV' % nanoBeamlineResolution
    
    # analyser resolution
    nanoAnalyserResolution=calculatorConfig.calculateAnalyserResolution(nanoPassEnergy, 0.0);
    print "  NANO ANALYSER resolution is approx. %.2f meV " % nanoAnalyserResolution
    
    # combined
    nanoResolutionTotal=calculatorConfig.calculateTotalResolution(nanoAnalyserResolution,nanoBeamlineResolution);
    print "  NANO COMBINED resolution is approx. %.2f meV" % nanoResolutionTotal
    
