from gdaserver import GDAMetadata as meta
import time

def wait_for_calibration():
    print 'Waiting for calibration to complete'
    start = time.time()
    timeout = start + 300
    while time.time() < timeout:
        if meta['calibration_file']:
            break
        time.sleep(2)
    else:
        print('WARNING: No calibration result received after 300s')