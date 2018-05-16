'''
examples of creating a long counting time scaler object.

Created on 4 Nov 2010

@author: fy65
'''
from long_count_time_scaler_class import LongCountTimeScaler

deviceName = "BL12I-EA-DET-01"
pv_scaler = deviceName + ":SCALER"
pv_mca = deviceName + ":MCA-01"
dwelltime = 0.1

I0oh2l=LongCountTimeScaler("I0oh2l", pv_scaler, pv_mca, 17, dwelltime)
I0eh1l=LongCountTimeScaler("I0eh1l", pv_scaler, pv_mca, 18, dwelltime)
I0eh2l=LongCountTimeScaler("I0eh2l", pv_scaler, pv_mca, 19, dwelltime)