#
# A series of tools for viewing and manipulating the XH / XSTRIP regions of interest
#
#


def listroi():
    print xh.getName() + "regions of interest:"
    _print_roi()
    
def _print_roi():
    rois_array = xh.getRois()
    for roi in rois_array:
        print roi.getName(), "lower: ", str(roi.getLowerLevel()),"upper:",str(roi.getUpperLevel())
    print ""

def setevenroi(numberRois = 4):
    xh.setNumberRois(numberRois)
    print "Set",str(numberRois),"evenly sized regions of interest"
    _print_roi()
    
def setrois(numberRois,lower,upper):
    xh.setEvenRoisWithBookends(numberRois,lower,upper)
    print "Set",str(numberRois),"evenly sized central regions of interest"
    _print_roi()


alias listroi
alias setevenroi
alias setrois
