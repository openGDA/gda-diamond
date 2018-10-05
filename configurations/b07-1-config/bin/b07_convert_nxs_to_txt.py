#!/dls_sw/apps/python/anaconda/1.7.0/64/bin/python
"""
B07-92/B07-264 Script to convert .nxs files to plain text data files
https://jira.diamond.ac.uk/browse/B07-264
Requires python 2.7
Please make this file executable.
Example usage: b07_convert_nxs_to_txt.py fullpath_to_data_dir

@author: Olly King,
Last Modified October 2018
"""
import argparse
import h5py
import glob
import os
import csv

NUMBER_FORMAT = "{0:.8g}"


class ScanType(object):
    """An enum to represent scan types"""
    XPS = 0
    NEXAFS = 1  # Simple NEXAFS with just photon energy vs current
    NEXAFS_ANALYSER = 2  # NEXAFS using the analyser in addition to current


def collect_files(path):
    """Get list of directory paths to nexus files within a directory

    Args:
        path (string): Path to a directory
    Returns:
        file_list [nexus_file_paths]
    """
    if not os.path.exists(path):
        raise ValueError("The directory you specified does not appear to exist")
    file_list = []
    # Loop through the .nxs files in the given directory
    file_list = glob.glob(os.path.join(path, '*.nxs'))
    if not file_list:
        raise ValueError("Could not find any *.nxs files in the specified"
                         " directory")
    return file_list


def get_instrument_node(filepath):
    """Open a nexus file and retrieve the instrument node.

    Args:
        filepath (string): Path to a nexus file
    Returns:
        instrument_node (h5py.Group): The group containing datasets produced
        in the scan.
    """
    try:
        nexus = h5py.File(filepath, 'r')
    except IOError:
        print ("\n{}: There was a problem opening"
               " this file.".format(os.path.basename(filepath)))
        return
    try:
        instrument_node = nexus['/entry1/instrument']
    except KeyError:
        print ("\n{}: Could not access the path to the instrument"
               " data in file.".format(os.path.basename(filepath)))
        return
    return instrument_node


def output_data(instrument_node, filepath):
    """Controls the data output according to scan file type"""
    scan_type = classify_scan_type(instrument_node)
    filename = os.path.basename(filepath)

    try:
        if scan_type == ScanType.XPS:
            print "\n{} determined to be an XPS scan.".format(filename)
            region_list = instrument_node["analyser/region_list"]
            print "Number of regions found: {}".format(region_list.len())
            for region in region_list:
                export_xps_data(instrument_node[region], filename)

        elif scan_type == ScanType.NEXAFS:
            print "\n{} determined to be a simple NEXAFS scan.".format(filename)
            export_nexafs_data(instrument_node, filename, None)

        elif scan_type == ScanType.NEXAFS_ANALYSER:
            print "\n{} determined to be a NEXAFS scan with analyser output.".format(filename)
            region_list = instrument_node["analyser/region_list"]
            if region_list.len() == 1:
                region_name = region_list[0]
                print "Region name: {}".format(region_name)
                export_nexafs_data(instrument_node, filename, region_name)
            else:
                print "Number of regions does not equal 1. Not sure what to do with this file."
    finally:
        instrument_node.file.close()

    if scan_type is None:
        print ("\nCould not detect type of scan for {}. No output file will"
               " be written.".format(filename))


def classify_scan_type(instrument_node):
    """Given an instrument node from a nexus file, classify
    the type of scan it is. If pgm_energy plus a 'current' measurement is
    involved, classify as simple NEXAFS. If the analyser is involved in
    addition, classify as NEXAFS with analyser. Otherwise, if just 'analyser'
    is involved, classify as XPS
    """

    instrument_keys = instrument_node.keys()
    if ("pgm_energy" in instrument_keys
                     and (any("current" in s for s in instrument_keys)
                     or (any("femto" in s for s in instrument_keys)))):
        # File is some sort of NEXAFS scan
        if "analyser" in instrument_keys:
            return ScanType.NEXAFS_ANALYSER
        else:
            return ScanType.NEXAFS
    elif "analyser" in instrument_keys:
        return ScanType.XPS
    else:
        return


def export_nexafs_data(instrument_node, filename, region_name):
    """Format data and trigger writing to a file. If a region_name
    is passed in, the scan type is NEXAFS_ANALYSER and the integrated
    intensities are output along with the pgm_energy and current
    measurements.
    """

    #TODO: Store title and data in a list of tuples rather than having separate lists
    title_list = []  # list to store column titles
    data_list = []  # list to store data

    if region_name:
        integrated_data = convert_and_format(region_name, instrument_node)
        title_list.append(region_name)
        data_list.append(integrated_data)

    for item in instrument_node:
        # Adds pgm_energy as well as any scannables with current/femto in their name
        if item == "pgm_energy": # Hacky special case - want this to be the first column
            title_list.insert(0, item)
            formatted_list = convert_and_format(item, instrument_node)
            data_list.insert(0, formatted_list)
        elif ("current" in item) or ("femto" in item):
            title_list.append(item)
            formatted_list = convert_and_format(item, instrument_node)
            data_list.append(formatted_list)

    if data_list:
        print "Data types found: {}".format(" ".join(title_list))
        # Combine the datasets into a list of tuples
        zipped = zip(*data_list)
        filename = filename.split(".")[0] + "_NEXAFS.dat"
        filename = filename.replace(" ", "_")
        write_data_out(filename, title_list, zipped)
        print "Data written to file {}".format(filename)


def convert_and_format(dataset_name, instrument_node):
    """Return formatted data from the instrument
    node when given the dataset name."""
    path_string = "{0}/{0}".format(dataset_name)
    # Convert numpy array to list
    temp_list = instrument_node[path_string][:].tolist()
    return [NUMBER_FORMAT.format(x) for x in temp_list]


def export_xps_data(region, filename):
    """Format kinetic_energy vs intensity data and trigger writing to
    a file
    """

    title_list = ["kinetic_energy", "intensity"]
    ke_list = [NUMBER_FORMAT.format(x)
               for x in region["kinetic_energy"][:].tolist()]
    intensity = [NUMBER_FORMAT.format(x)
                 for x in region["spectrum"][0][:].tolist()]
    zipped = zip(ke_list, intensity)
    region_name = region.name.split("/")[-1]
    filename = filename.split(".")[0] + "_" + region_name + "_XPS.dat"
    filename = filename.replace(" ", "_")
    write_data_out(filename, title_list, zipped)
    print "Data for region {} written to file {}".format(region_name,
                                                         filename)


def write_data_out(filename, title_list, zipped):
    """Write out the zipped list of data to a file."""

    output_path = os.path.join(ARGS.data_dir_path, filename)
    with open(output_path, 'w') as output_file:
        writer = csv.writer(output_file, delimiter='\t')
        if ARGS.titles_on:
            writer.writerow(title_list)
        writer.writerows(zipped)


def main():
    """One function to rule them all"""
    file_list = collect_files(ARGS.data_dir_path)
    print "-" * 20
    print "\n{} nexus files found in directory".format(len(file_list))
    for filepath in file_list:
        instrument_node = get_instrument_node(filepath)
        if instrument_node:
            output_data(instrument_node, filepath)


if __name__ == '__main__':

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("data_dir_path", help=("Full path to the data directory"
                                               " containing the files that you "
                                               "want to convert"))
    PARSER.add_argument("--titles_on", help="Switch on column titles",
                        action="store_true")
    ARGS = PARSER.parse_args()
    main()
