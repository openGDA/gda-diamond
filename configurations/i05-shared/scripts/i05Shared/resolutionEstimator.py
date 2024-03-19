from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from uk.ac.gda.arpes.calculator import IResolutionCalculatorConfiguration #@UnresolvedImport

def estimateResolution(*args):
    """ Script to calculate APPROXIMATE beamline and analyser resolutions

    Usage: estimateResolution()  - print out all resolutions
    """
    beamline = LocalProperties.get("gda.beamline.name")
    # pull relevant PVs
    try:
        exit_slit       = Finder.find("exit_slit")
        pgm_energy      = Finder.find("pgm_energy")
        analyser        = Finder.find("analyser")
        pgm_linedensity = Finder.find("pgm_linedensity")

        ExitSlit      = exit_slit.getPosition()
        PhotonEnergy  = pgm_energy.getPosition()
        PassEnergy    = analyser.getPassEnergy()
        Grating         = pgm_linedensity.getPosition()
        calculatorConfig =  Finder.findSingleton(IResolutionCalculatorConfiguration)

        if (len(args) == 0):
            AnalyserSlit = analyser.getEntranceSlitInformationProvider().getCurrentSlit().getSize()*1000
        else:
            AnalyserSlit = args[0]
    except Exception as e:
        print e
        print " Pulling PVs for resolution estimation failed"
        return
    finally:
        print "Exit slit:                   ", ExitSlit, " mm"
        print "Photon energy:               ", PhotonEnergy, " eV"
        print "Pass Energy:                 ", PassEnergy, " eV"
        print "Grating:                     ", Grating, " l/mm"
        print "Analyser slit:               ", AnalyserSlit, " micron"
        print "calculatorConfig file path:  ", calculatorConfig.getBlResolutionParamsFilePath()

    #Check values are reasonable
    if (ExitSlit<-10.0) or (ExitSlit>10) or (not isinstance(ExitSlit,float)):
        print " Exit slit value is not in [-10 10] interval or not float"
        return

    if (PhotonEnergy<=0.0) or (PhotonEnergy>1000) or (not isinstance(PhotonEnergy,float)):
        print " Photon Energy value is not in [0 1000] interval or not float"
        return
    print "="*20

    beamlineResolutionParameters = calculatorConfig.getParametersFromFile(calculatorConfig.getBlResolutionParamsFilePath());

    blResolvingPower = calculatorConfig.calculateResolvingPower(ExitSlit*1000, Grating, beamlineResolutionParameters);
    BeamlineResolution = calculatorConfig.calculateBeamlineResolution(PhotonEnergy, blResolvingPower);
    print "BEAMLINE resolution is approx. %.2f meV" % BeamlineResolution

    # analyser resolution
    if (beamline == "i05"):
        AnalyserResolution = calculatorConfig.calculateAnalyserResolution(PassEnergy, AnalyserSlit); #meV
    elif (beamline == "i05-1"):
        AnalyserResolution = calculatorConfig.calculateAnalyserResolution(PassEnergy, 0.0); #meV
    print "ANALYSER resolution is approx. %.2f meV " % AnalyserResolution

    # combined
    ResolutionTotal=calculatorConfig.calculateTotalResolution(BeamlineResolution, AnalyserResolution);
    print "COMBINED resolution is approx. %.2f meV" % ResolutionTotal
    print "="*20