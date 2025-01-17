from time import sleep
from gda.epics import CAClient #@Unresolvedimport

from gda.util.osgi import OsgiJythonHelper #@Unresolvedimport

from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService #@Unresolvedimport

from uk.ac.diamond.daq.mapping.api import PolarisationParameters #@Unresolvedimport
from uk.ac.diamond.daq.mapping.api.PolarisationParameters.Polarisation import Direction #@Unresolvedimport

from gdaserver import idgap, energyFocus, phase, phase_top, phase_bottom #@Unresolvedimport

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)
polarisationParams = marshaller_service.unmarshal(customParams, PolarisationParameters) #@Undefinedvariable

caClient = CAClient()

tolerance_energy_value = 0.1

print("Running polarisation script")

typeOfExperiment = polarisationParams.getPolarisation()

if str(typeOfExperiment) == "LINEARDEGREES":
    selected_degree_experiment = int(selectedDegreeExperiment) #@UndefinedVariable
    print("Selected degree: {}").format(selected_degree_experiment) 

    energy_target_value, idgap_target_value, phase_target_value = get_idgap_energy_phase_for_mn(selected_degree_experiment) #@Undefinedvariable
    print("Energy target value: {}").format(energy_target_value)
    print("Id gap target value: {}").format(idgap_target_value)
    
    current_energyFocus_value = energyFocus.getPosition()
    print("Current Energy target value: {}").format(current_energyFocus_value)
    if abs(current_energyFocus_value - energy_target_value) >= tolerance_energy_value:
        raise Exception("energyFocus is not in the correct position")
    
    print("Moving phase top")
    pos phase_top phase_target_value
    
    print("Moving phase bottom")
    pos phase_bottom -phase_target_value
    
    print("Moving idgap")
    pos idgap idgap_target_value
    
else:
    print(polarisationParams)
    
    polarisation_value = polarisationParams.getPolarisation()
    print("Polarisation: " + polarisation_value.getLabel())
    
    phase_value = polarisationParams.getPhase()
    print("Phase: " + str(phase_value))
    
    print("Starting polarisation procedure")
    
    if polarisation_value.getDirection() == Direction.LINEAR:
        print("Linear")
        set_ID_poly(str(polarisation_value))
    elif polarisation_value.getDirection() == Direction.CIRCULAR:
        print("Circular")
        set_ID_poly("C")
        
    sleep(1)
    
    print("Moving phase")
    pos phase phase_value
    
    # caClient.caput("SR08I-MO-SERVC-01:BLGSETP",1)
    # sleep(25)
    
    print("Moving energyFocus to its current position")
    current_energy = energyFocus.getPosition()
    new_energy_value = current_energy + 0.001
    pos energyFocus new_energy_value
    
    sleep(1)