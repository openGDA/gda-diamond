#
# Runs a single spectrum experiment collecting dark, I0, It spectra in Nexus 
# files and then writing the normalised, calibrated spectrum to an EDE format 
# ascii file.
#
# Uses new EDE scanning mechanism
#
# Richard Woolliscroft 22 July 2013
#

from gda.scan import EdeSingleExperiment
from gda.scan import ExplicitScanPositions;
from gda.scan import EdePositionType;
from uk.ac.gda.exafs.ui.data import EdeScanParameters;


class SingleScanExperiment():
    
    def __init__(stripdetector,i0_x_position,i0_y_position,i0_scantime,i0_numberscans,it_x_position,it_y_position,it_scantime = -1,it_numberscans = -1):
        
        self.stripdetector = stripdetector
        self.i0_x_position = i0_x_position
        self.i0_y_position = i0_y_position
        self.i0_scantime = i0_scantime
        self.i0_numberscans = i0_numberscans
        self.it_x_position = it_x_position
        self.it_y_position = it_y_position
        self.it_scantime = it_scantime
        self.it_numberscans = it_numberscans
        if self.it_scantime == -1:
            self.it_scantime = self.i0_scantime
            
        if self.it_numberscans == -1:
            self.it_numberscans = self.i0_numberscans

        # assumed values:
        self.xmotorobject   = sample_x
        self.ymotorobject   = sample_y
        
    def doCollection(self):
        i0scanparams = EdeScanParameters.createSingleFrameScan(self.i0_scantime,self.i0_numberscans);
        itscanparams = EdeScanParameters.createSingleFrameScan(self.it_scantime,self.it_numberscans);
        
        inBeamPosition = ExplicitScanPositions(EdePositionType.INBEAM, self.it_x_position, self.it_y_position, self.xmotorobject, self.ymotorobject);
        outBeamPosition = ExplicitScanPositions(EdePositionType.OUTBEAM,self.i0_x_position,self.i0_y_position,self.xmotorobject,self.ymotorobject);
        
        theExperiment = EdeSingleExperiment(i0scanparams, itscanparams, inBeamPosition, outBeamPosition, self.stripdetector);
        theExperiment.runExperiment()
        
        return theExperiment.getAsciiFilename()


