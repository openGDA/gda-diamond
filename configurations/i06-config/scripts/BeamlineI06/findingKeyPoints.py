from Diamond.PseudoDevices.PointFindingInFile import PointFindingInFileClass
#from BeamlineI06.PseudoDevices.EnergyPointFindingInFile import EnergyPointFindingInFileClass

#pfif= PeakFindingInFileClass("pfif", "testMotor1","y1", []);
pfif= PointFindingInFileClass("pfif", "pgmenergy","ca31sr",[]);

pfe= PointFindingInFileClass("pfe", "pgmenergy","ca31sr", ["iddgap",  "iddtrp"]);

