# Initialise the function that maps zoneplate z position to osa z position

from gdaserver import ZonePlateZ, osa_z
from gda.util import QuantityFactory
from tec.units.indriya.quantity import Quantities
from gda.factory import Finder

def initialise_zpz_osa_function():
    # Calculate the parameters of the linear function that combines ZonePlateZ & OSA Z motion
    #
    # Assuming the current positions of the motors are correct, we always want the OSA to move an equal
    # and opposite distance to the zone plate.
    #
    # Therefore, in the equation y = mx + c, y is the position of the OSA, x is the position of the zone plate
    # m is -1 (to produce the contrary motion) and we have to calculate the interception c from the current positions
    # i.e. c = y - mx which since m = -1, becomes c = x + y

    zpz_quantity = QuantityFactory.createFromObject(ZonePlateZ.getPosition(), ZonePlateZ.getUserUnits())
    osaz_quantity = QuantityFactory.createFromObject(osa_z.getPosition(), osa_z.getUserUnits())
    interception = zpz_quantity.add(osaz_quantity)
    print(u'Calling initialise_zpz_osa_function: zpz: {}, osaz: {}, interception: {}'.format(zpz_quantity, osaz_quantity, interception))

    zpz_osa_function = Finder.find('zpz_osa_function')
    zpz_osa_function.setSlopeDividend(Quantities.getQuantity('-1 mm'))
    zpz_osa_function.setSlopeDivisor(Quantities.getQuantity('1 mm'))
    zpz_osa_function.setInterception(interception)
    print(u'zpz_osa_function: {}'.format(zpz_osa_function))

# Run the function after definition
initialise_zpz_osa_function()