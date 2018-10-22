
import time;

def uvSpeedTesting(imageFunExpression, numberOfRun):
    totalTime=0.;
    for i in range(numberOfRun):
        t0=time.time();
        exec(imageFunExpression);
        t1=time.time();
        td=t1-t0;
        totalTime += td;
        time.sleep(1);

    averageTime=1.0*totalTime/numberOfRun;
    return averageTime;

def runTest():

    numberOfRun=10;
    averageTime=uvSpeedTesting("uv.singleShot()", numberOfRun);
    print "Single shot without integration time setting: " + str(averageTime);

    averageTime=uvSpeedTesting("uv.singleShot(1)", numberOfRun);
    print "Single shot with integration time setting: " + str(averageTime);
    
    numberOfRun=1;
    numberOfImages=10;
    
    averageTime=uvSpeedTesting("uv.multiSafeShot(10, None, False)", numberOfRun)
    print "Safe multishot in old folder without integration time setting: " + str(averageTime/numberOfRun);

    averageTime=uvSpeedTesting("uv.multiSafeShot(10, 1, False)", numberOfRun)
    print "Safe multishot in old folder with integration time setting: " + str(averageTime/numberOfRun);

    averageTime=uvSpeedTesting("uv.multiSafeShot(10, None, True)", numberOfRun)
    print "Safe multishot in new folder without integration time setting: " + str(averageTime/numberOfRun);

    averageTime=uvSpeedTesting("uv.multiSafeShot(10, 1, True)", numberOfRun)
    print "Safe multishot in new folder with integration time setting: " + str(averageTime/numberOfRun);


"""
>>>uv.setFileFormat('tif')
>>>run "scratch/uvTesting"
>>>runTest()
Single shot without integration time setting: 1.34160001278
Single shot with integration time setting: 1.48869998455
Safe multishot in old folder without integration time setting: 13.3420000076
Safe multishot in old folder with integration time setting: 13.5250000954
Safe multishot in new folder without integration time setting: 13.8239998817
Safe multishot in new folder with integration time setting: 13.9500000477
>>>uv.setFileFormat('png')
>>>runTest()
Single shot without integration time setting: 1.7496999979
Single shot with integration time setting: 1.9098000288
Safe multishot in old folder without integration time setting: 17.4019999504
Safe multishot in old folder with integration time setting: 17.5309998989
Safe multishot in new folder without integration time setting: 17.7699999809
Safe multishot in new folder with integration time setting: 17.8420000076

"""