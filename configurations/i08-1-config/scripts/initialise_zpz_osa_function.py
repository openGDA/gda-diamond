# Initialise the function that maps zoneplate z position to osa z position

from tec.units.indriya.quantity import Quantities
from gda.factory import Finder

def initialise_zpz_osa_function():
    # Set the parameters of the linear function that combines ZonePlateZ & OSA Z motion
    #
    # Assuming the current positions of the motors are correct, we always want the OSA to move an equal
    # and opposite distance to the zone plate.
    zpz_osa_function = Finder.find('zpz_osa_coupling_function')
    zpz_osa_function.setSlopeDividend(Quantities.getQuantity('-1 mm'))
    zpz_osa_function.setSlopeDivisor(Quantities.getQuantity('1 mm'))
    zpz_osa_function.setInterception(Quantities.getQuantity('0 mm'))
    print(u'zpz_osa_function: {}'.format(zpz_osa_function))

# Run the function after definition
initialise_zpz_osa_function()