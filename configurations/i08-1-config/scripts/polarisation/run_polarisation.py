from time import sleep
from gda.epics import CAClient #@Unresolvedimport

from gda.util.osgi import OsgiJythonHelper #@Unresolvedimport

from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService #@Unresolvedimport

from uk.ac.diamond.daq.mapping.api import PolarisationParameters #@Unresolvedimport
from uk.ac.diamond.daq.mapping.api.PolarisationParameters import Polarisation #@Unresolvedimport
from uk.ac.diamond.daq.mapping.api.PolarisationParameters.Polarisation import Direction #@Unresolvedimport

from gdaserver import idgap, phase, energyFocus


print("Running polarisation script")

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)
polarisationParams = marshaller_service.unmarshal(customParams, PolarisationParameters) #@Undefinedvariable
print(polarisationParams)

polarisationValue = polarisationParams.getPolarisation()
print("Polarisation: " +  polarisationValue.getLabel())

phaseValue = polarisationParams.getPhase()
print("Phase: " + str(phaseValue))

print("Starting polarisation procedure")
print("Moving idgap to 50")
pos idgap 50

sleep(5)

if polarisationValue.getDirection() == Direction.LINEAR :
    print("Changing ID/eV polynomials")
    set_ID_poly(str(polarisationValue))
    
    sleep(5)
    
    print("Moving phase")
    pos phase phaseValue
    
    sleep(5)

elif polarisationValue.getDirection() == Direction.CIRCULAR:
    print("Changing ID/eV polynomials")
    set_ID_poly("C")
    
    sleep(5)
    
    print("Moving phase")
    pos phase phaseValue
    
    sleep(5)

# executing changes

# moving energy to current position
print("Moving energyFocus to current position")
current_energy = energyFocus.getPosition()
pos energyFocus current_energy

sleep(5)