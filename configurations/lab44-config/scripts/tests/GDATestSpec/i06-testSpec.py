'''
Created on 3 Dec 2018

@author: fy65
'''
from utils.ExceptionLogs import localStation_exception, localStation_exceptions
from datetime import date, datetime

#undulator/pgm/energy
try:
    pos smode idd
except:
    localStation_exception(sys.exc_info(), "test - 'pos smode idd'")
try:
    pos pol pc
except:
    localStation_exception(sys.exc_info(), "test - 'pos pol pc'")
try:    
    pos energy 400
except:
    localStation_exception(sys.exc_info(), "test - 'pos energy 400' in 'idd' and 'pc' mode")

try:
    pos smode idu
except:
    localStation_exception(sys.exc_info(), "test - 'pos smode idu'")
try:
    pos pol nc
except:
    localStation_exception(sys.exc_info(), "test - 'pos pol nc'")
try:  
    pos energy 400
except:
    localStation_exception(sys.exc_info(), "test - 'pos energy 400' in 'idu' and 'nc' mode")
   
try:
    pos smode dpu
except:
    localStation_exception(sys.exc_info(), "test - 'pos smode dpu'")
try:
    pos pol lh
except:
    localStation_exception(sys.exc_info(), "test - 'pos pol lh'")
try:
    pos energy 400
except:
    localStation_exception(sys.exc_info(), "test - 'pos energy 400' in 'dpu' and 'lh' mode")

try:
    pos smode dmu
except:
    localStation_exception(sys.exc_info(), "test - 'pos smode dmu'")
try:
    pos pol lv
except:
    localStation_exception(sys.exc_info(), "test - 'pos pol lv'")
try:
    pos energy 400
except:
    localStation_exception(sys.exc_info(), "test - 'pos energy 400' in 'dmu' and 'lv' mode")

#scan
try:
    scan energy 395 405 1 pcotif 1 ca52sr 1
except:
    localStation_exception(sys.exc_info(), "test - 'scan energy 395 405 1 pcotif 1 ca52sr 1'")
   
try:
    scan pol (pc nc) energy (410 400) t 1 2 1 pcotif 1 ca52sr 1
except:
    localStation_exception(sys.exc_info(), "test - 'scan pol (pc nc) energy (410 400) t 1 2 1 pcotif 1 ca52sr 1'")

#leem2000 communication
try:
    obj_start = leem_obj.getPosition()
except:
    localStation_exception(sys.exc_info(), "test - 'leem_obj.getPosition()'")
try:
    pos leem_obj obj_start+10
except:
    localStation_exception(sys.exc_info(), "test - 'pos leem_obj obj_start+10'")
try: 
    pos leem_obj obj_start
except:
    localStation_exception(sys.exc_info(), "test - 'pos pos leem_obj obj_start'")

#selected motors tests
try:
    pos s4ygap 100
except:
    localStation_exception(sys.exc_info(), "test - 'pos s4ygap 100'")
try:   
    pos s4ygap 25
except:
    localStation_exception(sys.exc_info(), "test - 'pos s4ygap 25'")

try:
    pos d6y -41
except:
    localStation_exception(sys.exc_info(), "test - 'pos d6y -41'")
try:
    pos d6y -16
except:
    localStation_exception(sys.exc_info(), "test - 'pos d6y -16'")

#zacscan
#zacscan ......
messages=""
if not localStation_exceptions:
    for each in localStation_exceptions:
        messages=messages+'\n'+str(each)
if not messages:
    messages=messages+"\n"
else:
    messages="Test completed without any error."
    
print messages
testlogfilename="/scratch/GDATestSpecsOutput_"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S".log
with open(testlogfilename, 'w') as testlog
    testlog.write(messages)
print "Test results are stored in file: " + testlogfilename

