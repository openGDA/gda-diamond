# Script to be called by the Standards scan GUI
# It passes the contents of the energy and exposure time text boxs to standards_scan()
# The values to be passed must have been set as named values in the script service as
# "scanPath" and "exposureTime" respectively.

print("Running submit_standards_scan.py")
standards_scan(scanPath, exposureTime)
