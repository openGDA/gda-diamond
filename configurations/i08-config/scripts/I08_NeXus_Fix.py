'''
Created on 26 Sep 2014

@author: ssg37927
original file in /dls_sw/i08/scripts/scisoft/
modified by dfq16044 on 13 Jan 2016
'''


import h5py
import os
import sys
import shutil
import numpy as np

if __name__ == "__main__":

    import optparse
    usage = "%prog NeXus_filename processed_directory"
    parser = optparse.OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    # this part was added to use the script automatically at the end of a scan.
    find_nexus = args[0].find("nexus")
    if (find_nexus == -1):
        print "nexus not present in the directory path"
        exit()

    root_directory = args[0][0:args[0].find("nexus")]
    new_path = root_directory + "processed/"
    # create this directory 
    if not os.path.exists(new_path):
        os.mkdir(new_path)
    
    new_filename = os.path.join(new_path, os.path.basename(args[0]))
    print "new_filename:",new_filename
    
    if os.path.exists(new_filename):
        os.remove(new_filename)

    print "original filename is : ",args[0]
    orig_file = h5py.File(args[0], 'r')

    orig_file_entry = orig_file["entry1"]
    print "orig_file_entry:",orig_file_entry.keys()
    
    if (not('_xmap' in orig_file_entry)):
        print "No Xmap used in this scan"
        exit()
        
    # this part is from the original script
    shutil.copy(args[0], os.path.dirname(new_filename))
    print "Starting corrections"
    
    # copy the andor file (Only if you need to), this was added as I08 staff required andor data available for PyMCA
    if '_andorrastor' in orig_file_entry:
        external_andor_file = orig_file['entry1/_andorrastor/data'].file.filename
        new_external_andor_filename = os.path.join(new_path,
                                         os.path.basename(external_andor_file))
        if os.path.exists(new_external_andor_filename):
            os.remove(new_external_andor_filename)
        shutil.copy(external_andor_file, new_path)
        print "external andor filename is : ", external_andor_file
        print "new external andor filename is : ", new_external_andor_filename
    
    print "new filename is : ", new_filename
    new_file = h5py.File(new_filename, 'a')

    # copy the xmap data file
    external_xmap_file = orig_file['entry1/_xmap/data'].file.filename
    new_external_xmap_filename = os.path.join(new_path,
                                         os.path.basename(external_xmap_file))
    if os.path.exists(new_external_xmap_filename):
        os.remove(new_external_xmap_filename)
    shutil.copy(external_xmap_file, new_path)

    print "external xmap filename is : ", external_xmap_file
    print "new external xmap filename is : ", new_external_xmap_filename

    # Now copying is complete, process the file.
    xmap_group = new_file['entry1'].create_group('xmap')
    xmap_group.attrs['NX_class'] = 'NXdata'

    for key in new_file['entry1/_xmap'].keys():
        if 'data' not in key:
            print "copying : ", key
            ds = new_file['entry1/_xmap'][key]
            xmap_group.create_dataset(key, ds.shape, ds.dtype, ds[...])

    # copy the raw data
    raw_data = new_file['entry1/_xmap/data']
    dshape = np.array(raw_data.shape[:])
    mask = np.ones(dshape.shape[0],np.bool)
    mask[-2] = False
    dshape = dshape[mask]
    xmap_group.create_dataset('data', dshape, raw_data.dtype)
    for i in range(raw_data.shape[0]):
        print i
        xmap_group['data'][i] = raw_data[i,:,0,:] # Was just 'i' when all detectors

    # now get the additional data in from the external file
    ext_file = h5py.File(new_external_xmap_filename, 'r')

    attr_group = ext_file['entry/instrument/NDAttributes']
    attr_shape = raw_data.shape[:-2] # -1 for all detectors
    for name in ('energy_live_time', 'events', 'icr', 'ocr', 'real_time',
                 'trigger_live_time', 'triggers'):
        print "Dealing with ", name
        parts = []
        for i in range(1):  # Was 4 for all detectors
            parts.append(attr_group["%s_ch_%i" % (name, i)][...])
        ds = np.dstack(parts).reshape(attr_shape)
        xmap_group.create_dataset(name, ds.shape, ds.dtype, ds[...])

    ext_file.close()
    new_file.close()

    # tidy up, as we don't need the other file now
    if os.path.exists(new_external_xmap_filename):
        os.remove(new_external_xmap_filename)
    #if os.path.exists(new_external_andor_filename):
    #    os.remove(new_external_andor_filename)


    print "Done"
