### known issues:    unpacked attributes are not deleted so remain from previous scan (safer to use dict)

### change sequence so data are in main dictionary, not d.s

### use listdict (dnp)?



import scisoftpy
import os.path
import numpy as np
try:
    import specfilewrapper
except:
    print '=== Need to obtain specfilewrapper.py and compatible specfile.so from ERSF PyMCA package in order to load spec files'

#import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
import matplotlib.cm as cm
from matplotlib.colors import Normalize

class quickplot():
    #experimental - do not use!
    #no parameter checks kwargs etc
    #quick test of quickplot- eventually have all automatic params
    def plot(self,*args):
        xstr, ystr=args[0], args[1]
        figure()
        plot(self.dict[xstr], self.dict[ystr])
        xlabel(xstr)
        ylabel(ystr)
        grid(True)
        title('#'+str(self.datanumber)+' '+self.date)
        axis('tight')
    def cards(self, xstr, ystr, zstr, cmap=cm.jet):
        #experimental!
        fig = figure()
        ax = fig.gca(projection='3d')
        verts = []
        zs = self.s.dict[xstr][:,0]
        cols=cmap(np.linspace(0,1,len(zs)))
        for jj in range(len(zs)):
            verts.append(list(zip([self.s.dict[ystr][jj,0]]+list(self.s.dict[ystr][jj,:])+[self.s.dict[ystr][jj,-1]], [0]+list(self.s.dict[zstr][jj,:])+[0])))
            #verts.append(list(zip(self.s.dict[ystr][jj,:], self.s.dict[zstr][jj,:])))
        #poly = PolyCollection(verts, facecolors = [cm.hot(e) for e in 256.*np.array(range(len(zs)))/np.array(range(len(zs))).max()])
        poly = PolyCollection(verts, facecolors = cols)
        poly.set_alpha(0.5)
        ax.add_collection3d(poly, zs=zs, zdir='y')
        ax.set_xlim3d(self.s.dict[ystr].min(),self.s.dict[ystr].max())
        ax.set_ylim3d(self.s.dict[xstr].min(),self.s.dict[xstr].max())
#        ax.set_zlim3d(self.s.dict[zstr].min(),self.s.dict[zstr].max())
        ax.set_zlim3d(0,self.s.dict[zstr].max())
        show()

class dataloader():
    '''
    Data loader base class
    Can use d=np.loadtxt(filename).transpose() to load ascii file with nympy function
    dataloader initializes and returns data loader object
    e.g. d=dataloader(obj, func)
    func is a function that calls the object obj and returns a format specifier for the file location
    if func is not defined the obj should be the format specifier string, e.g.
    d=dlsloader('/data/cm5940-1/%i.dat')
    d(100) loads scan no. 100 etc
    '''
    def __init__(self, source=None, f = lambda obj: obj, unpack=True, warn=False):
        self.warn=warn
        self.source=source
        self.sourcefunc=f
        self.unpack=unpack
        #self.open_source(source, f)    #open_source moved to load
    def get_preamble(self):
        return 'Base class - no preamble'
    def __call__(self, datanumber):
        self.dict=self.load(int(datanumber))
        if self.unpack:
            self.unpackdict(self.dict)
        self.datanumber=int(datanumber)
        return self
    def unpackdict(self, dict):
        #globals().update(self.dict)
        for key in dict.keys():
            try:
                newstr=str(key).replace('-','').replace(' ','')
                if newstr[0].isdigit(): #prepend _ if first character numeric
                    newstr='_'+newstr
                exec('self.'+newstr+'=dict["'+str(key)+'"]')
                #print "=== Unpacking  "+str(key)+" now called "+newstr
                if not newstr==str(key):
                    print '=== '+str(key)+' replaced by '+ newstr
            except:
                pass
             #   print "=== Warning: could not unpack "+str(key)
    def load(self,datanumber):
        self.open_source(self.source, self.sourcefunc)
        #overload with specific method to obtain dictionary from data source
        return {'Testdata':7.1}
    def open_source(self, source, f):
        self.pathfmt=f(source)
    def __repr__(self):
        return self.get_preamble()
    def inc(self,n=1):
        print self.__call__(self.datanumber+n)

    def findscans(self,numlist, expr='True'):
        '''
        findscans(numlist, expr='True')
        return list of scans within numlist that satisfy the logical expression expr
        example 1: scans involving phi
        d.findscans(range(260277,260300),'len(self.phi)>1')
        example 2: scans with identical scan command as 260277
        d.findscans(range(260277,260300),'self.cmd=="%s"'%d(260277).cmd)
        '''
        self.expr=expr
        goodscans=[]
        for num in numlist:
            if self.scanexists(num):
                if expr=='True':  #don't read file if expression is trival 'True'
                    goodscans+=[num]
                else:
                    self(num)
                    try:
                        if eval(expr):
                            goodscans+=[num]
                    except:
                        pass
        return goodscans
    def scanexists(self, n):
        try:
            self(n)
            return True
        except:
            return False
        
   
class specloader(dataloader):
    '''
    specloader object
    create with full name of spec file as input
    call with a number n to load data from scan n into object as attributes
    allmotors returns all metadata
    cols returns scan columns
    cmd is the spec scan command
    '''
    def get_preamble(self): #string for message
        try:
            return str(self.datanumber)+': '+self.scan.command()+': '.join(self.scan.alllabels())
        except:
            return 'Error: Maybe not a valid scan number?'
    def open_source(self, source, f=None):
        self.specfile=specfilewrapper.specfile.Specfile(self.source)
        
    def load(self,datanumber):
        self.open_source(self.source, self.sourcefunc)
        dict={} 
        self.allmotors=self.specfile.allmotors()
        #print self.allmotors
        self.scan=self.specfile.select(str(datanumber)+'.1')
        self.cols=self.scan.alllabels()
        for ii in range(len(self.allmotors)):
            dict[self.allmotors[ii]]=self.scan.allmotorpos()[ii]
        try:
            dict['hkl']=self.scan.hkl()
        except:
            pass    #no hkl
        try:
            dict['date']=self.scan.date()
        except:
            pass    #no date                      
        for col in self.cols:
            dict[col]=self.scan.datacol(col)
            #print col
        self.cmd=self.scan.command()
        return dict

class data():
    pass

class ScanSequence():
    'Tools for handling data from a sequence of scans'
    def sequence_to_dict(self, scanlist, fields=True):
        '''
        reads data from scanlist, selects fields from field list 
        and creates disctionary of field values
        fields is a list of fields of a field name string that is contains other fields
        '''
        if fields:  #all fields - need to load a file and get all field names
            self(scanlist[0])
            fields=self.dict.keys() #use all fields in dictionary
            
                        
        self.s=data()
        self.s.dict={}       #create empty dictionary
        
        for field in fields:
            self.s.dict[field]=[] #create empty list for each field           
        for scan in scanlist:
            self(scan)
            for field in fields:
                try:
                    self.s.dict[field]+=[self.dict[field]]
                except:
                    print '=== Warning: Did not find %s in scan %i' % (field, scan)

    def reshape_dict(self):
        'reforms dictionary items (lists) to NumPy arrays'
        self.s.shapes={}
        for field in self.s.dict.keys():
            try:
                self.s.shapes[field]=list(self.s.dict[field][0].shape)  #save shape of first list element as list
                bigshape=list(self.s.dict[field][0].shape)              #keep track of shape of large object
            except:
                self.s.shapes[field]=[1]                             #assume number if no shape attribute
        for field in self.s.shapes.keys():
            try:
                if not (self.s.shapes[field] == [1] or self.s.shapes[field] == bigshape):         #unexpected shape!
                    raise ValueError('Inconsistent shapes or data types in scan sequence')
                if self.s.shapes[field] == [1]:
                    self.s.dict[field]=np.outer(np.array(self.s.dict[field]),np.ones(bigshape)) #pad out scalars to make same size as arrays
                else:
                    self.s.dict[field]=np.array(self.s.dict[field])
            except:
                pass    #can't deal with non-numeric fields
    def unpack_sequence(self):
        'Unpacks sequence disctionary to attributes of self.s'
        for field in self.s.dict.keys():
            setattr(self.s,field, self.s.dict[field])
    def sequence(self, scanlist, fields=True):
        'Loads scan sequence and unpacks pictionary'
        self.sequence_to_dict(scanlist,fields)
        self.reshape_dict()
        self.unpack_sequence()

            
                
        
        
#renamed dlsloader
class dlsloader(dataloader,ScanSequence, quickplot):
    '''
    Data loader for dls data files
    Initialize with format string for numbered data file
    e.g. d=dataloader.dlsloader(datapath+'cm5940_4/%i.dat')
    call with scan number to load data
    e.g. d(382658)
    The data are then attributes of the dataloader object, d and can also be found in the dictionary .dict
    '''
    def get_preamble(self):
        str=''
        try:
            str+='#%.0f ' % self.datanumber
        except:
            pass          
        try:
            str+=self.dict['scancommand']+': '
        except:
            pass
        try:            
            for label in self.dict['labels']:
               str+=' '+label
        except:
            pass
        return str
#     def open_source(self, source):
#         'source is a format specifier string that can be used with a run number to generate the data file name'
#         self.pathfmt=source # for pilloader the path format specifier is given directly - could change srsloader to do the same
#         try:
#             self.pathfmt % 0
#         except:
#             #If this doesn't work then try it the old way where a specific number is geven rather then specifier
#             #open location and type of data by giving a complete file name (the file number does not need to exist)
#             #This option is historical and should be deleted eventually
#             self.source=source
#             (first,dot,ext)=source.rpartition('.')
#             numstr=''
#             for i in range(len(first)-1,-1,-1):
#                 if first[i].isdigit():
#                     numstr+=first[i]
#                 else:
#                     first=first[0:i+1]
#                     break
#             self.datanumber=int(numstr[::-1])
#             self.first=first #no longer used
#             #self.ext=ext
#             self.pathfmt=first+'%i.'+ext
#             #self.rr=readpil.readpil(directory=self.first)#open file in read_dat
                    
    def load(self,datanumber):
        self.open_source(self.source, self.sourcefunc)
        dict={}
        #self.file=self.first+str(datanumber)+'.'+self.ext
        self.file=self.pathfmt % datanumber
        #print self.file
        self.dirname=os.path.dirname(self.file)+os.sep #directory name with trailing separator - used for reading secondary data files etc
        self.dataobject=scisoftpy.io.load(self.file, formats=['srs','tiff'],warn=self.warn)
        labels=self.dataobject.keys()
        try:        
            scan=self.dataobject['scancommand']
        except:
            scan=''
        dict.update(self.dataobject.metadata) #update dict with metadata
        dict.update(self.dataobject); # then data
        dict['scan']=scan; dict['labels']=labels; # then scan and labels
        return dict
    def scanexists(self, n):#should be faster than the one in base class
        #print self.pathfmt % n
        return os.path.exists(self.pathfmt % n)

class piloader(dlsloader):
    def load(self,datanumber):
        self.open_source(self.source, self.sourcefunc)
        dict={}
        #self.file=self.first+str(datanumber)+'.'+self.ext  
        self.file=self.pathfmt % datanumber
        #print self.file
        self.dataobject=scisoftpy.io.load(self.file, formats=['tiff'])
        labels=self.dataobject.keys()
        try:        
            scan=self.dataobject['scancommand']
        except:
            scan=''
        dict.update(self.dataobject.metadata) #update dict with metadata
        dict.update(self.dataobject); # then data
        dict['scan']=scan; dict['labels']=labels; # then scan and labels
        return dict
    
    def get_preamble(self):
        return self.file



#tryp tif then tiff
#make generic loader ['srs,'tif',...]















'''
import scisoftpy as dnp
dnp.io.load('/media/Kingston/data/mt6869-1/32208.dat')
'/media/Kingston/data/mt6869-1/'
32208

#print locals()
#print locals()['Energy']



sf=specfile.Specfile('/media/Kingston/data/xmas_feb11/eusto')
n=790
scan=sf.select(str(n)+'.1')


populates main namespace only if modules run
clear workspace - still works
from loader import * doesn't work

testload=loader(main=True)
testload(3)
print Energy    

    
dd={'Energy':7.1,'theta':44, 'headache':'bad'}
dd['theta']
dd.keys()
'''
