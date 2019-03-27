# Scripts for running XANES scanning in dummy mode

def run_xanes_scan_request(scanRequest, xanesEdgeParams):
    print("Running XANES scan")
    print("scanRequest = {0}".format(scanRequest))
    print("xanesEdgeParams = {0}".format(xanesEdgeParams))

    # For testing purposes, submit the same scan multiple times
    num_scans = 5
    for i in range(1, num_scans + 1):
        scan_name = "XANES scan {0} of {1}".format(i, num_scans)
        submit(scanRequest, block=False, name=scan_name)

def run_xanes_scan(params):
    print("Running XANES scan with parameters: {0}".format(params))