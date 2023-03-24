from dummy.insitu.utils import get_scan_request, pprint_scan_request, run_scan

scan_1 = get_scan_request("scan1.json")
scan_2 = get_scan_request("scan2.json")
scan_3 = get_scan_request("scan3.json")

pprint_scan_request("scan1.json")

run_scan(scan_1, name="scan1", num_repetitions=3)
run_scan(scan_2, name="scan2", num_repetitions=2)
run_scan(scan_3, name="scan3")
    
print("Scans done")
