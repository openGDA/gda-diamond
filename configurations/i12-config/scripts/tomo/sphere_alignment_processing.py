# Example data at
#/dls/i12/data/2014/cm4963-1/rawdata/35802.nxs
#/dls/i12/data/2014/cm4963-1/rawdata/35803.nxs

import os
import time
import scisoftpy as dnp
import math
#from uk.ac.diamond.scisoft.analysis.fitting import EllipseFitter as _efitter
# from org.eclipse.dawnsci.analysis.dataset.impl import AbstractDataset as absd
# 
# DUMMY MEDIAN FILTER from org.eclipse.dawnsci.analysis.dataset.impl import Image as javaImage


print "Loading the  sphere alignment processing functions"

def readTestInputs(filename='height.txt',idealname='ideal.txt',visit_directory='/dls/i12/data/2014/cm4963-2',input_directory='tmp',printres=False):
    infilename="%s/%s/%s"%(visit_directory,input_directory,filename)
    idealfilename="%s/%s/%s"%(visit_directory,input_directory,idealname)
    inlist=[]
    ideallist=[]
    try:
        infile=open(infilename,'r')
    except:
        print("File %s not opened properly"%infilename)
        return(None)
    n=0
    for line in infile:
        if printres:
            print n,line
            n=n+1
        inlist.append(float(line))
    infile.close()
    try:
        infile=open(idealfilename,'r')
    except:
        print("File %s not opened properly"%idealfilename)
        return(None)
    for line in infile:
        if printres:
            print n,line
            n=n+1
        ideallist.append(float(line))
    infile.close()
    if printres:
        print inlist
        print ideallist
    inarray=dnp.array(inlist)
    idealarray=dnp.array(ideallist)
    print len(inarray)
    angarray=((dnp.linspace(0,dnp.pi*2.0,len(inarray),True)))
    horizarray=2500.0*dnp.cos(angarray)
    ofile=open("%s/%s/testpoints.txt"%(visit_directory,input_directory),'w')
    ofile.write("angle,X,idealY,noisyY\n")
    for i in range(0,len(angarray)):
        ofile.write("%g,%g,%g,%g\n"%(angarray[i],horizarray[i],idealarray[i],inarray[i]))
    ofile.close()
    return((horizarray,inarray,idealarray))

def request_DAWN_Input(message):
    return raw_input(message)

def dofourier(yarray,printres=False):
    """
    Perform numerically the integration of the first Fourier cosine and sine components
    Requirment is that sample points be equally spaced and cover 360 degrees 
    """
    nvals=len(yarray)
    avht=yarray.mean()
    angles=dnp.linspace(0,2*dnp.pi,len(yarray))
    #print angles
    ycarray=yarray-avht
    cosines=dnp.cos(angles)
    sines=dnp.sin(angles)
    cosint=cosines*ycarray
    sinint=sines*ycarray
    if printres:
        print "Yarray:",yarray
        print "Ycarray:",ycarray
        print "Sinint:",sinint
        print "Cosint:",cosint
    cosum=cosint[:-1].sum()
    sinsum=sinint[:-1].sum()
    cosfactor=cosum/float(nvals-1)
    sinfactor=sinsum/float(nvals-1)
    if printres:
        print "sinfactor, cosfactor: %.4f %.4f"%(sinfactor,cosfactor)
    ratio=sinfactor/cosfactor
    delta=math.atan(ratio)
    deltadeg=math.degrees(delta)
    if printres:
        print"Delta degrees %06.4f"%deltadeg
    halfmag=math.sqrt(sinfactor**2+cosfactor**2)
    mag=2.0*halfmag
    if printres:
        print"Magnitude: %06.4f"%mag
        print "vertical centre %7.4f"%avht
    
    calcresult=avht+mag*dnp.cos(angles-delta)
    if printres:
        print"Calcresult:",calcresult
        for idx in range(0,len(yarray)):
            print yarray[idx],calcresult[idx]
        
    return(avht,mag,delta,calcresult)
# def get_image_data(previewmean=False, preview_frames=False,visit_directory='/dls/i12/data/2014/cm4963-1/',flatfile=37384, projectionfile=37385, threshold=0.5, max_tries=15,prompt=False, request_input_command=request_DAWN_Input):

def get_image_data(previewmean=False, preview_frames=False,visit_directory='/dls/i12/data/2015/cm12163-1/',input_directory='rawdata',flatfile=43185, projectionfile=43184, cropleft=10,cropwidth=2540,croptop=900,cropheight=550,threshold=0.3, max_tries=15,prompt=False, request_input_command=request_DAWN_Input):

    workinx_directory="%s/%s"%(visit_directory,input_directory)
    flatfilename="%s/%i.nxs"%(workinx_directory,flatfile)
    projectionfilename="%s/%i.nxs"%(workinx_directory,projectionfile)
    #TODO put a unique time stamp on the otuput
    #TODO make a folder for the outputs
    cropright=cropleft+cropwidth
    cropbot=croptop+cropheight
    
    print("FlatFilename = %s"% flatfilename)
    print("projectionfilename = %s"% projectionfilename)
    
    print "Loading flat field image %s\n\t to data processing pipeline" % flatfilename
    ff = None
    try_number = 0
    while (ff == None and try_number < max_tries):
        try_number += 1
        try:
            print("Trying to open the file %s" % (flatfilename))
            data = dnp.io.load(flatfilename)
            ff = data['entry1']['pco4000_dio_hdf']['data'][...].mean(0)
        except:
            print("ff is not null is it %s" % ff)
            print("ff is not null is of type %s" % type(ff))
            print("Failed to load %i, will try again in 5 seconds" % (try_number))
            time.sleep(5)
    
    # DUMMY MEDIAN FILTER ffilt = dnp.array(javaImage.medianFilter(ff._jdataset(), [3, 3]))
    ffilt=dnp.array(ff._jdataset())
    dnp.plot.image(ffilt)
    ffinvfull=1.0/ffilt
    ffinv=ffinvfull[croptop:cropbot,cropleft:cropright]
    dnp.plot.image(ffinv)
    
    time.sleep(.1)

    
    print "Loading projections %s into data processing pipeline"% projectionfilename
    data = dnp.io.load(projectionfilename)
    try:
        ddraw = data['entry1']['pco4000_dio_hdf']['data']
    except:
        print"Couldn not find the data in %s"%projectionfilename
        raise
    dd=ddraw[:,croptop:cropbot,cropleft:cropright]
    
    print "Processing data"
    
    # apply any filtering
    # exclude spheres which are not completely in the field of view
    
    if (previewmean):
        print "slow look at all the data"
        preview = dd.mean(0)*ffinv
        
#         dnp.plot.image(preview[10:-1,:])
        dnp.plot.image(preview)
        time.sleep(2)
    print "Generating centroid data"
    
    thresholdOK = False
    xs = []
    ys = []
    while not thresholdOK:
        xs = []
        ys = []
        for i in range(dd.shape[0]):
            cor = dd[i,:,:]*ffinv
            #print "Applying median filter"
            #DUMMY MEDIAN FILTER cor = dnp.array(javaImage.medianFilter(cor._jdataset(), [3, 3]))
            cor=dnp.array(cor._jdataset())
            cor = cor[10:-1,:]<threshold
            if (preview_frames):
                dnp.plot.clear()
                time.sleep(0.01)
                dnp.plot.image(cor)
                time.sleep(.2)
            y,x = dnp.centroid(cor)
            xs.append(x)
            ys.append(y)
        

        if (prompt==False):
            thresholdOK=True
        else:
            response = request_input_command("Current threshold is %f, y for ok, otherwise enter a new threshold value " % (threshold))
            if response == 'y' :
                thresholdOK = True
            else :
                try :
                    threshold = float(response)
                except :
                    print "could not interpret %s as a float" % response
                    
    return(xs,ys)
# def sphere_alignment_processing(previewmean=False,visit_directory='/dls/i12/data/2014/cm4963-2/',flatfile=37384, projectionfile=37385, threshold=0.4, max_tries=15,prompt=False,testdata=False, request_input_command=request_DAWN_Input):
#def sphere_alignment_processing(previewmean=False,visit_directory='/dls/i12/data/2015/cm12163-1/',flatfile=43185, projectionfile=43184, threshold=0.4, max_tries=15,prompt=False,testdata=False, request_input_command=request_DAWN_Input):
def sphere_alignment_processing(previewmean=False,visit_directory='/dls/i12/data/2015/cm12163-1/',flatfile=43215, projectionfile=43222, threshold=0.4, max_tries=15,prompt=False,testdata=False, request_input_command=request_DAWN_Input):
    results_directory="%s/tmp/orbit_test"%visit_directory
    if not os.path.exists(results_directory) :
        os.makedirs(results_directory)
    #The acquisition of the data is separated into another fuction, returning the lists of x and y data
    if not testdata:
        #the image processing step might fail. 
        try:
            xs,ys=get_image_data(previewmean=previewmean,visit_directory=visit_directory,preview_frames=True, flatfile=flatfile ,projectionfile=projectionfile, threshold=threshold,max_tries=max_tries,prompt=prompt,request_input_command=request_input_command)
        except:
            print("COuld not get_image_data")
            raise
        
#         ydata = absd.createFromList(ys)
#         xdata = absd.createFromList(xs)
        xarray=dnp.array(xs)
        yarray=dnp.array(ys)
    else:
        #Lists of numbers can be read in to compare results
        xarray,yarray,idealarray=readTestInputs(printres=False)
        #is there a less annoying way? 
#         xdata=absd.createFromList(xarray.tolist())
#         ydata=absd.createFromList(yarray.tolist())
#         
#     t = dnp.arange(100)*dnp.pi/50.
#     t = absd.createFromList(t.tolist())
    npoints=len(xarray)
    xmax=dnp.argmax(xarray)
    xmin=dnp.argmin(xarray)
    print "Now applying direct fourier integral method"
    y_ht,y_mag,y_delta,y_calcres=dofourier(yarray,printres=False)
    x_ht,x_mag,x_delta,x_calcres=dofourier(xarray,printres=False)
    rxrad=dnp.arcsin(dnp.sin(y_delta)*y_mag/x_mag)
    rzrad=dnp.arcsin(dnp.cos(y_delta)*y_mag/x_mag)
    rx=dnp.rad2deg(rxrad)
    rz=dnp.rad2deg(rzrad)
    print("rxrad=",rxrad,"rzrad=",rzrad)
    #dnp.plot.addline(xdata,y_calcres)
    dnp.plot.line(xarray,y_calcres)
    dnp.plot.addline(xarray,yarray)
    if(testdata):
        dnp.plot.addline(xarray,idealarray)
        
    resultsfilename="%s/input_%s.dat"%(results_directory,projectionfile)
    fout=open(resultsfilename,"w")
    for i in range(0,npoints):
        fout.write("%i,%f,%f\n"%(i,xarray[i],yarray[i]))
    fout.close()
    
    resultsfilename="%s/fcalc_%s.dat"%(results_directory,projectionfile)
    fout=open(resultsfilename,"w")
    for i in range(0,npoints):
        fout.write("%i,%f,%f\n"%(i,x_calcres[-i-1],y_calcres[i]))
    fout.close()
    print "y_ht",y_ht,"y_mag",y_mag,"y_delta",y_delta
    print "x_ht",x_ht,"x_mag",x_mag,"x_delta",x_delta
    print "rx",rx,"rz",rz
    return (rx,rz,xarray,yarray)

def doseveral():
    orbits=[]
    infilename="/dls/i12/data/2014/cm4963-2/tmp/orbitlist.txt"
    try:
        infile=open(infilename,'r')
    except:
        print("File %s not opened properly"%infilename)
        return(None)
    n=0
    for line in infile:
        orbits.append(int(line))
    infile.close()
    oray=dnp.array(orbits)
    fray=oray-1
    print oray
    print fray
    for i in range(0,len(oray)):
        print i,oray[i]
        try:
            sphere_alignment_processing(previewmean=True,flatfile=fray[i],projectionfile=oray[i])
        except:
            print("%i didn't work"%oray[i])
        print("finished %i"%oray[i])
    return
print "Finished loading the  sphere alignment processing functions"
    
