from gda.configuration.properties import LocalProperties
from uk.ac.gda.exafs.ui.data import EdeScanParameters, TimingGroup
from gda.scan import SimpleContinuousScan

LocalProperties.set("gda.data.scan.datawriter.dataFormat","SrsDataFile");

print "create timing groups and scan"

sp = EdeScanParameters()
group1 = TimingGroup();
group1.setLabel("group1");
group1.setNumberOfFrames(3);
group1.setTimePerScan(0.6);
group1.setTimePerFrame(3);    
#group1.setDelayBetweenFrames(5);
sp.addGroup(group1);

group2 = TimingGroup();
group2.setLabel("group2");
group2.setNumberOfFrames(6);
group2.setTimePerScan(0.1);
group2.setTimePerFrame(3);    
#group2.setPreceedingTimeDelay(10);
sp.addGroup(group2);

print "load scan into XH detector"
XHDetector.loadParameters(sp)

print "run scan"
thisscan = SimpleContinuousScan(XHDetector)
thisscan.runScan()  