from Diamond.PseudoDevices.EuroThermo import EuroThermoLoopOutputClass

etc11=finder.find("etcontroller11");
etc12=finder.find("etcontroller12");
etc13=finder.find("etcontroller13");
etc21=finder.find("etcontroller21");
etc22=finder.find("etcontroller22");
etc23=finder.find("etcontroller23");

etoutput11 = EuroThermoLoopOutputClass("etoutput11", etc11);
etoutput12 = EuroThermoLoopOutputClass("etoutput12", etc12);
etoutput13 = EuroThermoLoopOutputClass("etoutput13", etc13);
etoutput21 = EuroThermoLoopOutputClass("etoutput21", etc21);
etoutput22 = EuroThermoLoopOutputClass("etoutput22", etc22);
etoutput23 = EuroThermoLoopOutputClass("etoutput23", etc23);
