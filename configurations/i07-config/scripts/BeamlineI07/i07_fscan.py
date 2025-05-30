from gdascripts.mscanHandler import mscan as mscan_master, submit, axis, cont, line, pts, step
from org.eclipse.scanning.api.points.models import AxialArrayModel, ConcurrentMultiModel, CompoundModel
from org.eclipse.scanning.sequencer import ScanRequestBuilder
from gda.scan import ImplicitScanObject
from gda.device.scannable import ScannableUtils
import scisoftpy as dnp
import datetime as fscan_datetime
from org.eclipse.scanning.api.scan import ScanningException

def log_error(error_message):
    timestamp = fscan_datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file = "/dls_sw/i07/logs" + '/malcolmErrorLog.txt'
    with open(log_file, 'a') as file:
        file.write('%s ERROR: %s\n' % (timestamp, error_message))

def perform_scan(args, motors_to_reset=[], scan_method=mscan_master):
    reset_posns = {}
    for motor in motors_to_reset :
        reset_posns[motor] = motor.getPosition()
    tries = 0
    while tries < 3:
        try:
            return scan_method(*args)
        except ScanningException as e:
            print "Error encountered running malcolm scan, attempting to restart.  Error is seen below."
            print 'ERROR:', e
            log_error(e)
            tries += 1
            for motor in motors_to_reset :
                pos(motor, reset_posns[motor])
    else:
        print 'Maximum number of tries reached'

def mscan(*args_here):
    perform_scan(args=args_here)

def fscan(*args):
    '''
    Continuous scan of one or two motors, specifying the step size.

    Syntax:
       fscan motor start end step_size detector count_in_milliseconds
       fscan motor1 start1 end1 motor2 start2 end2 step_size1 detector count_in_milliseconds
    '''
    if len(args) == 6:
        # single motor scan
        (motor, start, end, arg_step, detector, count) = args
        pos(motor, start)
        perform_scan(motors_to_reset=[motor], args=[motor, axis, start, end, step, arg_step, cont, detector, count / float(1000)])

    elif len(args) == 9:
        # dual motor scan
        (motor1, start1, end1, motor2, start2, end2, step1, detector, count) = args
        pos(motor1, start1, motor2, start2)
        points = abs(int((end1 - start1)/step1) + 1)
        perform_scan(motors_to_reset=[motor1, motor2], args=[motor1, motor2, line, start1, start2, end1, end2, pts, points, cont, detector, count / float(1000)])
    else:
        print "fscan syntax:\n"
        print "Single motor:"
        print "   fscan motor start end step_size detector count_in_milliseconds"
        print "Dual motor:"
        print "   fscan motor1 start1 end1 motor2 start2 end2 step_size1 detector count_in_milliseconds"

def cfscan(*args):
    '''
    Centred continuous scan, same as fscan but specify width rather than start/end points

    Syntax:
       cfscan motor halfwidth step_size detector count_in_milliseconds
       cfscan motor centre halfwidth step_size detector count_in_milliseconds
    '''
    if len(args) == 5:
        (motor, halfwidth, step, detector, count) = args
        centre = motor.getPosition()
        (start, end) = centre-halfwidth, centre+halfwidth
        fscan(motor, start, end, step, detector, count)
        pos(motor, centre)
    elif len(args) == 6:
        (motor, centre, halfwidth, step, detector, count) = args
        (start, end) = centre-halfwidth, centre+halfwidth
        fscan(motor, start, end, step, detector, count)
        pos(motor, centre)
    else:
        print "cfscan syntax:\n"
        print "At current position:"
        print "   cfscan motor halfwidth step_size detector count_in_milliseconds"
        print "At arbitrary position (centre):\n"
        print "   cfscan motor centre halfwidth step_size detector count_in_milliseconds"


def fpscan(*args):
    '''
    Continuous scan of one or two motors, specifying the number of points.

    Syntax:
       fpscan motor start end points detector count_in_milliseconds
       fpscan motor1 start1 end1 motor2 start2 end2 points detector count_in_milliseconds
    '''
    if len(args) == 6:
        # single motor scan
        (motor, start, end, points, detector, count) = args
        pos(motor, start)
        if(points == 1) : #the mscan practice of treating the point positions as the centre of a region gives odd
            #results when only a single point is requested.  This should make the points make more sense
            halfwidth = (end-start) / 2.0
            perform_scan(motors_to_reset=[motor], args=[motor, axis, start + halfwidth, end + halfwidth, pts, points, cont, detector, count / float(1000)])
        else :
            perform_scan(motors_to_reset=[motor], args=[motor, axis, start, end, pts, points, cont, detector, count / float(1000)])

    elif len(args) == 9:
        # dual motor scan
        (motor1, start1, end1, motor2, start2, end2, points, detector, count) = args
        pos(motor1, start1, motor2, start2)
        if(points == 1) : #the mscan practice of treating the point positions as the centre of a region gives odd
            #results when only a single point is requested.  This should make the points make more sense
            hw1 = (end1-start1) / 2.0
            hw2 = (end2-start2) / 2.0
            perform_scan(motors_to_reset=[motor1, motor2], args=[motor1, motor2, line, start1+hw1, start2+hw2, end1+hw1, end2+hw2, pts, points, cont, detector, count / float(1000)])
        else :
            perform_scan(motors_to_reset=[motor1, motor2], args=[motor1, motor2, line, start1, start2, end1, end2, pts, points, cont, detector, count / float(1000)])

    else:
        print "fpscan syntax:\n"
        print "Single motor:"
        print "   fpscan motor start end points detector count_in_milliseconds"
        print "Dual motor:"
        print "   fpscan motor1 start1 end1 motor2 start2 end2 points detector count_in_milliseconds"

def fhklscan_e(hkl, start, stop, step, runnable_device, exposure_time):

    # e.g. fhklscan([0, 0.6, 0.6], [0, 0.6, 2.0], [0.0, 0.0, 0.1], m1, 1)

    # TODO validate args
    diff_group =  hkl.diffhw

    # Use classic scan's ImplicitScanObject to gen points from start stop step
    sobj = ImplicitScanObject(hkl, start, stop, step)
    num_points = sobj.getNumberPoints()
    hkl_posns = [sobj.getStart()]
    for _ppt in range(num_points - 1):
        hkl_posns += [ScannableUtils.calculateNextPoint(hkl_posns[-1], sobj.getStep())]

    angles = []
    for posn in hkl_posns:
        angles += [hkl._diffcalc.hkl_to_angles(posn[0], posn[1], posn[2])[0]]
    angles_ds = dnp.array(angles)

    cmodel = ConcurrentMultiModel()
    for idx, axis in enumerate(diff_group.getGroupMembersAsArray()):
        model = AxialArrayModel(axis.getName())
        model.setPositions(angles_ds[:, idx].tolist())
        model.setContinuous(True)
        cmodel.addModel(model)

    scan_model = CompoundModel([cmodel])

    det_model = runnable_device.getModel()
    det_model.setExposureTime(exposure_time)

    dets = {runnable_device.getName(): det_model}

    # TODO add monitors, per point and per scan
    request = ScanRequestBuilder().withCompoundModel(scan_model).withDetectors(dets).build()

    pos(hkl, start)
    submit(request)

def fhklscan(hkl, start, stop, step, runnable_device, exposure_time):
    perform_scan(scan_method=fhklscan_e, args=[hkl, start, stop, step, runnable_device, exposure_time])
