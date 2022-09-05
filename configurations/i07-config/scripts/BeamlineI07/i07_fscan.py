from gdascripts.mscanHandler import *
from org.eclipse.scanning.api.points.models import AxialArrayModel, ConcurrentMultiModel, CompoundModel
from org.eclipse.scanning.sequencer import ScanRequestBuilder
from gda.scan import ImplicitScanObject
from gda.device.scannable import ScannableUtils
import scisoftpy as dnp

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
        mscan(motor, axis, start, end, step, arg_step, cont, detector, count / float(1000))

    elif len(args) == 9:
        # dual motor scan
        (motor1, start1, end1, motor2, start2, end2, step1, detector, count) = args
        pos(motor1, start1, motor2, start2)
        points = int((end1 - start1)/step1) + 1
        mscan(motor1, motor2, line, start1, start2, end1, end2, pts, points, cont, detector, count / float(1000))
    else:
        print "fscan syntax:\n"
        print "Single motor:"
        print "   fscan motor start end step_size detector count_in_milliseconds"
        print "Dual motor:"
        print "   fscan motor1 start1 end1 motor2 start2 end2 step_size1 detector count_in_milliseconds"

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
        mscan(motor, axis, start, end, pts, points, cont, detector, count / float(1000))

    elif len(args) == 9:
        # dual motor scan
        (motor1, start1, end1, motor2, start2, end2, points, detector, count) = args
        pos(motor1, start1, motor2, start2)
        mscan(motor1, motor2, line, start1, start2, end1, end2, pts, points, cont, detector, count / float(1000))
    else:
        print "fpscan syntax:\n"
        print "Single motor:"
        print "   fpscan motor start end points detector count_in_milliseconds"
        print "Dual motor:"
        print "   fpscan motor1 start1 end1 motor2 start2 end2 points detector count_in_milliseconds"


def fhklscan(hkl, start, stop, step, runnable_device, exposure_time):

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
    for pos in hkl_posns:
        angles += [hkl._diffcalc.hkl_to_angles(pos[0], pos[1], pos[2])[0]]
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

    submit(request)

