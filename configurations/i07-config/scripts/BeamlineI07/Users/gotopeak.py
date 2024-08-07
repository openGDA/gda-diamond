# Move to the peak of the last scan
# accepts motor(s) and detector as optional parameters, and attempts to work out
# intelligently which columns of the data file to use
#
# Jonathan Rawle, beamline I07, June 2010
#
# Note: use at your own risk! Moving certain combinations of motors may result in collisions
# and this script may not always move what/where you were expecting

from os import path
from array import array

peakFindMotors = []
peakFindDetector = ""

def peak(*args):
    global peakFindMotors, peakFindDetector

    (data, counts, headings, detectorName, motorNames, dispOnly, nexus) = peakFindCommon(args, "to peak in")

    counts = counts.tolist()
    peakPos = counts.index(max(counts))
    peakVal = max(counts)
    print " Peak is " + detectorName + '\x20=\x20' + str(peakVal)

    print "Moving to:"
    moveString = ""
    motorPos = []
    execString = "pos("
    for i in range(0, len(peakFindMotors)):
        if nexus:
            motorPos.append( findNxMotor(data, detectorName, peakFindMotors[i])[peakPos] )
        else:
            motorPos.append( data.getAxis(motorUsedCol(peakFindMotors[i], headings)).getData()[peakPos] )
        print " " + motorNames[i] + '\x20=\x20' + str(motorPos[i])

        if not dispOnly:
            if nexus:
                mt = motorNames[i].split('_', 1)[0]
                execString += mt + "," + str(motorPos[i]) + ","
            else:
                execString += motorNames[i] + "," + str(motorPos[i]) + ","

    if not dispOnly:
        execString += ")"
        exec execString

def com(*args):
    global peakFindMotors, peakFindDetector

    (data, counts, headings, detectorName, motorNames, dispOnly, nexus) = peakFindCommon(args, "to centre of mass in")

    mass = 0
    sum = 0

    for i in range(0, len(counts)):
        mass += i * counts[i]
        sum += counts[i]
    if sum > 0:
        mass = float(mass)/float(sum)

    (index, frac) = divmod(mass, 1)
#   print index, frac

    peakFindFracMove(data, motorUsedCol, headings, index, frac, motorNames, dispOnly, nexus, detectorName)

def cen(*args):
    global peakFindMotors, peakFindDetector

    (data, counts, headings, detectorName, motorNames, dispOnly, nexus) = peakFindCommon(args, "to centre of FWHM in")

    halfval = min(counts) + ( max(counts) - min(counts) )/2.0

    v1 = -1
    v2 = -1
    for i in range(0, len(counts)):
        if counts[i] == halfval:
            v1 = i
            break
        elif counts[i] > halfval:
            if i > 0:
                v1 = i - 1.0 + (halfval - counts[i-1]) / (counts[i] - counts[i-1])
            else:
                v1 = 0
            break
    for i in range(len(counts)-1, -1, -1):
        if counts[i] == halfval:
            v2 = i
            break
        elif counts[i] > halfval:
            if i < len(counts)-1:
                v2 = i + 1.0 - (halfval - counts[i+1]) / (counts[i] - counts[i+1])
            else:
                v2 = len(counts)-1
            break
    midpoint = ( v1 + v2 )/2.0
    (index, frac) = divmod(midpoint, 1)
#   print v1, v2, midpoint, index, frac

    peakFindFracMove(data, motorUsedCol, headings, index, frac, motorNames, dispOnly, nexus, detectorName)

def half(*args):
    global peakFindMotors, peakFindDetector

    (data, counts, headings, detectorName, motorNames, dispOnly, nexus) = peakFindCommon(args, "to half height in")
    halfval = min(counts) + ( max(counts) - min(counts) )/2.0

    print " Half value is " + detectorName + '\x20=\x20' + str(halfval)
    
    v1 = -1
    if counts[0] > halfval:
        sign = 1
    else:
        sign = -1
    for i in range(0, len(counts)):
        if counts[i] == halfval:
            v1 = i
            break
        elif (sign * counts[i]) < (sign * halfval):
            if i > 0:
                v1 = i - 1.0 + (halfval - counts[i-1]) / (counts[i] - counts[i-1])
            else:
                v1 = 0
            break
    (index, frac) = divmod(v1, 1)

    peakFindFracMove(data, motorUsedCol, headings, index, frac, motorNames, dispOnly, nexus, detectorName)    

def peakFindFracMove(data, motorUsedCol, headings, index, frac, motorNames, dispOnly, nexus, detectorName):
    global peakFindMotors, peakFindDetector    
    # will move to fractionally in between two adjacent data points
    print "Moving to:"
    moveString = ""
    motorPos = []
    execString = "pos("
    for i in range(0, len(peakFindMotors)):
        if nexus:
            motorPos.append( findNxMotor(data, detectorName, peakFindMotors[i])[int(index)] * (1-frac) + \
                             findNxMotor(data, detectorName, peakFindMotors[i])[int(index)+1] * frac )
        else:
            motorPos.append( data.getAxis(motorUsedCol(peakFindMotors[i], headings)).getData()[int(index)] * (1-frac) + \
                             data.getAxis(motorUsedCol(peakFindMotors[i], headings)).getData()[int(index)+1] * frac )
        print " " + motorNames[i] + '\x20=\x20' + str(motorPos[i])

        if not dispOnly:
            if nexus:
                mt = motorNames[i].split('_', 1)[0]
                execString += mt + "," + str(motorPos[i]) + ","
            else:
                execString += motorNames[i] + "," + str(motorPos[i]) + ","

    if not dispOnly:
        execString += ")"
        exec execString

def parseNx(scanfile):
    detlist = []
    motorlist = []
    motorlist2 = []

    for i in scanfile['/entry'].items():
        if i[0].startswith('EXCALIBUR_') or i[0].startswith('PILATUS_') or i[0].startswith('EIGER_'):
            detlist.append(i[0])

    for i in scanfile['/entry'][detlist[0]].items():
        if i[0].endswith('_value') or i[0].endswith('_value_set') or i[0].startswith('diff1'):
            motorlist2.append(i[0])

    # as remove method appears to be broken
    for i in motorlist2:
        if not i + '_set' in motorlist2:
                motorlist.append(i)

    if 'hkl' in scanfile['/entry']:
        for i in scanfile['/entry/hkl']:
            if i[0] == 'h' or i[0] == 'k' or i[0] == 'l':
                motorlist.append(i[0])
    print "Motors available: " + str(motorlist)
    print "Detectors available: " + str(detlist)
    return motorlist + detlist, motorlist, detlist

def findNxCounts(scanfile, detname):
    s = scanfile['entry'][detname][detname.split('_', 1)[1]]
    return s[0:s.shape[0]].squeeze()

def findNxMotor(scanfile, detname, motorname):
    if motorname == 'h' or motorname == 'k' or motorname == 'l':
        s = scanfile['entry']['hkl'][motorname]
    else:
        s = scanfile['entry'][detname][motorname]
    return s[0:s.shape[0]]

def peakFindCommon(args, textDesc):
    global peakFindMotors, peakFindDetector
    # load the data file
    data = []
    last = i07.getLastSrsScanFile()
    nexus = True
    if path.exists(last):
        nexus = False
        data = gda.analysis.ScanFileHolder()
        data.loadSRS(last)
        headings = data.getHeadings()
    else:
        print "Loading NeXus data, please wait..."
        data = dnp.io.load(path.dirname(last) + path.sep + 'i07-' + path.basename(last)[:-3] + 'nxs')
        (headings, headings_motors, headings_detectors) = parseNx(data)

    newMotor = False
    newDetector = False
    invert = False
    dispOnly = False

    # check the command line arguments and if any are given, decide if they are motors or detector
    oldMotors = peakFindMotors
    oldDetector = peakFindDetector
    peakFindMotors = []
    peakFindDetector = ""
    for i in range(0, len(args)):
        if(type(args[i]) == int and args[i] == -1):
            invert = True
        elif(type(args[i]) == int and args[i] == 0):
            dispOnly = True
        else:
            if nexus:
                if args[i] in headings_motors:
                    peakFindMotors.append(args[i])
                    newMotor = True
                elif args[i] in headings_detectors:
                    peakFindDetector = args[i]
                    newDetector = True
            else:
                try:
                    if (args[i].getClass() == gda.device.scannable.ScannableMotor) or ("DiffractometerAxisClass" in str(args[i].getClass())):
                        print  args[i]
                        if motorUsedInScan(args[i],headings):
                            peakFindMotors.append(args[i])
                            newMotor = True
                    else:
                        if motorUsedInScan(args[i],headings):
                            peakFindDetector = args[i]
                            newDetector = True
                except (NameError, AttributeError):
                    if motorUsedInScan(args[i],headings):
                        peakFindDetector = args[i]                    

    # if no new motors/detector given, use the previous ones
    if len(peakFindMotors) == 0:
        peakFindMotors = oldMotors
    if peakFindDetector == "":
        peakFindDetector = oldDetector

    # check at least one requested motor is used in the scan, or else use the first column
    validMotor = False
    for i in range(0, len(peakFindMotors)):
        if ( motorUsedInScan(peakFindMotors[i], headings) ):
            validMotor = True
    if ( not validMotor ) and ( not newMotor ):
        peakFindMotors = []
        peakFindMotors.append( headings[0] )

    # check the requested detector is used in the scan, or else use the last column
    if ( not motorUsedInScan(peakFindDetector, headings) ) and ( not newDetector ):
        peakFindDetector = headings[len(headings)-1]

    # note that everything is still complicated by the fact that the specified motors
    # could be scannables, or they could just be the name of a scannable
    # (if the name doesn't exist as a scannable it's not going to work anyway!)

    # print out what we are doing
    motorNames = []
    if dispOnly:
        outStr = "Would move "
    else:
        outStr = "Moving "
    for i in range(0, len(peakFindMotors)):
        try:
            motorNames.append( peakFindMotors[i].getName() )
        except AttributeError:
            motorNames.append( peakFindMotors[i] )
        outStr += motorNames[-1]
        if i < ( len(peakFindMotors) - 1 ):
            outStr += ", "
    outStr += " "+textDesc+" "
    try:
        detectorName = peakFindDetector.getName()
    except AttributeError:
        detectorName = peakFindDetector
    outStr += detectorName
    if invert:
        outStr += " (inverted)"
    print outStr    

    if nexus:
        cc = findNxCounts(data, detectorName)
    else:
        cc = data.getAxis(motorUsedCol(peakFindDetector, headings)).getData()

    counts = []
    if invert:
        for i in range(0,len(cc)):
            cc[i] = cc[i] * -1
    counts = cc
        
    return (data, counts, headings, detectorName, motorNames, dispOnly, nexus)

def motorUsedInScan(motor, headings):
    try:
        if ( headings.index(motor.getName()) > -1 ) or ( headings.index(motor.getInputNames()[0]) > -1 ):
          return True
    except ValueError:
        return False
    except (NameError, AttributeError):
        try:
            if ( headings.index(motor) > -1 ):
                return True
        except:
            pass
    return False

def motorUsedCol(motor, headings):
    try:
        col = headings.index(motor.getName())
        if col > -1:
            return col
        col = headings.index(motor.getInputNames()[0])
        if col > -1:
            return col
    except (NameError, AttributeError, ValueError):
        pass
    return headings.index(motor)

alias("peak")
alias("com")
alias("cen")
alias("half")
