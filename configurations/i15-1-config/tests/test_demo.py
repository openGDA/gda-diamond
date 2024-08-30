""" Copied from /i22-config/tests/test_demo.py at commit ebdc189
import pytest
from array import array

from uk.ac.diamond.scisoft.analysis.io import LoaderFactory

# Use java time parsing because jython can't handle time zones
from java.time import OffsetDateTime, Duration

def test_set_subdirectory(meta):
    meta['subdirectory'] = 'testing'
    assert meta['subdirectory'] == 'testing'
    from gda.jython import InterfaceProvider
    pc = InterfaceProvider.getPathConstructor()
    assert pc.createFromDefaultProperty().endswith('testing')

def test_single_metadata():
    from gdaserver import GDAMetadata as meta
    from gda.data.metadata import GDAMetadataProvider
    assert GDAMetadataProvider.getInstance() is meta

def test_expected_metadata_present(meta):
    assert 'subdirectory' in meta
    assert 'visit' in meta
    assert 'title' in meta
    assert 'sample_background' in meta
    assert 'instrument' in meta
    assert 'note' in meta
    assert 'federalid' in meta
    assert 'sample_name' in meta

@pytest.mark.parametrize("start,stop,step", [(0,4,0.1), (4,0,0.1)])
def test_1d_scan(scan_command, start, stop, step, main, meta, gaussian_pair):
    meta['subdirectory'] = 'testing'
    meta['title'] = 'test_1d_scan'
    meta['sample_name'] = 'test_sample_one'
    main.sample_thickness(0.42)
    gx, gy = gaussian_pair
    scan_command(gx, start, stop, step, gy)
    sdp = lastScanDataPoint()
    command = 'scan gx {} {} {} gy'.format(start, stop, step)
    assert sdp.getCommand() == command
    assert sdp.numberOfPoints == 41
    assert sdp.instrument == 'i22'
    assert sdp.numberOfChildScans == 0

    # Scan processors are run correctly
    assert main.maxval.result.maxval == 1
    assert abs(main.minval.result.minpos - 4) < 1e-6

    scan_file = sdp.currentFilename
    scan_data = LoaderFactory.getData(scan_file)
    scan_tree = scan_data.getTree().getGroupNode()

    entry1 = scan_tree.getGroupNode('entry1')
    assert entry1.getDataNode('scan_command').getString() == command
    assert entry1.getDataNode('title').getString() == 'test_1d_scan'
    start_time = str(entry1.getDataNode('start_time').getString())
    end = str(entry1.getDataNode('end_time').getString())
    # Scan should be quick with dummy scannables
    assert _duration(start_time, end) < 5

    sample = entry1.getGroupNode('sample')
    assert sample.getDataNode('name').getString() == 'test_sample_one'
    assert sample.getDataNode('thickness').getDataset().getSlice(None).getData()[0] == 0.42

    instrument = entry1.getGroupNode('instrument')
    assert instrument.getGroupNode('gx').getDataNode('gx').dataset.shape == array('i', [41])
    assert instrument.getGroupNode('gy').getDataNode('gy').dataset.shape == array('i', [41])

def test_single_xray_frame(main):
    from setup import tfgsetup
    tfgsetup.setupTfg(1, 800, 200)
    staticscan(main.ncddetectors)

@pytest.mark.mode('live', reason="Relies on shared file system permissions")
def test_permissions(config):
    from uk.ac.diamond.daq.linux import UserUtilities
    from os import path
    assert UserUtilities.groupCanWrite('i22_staff', path.join(config, 'xml', 'permissions.xml'))
    assert UserUtilities.groupCanWrite('i22_staff', path.join(config, 'scripts', 'beamlineScripts'))
    assert UserUtilities.groupCanWrite('i22_staff', path.join(config, 'scripts', 'sampleEnvironment'))
    assert UserUtilities.groupCanWrite('i22_staff', path.join(config, 'scripts', 'templatesRepository'))
    assert UserUtilities.groupCanWrite('i22_staff', path.join(config, 'etc', 'i22.cfg'))

def test_2d_scan(scan_command, main, meta, gaussian_2d):
    x,y,g = gaussian_2d
    meta['subdirectory'] == 'testing'
    meta['title'] == 'test_2d_scan'
    meta['sample_name'] == "test_sample_two"

    scan_command(x, -1, 1, 0.2, y, -1, 1, 0.4, g)
    sdp = lastScanDataPoint()
    command = 'scan x -1 1 0.2 y -1 1 0.4 g'
    assert sdp.command == command
    assert sdp.numberOfPoints == 66
    assert sdp.instrument == 'i22'

def _duration(start, end):
    start = OffsetDateTime.parse(start)
    end = OffsetDateTime.parse(end)
    return Duration.between(start, end).seconds

"""