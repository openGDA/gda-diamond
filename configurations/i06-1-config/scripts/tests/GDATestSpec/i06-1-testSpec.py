'''
Created on 3 Dec 2018

@author: fy65
'''
#Check smode, polarisation and energy moves
try:
    pos smode idu
except:
    localStation_exception(sys.exc_info(), "test - 'pos smode idu'")
try:
    pos pol lv
except:
    localStation_exception(sys.exc_info(), "test - 'pos pol lv'")
try:
    pos energy 701
except:
    localStation_exception(sys.exc_info(), "test - 'pos energy 701' in 'idu' and 'lv' mode")

try:
    pos smode dmu
except:
    localStation_exception(sys.exc_info(), "test - 'pos smode dmu'")
try:
    pos pol pc
except:
    localStation_exception(sys.exc_info(), "test - 'pos pol pc'")
try:
    pos energy 700
except:
    localStation_exception(sys.exc_info(), "test - 'pos energy 700' in 'dmu' and 'pc' mode")

try:
    pos smode dpu
except:
    localStation_exception(sys.exc_info(), "test - 'pos smode dpu'")
try:
    pos pol nc
except:
    localStation_exception(sys.exc_info(), "test - 'pos pol nc'")
try:
    pos energy 701
except:
    localStation_exception(sys.exc_info(), "test - 'pos energy 701' in 'dpu' and 'nc' mode")


try:
    pos smode idd
except:
    localStation_exception(sys.exc_info(), "test - 'pos smode idd'")
try:
    pos pol pc
except:
    localStation_exception(sys.exc_info(), "test - 'pos pol pc'")
try:    
    pos energy 450
except:
    localStation_exception(sys.exc_info(), "test - 'pos energy 450' in 'idd' and 'pc' mode")


#Check s6 slits
try:
    pos s6ygap 100
except:
    localStation_exception(sys.exc_info(), "test - 'pos s6ygap 100'")
try:
    pos s6xgap 20
except:
    localStation_exception(sys.exc_info(), "test - 'pos s6xgap 20'")

try:
    pos d10y -72.4
except:
    localStation_exception(sys.exc_info(), "test - 'pos d10y -72.4'")

#Energy scans
try:
    scan energy 455 465 0.1 ca62sr 1 ca142sr 1
except:
    localStation_exception(sys.exc_info(), "test - 'scan energy 455 465 0.1 ca62sr 1 ca142sr 1'")
try:
    zacscan 455 475 50 0.3
except:
    localStation_exception(sys.exc_info(), "test - 'zacscan 455 475 50 0.3'")

try:
    pos d10y -0.5
except:
    localStation_exception(sys.exc_info(), "test - 'pos d10y -0.5'")

# check SCM motors
try:
    pos scmth 
except:
    localStation_exception(sys.exc_info(), "test - 'pos scmth'")
try:
    pos scmy
except:
    localStation_exception(sys.exc_info(), "test - 'pos scmy'")

#Check SCM magnetic field
try:
    pos magx
except:
    localStation_exception(sys.exc_info(), "test - 'pos magx'")
try:
    pos magy
except:
    localStation_exception(sys.exc_info(), "test - 'pos magy'")
try:
    pos magz
except:
    localStation_exception(sys.exc_info(), "test - 'pos magz'")

#check DD motors
try:
    pos ddth
except:
    localStation_exception(sys.exc_info(), "test - 'pos ddth'")
try:
    pos dd2th
except:
    localStation_exception(sys.exc_info(), "test - 'pos dd2th'")
try:
    pos dddy
except:
    localStation_exception(sys.exc_info(), "test - 'pos dddy'")
try:
    pos ddchi
except:
    localStation_exception(sys.exc_info(), "test - 'pos ddchi'")
try:
    pos ddphi
except:
    localStation_exception(sys.exc_info(), "test - 'pos ddphi'")
try:
    pos ddsx
except:
    localStation_exception(sys.exc_info(), "test - 'pos ddsx'")
try:
    pos ddsy
except:
    localStation_exception(sys.exc_info(), "test - 'pos ddsy'")
try:
    pos ddsz
except:
    localStation_exception(sys.exc_info(), "test - 'pos ddsz'")
    
messages=""
if not localStation_exceptions:
    for each in localStation_exceptions:
        messages=messages+'\n'+str(each)
if not messages:
    messages=messages+"\n"
else:
    messages="Test completed without any error."
    
print messages
testlogfilename="/scratch/GDATestSpecsOutput_"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S").log
with open(testlogfilename, 'w') as testlog
    testlog.write(messages)
print "Test results are stored in file: " + testlogfilename

