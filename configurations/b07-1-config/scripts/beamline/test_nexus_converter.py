#!/dls_sw/apps/python/anaconda/1.7.0/64/bin/python
# module load python/ana before running these tests!
import os
import pytest
import h5py
from b07_convert_nxs_to_txt import (collect_files, get_instrument_node,
                                    classify_scan_type, ScanType)


@pytest.fixture()
def good_dir(tmpdir):
    directory = tmpdir.mkdir("good_dir")
    for i in range(3):
        filepath = directory.join("pytest{}.nxs".format(i))
        h5py.File(filepath)
    for i in range(7):
        filepath = directory.join("pytest{}.txt".format(i))
        filepath.write("content")
    yield directory


@pytest.fixture()
def no_nxs_dir(tmpdir):
    directory = tmpdir.mkdir("no_nxs_dir")
    for i in range(7):
        filepath = directory.join("pytest{}.txt".format(i))
        filepath.write("content")
    yield directory


@pytest.fixture()
def xps_file_node(tmpdir):
    """Creates an XPS nexus file and passes the instrument node for testing"""
    filepath = tmpdir.mkdir("sub").join("pytest_xps.nxs")
    print "Create XPS nexus file for testing"
    xps_nxs_file = h5py.File(filepath)
    xps_nxs_file.create_group("entry1/instrument/analyser")
    xps_nxs_file.create_group("entry1/instrument/region")
    xps_nxs_file.create_group("entry1/instrument/region2")
    yield xps_nxs_file['entry1/instrument/']
    print "teardown"
    xps_nxs_file.close()


@pytest.fixture()
def nexafs_file_node(tmpdir):
    """Creates an NEXAFS nexus file and passes the instrument node for
    testing"""
    filepath = tmpdir.mkdir("sub").join("pytest_nexafs.nxs")
    print "Create NEXAFS nexus file for testing"
    nexafs_nxs_file = h5py.File(filepath)
    nexafs_nxs_file.create_group("entry1/instrument/pgm_energy")
    nexafs_nxs_file.create_group("entry1/instrument/sample_current")
    yield nexafs_nxs_file['entry1/instrument/']
    print "teardown"
    nexafs_nxs_file.close()


@pytest.fixture()
def nexafs_analyser_file_node(tmpdir):
    """Creates an NEXAFS nexus file with analyser and passes the instrument node
    for testing"""
    filepath = tmpdir.mkdir("sub").join("pytest_nexafs_analyser.nxs")
    print "Create NEXAFS with analyser nexus file for testing"
    nexafs_analyser_file = h5py.File(filepath)
    nexafs_analyser_file.create_group("entry1/instrument/pgm_energy")
    nexafs_analyser_file.create_group("entry1/instrument/sample_current")
    nexafs_analyser_file.create_group("entry1/instrument/analyser")
    yield nexafs_analyser_file['entry1/instrument/']
    print "teardown"
    nexafs_analyser_file.close()


@pytest.fixture()
def not_nexafs_file_node(tmpdir):
    """Creates a nexus file with pgm_energy but no
    current and passes the instrument node for testing"""
    filepath = tmpdir.mkdir("sub").join("pytest_not_nexafs.nxs")
    print "Create non NEXAFS nexus file for testing"
    nxs_file = h5py.File(filepath)
    nxs_file.create_group("entry1/instrument/pgm_energy")
    yield nxs_file['entry1/instrument/']
    print "teardown"
    nxs_file.close()


@pytest.fixture()
def xps_file(tmpdir):
    """Fixture that creates an XPS nexus file for testing and passes the
    filepath to the file"""
    filepath = tmpdir.mkdir("sub").join("pytest_xps.nxs")
    print "Create XPS nexus file for testing"
    xps_nxs_file = h5py.File(filepath)
    xps_nxs_file.create_group("entry1/instrument/analyser")
    xps_nxs_file.create_group("entry1/instrument/region")
    xps_nxs_file.create_group("entry1/instrument/region2")
    yield filepath
    print "teardown"
    xps_nxs_file.close()


@pytest.fixture()
def non_standard_file(tmpdir):
    """Fixture that creates an non-standard nexus file for testing and passes the
    filepath to the file"""
    filepath = tmpdir.mkdir("sub").join("pytest_xps.nxs")
    print "Create non-standard nexus file for testing"
    nxs_file = h5py.File(filepath)
    nxs_file.create_group("entry1/banana/analyser")
    yield filepath
    print "teardown"
    nxs_file.close()


class TestCollectFiles(object):
    """Class to test the collect_files method"""

    invalid_dir = '/some/random/dir'

    def test_initial_dir_size(self, good_dir):
        """Check there are the right number of files
        to start with
        """
        assert len(os.listdir(str(good_dir))) == 10

    def test_filtered_list_length(self, good_dir):
        """Check the filtered list of filenames is the
        right length
        """
        file_list = collect_files(str(good_dir))
        assert len(file_list) == 3

    def test_filtered_list_extensions(self, good_dir):
        """Check the filtered list of filenames has
        right extension
        """
        file_list = collect_files(str(good_dir))
        for filename in file_list:
            assert filename.split('.')[-1] == "nxs"

    def test_no_nexus_error_thrown(self, no_nxs_dir):
        """Check error is thrown if no nexus files found"""
        with pytest.raises(ValueError):
            collect_files(str(no_nxs_dir))

    def test_collect_files_invalid_dir(self):
        """Check the collect_files function raises an
        OSError if the path does not exist
        """
        with pytest.raises(ValueError):
            collect_files(self.invalid_dir)


class TestGetInstrumentNode(object):
    """Class to test the get_instrument_node method"""

    invalid_file_path = "i/am/invalid"

    def test_returned_object_type(self, xps_file):
        """Check get_instrument_node returns an h5py.Group"""
        instrument = get_instrument_node(str(xps_file))
        assert isinstance(instrument, h5py.Group)

    def test_path_not_there(self, non_standard_file):
        """Check get_instrument_node returns None if the path
        to the data does not exist"""
        instrument_node = get_instrument_node(str(non_standard_file))
        assert instrument_node is None

    def test_not_a_real_file(self):
        """Check get_instrument_node returns None if the file
        path is invalid"""
        instrument_node = get_instrument_node(self.invalid_file_path)
        assert instrument_node is None


class TestClassifyScanType(object):
    """Class to test the classify_scan_type method"""

    def test_classify_xps_scan_file(self, xps_file_node):
        """Test that XPS file is correctly classfied as such"""
        scan_type = classify_scan_type(xps_file_node)
        assert scan_type == ScanType.XPS

    def test_classify_nexafs_scan_file(self, nexafs_file_node):
        """Test that NEXAFS file is correctly classfied as such"""
        scan_type = classify_scan_type(nexafs_file_node)
        assert scan_type == ScanType.NEXAFS

    def test_classify_nexafs_analyser_file(self, nexafs_analyser_file_node):
        """Test that NEXAFS file is correctly classfied as such"""
        scan_type = classify_scan_type(nexafs_analyser_file_node)
        assert scan_type == ScanType.NEXAFS_ANALYSER

    def test_classify_fake_scan_file(self, not_nexafs_file_node):
        """Test that non NEXAFS file is correctly classfied as such"""
        scan_type = classify_scan_type(not_nexafs_file_node)
        assert scan_type is None
