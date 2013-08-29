#
# This script is now deprecated. If you wish to collect a single spectrum then
# run from Jython:
#
# xstrip.loadParameters(EdeScanParameters.createSingleFrameScan(time_per_scan_in_s, number_of_scans)
# xstrip.collectData()
# xstrip.readFrameToArray(0)
#
# Alternatively to run a regular step scan and collect a spectrum at each point
# use the step scan detector objects: ssxh and ssxstrip.
#
# e.g. scan sample_x 1 10 1 ssxstrip 1
#
# If you wish to run a 'proper' experiment which collect darks and I0 and then
# normalises then use the singlescan.py script. 
#

