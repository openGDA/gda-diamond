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
/entry/instrument/calibration/energy_dispersion_process_file -> string
/entry/instrument/calibration/energy_dispersion_scan_file -> string
/entry/instrument/calibration/resolution -> float
/entry/instrument/calibration/elastic_process_file -> string
/entry/instrument/calibration/elastic_scan_file -> string
/entry/instrument/calibration/elastic_slope -> float
/entry/instrument/calibration/elastic_offset -> float

Usage:
    from calibration import set_dark_scan, set_energy_calibration, set_elastic_calibration

    # Set metadata
    set_dark_scan(123456)
    set_energy_calibration('processed_file.nxs')
    set_elastic_calibration('elastic_processed_file.nxs')
    #-or-
    set_energy_calibration(123456)  # searches for processed file
    set_elastic_calibration(123456)  # searches for processed file
    #-or-
    set_energy_calibration(0.8)
    set_elastic_calibration(-0.5, 123)

    # Remove metadata
    set_dark_scan(None)
    set_energy_calibration(None)
    set_elastic_calibration(None)
    
    # Show metadata
    meta.ll('calibration')


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
CMD_PATH = '/entry/scan_command'
ENERGY_PATH = '/entry/sample/beam/incident_energy'
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


def check_scan_file(filename, scan_type='energy', energy=None, energy_tol=10.):
    """Raises error if scan file does not exists or is wrong type"""

    hdf_obj = dnp.io.load(filename, 'hdf5', warn=False)
    if scan_type:
        cmd = str(_get_hdf_data(hdf_obj, CMD_PATH))
        if not cmd.startswith('scan %s' % scan_type):
            raise Exception("Expected %s scan, got '%s'" % (scan_type, cmd))

    if energy:
        scan_en = float(_get_hdf_data(hdf_obj, ENERGY_PATH))
        if abs(scan_en - energy) > energy_tol:
            raise Exception("Scan out of energy tolerance. Expected %.2f+/-%.2f, got %.2f" % (energy, energy_tol, scan_en))


def _is_processed_file(filename):
    """Returns True if the file is a processed NeXus file"""
    hdf_obj = dnp.io.load(filename, 'hdf5', warn=False)
    return _check_hdf_path(hdf_obj, '/processed')


def find_processed_files(filename):
    """
    Look in the processed and processing directories for files called *_processed*
    Returns a generator that can be expanded:
        files = list(find_processed_files(filename))  # all files
        file = next(find_processed_files(filename), None)  # first file
    """
    dirname, fname = os.path.split(filename)
    name, ext = os.path.splitext(fname)
    processed_spec = name + '_processed'

    print("Searching recursively for processed files like '%s*'" % processed_spec)
    for dirpath, dirnames, filenames in os.walk(dirname):
        for name in filenames:
            if name.startswith(processed_spec):
                full_path = os.path.join(dirpath, name)
                yield full_path


### SET FUNCTIONS ###


def set_dark_scan(relativefilenumber_or_filename=0, detector_name=None):
    """
    set the current dark scan as filename or file number
    This will set the dark scan array stored in any subsequent scans

        set_dark_scan() -> sets the last scan as the dark image
        set_dark_scan(12345) -> sets a specific scan number as the dark image
        set_dark_scan('some/file.nxs') -> sets a specific file as the dark image
        set_dark_scan(None) -> removes dark scan from future scans
    """
    if relativefilenumber_or_filename is None:
        meta.rm(detector_name, DARK_IMAGE)
        meta.rm(detector_name, 'dark_image_file')
        print('Removed dark image from metadata')
        return
    if isinstance(relativefilenumber_or_filename, (str, unicode)):
        filename = relativefilenumber_or_filename
    else:
        filename = get_scan_file(relativefilenumber_or_filename)

    check_scan_file(filename, 'ds')

    if detector_name is None:
        detector_name = get_nxdetector_name(filename)
    # see i21-config/scripts/acquisition/darkImageAcquisition.py
    external_link_path = str(Node.SEPARATOR).join([INSTRUMENT_PATH, detector_name, 'data'])
    meta.addLink(detector_name, DARK_IMAGE, external_link_path, filename)
    meta.addScalar(detector_name, 'dark_image_file', filename)
    print("A link to dark image data at '%s#%s' \nwill be added to detector '%s' as '%s' in subsequent scan data files \nwhen this detector is used until it is removed\n" % (filename, external_link_path, detector_name, DARK_IMAGE))


def set_energy_calibration(resolution_or_filename, search_for_processed=True):
    """
    Set the energy dispersion scannable
    Energy dispersion can be set by adding a processed file, or by setting resolution directly
    Input can be str, int, float or None and will behave differently in each case.

        set_energy_calibration('processed.nxs') -> read file and store metadata
        set_energy_calibration(12345) -> find & use processed file associated with scan 12345
        set_energy_calibration(12345, False) -> don't find processed, just store calibration scan
        set_energy_calibration(0.8) -> set metadata directly
        set_energy_calibration(None) -> remove metadata fields
        meta.ll('calibration') -> show current calibration metadata
    """
    if resolution_or_filename is None:
        meta.disable("energy_dispersion")
        meta.rm("calibration", "energy_dispersion_processed_file")
        meta.rm("calibration", "energy_dispersion_scan_file")
        print('Removed resolution from metadata')
        return
    
    if isinstance(resolution_or_filename, int):
        # scan number
        resolution_or_filename = get_scan_file(resolution_or_filename)

    if isinstance(resolution_or_filename, (str, unicode)):
        if not _is_processed_file(resolution_or_filename):
            # scan file
            check_scan_file(resolution_or_filename, 'energy')
            meta.addScalar('calibration', 'energy_dispersion_scan_file', resolution_or_filename)
            print('Added metadata "calibration/energy_dispersion_scan_file" = "%s"' % resolution_or_filename)
            if search_for_processed:
                resolution_or_filename = next(find_processed_files(resolution_or_filename), None)
            if resolution_or_filename is None or not search_for_processed:
                print('No processed file, disabling energy dispersion field.')
                meta.disable("energy_dispersion")
                meta.rm("calibration", "energy_dispersion_processed_file")
                return
        else:
            meta.rm("calibration", "energy_dispersion_scan_file")
        # processed file
        resolution = _get_resolution(resolution_or_filename)
        meta.addScalar('calibration', 'energy_dispersion_processed_file', resolution_or_filename)
        print('Added metadata "calibration/energy_dispersion_processed_file" = "%s"' % resolution_or_filename)

    else:
        resolution = float(resolution_or_filename)

    energy_dispersion(resolution)
    meta.enable("energy_dispersion")
    print('Added metadata "calibration/energy_dispersion" = %s eV' % resolution)


def set_elastic_calibration(slope_or_filename, offset=0, search=True):
    """
    Set the elastic line slope and offset
    Values can be set by adding a processed file, or by setting the values directly
    Input can be str, int, float or None and will behave differently in each case.

        set_elastic_calibration('processed.nxs') -> read file and store metadata
        set_elastic_calibration(12345) -> find & use processed file associated with scan 12345
        set_elastic_calibration(12345, search=False) -> don't find processed, just store calibration scan
        set_elastic_calibration(0.1, 450) -> set metadata directly (slope, offset)
        set_elastic_calibration(None) -> remove metadata fields
        meta.ll('calibration') -> show current calibration metadata
    """
    if slope_or_filename is None:
        meta.disable("elastic_slope", "elastic_offset")
        meta.rm("calibration", "elastic_processed_file")
        meta.rm("calibration", "elastic_scan_file")
        print('Removed elastic slope and offset from metadata')
        return
    
    if isinstance(slope_or_filename, int):
        # scan number
        slope_or_filename = get_scan_file(slope_or_filename)

    if isinstance(slope_or_filename, (str, unicode)):
        if not _is_processed_file(slope_or_filename):
            # scan file
            meta.addScalar('calibration', 'elastic_scan_file', slope_or_filename)
            print('Added metadata "calibration/elastic_scan_file" = "%s"' % slope_or_filename)
            if search:
                slope_or_filename = next(find_processed_files(slope_or_filename), None)
            if slope_or_filename is None or not search:
                print('No processed file, disabling energy elastic slope + offset fields.')
                meta.disable("elastic_slope", "elastic_offset")
                meta.rm("calibration", "elastic_processed_file")
                return
        else:
            meta.rm("calibration", "elastic_scan_file")
        # processed file
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
