from mapping_scan_commands import submit
from gda.util.osgi import OsgiJythonHelper
from org.eclipse.scanning.api.event.scan import ScanRequest
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from org.eclipse.scanning.api.points.models import IScanPointGeneratorModel
from org.eclipse.scanning.api.points.models import IAxialModel, AxialStepModel, AxialMultiStepModel, AxialArrayModel
from org.eclipse.scanning.api.script.IScriptService import VAR_NAME_SCAN_REQUEST_JSON, VAR_NAME_CUSTOM_PARAMS


print("Running submit_energy_scan.py")

def run_energy_scan_request(scanRequest, energyModel):
    
    print("Scan request: {}".format(scanRequest))
    print("Energy focus model: {}".format(energyModel))
    
    if isinstance(energyModel, AxialArrayModel):
        run_energy_scan_points(scanRequest, energyModel)
    elif isinstance(energyModel, AxialStepModel):
        run_energy_scan_range(scanRequest, [energyModel])
    elif isinstance(energyModel, AxialMultiStepModel):
        run_energy_scan_range(scanRequest, energyModel.getModels())
        
def run_scan(energy_value):
    pos(energyFocus, energy_value)
    scan_name = "Energy focus scan {} eV".format(energy_value)
    submit(scanRequest, block=True, name=scan_name)
    
def run_energy_scan_points(scanRequest, energyModel):
    energy_values = energyModel.getPositions()
    for value in energy_values:
        run_scan(value)

def run_energy_scan_range(scanRequest, energyModel):
    for energy_model in energyModel:
        start = energy_model.getStart()
        stop = energy_model.getStop()
        step = energy_model.getStep()
        
        print("Step model: start: {}, stop: {}, step: {}".format(start, stop, step))
        
        energy_value = start
        while energy_value <= stop:
            try:    
                run_scan(energy_value)
            except Exception:
                print("Error running scan with energy value {}".format(energy_value))
            energy_value = energy_value + step

           
marshaller_service = OsgiJythonHelper.getService(IMarshallerService)

scanRequest = marshaller_service.unmarshal(locals()[VAR_NAME_SCAN_REQUEST_JSON], ScanRequest)
energyModel = marshaller_service.unmarshal(locals()[VAR_NAME_CUSTOM_PARAMS], IAxialModel)

run_energy_scan_request(scanRequest, energyModel)