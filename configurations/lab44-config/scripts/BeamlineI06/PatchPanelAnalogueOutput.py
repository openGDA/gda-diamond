
from BeamlineI06.PseudoDevices.ScannableControlPoint import ScannalbeControlPointClass;

#Create the scannable PatchPanel Analogue Output

#from gda.factory import Finder
#ppao1 = Finder.find("cpPPAO1");
#ppao2 = Finder.find("cpPPAO2");
#ppao3 = Finder.find("cpPPAO3");
#ppao4 = Finder.find("cpPPAO4");
#ppao5 = Finder.find("cpPPAO5");
#ppao6 = Finder.find("cpPPAO6");
#ppao7 = Finder.find("cpPPAO7");
#ppao8 = Finder.find("cpPPAO8");

#####################################################################################
#
#The Class is for creating a scannable Control Point
#Usage:
#    ScannableControlPointClass(name, lowLimit, highLimit, refObj, delay)
#
#Parameters:
#   name:   Name of the exit slits gap
#    lowLimit: lower limit of slits gap
#    highLimit: Upper limit of slits gap
#    refObj: Name of the Control Point Object
#    delay: time needed in milli-second to reach the new value
#
#####################################################################################
ppao1 = ScannalbeControlPointClass("ppao1", -10, 10, "cpPPAO1", 100);
ppao2 = ScannalbeControlPointClass("ppao2", -10, 10, "cpPPAO2", 100);
ppao3 = ScannalbeControlPointClass("ppao3", -10, 10, "cpPPAO3", 100);
ppao4 = ScannalbeControlPointClass("ppao4", -10, 10, "cpPPAO4", 100);
ppao5 = ScannalbeControlPointClass("ppao5", -10, 10, "cpPPAO5", 100);
ppao6 = ScannalbeControlPointClass("ppao6", -10, 10, "cpPPAO6", 100);
ppao7 = ScannalbeControlPointClass("ppao7", -10, 10, "cpPPAO7", 100);
ppao8 = ScannalbeControlPointClass("ppao8", -10, 10, "cpPPAO8", 100);
