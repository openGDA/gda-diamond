"""
Dark Image, Energy Calibration and Elastic Line Processing

Process:
1. Dark image scan
1.1 Set current dark image
2. Energy calibration scan
2.1 Run energy calibration processing in Dawn, save processed file
2.1 Set current energy calibration processed file
2.2 Read energy dispersion value from current processed file
2.3 Set energy dispersion scannable
3. Elastic line scan
3.1 Run elastic line processing in Dawn, save processed file
3.2 Set current elastic line processed file
3.3 Read slope and offset from processed file
3.4 Set slope and offset scannables
4. RIXS processing reads dark image, energy dispersion, slope and offset from current nexus files.

Functions:
 - set_dark_scan
 - set_energy_calibration
 - set_elastic_calibration

Nexus fields in scan files
/entry/instrument/[NXDetector]/dark_image -> array (external link)
/entry/instrument/calibration/resolution_process_file -> string
/entry/instrument/calibration/resolution -> float
/entry/instrument/calibration/elastic_process_file -> string
/entry/instrument/calibration/elastic_slope -> float
/entry/instrument/calibration/elastic_offset -> float

Usage:
    from calibration import set_dark_scan, set_energy_calibration, set_elastic_calibration

    # Set metadata
    set_dark_scan(scanno)
    set_energy_calibration('processed_file.nxs')
    set_elastic_calibration('elastic_processed_file.nxs')
    #-or-
    set_energy_calibration(0.8)
    set_elastic_calibration(-0.5, 123)

    # Remove metadata
    set_dark_scan(None)
    set_energy_calibration(None)
    set_elastic_calibration(None)


See ticket:
https://jira.diamond.ac.uk/browse/I21-1242

By Dan Porter
April 2026
"""

import os
import scisoftpy as dnp
from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import NexusScanDataWriter
from org.eclipse.dawnsci.analysis.api.tree import Node
from gda.jython import InterfaceProvider
from gdascripts.metadata.nexus_metadata_class import meta
from metadata.energy_calibration import energy_dispersion, elastic_slope, elastic_offset


ENTRY_NAME = str(LocalProperties.get(NexusScanDataWriter.PROPERTY_NAME_ENTRY_NAME, NexusScanDataWriter.DEFAULT_ENTRY_NAME))
INSTRUMENT_PATH = str(Node.SEPARATOR).join(["", ENTRY_NAME, str(NexusScanDataWriter.METADATA_ENTRY_NAME_INSTRUMENT)])
DARK_IMAGE = 'dark_image'
RESOLUTION_PATH = '/processed/result/data'  # resolution = element 0 for linear or element 1 for quadratic
SLOPE_PATH = '/processed/summary/{ii:d}-RIXS elastic line reduction/line_0_m/data'
OFFSET_PATH = '/processed/summary/{ii:d}-RIXS elastic line reduction/line_0_c/data'


## SCANNABLES ##
meta.disable("energy_dispersion")
meta.disable("elastic_slope")
meta.disable("elastic_offset")


### CORE FUNCTIONS ###


def get_scan_file(relativefilenumber=0):
    """
    Return filename of scan using scan number.
    The current scan number is updated when the scan starts.
    relativefilenumber: int, if <1, uses current scan number, otherwise scan number
    """
    current_scan_info = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation()
    scan_number = current_scan_info.getScanNumber()

    if relativefilenumber <= 1:
        new_scan_number = scan_number + relativefilenumber
    else:
        new_scan_number = relativefilenumber
    # replace scan number in current scan Filename with new scan number
    scan_file = current_scan_info.getFilename()
    return str(new_scan_number).join(scan_file.rsplit(str(scan_number), 1))


def _check_hdf_path(hdf_obj, path):
    """Returns True if path in hdf_obj, False otherwise"""
    try:
        hdf_obj[path]
        return True
    except KeyError:
        return False


def _update_iterable_path(hdf_obj, path):
    """return path including iterable element '{ii:d}'"""
    for n in range(5):
        _path = path.format(ii=n)
        if _check_hdf_path(hdf_obj, _path):
            return _path
    raise ValueError('iterable path "%s" does not exist in file %s' % (path, hdf_obj))


def _get_hdf_data(hdf_obj, path):
    """Return value from HDF file object"""
    if '{ii:d}' in path:
        path = _update_iterable_path(hdf_obj, path)
    if _check_hdf_path(hdf_obj, path):
        dataset = hdf_obj[path]
        value = dataset[...].squeeze()
    else:
        raise ValueError('path "%s" does not exist in file %s' % (path, hdf_obj))
    return value


def _get_resolution(processed_filename):
    """Read processed NeXus file and return energy resolution"""
    hdf_object = dnp.io.load(processed_filename, 'hdf5', warn=False)
    resolution = _get_hdf_data(hdf_object, RESOLUTION_PATH)
    if len(resolution) == 2:
        # linear
        return resolution[0]
    elif len(resolution) == 3:
        # quadratic
        return resolution[1]
    else:
        raise ValueError('Processed data contains wrong number of elements:', resolution)


def _get_slope(processed_filename):
    """Read processed NeXus file and return elastic line slope and offset"""
    hdf_object = dnp.io.load(processed_filename, 'hdf5', warn=False)
    gradient = _get_hdf_data(hdf_object, SLOPE_PATH)
    intercept = _get_hdf_data(hdf_object, OFFSET_PATH)
    return dnp.mean(gradient), dnp.mean(intercept)


def get_nxdetector_name(filename):
    """Return name of first NXdetector object in /entry/instrument"""
    hdf_obj = dnp.io.load(filename, 'hdf5', warn=False)
    instrument = hdf_obj[INSTRUMENT_PATH]
    for name, group in instrument.items():
        if hasattr(group, 'attrs') and 'NX_class' in group.attrs and group.attrs['NX_class'] == 'NXdetector':
            return name
    raise RuntimeError('file contains no NXdetector instance')


### SET FUNCTIONS ###


def set_dark_scan(relativefilenumber=0, filename=None, detector_name=None):
    """
    set the current dark scan as filename or file number
    This will set the dark scan array stored in any subsequent scans

        set_dark_scan() -> sets the last scan as the dark image
        set_dark_scan(12345) -> sets a specific scan number as the dark image
        set_dark_scan(filename='some/file.nxs') -> sets a specific file as the dark image
        set_dark_scan(None) -> removes dark scan from future scans
    """
    if filename is None and relativefilenumber is None:
        meta.rm(detector_name, DARK_IMAGE)
        return
    if filename is None:
        filename = get_scan_file(relativefilenumber)

    if not os.path.isfile(filename):
        raise RuntimeError('files does not exist: %s' % filename)

    if detector_name is None:
        detector_name = get_nxdetector_name(filename)
    # see i21-config/scripts/acquisition/darkImageAcquisition.py
    external_link_path = str(Node.SEPARATOR).join([INSTRUMENT_PATH, detector_name, 'data'])
    meta.addLink(detector_name, DARK_IMAGE, external_link_path, filename)
    print("A link to dark image data at '%s#%s' \nwill be added to detector '%s' as '%s' in subsequent scan data files \nwhen this detector is used until it is removed\n" % (filename, external_link_path, detector_name, DARK_IMAGE))


def set_energy_calibration(resolution_or_filename):
    """
    Set the energy dispersion scannable
    Energy dispersion can be set by adding a processed file, or by setting resolution directly

        set_energy_calibration('processed.nxs') -> read file and store metadata
        set_energy_calibration(0.8) -> set metadata directly
        set_energy_calibration(None) -> remove metadata fields
    """
    if resolution_or_filename is None:
        meta.disable("energy_dispersion")
        meta.rm("calibration", "energy_dispersion_processed_file")
        print('Removed resolution from metadata')
        return

    if isinstance(resolution_or_filename, str):
        resolution = _get_resolution(resolution_or_filename)
        meta.addScalar('calibration', 'energy_dispersion_processed_file', resolution_or_filename)
        print('Added metadata "calibration/energy_dispersion_processed_file" = "%s"' % resolution_or_filename)
    else:
        resolution = float(resolution_or_filename)

    energy_dispersion(resolution)
    meta.enable("energy_dispersion")
    print('Added metadata "calibration/energy_dispersion" = %s eV' % resolution)


def set_elastic_calibration(slope_or_filename, offset=0):
    """
    Set the elastic line slope and offset
    Values can be set by adding a processed file, or by setting the values directly

        set_elastic_calibration('processed.nxs') -> read file and store metadata
        set_elastic_calibration(0.1, 450) -> set metadata directly (slope, offset)
        set_elastic_calibration(None) -> remove metadata fields
    """
    if slope_or_filename is None:
        meta.disable("elastic_slope")
        meta.disable("elastic_offset")
        meta.rm("calibration", "elastic_processed_file")
        print('Removed elastic slope and offset from metadata')
        return

    if isinstance(slope_or_filename, str):
        slope, offset = _get_slope(slope_or_filename)
        meta.addScalar('calibration', 'elastic_processed_file', slope_or_filename)
        print('Added metadata "calibration/elastic_processed_file" = "%s"' % slope_or_filename)
    else:
        slope = float(slope_or_filename)

    elastic_slope(slope)
    elastic_offset(offset)
    meta.enable("elastic_slope")
    meta.enable("elastic_offset")
    print('Added elastic slope = %s and offset %s to metadata' % (slope, offset))
