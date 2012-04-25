#!/dls_sw/apps/python/2.7.2/64/bin/python
import h5py
import time
import Image
import getopt
import sys
import os

class Ctrl:
   def __init__(self):
      self.inpath="/dls/i12/data/2011/cm2061-4/tmp/file.h5"
      self.outdir="/dls/i12/data/2011/cm2061-4/tmp/"
      self.outprefix="sino_"
      self.outsuffix="tif"
      self.inflag=False
      self.outflag=False
      self.nsino=10
      self.firstsino=0
      self.memlimit=1000000000
   def showme(self):
      print "inpath :",self.inpath
      print "outdir :",self.outdir
      print "outprefix :",self.outprefix
      print "outsuffix :",self.outsuffix
      print "inflag :",self.inflag
      print "outflag :",self.outflag
      print "nsino :",self.nsino
      print "firstsino :",self.firstsino
      print "memlimit :",self.memlimit
      

def usage():
   global ctrl
   print sys.argv[0]
   print "Usage: %s -i input-file-path -o output-directory -f first-slice -n number-of-slices [-m memory-limit]" % sys.argv[0]
   print "-i path to the input file"
   print "-o path to the output dirctory [parent directory must exist]"
   print "-f number of first sinogram to process"
   print "-n number of sinograms to process"
   print "-m memory limit [default %i]" % ctrl.memlimit


def parseopt():
   global ctrl

   print "Running parseopt"

   if (len(sys.argv) < 2):
      print len(sys.argv)
      usage()
      sys.exit(0)

   try:                                
      opts, args = getopt.gnu_getopt(sys.argv[1:],  "i:o:n:f:m:h")
   except getopt.GetoptError, err:           
      errprint ("Option parsing error")
      errprint ("Command line values: %s" % (sys.argv))
      errprint("Message is %s" % (str(err))) 
      usage()                          
      sys.exit(2)                     

   for o,a in opts:
      if o == "-i":
          ctrl.inpath=a
          ctrl.inflag=True
      elif o == "-o":
           ctrl.outdir=a
           ctrl.outflag=True
      elif o == "-n":
           ctrl.nsino=int(a)
           ctrl.nsinoflag=True
      elif o == "-f":
           ctrl.firstsino=int(a)
           ctrl.firstsinoflag=True
      elif o == "-m":
           ctrl.memlimit=int(a)
      elif o == "-h":
           usage()
           sys.exit(0)
      else:
           errprint ("Ignored option")
           errprint ("option %s value %s" % (o,a))

   if (ctrl.outflag==False):
      print("ERROR: must provide output folder")
      sys.exit(3)

   if (ctrl.inflag == False):
      print("ERROR: must provide input file path")
      sys.exit(4)

def savetiffs(thischunk,firstnum):
   global ctrl

   chunksize=thischunk.T.shape[1]
   print "chunk shape: ", thischunk.shape
   print "firstnum=", firstnum

   for sidx in range (0,chunksize):
      thissino=thischunk[:,sidx,:]

      sinonum=firstnum+sidx
      outpath="%s/%s%05d.%s" % (ctrl.outdir,ctrl.outprefix,sinonum,ctrl.outsuffix)

      print "sino_idx: %i sinonum %i filename %s sinogram_shape " %(sidx,sinonum,outpath),thissino.shape
      #simage=Image.frombuffer("I;16",thissino.shape,thissino.data)
      #simage=Image.fromstring("I;16",thissino.shape,thissino.tostring(order='C'))
      #simage.save(outpath)

      #simage=Image.fromstring("I;16",thissinot.shape,thissinot.tostring(order='C'))
      #simage.save(outpatht)

      #simage=Image.fromstring("I;16",(thissinot.shape[1],thissinot.shape[0]),thissinot.tostring(order='C'))
      #simage.save(outpatht)

      simage=Image.fromstring("I;16",thissino.T.shape,thissino.T.tostring(order='F'))

      # stime=time.time()

      simage.save(outpath)

      # etime=time.time()
      # tstamp=time.strftime("%Y_%m%d_%H%M%S")
      # thisbytes=thissino.nbytes
      # elapsed=etime-stime
      # print "SLICETIME: ",tstamp,sidx,stime,etime,elapsed,thisbytes,(float(thisbytes)/float(elapsed))/(1024.0*1024.0),"Mbytes/sec"
      # sys.stdout.flush()

      #simage=Image.fromstring("I;16",thissinot.shape,thissinot.tostring(order='F'))
      #simage.save(outpathft)


def main():
   global ctrl
   tstamp=time.strftime("%Y_%m%d_%H%M%S")
   pstime=time.time()
   print "STARTINGTIME ",tstamp,pstime
   ctrl=Ctrl()

   parseopt()
   ctrl.showme()

   stime=time.time()
   #fdir = "/dls/i12/data/2011/cm2061-4/rawdata/phasescans/"
   #fname = "phasescan2_00023.h5"
   #fname = "balls_m3_real_00004.h5"

   if not(os.access (ctrl.outdir,os.F_OK)):
      print "creating %s" % ctrl.outdir
      os.mkdir(ctrl.outdir)

   fpath=ctrl.inpath

   if not(os.access (ctrl.inpath,os.F_OK)):
      print "ERROR: input file %s does not exist!" % ctrl.inpath
      sys.exit(5)

   print stime,"opening file %s ... " %(fpath)
   data=h5py.File(fpath,mode="r")
   etime=time.time()

   tstamp=time.strftime("%Y_%m%d_%H%M%S")
   print "FileOpened",tstamp,stime,etime,etime-stime
   dset=data["/entry/instrument/detector/data"]
   print "shape: ", dset.shape
   print "chunks: ", dset.chunks, dset.chunks[0] * dset.chunks[1] * dset.chunks[2]
   print "memchunks: ", dset.shape[1]* dset.chunks[0] * dset.chunks[1] * dset.chunks[2]

   chunksize=ctrl.nsino
   memsize = 2*dset.shape[0]*dset.shape[2]*chunksize
   print "Requested memory per sino chunk = ",memsize,"bytes, sinogram chunk size = ",chunksize,"sinograms"
   if (memsize > ctrl.memlimit):
      print "Requested size exceeds available size",ctrl.memlimit
      maxchunk = ctrl.memlimit / ( 2 * dset.shape[0] * dset.shape[2])
      chunksize=maxchunk
      print "chunk size set to", chunksize,"sinograms"
      sys.exit(0)



   startsino=ctrl.firstsino
   endsino=startsino+ctrl.nsino

   nchunks=(endsino - startsino)/chunksize
   nchunksplus=nchunks + 1
   lastchunksize=(endsino - startsino) - (nchunks * chunksize)
   memsize = 2*dset.shape[0]*dset.shape[2]*chunksize
   print "nchunks %i chunksize %i  lastchunksize %i memsize %i" %(nchunks,chunksize,lastchunksize,memsize)
   sys.stdout.flush()


   for idx in range (0,nchunks):
      thisstart=startsino+idx*chunksize
      thisend=thisstart+chunksize

      stime=time.time()
      tstamp=time.strftime("%Y_%m%d_%H%M%S")
      print tstamp,idx,stime,"reading %i bytes ... " % memsize
      sys.stdout.flush()

      thischunk=dset[:,thisstart:thisend,:]
      tstamp=time.strftime("%Y_%m%d_%H%M%S")

      etime=time.time()
      elapsed=etime-stime

      thisbytes=thischunk.nbytes
      print "READINGTIME: ",tstamp,idx,stime,etime,etime-stime,thisbytes,(float(thisbytes)/float(elapsed))/(1024.0*1024.0),"Mbytes/sec"
      print thischunk.shape
      sys.stdout.flush()

      stime=time.time()
      savetiffs(thischunk,thisstart)
      etime=time.time()
      tstamp=time.strftime("%Y_%m%d_%H%M%S")
      print "WRITINGGTIME: ",tstamp,idx,stime,etime,etime-stime
      sys.stdout.flush()


   lastmemsize = 2*dset.shape[0]*dset.shape[2]*chunksize
   if(lastchunksize > 0):
      #process the last (oddsized) chunk
      idx = nchunks
      thisstart=idx*chunksize
      thisend=thisstart+lastchunksize

      stime=time.time()
      tstamp=time.strftime("%Y_%m%d_%H%M%S")
      print tstamp,idx,stime,"reading %i bytes ..." % lastmemsize

      thischunk=dset[:,thisstart:thisend,:]

      tstamp=time.strftime("%Y_%m%d_%H%M%S")
      etime=time.time()
      print "READINGTIME: ",tstamp,idx,stime,etime,etime-stime
      print thischunk.shape
      sys.stdout.flush()

      stime=time.time()
      savetiffs(thischunk,thisstart)
      etime=time.time()
      tstamp=time.strftime("%Y_%m%d_%H%M%S")
      print "WRITINGTIME: ",tstamp,idx,stime,etime,etime-stime
      sys.stdout.flush()


   etime=time.time()
   tstamp=time.strftime("%Y_%m%d_%H%M%S")
   print "TOTALTIME: ",tstamp,idx,ptime,etime,etime-ptime
   print "Job finished"
   sys.stdout.flush()



if __name__ == "__main__":
      print "Running main"
      main()
