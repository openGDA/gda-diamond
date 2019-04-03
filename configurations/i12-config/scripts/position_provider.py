from gda.scan import ScanPositionProviderFactory
def readfile(filepath, n=2):
    """
    reads n-column csv file 
    returns list of n-tuples
    """
    values=[]
    f = open(filepath)
    lines = f.readlines()
    f.close()

    lineno=0
    for l in lines:
        lineno +=1
        if not l.startswith("#") and not len(l) == 0:
            parts=l.split()
            #print parts
            if len(parts) != n:
                raise ValueError("File contents is invalid - line %d has more than %d parts :' %s" %(lineno, n, l))
            pos_tuple = (float(parts[0].strip()),)
            for i in range(1,n):
                pos_tuple += (float(parts[i].strip()),)
            values.append(pos_tuple)
    return values
   
from gda.scan import ScanPositionProvider   
class   ScanPositionProviderFromFile(ScanPositionProvider):
    def __init__(self, n=2):
        self.values=[]
        self.offset=(0.,)*n
        self.filepath=""
        self.scale=1.0
        self.dim=n
        
    def load(self, filepath, offset, scale=1.0):
        self.values = readfile(filepath, self.dim)
        self.offset=offset
        self.filepath=filepath
        self.scale=scale
        
    def get(self, index):
        val = self.values[index]
        finalval=[]
        #add index last so that it is plotted as the dependent axis
        for i in range(0, self.dim):
            finalval.append(val[i] * self.scale + self.offset[i])
        finalval.append(index)
        return finalval
    
    def size(self):
        return len(self.values)
    
    def __str__(self):
        return "File: %s Offset: %s Scale: %s Values: %s Dim: %d" % (self.filepath, self.offset, self.scale, self.values, self.dim)
     
    def toString(self):
        return self.__str__()

