"""
from datetime import datetime, timedelta

from uk.ac.diamond.scisoft.analysis.io import LoaderFactory

DT_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

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
def test_1d_scan(start, stop, step, main, meta, gaussian_pair):
    meta['subdirectory'] = 'testing'
    meta['title'] = 'test_1d_scan'
    meta['sample_name'] = 'test_sample_one'
    main.sample_thickness(0.42)
    gx, gy = gaussian_pair
    main.scan(gx, start, stop, step, gy)
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
    start = str(entry1.getDataNode('start_time').getString())
    end = str(entry1.getDataNode('end_time').getString())
    # Scan should be quick with dummy scannables
    assert datetime.strptime(end, DT_FORMAT) - datetime.strptime(start, DT_FORMAT) < timedelta(seconds=5)

    sample = entry1.getGroupNode('sample')
    assert sample.getDataNode('name').getString() == 'test_sample_one'
    assert sample.getDataNode('thickness').getDataset().getSlice(None).getData()[0] == 0.42

    instrument = entry1.getGroupNode('instrument')
    assert instrument.getDataNode('gx').shape == [41]
    assert instrument.getDataNode('gy').shape == [41]

def test_single_xray_frame(main):
    from setup import tfgsetup
    tfgsetup.setupTfg(1, 800, 200)
    staticscan(main.ncddetectors)
"""