import sys
#
#       pathscanTable
#
# Simple prototype for segmented path scan with a master (independent) motion axis
# and one or more slave (dependent) motion axes. Specifying anchor coordinates between
# these segments defines the slave axis steps size from the given master step size. 
#
# Sample program
#   from pathscanTable import pathscanTable
#   pst = pathscanTable(mstrAxis='sapolar', mstrStep=2.0, mstrAnchors=[-5,-1,7])
#   pst.addSlvAxis(slvAxis='say', slvAnchors=[0.1, 0.2, 0.3])
#   pst              # prints the table and 
#   pst.printScan()  # prints the pathscan command for copy-paste
#   pst.go()         # invoked the pathscan command directly
#
# Data structure is "picket fence", for n anchors points,  n + n-1 elements are
# created, the latter recording the segments between the points (length, slope, numsteps, point values)
# picket of picket fence has 4-element dictionary {'d':distance, 's':step, 'n':numberOfSteps, 'l':listOfStepPositionValues}
#
# Sample data structure
# mstrAnchors  =           [-20.0, {d: 24,   s:2.0,   n:1},   4.0, {d:  8,   s:2.0,   n:1},   12.0]
# slvAnchors   = [ ['sax', [0.840, {d:0.008, s:0.001, n:1}, 0.848, {d:0.008, s:0.002, n:1},  0.856]],
#                  ['say', [  8.0, {d: 1.2,  s:0.3,   n:1},   9.2, {d:  3,   s:0.5,   n:1},   11.2]] ]
# invariant for all slvs axes: len(slvAnchors) = len(mstrAnchors)

# DEPENDENCY: requires "uk.ac.gda.core/scripts/gdascripts/scan/pathscanCommand.py" to be run beforehand
import gda.factory.Finder as Finder
from gda.jython import JythonServerFacade

debug = False

def dirCmp(step, sv, end):          # compare in the direction of travel
    if step > 0.0:
        return sv < end
    elif step < 0.0:
        return sv > end
    else:
        raise ValueError, "Step size should not be zero"

def genRangeByStep(start, end, step, incEndPoint=False): # option to include last element even if it is > than end
    sv = start
    fRng = [sv]
    while dirCmp(step, sv, end):
        sv += step
        fRng += [sv]
    if debug: print >> sys.stderr, "genRangeByStep", incEndPoint, fRng, start, end, step
    if incEndPoint:  return fRng           # for all but last segment, exclude the last point
    else:            return fRng[:-1]

def genRangeByCount(start, end, step, count):
    fRng = [start+step*i for i in range(count)]
    if debug: print >> sys.stderr, "genRangeByCount", count, step, fRng
    return fRng

class pathscanTable:
    ''' pathscanTable class to represented segmented scan 
        step size of slave scannables calculated from master scannable
    '''
    mstrColWidth = 22  # width of master column  in ASCII table
    slvColWidth  = 21  # width of slave  columns in ASCII table

    def __init__(self, mstrAxis=None, mstrStep=None, mstrAnchors=None):
        self.mstrAxis     = None
        self.mstrStep     = None
        self.mstrAnchors  = []
        self.slvAnchors   = []
        self.segsLen      = None        # number of anchors points * 2 - 1
        self.numSlvs      = 0           # columns = number of dependent axes + 1
        # for direct execution populated by config method
        self.sg       = None
        self.path     = None
        self.detector = 'analyser' # globals()['analyser']  # from global name space!
        self.args     = None

        self.mstrAxis = mstrAxis
        self.setMstrStep(mstrStep)
                                        #  insert from rhs to grow list from n to picket list n+n-1
        for i in range(len(mstrAnchors)-1,0,-1): mstrAnchors.insert(i, {'d':0, 's':self.mstrStep, 'n':None})  
        self.mstrAnchors = mstrAnchors
        self.segsLen = len(self.mstrAnchors)

        self.recalc()
    
    def __repr__(self):
        tblRws = self.tblRowsLst()
        mxWidth = max([len(r) for r in tblRws])
        boxStr = "="*mxWidth+"\n"
        return boxStr+"\n".join(tblRws)+boxStr

    # axis stuff = columns
    def setMstrStep(self, mstrStep): self.mstrStep = float(mstrStep)
    def setMstrOverScanPlus(self, oscan=1): pass         # tbd must be positive
    def setMstrOverScanMinus(self, oscan=-1): pass       # tbd must be negative

    def addSlvAxis(self, slvAxis=None, slvAnchors=None): # manipulate dependent axes entries
        for i in range(len(slvAnchors)-1,0,-1): slvAnchors.insert(i, {'d':0, 's':0.0, 'd':None})
        self.slvAnchors += [[slvAxis, slvAnchors]]       
        self.numSlvs = len(self.slvAnchors)
        self.recalc()

    def addSegment(self, mstrAnchor, slvAnchors):
        if len(slvAnchors)==self.numSlvs:
            self.mstrAnchors += [{'d':0, 's':self.mstrStep, 'n':None}, mstrAnchor]
            for di, da in enumerate(self.slvAnchors): da[1] += [{'d':0, 's':0, 'n':None}, slvAnchors[di]]      # add picket items to depAxes anchorList # could mutate lists sans indexing
            self.segsLen += 2
        else:
            print slvAnchors, "doesn't match number of dependent axes"
        self.recalc()

    # recalc segment values: d=distance, s=step, l=list of positions, n=number of positions
    def recalc(self):                                                 # compute dependent values (in odd rows)
        for ri,ida in enumerate(self.mstrAnchors):                    # traverse mstr picketfence
            if ri%2==1:
                lastSegmentFlg = len(self.mstrAnchors)==ri+2
                if debug: print >>sys.stderr, ri, "lastSegmentFlg", lastSegmentFlg, len(self.mstrAnchors)
                ida['d'] = self.mstrAnchors[ri+1] - self.mstrAnchors[ri-1]  # = "mstrDelta"  # ida['s'] = self.mstrStep superfluous
                ida['l'] = genRangeByStep(self.mstrAnchors[ri-1], self.mstrAnchors[ri+1], ida['s'], lastSegmentFlg)
                ida['n'] = len(ida['l'])                              # was int(ida['d']/ida['s'])
                if debug: print >> sys.stderr, "MSTR d", ida['d'], ida['s'], int(ida['d']/ida['s']), len(ida['l']), ida['l']
                for di,da in enumerate(self.slvAnchors):              # each slv column
                    da[1][ri]['d'] = da[1][ri+1] - da[1][ri-1]        # slv delta
                    da[1][ri]['s'] = self.mstrStep * da[1][ri]['d'] / ida['d'] # get slv step from mstr step & slope
                    da[1][ri]['l'] = genRangeByCount(da[1][ri-1], da[1][ri+1], da[1][ri]['s'], ida['n'])
                    da[1][ri]['n'] = len(da[1][ri]['l'])              # was int(da[1][ri]['d']/da[1][ri]['s'])
                    if debug: print >> sys.stderr, "SLV  d", da[1][ri]['d'], da[1][ri]['s'], int(da[1][ri]['d']/da[1][ri]['s']), len(da[1][ri]['l']), da[1][ri]['l']

    # printing the table
    def tblRowsLst(self):
        tblStrLst  = []
        # title
        tblStrLst += ["Master Axis=%s, step=%2.3f" % (self.mstrAxis, self.mstrStep)]
        bdrStr = ''.join(["  |"] + ["-"*self.mstrColWidth] +[ "+" + "-"*self.slvColWidth for i in range(self.numSlvs)] + ["|"])
        tblStrLst += [ bdrStr ]
        # column headers
        hdrStr = ''.join(["  | %-*s " % (self.mstrColWidth-2, self.mstrAxis)] + ["| %-*s  " % (self.mstrColWidth-4, r[0]) for r in self.slvAnchors] + ["|"])
        tblStrLst += [ hdrStr ]
        tblStrLst += [ bdrStr ]
        # picket rows
        oddRowFmt = "}%(d) 7.3f=%(s) 6.3f*%(n)-3i"  # values supplied by dict
        for ri in range(self.segsLen):
            rowStr = ""
            if ri%2==1: rowStr += "  |   "+oddRowFmt % self.mstrAnchors[ri]             # dict values
            else:       rowStr += "A%1i|% 7.3f               " % (ri/2, self.mstrAnchors[ri])
            for ci in range(self.numSlvs):
                if ri%2==1: rowStr += "|  "+oddRowFmt % self.slvAnchors[ci][1][ri]      # dict values
                else:       rowStr += "| % 9.3f           " % self.slvAnchors[ci][1][ri]
            rowStr += "|"
            tblStrLst += [rowStr]
        tblStrLst += [ bdrStr ]
        tblStrLst += [""]
        return tblStrLst

    def pr(self):                                                     # raw print for debugging
        print self.mstrAnchors
        for r in self.slvAnchors: print r

    def mkRanges(self):  # transpose suitable for pathscan
        mstrRange = []
        for ri,ida in enumerate(self.mstrAnchors):                   # traverse mstr picketfence
            if ri%2==1: mstrRange += ida['l']
        slvRanges = []
        for da in self.slvAnchors:
            slvRange = []
            for ri,dr in enumerate(da[1]):
                if ri%2==1: slvRange += da[1][ri]['l']
            slvRanges += [slvRange]
        scnRanges = [mstrRange] + slvRanges
        return zip(*scnRanges)
        
    def printScan(self):   # use the "pathscan" command defined in core/pathScanCommand.py
        scanStr = "pathscan " 
        scanStr += "(%s, "% self.mstrAxis +', '.join([da[0] for da in self.slvAnchors])+") "
        pthStr = "("
        for ei,e in enumerate(self.mkRanges()):
            if ei!=0: pthStr +=","
            pthStr += "[" + ', '.join(["%6.4f" % v for v in e]) + "]"   ## \n
        scanStr += pthStr+") "
        scanStr +="analyser"  # pathscan requires additonal argument, but in this context it is ignored
        print scanStr
        print
    
    def makePathScan(self):   # use the "pathscan" command defined in core/pathScanCommand.py
        scanStr = "pathscan " 
        scanStr += "(%s, "% self.mstrAxis +', '.join([da[0] for da in self.slvAnchors])+") "
        pthStr = "("
        for ei,e in enumerate(self.mkRanges()):
            if ei!=0: pthStr +=","
            pthStr += "[" + ', '.join(["%6.4f" % v for v in e]) + "]"   ## \n
        scanStr += pthStr+") "
        scanStr +="analyser"     # pathscan requires additonal argument, but in this context it is ignored
        return scanStr

    def go(self):
        psc = self.makePathScan()
        JythonServerFacade.getInstance().runCommand(psc)
        

