#
# peem_analysis.py - script to alignment PEEM images and calculate a degree of
#                    polarization map
#
'''
PEEM analysis script

'''
import scisoftpy as np
import scisoftpy.plot as pl
import scisoftpy.io as io

NPEEM = 4 # number of images in a set (two wavelengths, two polarizations)

IMAGEEXPNAME = "Image Explorer"
IMAGEDPYNAME = "PEEM Image"

_PEEMDIR = None

def load_peem(dirname, explorerview=IMAGEEXPNAME):
    '''
    Load images to allow selection and region of interest choice

        load_peem(path, explorerview="Image Explorer")
    '''
    pl.scanforimages(dirname, "alpha", [".png"], NPEEM, False, explorerview)
    global _PEEMDIR
    _PEEMDIR = dirname
    #RCPPlotter.scanForImages(IMAGEEXPNAME, dirname, RCPPlotter.IMAGEORDERALPHANUMERICAL, [".png"], NPEEM, False)
    #gb = RCPPlotter.getGuiBean("ImageExplorer View")
    # set grid width to 4

def get_peem_files_from_selection(explorerview=IMAGEEXPNAME):
    gb = pl.getbean(explorerview)
    return pl.getfiles(gb)

def get_peem_rrois(displayname=IMAGEDPYNAME):
    gb = pl.getbean(displayname)
    crs = pl.getrects(gb)
    if not crs:
        cr = pl.getrect(gb)
        if cr is None:
            return None
        crs = [ cr ]
    print crs
    return crs

def peem_load_dataset(name):
    s = io.load(name, formats=['png'])
    return s[0]

def save_peem_shifts(name, shifts):
    print "saving %d shifts" % (len(shifts) * len(shifts[0]))
    f = open(name, 'w')
    for s in shifts:
        for x in s:
            f.write("%g %g\n" % (x[0], x[1]))
    f.close()
    print "saved"

def peem_save_dataset(name, d, scaled=False):
    if scaled:
        io.save(name, d, range=(-1.0, 1.0))
    else:
        io.save(name, d)

def xmcd(images):
    '''Calculate circular dichroism image from four images:
    sigma+ at lambda_1
    sigma+ at lambda_2
    sigma- at lambda_1
    sigma- at lambda_2
    '''
    if len(images) != NPEEM:
        return None

    ipos = images[1] / images[0] - 1
    ineg = images[3] / images[2] - 1
    return (ipos - ineg)/(ipos + ineg), ipos, ineg

import scisoftpy.image as img
import jarray
from os.path import basename
import time

def align_peem_images(files, croi, fromtop=True):
    '''
    Align a set of images using current ROI
    '''
    print "Aligning images"
    shift = []
    if fromtop:
        anchor = files[0]
        lfiles = files[1:]
    else:
        anchor = files[-1]
        lfiles = files[:-1]

    da = peem_load_dataset(anchor) #@UndefinedVariable
    for f in lfiles:
        print "Processing %s" % basename(f)
        db = peem_load_dataset(f) #@UndefinedVariable
        s = img.findshift(da, db, croi)
        print "For %s, shift is (%g, %g)" % (basename(f), s[0], s[1])
        shift.append(s)

    if fromtop:
        shift.insert(0, jarray.zeros(2,'d'))
    else:
        shift.append(jarray.zeros(2,'d'))
    return shift, da

def process_peem(prefix=None, displayname=IMAGEDPYNAME, explorerview=IMAGEEXPNAME):
    '''Process PEEM images selection from ImageExplorer view after defining rectangular regions of interest
    
        process_peem(prefix=None, displayname="PEEM Image", explorerview="Image Explorer")

    Results are returned as the CD map, positive and negative images and a list of averaged images.
    They are also saved as prefix+ave-[0-3].png and prefix+pmap.png. The shifts are saved in prefix+shift.dat
    '''
    start = time.time()
    files = get_peem_files_from_selection(explorerview)
    if files == None:
        print "No images selected"
        if _PEEMDIR:
            print "Using images in ", _PEEMDIR
            import glob, os.path
            names = glob.glob(os.path.join(_PEEMDIR, '*.png'))
            omit = glob.glob(os.path.join(_PEEMDIR, '*ave-[0-3].png'))
            omit += glob.glob(os.path.join(_PEEMDIR, '*pmap.png'))
            files = [ n for n in names if not n in omit ]
        else:
            return None
    num = len(files)
    nsets = num // NPEEM # number of sets of images
    print "%d sets of PEEM images" % nsets
    if (num % NPEEM) != 0:
        print "Need to select multiples of %d images" % NPEEM
        return

    # divide up images to (s+,la), (s+,lb), (s-,la) and (s-,lb)
    ifiles = []
    ifiles.append(files[0:nsets])
    ifiles.append(files[nsets:2*nsets])
    ifiles.append(files[2*nsets:3*nsets])
    ifiles.append(files[3*nsets:4*nsets])

    crs = get_peem_rrois(displayname)
    if crs == None:
        print "WARNING, no rectangular region of interest selected"

        aimages = []
        da = peem_load_dataset(ifiles[0][0])
        shape = da.shape
        for n in range(NPEEM):
            aimage = np.zeros(shape) #@UndefinedVariable
            # images are organised to groups of nsets
            lfiles = ifiles[n]
            for s,im in enumerate(lfiles):
                print "    %s" % basename(im)
                db = peem_load_dataset(im) #@UndefinedVariable
                aimage += db

            aimage /= nsets
            aimage.name = "average %d" % n
            peem_save_dataset(prefix + "ave-%d" % n + ".png", aimage)
            aimages.append(aimage)
    else:
        rois = []
        if len(crs) == 1:
            rois.append(crs[0])
            rois.append(crs[0])
            rois.append(crs[0])
            rois.append(crs[0])
        elif len(crs) < 4:
            rois.append(crs[0])
            rois.append(crs[0])
            rois.append(crs[1])
            rois.append(crs[1])
        elif len(crs) >= 4:
            rois.append(crs[0])
            rois.append(crs[1])
            rois.append(crs[2])
            rois.append(crs[3])
    
        shifts = []
        fromtop = False
        for n in range(NPEEM):
            shift, da = align_peem_images(ifiles[0], rois[0], fromtop)
            shifts.append(shift)
            fromtop = not fromtop

        save_peem_shifts(prefix + "shifts.dat", shifts)
        shape = da.shape
        # work out average (save averaged set)
        print "working out average"
        aimages = []
        for n in range(NPEEM):
            aimage = np.zeros(shape) #@UndefinedVariable
            lfiles = ifiles[n]
            shift = shifts[n]
            print "average %d" % n
            for s,im in enumerate(lfiles):
                print "    %s" % basename(im)
                db = peem_load_dataset(im) #@UndefinedVariable
                sim = img.shiftimage(db, shift[s])
                aimage += sim

            aimage /= nsets
            aimage.name = "average %d" % n
            peem_save_dataset(prefix + "ave-%d" % n + ".png", aimage)
            aimages.append(aimage)

    # calculate degree of polarization map
    pmap, pos, neg = xmcd(aimages)
    pmap.name = "poln map"
    peem_save_dataset(prefix + "pmap.png", pmap, scaled=True)
#   pl.image(pmap)
    print 'Aligned and processed images: %.2fs' % (time.time() - start)
    return pmap, pos, neg, aimages
