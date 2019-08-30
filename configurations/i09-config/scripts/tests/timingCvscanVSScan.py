'''
Created on 30 Aug 2019

@author: fy65
'''

def test_time_taken_difference():
    start_cvscan_time=time.time()
    cvscan(cenergy, 0.500, 0.550, 0.0002, mcs3, 0.1, mcs4, mcs5)
    end_cvscan_time=time.time()
    start_scan_time=time.time()
    scan([cenergy, 0.500, 0.550, 0.0002, mcs3, 0.1, mcs4, mcs5])
    end_scan_time=time.time()
    print "time taken for cvscan %f" % (end_cvscan_time-start_cvscan_time)
    print "time taken for scan %f" % (end_scan_time-start_scan_time)
    
if __name__ == '__main__':
    test_time_taken_difference()