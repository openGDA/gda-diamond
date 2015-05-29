import numpy as np
import h5py
from optparse import OptionParser

def detectorLinkInserter(nexusFileName, detectorFileName, nexusPathList, detectorPath):
    nexusFile = h5py.File(nexusFileName, "a")
    for path in nexusPathList:
        entry = nexusFile[path]
        entry['data'] = h5py.ExternalLink(detectorFileName, detectorPath)
    nexusFile.close()

if __name__ == "__main__":
    parser = OptionParser(usage = "usage: %prog [options] nexusFileName detectorFileName")
    parser.add_option("--nexusPathList", dest="nexusPathList", default="/entry1/instrument/simd,entry1/simd")
    parser.add_option("--detectorPath", dest="detectorPath", default="/entry/instrument/detector/data")
    (options, args) = parser.parse_args()

    detectorLinkInserter(args[0], args[1], options.nexusPathList.split(","), options.detectorPath)
