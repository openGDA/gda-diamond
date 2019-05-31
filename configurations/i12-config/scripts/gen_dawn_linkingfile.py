import os
import optparse
import time
import glob
import csv

import re
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

#82497-pilatus2M-files-2019-01-09T19-44-47-#869of8687.dawn

#    # DIR_NAME: indir_path
#    # DATASET_NAME: dset_name[0]
#    [# DATASET_NAME: dset_name[1]]
#    # SHAPE: 3,4
#    # FILE_NAME
#    in_fname[0]
#   in_fname[1]
#    in_fname[2]

#    For example
#    # DIR_NAME: /home/me/data/tiffs/
#    # DATASET_NAME: image-01
#    # SHAPE: 3,4
#    # FILE_NAME
#    00001.tif
#    00002.tif
#    00003.tif

if __name__ == "__main__" : 

    usage = "%prog [options] input_dir output_dir"
    parser = optparse.OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-b", "--begin", dest="begin", help="(zero-based) index from which to begin selection of files; default=0", default=0, type='int')
    parser.add_option("-n", "--nfiles", dest="nfiles", help="total number of files to select; default=-1 (ie all)", default=-1, type='int')
    parser.add_option("-d", "--dset", dest="dset", help="Nexus path to the dataset to link to; default='image-01'", default='image-01')
    parser.add_option("-s", "--step", dest="step", help="select every s-th file from the input directory; default=1", default=1, type='int')
    parser.add_option("-f", "--fmt", dest="fmt", help="filename format for the input files; default='*.cbf'", default='*.cbf')
    parser.add_option("-x", "--ext", dest="ext", help="filename extension for the output file; default='dawn'", default='dawn')
    parser.add_option("-a", "--all", dest="all", help="if supplied, all matching files in the input directory are selected, otherwise the (alphanumerically) last file is omitted (as it may still be in use for writing)", default=False, action="store_true")
    parser.add_option("-t", "--timestamp", dest="timestamp", help="if supplied, the output filename contains some additional stats and timestamp", default=False, action="store_true")
    parser.add_option("--dbg", dest="dbg", help=optparse.SUPPRESS_HELP, default=False, action="store_true")
    
    (options, args) = parser.parse_args()
    
    in_dir_path = args[0]
    in_dir_path_abs = os.path.abspath(in_dir_path)
    in_dir_path_abs = in_dir_path_abs.rstrip('/')
    print("in_dir_path_abs = %s" %(in_dir_path_abs))
    out_dir_path = args[1]
    print("out_dir_path = %s" %(out_dir_path))

    print("start ind = %s" %(options.begin))
    print("nfiles (pre) = %d" %(options.nfiles))
    print("step = %s" %(options.step))
    print("input fname format = %s" %(options.fmt))
    print("all = %s" %(options.all))
    print("timestamp = %s" %(options.timestamp))

    out_fname_ext = options.ext
    out_fname_ext.lstrip('.')

    timestr = time.strftime("%Y-%m-%dT%H-%M-%S")		# 2019-01-09T19-44-47

    # create output dir
    try:
        os.makedirs(out_dir_path)
    except OSError, e:
        if not os.path.isdir(out_dir_path):
            msg = "Output location %s is not a directory: " %(out_dir_path)
            raise ValueError(msg + str(e))

    in_dir_name = os.path.basename(in_dir_path_abs)

    fnames_lst = []
    if any(ch in options.fmt for ch in '?*'):
        for fpath in glob.glob(os.path.join(in_dir_path_abs, options.fmt)):
            fnames_lst.append(os.path.basename(fpath))

    #fnames_sorted_lst = sorted(fnames_lst if options.all else fnames_lst[:-1], key=natural_key)
    fnames_sorted_lst = sorted(fnames_lst, key=natural_key)

    fnames_sorted_len = len(fnames_sorted_lst)
    print("TOTAL number of input files = %d (sorted), %d (raw)" %(fnames_sorted_len,len(fnames_lst)))

    if options.dbg:
        dbg_n = min(3,fnames_sorted_len)
        for h in range(dbg_n):
            print("@%d: %s" %(h,fnames_sorted_lst[h]))
        for t in reversed(range(dbg_n)):
            print("@%d: %s" %(-t-1+fnames_sorted_len,fnames_sorted_lst[-t-1]))

    nfiles = min(options.nfiles,fnames_sorted_len) if options.nfiles > 0 else fnames_sorted_len
    print("nfiles (post) = %d" %(nfiles))
    start_ind_inc = options.begin
    end_ind_inc = start_ind_inc + nfiles - 1
    print("start_ind_inc = %d" %(start_ind_inc))
    print("end_ind_inc = %d" %(end_ind_inc))
    fnames_out_lst = fnames_sorted_lst[start_ind_inc:end_ind_inc+1:options.step]      

    fnames_out_len = len(fnames_out_lst)
    print("number of SELECTED input files = %d" %(fnames_out_len))
    
    if options.dbg:
        for h in range(dbg_n):
            print("@%d: %s" %(h,fnames_out_lst[h]))
        for t in reversed(range(dbg_n)):			# range(dbg_n-1,-1,-1)
            print("@%d: %s" %(-t-1+fnames_out_len,fnames_out_lst[-t-1]))

    out_fname_fmt = "%s-%s-#%d-of-%d.%s" 			# 82497-pilatus2M-files-2019-01-09T19-44-47-#869of8687.dawn
    if options.timestamp: 
        out_fname = out_fname_fmt %(in_dir_name, timestr, fnames_out_len, fnames_sorted_len, out_fname_ext)
    else:
        out_fname = "%s.%s" %(in_dir_name, out_fname_ext)	# allow overwriting of the same output file
    print("output fname = %s" %(out_fname))
    out_fpath = os.path.join(out_dir_path, out_fname)
    print("output fpath = %s" %(out_fpath))

    header_lines_lst = []
    header_lines_lst.append("# DIR_NAME: %s" %(in_dir_path_abs))
    header_lines_lst.append("# DATASET_NAME: %s" %(options.dset))
    #header_lines_lst.append("# SHAPE: %s" %())
    header_lines_lst.append("# FILE_NAME")

    lines_out_lst = []
    lines_out_lst.extend(header_lines_lst)
    lines_out_lst.extend(fnames_out_lst)

    with open(out_fpath, mode='w') as out_fh:
        writer = csv.writer(out_fh, delimiter='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for l in lines_out_lst:
            writer.writerow([l])

    print("All done - bye!")
