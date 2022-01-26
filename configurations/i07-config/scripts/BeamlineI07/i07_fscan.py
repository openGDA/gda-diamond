from gdascripts.mscanHandler import *

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
        mscan(motor, axis, start, end, step, arg_step, cont, detector, count / float(1000))

    elif len(args) == 9:
        # dual motor scan
        (motor1, start1, end1, motor2, start2, end2, step1, detector, count) = args
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
        mscan(motor, axis, start, end, pts, points, cont, detector, count / float(1000))

    elif len(args) == 9:
        # dual motor scan
        (motor1, start1, end1, motor2, start2, end2, points, detector, count) = args
        mscan(motor1, motor2, line, start1, start2, end1, end2, pts, points, cont, detector, count / float(1000))
    else:
        print "fpscan syntax:\n"
        print "Single motor:"
        print "   fpscan motor start end points detector count_in_milliseconds"
        print "Dual motor:"
        print "   fpscan motor1 start1 end1 motor2 start2 end2 points detector count_in_milliseconds"

