from time import sleep


print "\n Running test_scan.py"


def run_scans(start, stop, n_img, n_scans, expo_tm, speed_fwd, speed_bwd, extra=2.0, eps=0.01, sec2sleep=1, max_attempts=10):
    """
    Charan's magical function to run a sequence of repscans while rotation stage is moving, at a precalculated constant speed, from start angle to stop angle
    Arg(s)
        start: start position of rotation stage
        stop: stop position of rotation stage
        n_img: number of images per single scan
        n_scans: total number of scans to be run
        expo_tm: exposure time for each image
        speed_fwd: rotation speed forward, ie for moving from -90 to +90 (this speed needs to be provided by the user and it needs to match n_img and expo_tm)
        speed_bwd: rotation speed backward, ie from +90 to -90 (any safe value)
        eps: threshold for checking if rotation stage is at start position
        extra: positive angular amount for run-up and overshoot of start and stop positions, ie -90-extra and +90+extra 
        sec2sleep: amount of time to sleep between polling values in while loops
        max_attempts: maximum number of attempts in while loops (to avoid infinite loops)
    """
    _fname = run_scans.__name__
    print "Running %s" %(_fname)
    rot_stage = t1_theta
    
    speed_saved = rot_stage.getSpeed()
    try:
        # calc effective start and stop pos 
        start_eff = start - extra
        stop_eff = stop + extra
        # set rot speed to speed_fwd
        t1_theta.setSpeed(speed_bwd)
        # move rot stage to start_eff
        print "Moving rot stage to start pos of %f at speed %f..." %(start_eff,speed_bwd)
        rot_stage.moveTo(start_eff)
        print "Finished moving rot stage to start pos of %f at speed %f" %(start_eff,speed_bwd)
        t1_theta.setSpeed(speed_fwd)
        # move rot stage to stop_eff
        print "Moving rot stage asynchronously to stop pos of %f at speed %f..." %(stop_eff,speed_fwd)
        rot_stage.asynchronousMoveTo(stop_eff)
        nattempts = 0
        for i in range(n_scans):
            while abs(rot_stage.getPosition()-start) > eps and nattempts < max_attempts:
                print "Sleeping for %fs while waiting for rot stage to be at start pos of %f (attempt %i)..." %(sec2sleep,start_eff,nattempts)
                sleep(sec2sleep)
                print "Finished sleeping for %f s while waiting for rot stage to be at start pos of %f (attempt %i)" %(sec2sleep,start_eff,nattempts)
                nattempts += 1
            if nattempts < max_attempts:
                print "Running scan %i (of %i)..." %(i+1,n_scans)
                #repscan n_img merlin_config_no_chunking expo_tm
                print "repscan n_img merlin_config_no_chunking expo_tm"
                
                # fudge - BEGIN!
                while abs(rot_stage.getPosition()-stop) > eps:
                    sleep(5)
                # fudge - END!
                
                print "Finished running scan %i (of %i)..." %(i+1,n_scans)
                nattempts = 0
                while rot_stage.isBusy() and nattempts < max_attempts:
                    print "Sleeping for %fs while waiting for rot stage to be not busy (attempt %i)..." %(sec2sleep,nattempts)
                    sleep(sec2sleep)
                    print "Finished sleeping for %f s while waiting for rot stage to be not busy (attempt %i)" %(sec2sleep,nattempts)
                    nattempts += 1
                if nattempts < max_attempts:
                    # set rot stage to speed_bwd
                    t1_theta.setSpeed(speed_bwd)
                    # move rot stage to start_eff
                    print "Moving rot stage to start pos of %f at speed %f..." %(start_eff,speed_bwd)
                    rot_stage.moveTo(start_eff)
                    print "Finished moving rot stage to start pos of %f at speed %f" %(start_eff,speed_bwd)
                    if i < n_scans-1:
                        # set rot stage to speed_fwd
                        t1_theta.setSpeed(speed_fwd)
                        # move rot stage to stop_eff
                        print "Moving rot stage asynchronously to stop pos of %f at speed %f..." %(stop_eff,speed_fwd)
                        rot_stage.asynchronousMoveTo(stop_eff)
                    else:
                        # reset rot speed to saved value coz no more scans to run
                        rot_stage.setSpeed(speed_saved)
                else:
                    print "Timed out on waiting for rot stage to be not busy - aborting the loop at scan %i!" %(i+1,)
                    break
            else:
                print "Failed to catch rot start pos of %f - aborting the loop at scan %i!" %(start, i+1)
                break
    except:
        print "Trouble in run_scans!"
    finally:
        nattempts = 0
        while rot_stage.isBusy() and nattempts < max_attempts:
            sleep(5)
            nattempts += 1
        if nattempts < max_attempts:
            # reset rot speed to saved value on exception or at the end of 
            rot_stage.setSpeed(speed_saved)
        else:
            print "Failed to restore the speed to %f at the very end - rotation stage is busy!" %(speed_saved,)

    print "Finished running %s - bye!" %(_fname)


