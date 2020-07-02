from gda.factory import Finder

def writefile(scannable1Name,scannable2Name,filepath):
    """
    add a line with 2 column for calibration scannable1 versus scannable2
    """
    Scannable1 = Finder.find("photoDiode1")
    Scannable1Position = Scannable1.getPosition()
    print "Scannable1Position", Scannable1Position
    
    
    values=[]
    f = open( filepath )
    lines = f.readlines()
    f.close()
