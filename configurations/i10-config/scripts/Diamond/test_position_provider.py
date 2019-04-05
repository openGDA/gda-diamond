# make an index scannable
from gda.device.scannable import SimpleScannable
ix = SimpleScannable()
ix.name = "ix"
pos ix 0

#make scannablegroup for driving sample stage
from gda.device.scannable.scannablegroup import ScannableGroup
idd_pos_neg = ScannableGroup()
#idd_pos_neg.addGroupMember(idd_pos_neg_switchable)
idd_pos_neg.addGroupMember(idd_pos_neg_switcher)
idd_pos_neg.addGroupMember(idd_pos_neg_switchable)
idd_pos_neg.addGroupMember(ix)
idd_pos_neg.setName("idd_pos_neg")
idd_pos_neg.configure()

#make ScanPointProvider

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
class ScanPositionProviderFromFile(ScanPositionProvider):
    def __init__(self):
        self.filepath = None
        self.offset= (0.0, 0.0)
        self.scale = (1.0, 1.0)
        self.values=[]

    def load(self, filepath=None, offset=None, scale=None):
        if filepath != None:
            print "Setting file to", filepath
            self.filepath = filepath
        
        if offset != None:
            print "Setting offset to", offset
            self.offset=offset
        
        if scale != None:
            print "Setting scale to", scale
            self.scale = scale
        
        if self.filepath == None:
            raise ValueError("Filepath must be specified at least once!")
        
        self.values = readfile(self.filepath)

    def get(self, index):
        val = self.values[index]
        finalval=[]
        #add index last so that it is plotted as the dependent axis
        finalval.append (val[0] * self.scale[0] + self.offset[0])
        finalval.append (val[1] * self.scale[1] + self.offset[1])
        finalval.append (index)
        return finalval

    def size(self):
        return len(self.values)

    def __str__(self):
        return "File:%s Offset:%s Scale:%s Values:%s" % (self.filepath, self.offset, self.scale, self.values )

    def toString(self):
        return self.__str__()

idd_pos_neg_positions = ScanPositionProviderFromFile()
idd_pos_neg_positions.load("/dls_sw/i10/software/gda/workspace_git/gda-diamond.git/configurations/i10-config/scripts/Diamond/test_position_provider.dat")

# To replicate
example_file = """
#scan idd_pos_neg_switcher 0 1 1 idd_pos_neg_switchable 774 780 3
#
#idd_pos_neg_switchable , idd_pos_neg_switcher
774.0 0
774.0 1
777.0 0
777.0 1
780.0 0
780.0 1
#idd_pos_neg_switchable , idd_pos_neg_switcher
"""
