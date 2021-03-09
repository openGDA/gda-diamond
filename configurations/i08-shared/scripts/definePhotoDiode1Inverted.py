import sys

from ScannableInvertedValue import PositionInvertedValue
from gda.device import DeviceException

# Define the scannable photoDiode1Inverted
# As the associated IOC may not always be available, handle any exception arising from the definition.
try:
    photoDiode1Inverted = PositionInvertedValue("photoDiode1Inverted", "photoDiode1")
except DeviceException as e:
    print("Error defining photoDiode1Inverted: " + e.message)
except:
    print("Error defining photoDiode1Inverted:", sys.exc_info()[0])