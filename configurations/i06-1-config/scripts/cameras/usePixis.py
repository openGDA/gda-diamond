
#import Diamond.Pixis.PixisDetector; reload(Diamond.Pixis.PixisDetector)

from Diamond.Pixis.PixisDetector import PixisDetectorClass


print "-"*100
ViewerPanelName = "Plot 2"
adPixis='pixis1det'
print "Create a GDA pseudo detector pixis to use the PIXIS AreaDetector adPixis"
pixis = PixisDetectorClass("pixis", ViewerPanelName, adPixis);
#pixis.connect();

