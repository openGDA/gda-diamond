'''There is some metadata that's required by i16 but they have no direct way of 
measuring it, this script will allow the user to input as much of that data as 
they wish to.
'''
from gdaserver import chemical_formula as chem_scannable, electric_field as elec_scannable,\
    magnetic_field as mag_scannable, pressure as pressure_scannable,\
    incidentBeamDivergenceScannable, incidentPolarizationScannable,\
    beamExtentScannable, fluxScannable
from gda.jython.commands.ScannableCommands import pos
from gda.device.scannable import ScannableBase

class TextsScannable (ScannableBase):
    def __init__(self, name, contents):
        self.name = name
        self.contents = contents

    def getPosition(self):
        return self.contents

    def rawAsynchronousMoveTo(self, contents):
        self.contents = contents

    def isBusy(self):
        return False

_title = TextsScannable('title', 'Scan of sample with GDA')

def title(title = None):
    if not title == None:
        _title.rawAsynchronousMoveTo(title)
    return _title.getPosition()

_sample= TextsScannable('sample', 'Default Sample')

def sample(sampleName = None):
    if not sampleName == None:
        _title.rawAsynchronousMoveTo(title)
    return _title.getPosition()

def input_metadata(sample_name=None, chemical_formula=None, electric_field=None,
               magnetic_field=None, pressure=None, incident_beam_divergence=None, 
               incident_polarization=None, beam_extent=None, flux=None):
    if (sample_name is None and chemical_formula is None and electric_field is None and magnetic_field is None and pressure is None and incident_beam_divergence is None and incident_polarization is None and beam_extent is None and flux is None) :
        print("Used to input user metadata not measurable during experiment.  Fields that can be defined:")
        print("sample_name, chemical_formula, electric_field, magnetic_field, pressure, "
            +"incident_beam_divergence, incident_polarization, beam_extent, flux")

    if sample_name is not None :
        pos(_sample, sample_name)
    if chemical_formula is not None :
        pos(chem_scannable, chemical_formula)
    if electric_field is not None :
        elec_scannable.setValue(electric_field)
    if magnetic_field is not None :
        mag_scannable.setValue(magnetic_field)
    if pressure is not None :
        pressure_scannable.setValue(pressure)
    if incident_beam_divergence is not None :
        incidentBeamDivergenceScannable.setValue(incident_beam_divergence)
    if incident_polarization is not None :
        incidentPolarizationScannable.setValue(incident_polarization)
    if beam_extent is not None :
        beamExtentScannable.setValue(beam_extent)
    if flux is not None :
        fluxScannable.setValue(flux)

input_metadata(sample_name='not set', chemical_formula='not set', electric_field=0, magnetic_field=0,
               pressure=101.235, incident_beam_divergence=0, incident_polarization=0, 
               beam_extent=0, flux=0)