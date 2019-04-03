from gda.scan import ScanPositionProviderFactory
def readfile(filepath):
    """
    reads a 2 column csv file 
    returns a list of tuple
    """
    values=[]
    f = open( filepath )
    lines = f.readlines()
    f.close()

    lineno=0
    for l in lines:
        lineno +=1
        if not l.startswith("#") and not len(l) == 0:
            parts=l.split()
            if len(parts) != 2:
                raise ValueError("File contents is invalid line " + `lineno` +" has more than 2 parts :'" + l)
            values.append( ( float(parts[0]), float(parts[1]) ) )
    return values
   
from gda.scan import ScanPositionProvider   
class   ScanPositionProviderFromFile(ScanPositionProvider):
    def __init__(self):
        self.values=[]
        self.offset=(0.,0)
        self.filepath=""
    def load(self, filepath, offset, scale=1.0):
        self.values = readfile(filepath)
        self.offset=offset
        self.filepath=filepath
        self.scale=scale
    def get(self, index):
        val = self.values[index]
        finalval=[]
        #add index last so that it is plotted as the dependent axis
        finalval.append (val[0] * self.scale + self.offset[0])
        finalval.append (val[1] * self.scale + self.offset[1])
        finalval.append (index)
        return finalval
    
    def size(self):
        return len(self.values)
    
    def __str__(self):
        return "File:%s Offset:%s Scale:%s Values:%s" % (self.filepath, self.offset, self.scale, self.values ) 
    def toString(self):
        return self.__str__()

