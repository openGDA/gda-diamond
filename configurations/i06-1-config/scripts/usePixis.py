
#import Diamond.Pixis.PixisDetector; reload(Diamond.Pixis.PixisDetector)

from Diamond.Pixis.PixisDetector import PixisDetectorClass


print "-------------------------------------------------------------------"
ViewerPanelName = "Plot 2"
print "Create a GDA pseudo detector pixis to use the PIXIS AreaDetector adPixis"
pixis = PixisDetectorClass("pixis", ViewerPanelName, 'adPixis');
#pixis.connect();

