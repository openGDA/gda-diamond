import logging
from os import path

from gda.device.detector.mythen.data import MythenRawDataset
from gda.device.detector.mythen.data import MythenSum
from gda.device.detector.mythen.data import MythenDataFileUtils
from gda.device.detector.mythen.data import DataConverter
from gda.device.detector.mythen.data import FileBadChannelProvider
from gda.device.detector.mythen.data import MythenRawDataset
from gda.device.detector.mythen.data import AngularCalibrationParametersFile
from gda.data import PathConstructor
from uk.ac.diamond.scisoft.analysis.io import SRSLoader
from gda.configuration.properties import LocalProperties
from uk.ac.diamond.daq.concurrent import Async

from java.io import File

logger = logging.getLogger('i11.mython_processing')

"""
Functions for reprocessing Mythen data
"""


DEFAULT_FLATFIELD = '/dls_sw/i11/software/var/mythen/diamond/flatfield/current_flat_field_calibration'
DEFAULT_BAD_CHANNELS = '/dls_sw/i11/software/var/mythen/diamond/calibration/badchannel_detector_standard.list'
DEFAULT_ANGLES = '/dls_sw/i11/software/var/mythen/diamond/calibration/ang.off'

def _make_converter(flatfield=None, bad_channel=None, angular_calibration=None, beamline_offset=None, default_converter=None):
    converter = DataConverter()
    
    if flatfield:
        converter.flatFieldData = MythenRawDataset(File(flatfield))
    else:
        converter.flatFieldData = default_converter.flatfieldCorrections

    if angular_calibration:
        converter.angularCalibrationParameters = AngularCalibrationParametersFile(File(angular_calibration))
    else:
        converter.angularCalibrationParameters = default_converter.angularCalibrationParameters

    if bad_channel:
        converter.badChannelProvider = FileBadChannelProvider(File(bad_channel))
    else:
        converter.badChannelProvider = default_converter.badChannelProvider

    if beamline_offset is not None:
        converter.beamlineOffset = beamline_offset
    else:
        converter.beamlineOffset = default_converter.beamlineOffset
       
    
    return converter


def load_raw_data(raw_path):
    """
    Load raw mythen data from the given file path

    Args:
        raw_path: The absolute path to the raw data file
    
    Returns:
        A MythenRawDataset of the data in the given file
    """
    logger.debug('Loading raw data from %s', raw_path)
    return MythenRawDataset(File(raw_path))

def save_processed_data(raw_data, target_file_path, delta_position, converter=None, flatfield=None, bad_channel=None, angular_calibration=None, beamline_offset=None, channel_info=False, headers=False):
    """
    Process a raw data file and save it to the given output file

    Args:
        raw_data:                The raw Mythen data (as MythenRawDataset) - see load_raw_data
        target_file_path:        The absolute path of the processed file to be written
        converter:               The existing DataConverter instance to use. If additional fields are given they will override the existing converter
        flatfield:               The flatfield data to use if not using existing converter
        bad_channel:             The bad_channel data to use if not using existing converter
        angular_calibration:     The angular_calibration data to use if not using existing converter
        beamline_offset:         The beamline_offset data to use if not using existing converter
        delta_position:          The position of delta during the collection of raw_data
        channel_info (Optional): Whether the raw data has channel info (default False)
        headers (Optional):      Whether there is additional data to be written (default False)
    
    Returns:
        A MythenRawDataset of the data in the given file
    """
    converter = _make_converter(flatfield, bad_channel, angular_calibration, beamline_offset, converter)
    processed_data = converter.process(raw_data, delta_position)
    logger.debug('Saving processed data to %s', target_file_path)
    processed_data.save(File(target_file_path), channel_info, headers)

def save_summed_data(processed_files, number_of_modules, converter, output_file, step=0.004):
    """
    Sum data from several processed files 

    Takes a list of processed file paths and writes a summed data file to a file.
    
    Args:
        processed_files:   The absolute paths to processed Mythen files
        number_of_modules: The number of modules on the detector that created the data
        converter:         The DataConverter instance to use
        output_file:       The summed data file to write 
        step (Optional):   The step size to use when summing the data
    """
    logger.debug('Summing data from %s', processed_files)
    all_data = MythenDataFileUtils.readMythenProcessedDataFiles(processed_files)
    summed_data = MythenSum.sum(all_data, number_of_modules, converter.getBadChannelProvider(), step)
    logger.debug('Saving summed data to %s', output_file)
    MythenDataFileUtils.saveProcessedDataFile(summed_data, output_file)
    
def reprocess_files(raw_files, deltas, output_directory, flatfield, bad_channel, angular_calibration, beamline_offset, number_of_modules, step=0.004, root_directory='/', summed_name=None, suffix='', overwrite=False):
    """
    Sum data from several raw data files 

    Takes a list of raw file paths and writes a summed data file.
    
    Args:
        raw_files:           The paths to raw Mythen files. Relative to root_directory (default '/')
        deltas:              The angles at which the raw data files were collected. Should be one value for each raw file
        output_directory:    The directory in which to write the summed data and intermediate processing files
        flatfield:           The absolute path to a file holding flatfield data
        bad_channel:         The absolute path to a file holding bad channel data
        angular_calibration: The absolute path to a file holding angular calibration data
        beamline_offset:     The angle of the first channel when the detector is at 0 degrees
        number_of_modules:   The number of modules on the detector that created the data
        step:                (Optional) The step size to use when summing the data (default 0.004)
        root_directory:      (Optional) The directory common to all raw_files (default '/')
        summed_name:         (Optional) The name of the summed data file to write. If none given, 'summed.dat' will be
                             appended to the common root of the raw file names (if there is one)
        overwrite:           (Optional) Overwrite any existing files (processed or summed) (default False)
    Raises:
        ValueError if the number of delta positions doesn't match the number of raw data files
        ValueError if the summed_name is not given and there is no common prefix in the raw files
        IOError if any of the output files already exist and overwrite is not specified
    """
    if len(raw_files) != len(deltas):
        raise ValueError('Number of raw files must match number of delta positions')
 
    processed_file_names = [path.join(output_directory, path.splitext(path.basename(p))[0] + suffix + '.dat') for p in raw_files]
    if not overwrite and any(path.exists(p) for p in processed_file_names):
        logger.error('Processed files would overwrite existing files')
        raise IOError('Processed files would overwrite existing files')
    
    if not summed_name:
        summed_name = path.basename(path.commonprefix(processed_file_names))
        if not summed_name:
            logger.error('Could not determine summed data file name')
            raise ValueError("Couldn't determine summed data name, specify summed_name")
        summed_name = summed_name + 'summed' + suffix + '.dat'
        logger.debug('Writing summed data to %s', summed_name)
    
    summed_name = path.join(output_directory, summed_name)
    if not overwrite and path.exists(summed_name):
        logger.error('Not overwriting %s', summed_name)
        raise IOError('Summed data file would overwrite existing file')

    converter = DataConverter()
    converter.angularCalibrationParameters = AngularCalibrationParametersFile(File(angular_calibration))
    converter.badChannelProvider = FileBadChannelProvider(File(bad_channel))
    converter.flatFieldData = MythenRawDataset(File(flatfield))
    converter.beamlineOffset = beamline_offset
    
    
    raw_data = [load_raw_data(path.join(root_directory, filename)) for filename in raw_files]
    processed_data = [converter.process(data, delta) for (data, delta) in zip(raw_data, deltas)]
    
    for data, name in zip(processed_data, processed_file_names):
        data.save(File(name), False, False)
        
    save_summed_data(processed_file_names, number_of_modules, converter, summed_name, step)


def _load_srs_file_data(file_path, delta='delta', detector='smythen'):
    loader = SRSLoader(file_path)
    loader.useImageLoaderForStrings = False
    loader.storeStringValues = True
    data = loader.loadFile()
    filenames = data.getDataset(detector)
    deltas = data.getDataset(delta)
    return (list(d.getData()) for d in (filenames, deltas))

def _visit_directory_for(visit):
    # return '/scratch/sample/i11'
    return PathConstructor.createFromProperty(LocalProperties.GDA_VISIT_DIR, {'visit': visit})

def _process_scan(number, visit, output_directory, flatfield, bad_channels, angular_offsets, suffix=''):
    visit_directory = _visit_directory_for(visit)
    scan_file = path.join(visit_directory, '%d.dat' %number)
    files, deltas = _load_srs_file_data(scan_file)
    raw_files = [path.splitext(p)[0] + '.raw' for p in files]
    reprocess_files(raw_files, deltas, output_directory, flatfield, bad_channels, angular_offsets, beamline_offset=0.08280, number_of_modules=18, step=0.004, root_directory=visit_directory, summed_name=None, suffix=suffix, overwrite=False)

def process_mythen_scans(numbers, visit, output_directory, flatfield=DEFAULT_FLATFIELD, bad_channels=DEFAULT_BAD_CHANNELS, angular_offsets=DEFAULT_ANGLES, suffix=''):
    """
    Reprocess previous mythen scans

    Args:
        numbers:                 The numbers of the scans to reprocess - can be a single number or a list
        visit:                   The visit that collected the data
        output_directory:        The absolute path to the directory to save the processed data
        flatfield:               The flatfield data to use if not using existing converter (optional)
        bad_channel:             The bad_channel data to use if not using existing converter (optional)
        angular_calibration:     The angular_calibration data to use if not using existing converter (optional)

    Examples:
        # ==== Reprocess scans with the current settings === #
        # reprocess list of scans
        process_mythen_scans([813447, 813448, 813449], 'cm22960-1', '/dls/i11/data/2019/cm22960-1/processing/mythen_reprocessing', suffix='_reprocess')

        # reprocess sinle scan
        process_mythen_scans(813447, 'cm22960-1', '/dls/i11/data/2019/cm22960-1/processing/mythen_reprocessing', suffix='_reprocess')

        # reprocess range of scans (inclusive start, exclusive end)
        process_mythen_scans(range(813447, 813450), 'cm22960-1', '/dls/i11/data/2019/cm22960-1/processing/mythen_reprocessing', suffix='_reprocess')

        # === Reprocess scans with changed settings === #
        # Any combination of these can be used. Omitted fields will use the current settings
        process_mythen_scans(813447, 'cm22960-1', '/dls/i11/data/2019/cm22960-1/processing/mythen_reprocessing', suffix='_reprocess', flatfield='/path/to/flatfield/file.dat')
        process_mythen_scans(813447, 'cm22960-1', '/dls/i11/data/2019/cm22960-1/processing/mythen_reprocessing', suffix='_reprocess', bad_channels='/path/to/bad_channel.dat')
        process_mythen_scans(813447, 'cm22960-1', '/dls/i11/data/2019/cm22960-1/processing/mythen_reprocessing', suffix='_reprocess', angular_offsets='/path/to/ang.off')

    """
    if isinstance(numbers, int):
        logger.debug('Processing single scan "%d" in visit %s', numbers, visit)
        _process_scan(numbers, visit, output_directory, flatfield, bad_channels, angular_offsets, suffix=suffix)
    else:
        logger.debug('Processing %d files in visit %s', len(numbers), visit)
        processes = [lambda num=num:_process_scan(num, visit, output_directory, flatfield, bad_channels, angular_offsets, suffix=suffix) for num in numbers]
        Async.executeAll(processes).get()
    
