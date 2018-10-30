import optparse
import numpy as np
import subprocess
import os


def wait_for_file(filepath, mode=os.R_OK, sleepdelta=3, niter=60):
    """
    Waits for file to be accessible in given access mode
    Returns True if file was successfully accessed in given mode within specified number of attempts
    
    filepath: the path to file to be accessed 
    mode: the file mode in which file is to be accessed, eg os.R_OK
    sleepdelta: time interval in seconds between two consecutive attempts to access file; default=1, 
    niter: max number of file-access attempts to be made; default=60
    """

    cnt = 0
    inaccessible = True 
    #wait for file to become accessible in given mode
    while inaccessible and (cnt < niter):
        if os.access(filepath, mode):
            inaccessible = False
            print "File %s was successfully accessed on count = %i" %(filepath, cnt)
        else:
            cnt += 1
            time.sleep(sleepdelta)
            #print " %i zzz..." %(cnt)
    return (not inaccessible)        

if __name__ == '__main__' :
    
    usage = "%prog [options] indir oudir"
    parser = optparse.OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-b", "--begin", dest="begin", help="Rank of the first input file to be processed (default: 0)", default=0, type='int')
    parser.add_option("-n", "--nfiles", dest="nfiles", help="Total number of input files to be processed (default: 1)", default=1, type='int')
    parser.add_option("-r", "--nranks", dest="nranks", help="Total number of frame receiver-processor pairs (default: 4)", default=4, type='int')
    parser.add_option("-i","--in_fmt", dest="in_fmt", help="Filename format for the input files (default: 'excalibur_%s_r%d.h5')", default='excalibur_%s_r%d.h5')
    parser.add_option("-o","--out_fmt", dest="out_fmt", help="Prefix for the output files (default: 'excalibur_%s')", default='excalibur_%s')
    parser.add_option("-u", "--utype", dest="utype", help="Bit-depth of data in the input files (default: 16)", default=16, type='int')
    parser.add_option("-s","--scan_id", dest="scan_id", help="Scan number (or some unique ID)")
    parser.add_option("-l", "--log", dest="log", help="Log level (default: 2)", default=2, type='int')
    
    (options, args) = parser.parse_args()

    # any logging?

    dirpath = args[0]

    scan_id = options.scan_id

    dtypes = {16: "uint16", 32: "uint32"}
    dtype = dtypes[options.utype]
    print("Input data type: %s" % (dtype))

    # note the trailing white space (for later use)!
    interleaved_fname = options.out_fmt %(scan_id)
    interleaved_fname += "_inter.h5"    # excalibur_<scan number>_inter.h5
     
    gapfilled_fname = options.out_fmt %(scan_id)
    gapfilled_fname += "_vds.h5"      # excalibur_<scan number>_vds.h5     

    in_fname = options.in_fmt
    ind_from = options.begin
    ind_to = ind_from + options.nfiles

    in_fname_template = options.in_fmt + " "
    in_fnames = ""
    for i in range(ind_from, ind_to):
        in_fnames += in_fname_template %(scan_id, i)

    # create the interleaved vds
    scriptpath = "/dls_sw/prod/tools/RHEL6-x86_64/defaults/bin/dls-vds-gen.py"
    cmd = scriptpath
    cmd += " %s" %(dirpath)
    cmd += " -f %s" %(in_fnames)
    cmd += " -t %s" %(dtype)
    cmd += " --mode interleave"
    cmd += " -l %d" %(options.log)
    cmd += " -o %s" %(interleaved_fname)
    print("Command to create the interleaved VDS file: %s" %(cmd))

    interleaved_proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
    interleaved_result = interleaved_proc.communicate()
    print interleaved_result

    interleaved_fpath = os.path.join(dirpath, interleaved_fname)
    interleaved_accessible = wait_for_file(interleaved_fpath)

    gapfilled_fpath = os.path.join(dirpath, gapfilled_fname)

    if interleaved_accessible:
        # Check the output file exists and, if it does, append timestamp to its name 
        # execute the command

        # wait for output file to appear on the file system before running the next command (with timeout?)

        # Check the output file exists and, if it does, append timestamp to its name 
        # execute the next command, adjusting if necessary the input and output filenames 

        # create the gap-filled vds
        cmd = scriptpath
        cmd += " %s" %(dirpath)
        cmd += " -f %s" %(interleaved_fname)
        cmd += " -t %s" %(dtype)
        cmd += " --mode gap-fill -M 3 -s 3 -m 124 -F -1"
        cmd += " -l %d" %(options.log)
        cmd += " -o %s" %(gapfilled_fname)
        print("Command to create the gap-filled VDS file: %s" %(cmd))

        gapfilled_proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
        gapfilled_result = gapfilled_proc.communicate()
        print gapfilled_result
    else:
        print("Failed to access the interleaved VDS file %s, so NOT attempting to create the gap-filled VDS file %s!" %(interleaved_fpath, gapfilled_fpath))
        
    print("All done - bye!")

 

    
 
