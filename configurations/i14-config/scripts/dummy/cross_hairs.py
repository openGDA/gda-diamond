# Define a function to set cross hairs in a roughly central position in the MJPEG viewer
# for the simulator, as a starting point for testing
from gdaserver import sample_dtab_addetector

print("Defining function setup_cross_hairs()")

def setup_cross_hairs():
    overlay = sample_dtab_addetector.getNdOverlays().get(0)
    overlay.setName("Beam position")
    overlay.setUse(1)
    overlay.setShape(0)
    overlay.setDrawMode(1)
    overlay.setRed(65535)
    overlay.setGreen(65535)
    overlay.setBlue(65535)
    overlay.setCentreX(483)
    overlay.setSizeX(500)
    overlay.setCentreY(448)
    overlay.setSizeY(500)