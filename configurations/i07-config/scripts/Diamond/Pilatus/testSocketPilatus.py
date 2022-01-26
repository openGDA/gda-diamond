from time import sleep
import socket;

#from Diamond.Pilatus.PilatusDetector import Pilatus, PilatusOverEpics, PilatusOverSocket;
from Diamond.Pilatus.PilatusDetector import PilatusFactory;
from Diamond.Pilatus.PilatusDetectorPseudoDevice import PilatusPseudoDeviceClass;
from Diamond.Pilatus.PilatusInfo import PilatusInfo;


from Diamond.Analysis.DetectorAnalyser import DetectorAnalyserClass;
from Diamond.Analysis.DetectorAnalyserROI import DetectorAnalyserWithRectangularROIClass;
from Diamond.Analysis.Processors import MinMaxSumMeanDeviationProcessor;

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gda.analysis.io import PilatusTiffLoader



hostName = socket.gethostname();
#hostName = '172.23.243.157'
#portNumber = 2730;
portNumber = 41234;

## Step 1. Make sure the Pilatus Camserver is running or to start the Camserver Simulation: runCamServerSim.py

## Step 2. Create a Pilatus detector client from the factory and connect to the Camserver over socket
pf = PilatusFactory();
pilatus100K = pf.create('pilatus100K', PilatusInfo.PILATUS_TYPE_100K_SOCKET);
pilatus100K.setupServer(hostName, portNumber);
pilatus100K.turnOn();

##Step 3. Create a GDA pseudo device that use the pilatus detector client
pil1 = PilatusPseudoDeviceClass("pil1", "Area Detector", "pilatus100K");
pil1.setAlive(False);
#pil1.setFile("Pilatus/","p100kImage");
print "             Use pil1.setFile('path/','prefix') to set the image directory and name"
print "             Current image directory: ", pil1.getFilePath();
print "             Current image prefix: ",    pil1.getFilePrefix();


#pilatus_processors=[SumMaxPositionAndValue(), TwodGaussianPeak()];
#pil1da = DetectorAnalyserClass("pil1da", pil1, ps100k_processors, panel_name="Pilatus100K", iFileLoader=PilatusTiffLoader);
#pil1da.setAlive(False);

#For the RCP GUI
print "Usage: use pil1stats to find the key statistics values such as minium, maxium  with locations, sum, mean and standard deviation"
pil1stats = DetectorAnalyserClass("pil1stats", pil1, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil1stats.setAlive(True);

print "Usage: use pil1fit for peak fitting"
pil1fit = DetectorAnalyserClass("pil1fit", pil1, [TwodGaussianPeak()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil1fit.setAlive(True);

print "Usage: use pilroi for Region Of Interest operations"
print "For example: pil1roi.setRoi(starX, starY, width, height) to set up the ROI"
print "             pil1roi.getRoi(starX, starY, width, height) to get current ROI"
print "             pil1roi.getGuiRoi(starX, starY, width, height) to set ROI info from GUI selection"
print "             pil1roi.createMask(low, high) to mask out pixels out of low/high region"
print "             pil1roi.setAlive(True) to enable the data display on GUI panel"
print "             pil1roi.setAlive(False) to stop data update on GUI panel"
pil1roi = DetectorAnalyserWithRectangularROIClass("pil1roi", pil1, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);

pil1roi.setAlive(True);
pil1roi.setPassive(False);
#pil1roi.clearRoi();
#pil1roi.setRoi(0,0,100,100);
#pil1roi.addRoi(100, 100, 50, 50);
#pil1roi.createMask(0,5000000);
#pil1roi.applyMask(pil1roi.createMask(1000,5000));
