

from Diamond.Pilatus.PilatusDetector import Pilatus, PilatusOverEpics, PilatusOverSocket, PilatusFactory;
from Diamond.Pilatus.PilatusDetectorPseudoDevice import PilatusPseudoDeviceClass;
from Diamond.Pilatus.PilatusInfo import PilatusInfo;

from Diamond.Analysis.DetectorAnalyser import DetectorAnalyserClass, DetectorWithROIClass;
from Diamond.Analysis.DummyProcessor import DummyTwodPorcessor;

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gda.analysis.io import PilatusLoader, PilatusTiffLoader

pilatusHostName = 'i07-pilatus1.diamond.ac.uk';
pilatusPortNumber = 41234;


##Create a Pilatus detector client from the factory and connect to the EPICS, which handles the camserver operation
pf = PilatusFactory();
p1e = pf.create('p1e', PilatusInfo.PILATUS_TYPE_100K_EPICS);
pvRoot = 'BL07I-EA-PILAT-01:';
p1e.setup(pvRoot);

##Step 3. Create a GDA pseudo device that use the pilatus detector client
ps100k = PilatusPseudoDeviceClass('ps100k', 'p1e');
ps100k.setFile('pilatus100k/im4/','test');
ps100k.setAlive(False);


ps100k_processors=[SumMaxPositionAndValue(), TwodGaussianPeak()];
pda = DetectorAnalyserClass('pda', ps100k, ps100k_processors, panel_name='Pilatus', iFileLoader=PilatusTiffLoader);
pda.setAlive(False);

pdamax = DetectorAnalyserClass('pdamax', ps100k, [SumMaxPositionAndValue()], panel_name='Pilatus', iFileLoader=PilatusTiffLoader);
pdamax.setAlive(False);

pdapeak = DetectorAnalyserClass('pdapeak', ps100k, [TwodGaussianPeak()], panel_name='Pilatus', iFileLoader=PilatusTiffLoader);
pdapeak.setAlive(False);

#pdaRoi = DetectorWithROIClass('pdaRoi', ps100k, [DummyTwodPorcessor()], panel_name='Pilatus', iFileLoader=PilatusTiffLoader);
pdaroi = DetectorWithROIClass('pdaroi', ps100k, [SumMaxPositionAndValue()], panel_name='Pilatus', iFileLoader=PilatusTiffLoader);
pdaroi.setAlive(True);
#pdaRoi.setRoi(0,0,100,100);
pdaroi.setRoi(240, 100, 100, 50);

