from Diamond.PseudoDevices.EuroThermo import EuroThermoLoopOutputClass
from gda.factory import Finder

etc11=Finder.find("etcontroller11");
etc12=Finder.find("etcontroller12");
etc13=Finder.find("etcontroller13");
etc21=Finder.find("etcontroller21");
etc22=Finder.find("etcontroller22");
etc23=Finder.find("etcontroller23");
etc3=Finder.find("etcontroller3");
etc4=Finder.find("etcontroller4");
etc5=Finder.find("etcontroller5");

etoutput11 = EuroThermoLoopOutputClass("etoutput11", etc11);
etoutput12 = EuroThermoLoopOutputClass("etoutput12", etc12);
etoutput13 = EuroThermoLoopOutputClass("etoutput13", etc13);
etoutput21 = EuroThermoLoopOutputClass("etoutput21", etc21);
etoutput22 = EuroThermoLoopOutputClass("etoutput22", etc22);
etoutput23 = EuroThermoLoopOutputClass("etoutput23", etc23);
etoutput3 = EuroThermoLoopOutputClass("etoutput3", etc3);
etoutput4 = EuroThermoLoopOutputClass("etoutput4", etc4);
etoutput5 = EuroThermoLoopOutputClass("etoutput5", etc5);
