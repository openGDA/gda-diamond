#!/bin/env python2.4
from optparse import OptionParser
import sys, os
# import array stuff
from numpy import *
# import the calibration figures
from mac_calibration import offs,effs,dets

def bin(pos,opts):
    # this function calculates the bin number from a 2theta position
    # e.g. bin(i) = 0, for start - 0.5*step < start <= start + 0.5*step
    b = (pos - opts["start"] + opts["step"]*0.5 ) / opts["step"]
    if b<0:
        b = -1
    else:
        b = int( b - b%opts["step"] )
    return b

def correct(line,opts):
    # concept: we want to return the orignal intensity and monitor values, shifted by mac offset
    if not opts.has_key("last_err"):
        opts["last_err"] = 0
    # this function reads a line and normalises and offsets the positions
    split = line.rstrip("\r").split("\t")
    # this is 2theta pos
    posn = float(split[opts["tth"]])
    # this is the error
    try:
        err = float(split[opts["ttherror"]])
    except IndexError:
        err = 0
    if abs(err) > 0.01:
        print "Dodgy position %s"%posn
        posn = posn - err + opts["last_err"]
    opts["last_err"] = err
    # this is IO + IE
    # intensity in cts/s would be IO+IE/time.
    # in reality we should multiply by 50000000 as scalar clock is 50Mhz
    # but as we multiply by imav this factor disappears
    # also, time disappears as we need to divide by that to get vals    
    if opts["raw"]:
        # just normalise by time
        im = float(split[opts["S1"]])
    else:
        # normalise (later on) by time and intensity add 0.5 to avoid divide by 0
        im = float(split[opts["S1"]+47]) + float(split[opts["S1"]+48]) +0.5
        # make sure we don't divide by 0
        if int(im)<2:
            return
    # this is an array of positions with the offsets applied
    posns = []
    # this is an array of detector counts for the MACs
    vals = []
    # this is an array of monitor counts for the macs
    mon = []
    # this is the error array for the 45 dets
    errs = []
    # and this is the error array for the monitor
    errm = []
    # now populate and return them    
    for det in dets:
        # also add a constant (0.5) to the value to avoid divide by zero errors
        v = float(split[det-1+opts["S1"]])*effs[det] + 0.5
        posns.append(posn+offs[det])
        vals.append(v)
        mon.append(im)
        errs.append(sqrt(v))        
        errm.append(sqrt(im))
    return (im,posns,vals,errs,mon,errm)

def do_rebin(filename,opts):
    # rebins counts and monitor values and stores accumulative errors
    # First we read in the raw data file
    print "Reading file %s ..."%filename
    lines = open(filename,"r").readlines()
    opts["header"] = ""
    # copy the header over
    while not lines[0].startswith("tth"):
        opts["header"] += lines.pop(0)
    # look at the column headers
    columns = [ x.strip() for x in lines.pop(0).split("\t") ]
    opts["tth"] = columns.index("tth")
    opts["S1"] = columns.index("S1")
    opts["ttherror"] = columns.index("ttherror")
    # strip off empty lines
    while not lines[0].strip():
        lines.pop(0)

    # Work out the start and end positions
    step = opts["step"]
    start = float(lines[0].split("\t")[0])+offs[2]-2*step
    start = int(start/step)*step
    opts["start"] = start
    end = float(lines[-1].split("\t")[0])+offs[47]+2*step
    pts = bin(end,opts)

    # create the arrays for positions...
    P = arange(pts)*step+start
    # Counts...
    dC = [ zeros(pts) for d in dets ]
    # Monitor counts...
    M=[ zeros(pts) for d in dets ]
    # and number of data points in the bin
    bins = zeros(pts)
    # and total errors for final merged array
    E = zeros(pts)
    # and monitor errors for final merged monitor
    EM = zeros(pts)
    # and similarly counts errors
    EV = zeros(pts)
    # and im
    ims = zeros(len(lines[1:]))

    # initialise lastposns
    lastposns = correct(lines[0],opts)[1]

    print "  Rebinning at %s deg ... "%step
    # now count into the bins
    lenlines = len(lines)
    printlines = [ lenlines*x/10 for x in range(11) ]
    sys.stdout.write("  ")
    for l,line in enumerate(lines[1:]):
        # first get the 2thtea corrected intensity, errors in intensity, monitor and errors in monitor
        if l in printlines:
            sys.stdout.write(str(printlines.index(l)*10)+"% ")
            sys.stdout.flush()
        try:
            im,posns,vals,errs,mon,errm = correct(line,opts)
        except TypeError:
            continue
        # increase the total im for finding average monitor later
        ims[l] = im
        for i,det in enumerate(dets):
            if effs[det] < 0.01:
                # this is turned off
                continue
            # now check which bin to put it in
            bina = bin(lastposns[i],opts)
            binb = bin(posns[i],opts)
            mbins = range(bina,binb+1)
            for j,binm in enumerate(mbins):
                if len(mbins)==1:
                    # all in one bin, so dist is distance between 2 points 
                    dist = posns[i] - lastposns[i]
                    ch=1
                if j==0:
                    # dist is between lastposn and splitting point
                    dist = P[binm]+0.5*step-lastposns[i]
                    ch=2
                elif j==len(mbins)-1:
                    # dist is between posn and splitting point
                    dist = posns[i]-P[binm]+0.5*step
                    ch=3
                else:
                    # probably only use this if rebinning to smaller than 1mdeg
                    # distance is complete bin size
                    dist = step 
                    ch=4
                if (posns[i] - lastposns[i]) == 0:
                    #lastposns[i] falls exactly on posns[i] - enforce exact boundary
                    factor=1.0
                else:
                    factor = dist / (posns[i] - lastposns[i])
                # enforce boundary conditions for when dist almost, but doesnt quite fit
                # most if not all of these exception appear to arrise when ch=2 above
                if factor<=(-1.0):
                    #when lastposns[i] is just below posns[i] by -0.000xyz
                    factor=abs(factor)-1.0
                if factor>=1.0:
                    #and when lastposns[i] is just above posns[i] by +0.000xyz
                    factor=1.0
                dC[i][binm] += vals[i] * (factor)
                M[i][binm] += mon[i] * (factor)
                EV[binm] += pow(errs[i] * factor,2)
                EM[binm] += pow(errm[i] * factor,2)     
                bins[binm] += dist / step
                # or store the number of hits per bin
                #bins[binm] += 1
        lastposns = posns

    # trim the data to start where start_det starts, and finish where end_det stops
    if opts["tail"]:
        start_det = 2
        end_det = 47
    else:
        start_det = 10
        end_det = 39

    start_pt = bin(float(lines[0].split("\t")[0])+offs[start_det],opts) + 1
    end_pt = bin(float(lines[-1].split("\t")[0])+offs[end_det],opts) - 1

    # calculate average monitor intensity
    imav = average(ims)
    l = len(ims)
    # and the error in the average 
    imerr = sqrt(sum(pow(ims-imav,2))/(l*(l-1)))
    # store as (e/Im)^2
    imerr = pow(imerr / imav,2)
    # trim the arrays
    dC = [ c[start_pt:end_pt] for c in dC ]
    M = [ c[start_pt:end_pt] for c in M ]
    EV = EV[start_pt:end_pt]
    EM = EM[start_pt:end_pt]
    E = E[start_pt:end_pt]
    P = P[start_pt:end_pt]
    bins = bins[start_pt:end_pt]
    
    # return it
    print
    return (P,dC,M,bins,EV,EM,E,imav,imerr)

def add_traces(X,bins):
    """add all detectors into one trace, and normalise as if it was from 9 detectors"""
    C = zeros(len(X[0]))
    for c in X:
        C += c
#   dont need to do C*9/bins since /bins is lost during normalization 
    return C

def write_data(P,dC,bins,E,imav,filename,header=""):
    # write the file
    # red - reduced data for rebin, offset, normalise
    print "  Writing file %s ..."%filename
    f = open(filename,"w")
    f.write(header)
    f.write("2Theta")
    if options.sep:
        for det in dets:
            f.write("\tChan%i"%det)
    else:
        f.write("\tCounts")
    if options.bins:
        f.write("\tBins")
    f.write("\tError\tIO+IE=%f\n"%imav)
    for i,val in enumerate(P):
        f.write("%f"%val)
        if options.sep:
            for C in dC:
                f.write("\t%f"%C[i])
        else:
            f.write("\t%f"%dC[i])
        if options.bins:
            f.write("\t%f"%bins[i])
        f.write("\t%f\n"%E[i])
    f.close()
    print "=========== DATA REBIN COMPLETED ============"
    print 

if __name__=="__main__":
    # first we parse the options
    parser = OptionParser("%prog filename step [rebin_string]")
    parser.add_option("-p", "--plot", action="store_true", dest="plot", help="Plot the graph at the end")
    parser.add_option("-b", "--bins", action="store_true", dest="bins", help="Write a bins column in the output file")
    parser.add_option("-t", "--tail", action="store_true", dest="tail", help="Include the top and tail of the data")
    parser.add_option("-r", "--raw", action="store_true", dest="raw", help="Rebin the raw data, don't normalise to IO or IE")
    parser.add_option("-e", "--eff", action="store_true", dest="eff", help="Don't print out data, just work out the detector efficiencies")
    parser.add_option("-s", "--separate", action="store_true", dest="sep", help="Write out individual traces, don't sum them")
    parser.add_option("-a", "--additional", action="store", dest="additional", help='Comma separated list of other file numbers in the same dir to add in to results, e.g "3610,3612,3700"')    
    (options,args) = parser.parse_args()
    try:
        filename = args[0]
        path = filename[:filename.rfind("/")]
        step = float(args[1])
        if len(args)>2:
            rebin_string = "_"+args[2]
        else:
            rebin_string = ""
    except IndexError:
        parser.error("Incorrect number of arguments")
    
    print
    print "============== I11 DATA REBIN ==============="
    # then we rebin
    opts = { "bin": options.bins, "tail": options.tail, "raw": options.raw, "step": step }
    if options.eff:
        opts["tail"] = True
        for k,v in effs.items():
            effs[k] = 1
    P,dC,M,bins,EV,EM,E,imav,imerr = do_rebin(filename,opts)
    print "  Rebinning done"

    # now we add in additional files if needed
    if options.additional:
        #outs = [(P,dC,bins,E,imav)]
        outs = [(P,dC,M,bins,EV,EM,E,imav,imerr)]
        path = filename[:filename.rfind("/")]
        print path
        filenames = [ "%s/%s.dat"%(path,x.strip()) for x in options.additional.split(",") ]
        for f in filenames:
            print "  ...adding in file: %s"%f
            outs.append(do_rebin(f,opts))
        opts["header"] = ""

        # now combine
        #start = max([ min(P) for (P,dC,bins,E,imav) in outs ])
        start = max([ min(P) for (P,dC,M,bins,EV,EM,E,imav,imerr) in outs ])
        #end = min([ max(P) for (P,dC,bins,E,imav) in outs ]) + step
        end = min([ max(P) for (P,dC,M,bins,EV,EM,E,imav,imerr) in outs ]) + step
        opts["start"] = start
        pts = bin(end,opts)
    
        # create the arrays for positions...
        P = arange(pts)*step+start
        # Counts...
        dC = [ zeros(pts) for d in dC ]
        # monitor
        M = [ zeros(pts) for d in dC ]
        # and number of data points in the bin
        bins = zeros(pts)
        # average im
        imav = 0
        # errors
        E = zeros(pts)
        EM = zeros(pts)
        EV = zeros(pts)
    
        #for nP,ndC,nbins,nE,nimav in outs:
        for nP,ndC,nM,nbins,nEV,nEM,nE,nimav,nimerr in outs:
            opts["start"] = nP[0]
            for c,nc in zip(dC,ndC):
                c += nc[bin(start,opts):bin(end,opts)]
            for c,nc in zip(M,nM):
                c += nc[bin(start,opts):bin(end,opts)]
            bins += nbins[bin(start,opts):bin(end,opts)]
            imav += nimav
            #E += pow(nE[bin(start,opts):bin(end,opts)],2)
            EV = nEV[bin(start,opts):bin(end,opts)]
            EM = nEM[bin(start,opts):bin(end,opts)]
        
        bins = bins / len(outs)
        imav = imav / len(outs)
        #E = sqrt(E)
    
    # normalize everything
    print "  normalizing & calculating esd's..."
    # first merge counts & monitor arrays into two big ones
    mC=add_traces(dC,bins)
    mM=add_traces(M,bins)
    for i in range(len(mC)):
        #then calculate the error per point:
        #e.g. E[i] = I*sqrt((EV[i]/(mC[i]*mC[i]))+EM[i]/(mM[i]*mM[i])+imerr) but,
        #first add in error in average monitor since this very small (~10^-8)
        E[i] += imerr
        #next error in monitor (e/Im)^2 since next smallest
        E[i] += EM[i]/(mM[i]*mM[i])
        #then finally finally error in signal (e/I)^2
        E[i] = EV[i]/(mC[i]*mC[i])
        #calculate esd
        #E[i]= sqrt(E[i]/bins[i])
        E[i]= sqrt(E[i])
        #and then normalise the data
        #mC[i]=(mC[i]/(mM[i]))*imav
        mC[i]=(mC[i]/(mM[i]))
        #finally scale E by summed-&-normalized Intensity 
        E[i]=E[i]*mC[i]
        #but then find percentage error of unscaled summed & normed data
        percent = E[i]/mC[i]
        #and scale data by average mon
        mC[i]=mC[i]*imav*9
        #then calculate percentage error
        E[i]=mC[i]*percent

    print "  normalization complete"
    
    # then we write out the data
    new_filename = filename.replace(path,path+"/processing")
    if options.additional:
        new_filename = new_filename.replace(".dat","") + "_" + "_".join(options.additional.split(",")) + "_red%s.dat"%rebin_string
    else:
        new_filename = new_filename.replace(".dat","") + "_red%s.dat"%rebin_string
    
    if options.eff:
        opts["start"] = offs[2]
        # first find the indices where each new mac comes in
        indices = [ bin(offs[d],opts) for d in dets ][4:]
        indices.append(indices[-1] + indices[-1] - indices[-2] - 100)
        for k,v in effs.items():
            effs[k] = []        
        for i in range(1,len(indices)):
            for j,C in enumerate(dC):
                if C[indices[i]-2]<1 or C[indices[i-1]+2]<1:
                    cts = 0
                else:
                    cts = sum(C[indices[i-1]+2:indices[i]-2])
                effs[dets[j]].append(cts)
        
        # now work out the efficiences iteratively
        for i in range(len(indices)-1):
            d = 4
            ref_cts = effs[dets[d]][i]            
            # average to the mac15 if possible
            while ref_cts<0.1:
                # otherwise use the middle of the next batch / it's previous eff
                d += 9
                old_effs = [x for x in effs[dets[d]][:i] if x>0.1]
                if old_effs:
                    ref_cts = effs[dets[d]][i]/average(old_effs)
            #ref_cts = average([effs[d][i] for d in dets if effs[d][i]>0.1])
            for d in dets:
                effs[d][i] = effs[d][i]/ref_cts
        
        # now display the efficiencies
        string = "effs = {\n"
        for det in dets:
            eff = average([ x for x in effs[det] if x>0.1])
            string += '%s:\t%4.3f,\n'%(det,eff)
        print string[:-2]+"}"
        
    else:
        if options.sep:
#            write_data(P,dC,bins,E,imav,new_filename)
             write_data(P,dC,bins,mM,imav,new_filename,opts["header"])
        else:
#            write_data(P,add_traces(dC,bins),bins,E,imav,new_filename)
            write_data(P,mC,bins,E,imav,new_filename,opts["header"])

        
        # now we might want to display it
        if options.plot:
            print "Press ctrl-c to exit."
            os.system("/dls/i11/scripts/plot_rebinned.py %s"%new_filename)    
    
    

