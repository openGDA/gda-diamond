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
    
    linear_arbitrary_edge = str(selectedLinearArbitraryEdge) #@UndefinedVariable
    edge_lower_case = linear_arbitrary_edge.lower()
    if "mn" in edge_lower_case:
        energy_target_value, idgap_target_value, phase_target_value = get_idgap_energy_phase_for_mn(selected_degree_experiment) #@Undefinedvariable
    elif "fe" in edge_lower_case:
        energy_target_value, idgap_target_value, phase_target_value = get_idgap_energy_phase_for_fe(selected_degree_experiment) #@Undefinedvariable
    elif "co" in edge_lower_case:
        energy_target_value, idgap_target_value, phase_target_value = get_idgap_energy_phase_for_co(selected_degree_experiment) #@Undefinedvariable
    else:
        raise ValueError("Edge not supported. Please select another edge")
    
    current_energyFocus_value = energyFocus.getPosition()
    print("Current Energy target value: {}").format(current_energyFocus_value)
    if abs(current_energyFocus_value - energy_target_value) >= tolerance_energy_value:
        raise Exception("energyFocus is not in the correct position")
    
    print("Moving phase top to value: " + str(phase_target_value))
    pos phase_top phase_target_value
    
    print("Moving phase bottom to value: " + str(-phase_target_value))
    pos phase_bottom -phase_target_value
    
    print("Moving idgap to value: " + str(idgap_target_value))
    pos idgap idgap_target_value
    
else:
    print(polarisationParams)
    
    polarisation_value = polarisationParams.getPolarisation()
    print("Polarisation: " + polarisation_value.getLabel())
    
    phase_value = polarisationParams.getPhase()
    print("Phase: " + str(phase_value))
    
    print("Starting polarisation procedure")
    
    if polarisation_value.getDirection() == Direction.LINEAR:
        print("Setting ID polynomial coefficients for Linear polarisation")
        set_ID_poly(str(polarisation_value)) # 'LH' or 'LV'
    elif polarisation_value.getDirection() == Direction.CIRCULAR:
        print("Setting ID polynomial coefficients for Circular polarisation")
        set_ID_poly("C")
         
    sleep(1) # Allow time for ID changes to take effect
    
    print("Moving phase to: " + str(phase_value))
    pos phase phase_value # Move the phase motor to the predetermined phase value
    
    # caClient.caput("SR08I-MO-SERVC-01:BLGSETP",1)
    # sleep(25)
    
    print("Moving energyFocus to its current position")
    current_energy = energyFocus.getPosition()
    new_energy_value = current_energy + 0.001 # Small move to trigger position update
    pos energyFocus new_energy_value # Update the device
    
    sleep(1) # Wait for energyFocus move to complete
    
    
    
    