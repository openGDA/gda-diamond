#!/dls_sw/apps/python/2.7.2/64/bin/python
import getopt
import sys
import os
import platform
import time
vflag=False

def vprint(message):
    global vflag
    if vflag:
        print  message

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
      self.memlimit=10000000000
      self.nchunks=16
      self.myqueue="medium.q"
      self.sinodir="sinograms"
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
      print "nchunks :",self.nchunks
      print "myqueue :",self.myqueue
      print "sinodir :",self.sinodir
      

def usage():
   global ctrl
   print sys.argv[0]
   print "Usage: %s -i input-file-path -o output-directory -f first-slice -n number-of-slices [-m memory-limit]" % sys.argv[0]
   print "-i path to the input file"
   print "-o path to the output dirctory [parent directory must exist]"
   print "-s name of sinogram folder in the output directory [default %s]" % ctrl.sinodir
   print "-f number of first sinogram to process"
   print "-n number of sinograms to process"
   print "-N Number of parallel chunks to send to the queue [default %i]" % ctrl.nchunks
   print "-Q which Queue to send the jobs to [default %s]" % ctrl.myqueue
   print "-m memory limit [default %i]" % ctrl.memlimit
   print("watch this space ... ")

def parseopt():
   global ctrl

   print "Running parseopt"

   if (len(sys.argv) < 2):
      print len(sys.argv)
      usage()
      sys.exit(0)

   try:                                
      opts, args = getopt.gnu_getopt(sys.argv[1:],  "Q:i:o:n:f:N:s:h")
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
      elif o == "-s":
           ctrl.sinodir=a
      elif o == "-n":
           ctrl.nsino=int(a)
           ctrl.nsinoflag=True
      elif o == "-f":
           ctrl.firstsino=int(a)
           ctrl.firstsinoflag=True
      elif o == "-N":
           ctrl.nchunks=int(a)
      elif o == "-Q":
           ctrl.myqueue=a
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


def main():
   global ctrl
   tstamp=time.strftime("%Y_%m%d_%H%M%S")
   uniqueid=tstamp           #default
   ctrl=Ctrl()

   print ("Parsing the options")
   parseopt()
   print ("Showing the options")
   ctrl.showme()
   logsfolder="%s/%s" % (ctrl.outdir,"sino_h5_logs")
   sinofolder="%s/%s" % (ctrl.outdir,ctrl.sinodir)
   myfolder="r_%s_files" % uniqueid
   mypath="%s/%s" % (logsfolder,myfolder)


   print ("Checking the folders")
   if not(os.access (ctrl.inpath,os.F_OK)):
      print "ERROR: input file %s does not exist!" % ctrl.inpath
      sys.exit(5)

   if not(os.access (ctrl.outdir,os.F_OK)):
      print "creating %s" % ctrl.outdir
      os.mkdir(ctrl.outdir)

   if not(os.access (logsfolder,os.F_OK)):
      print "creating %s" % logsfolder
      os.mkdir(logsfolder)

   if not(os.access (sinofolder,os.F_OK)):
      print "creating %s" % sinofolder
      os.mkdir(sinofolder)

   if not(os.access (mypath,os.F_OK)):
      print "creating %s" % mypath
      os.mkdir(mypath)

   if not(os.access (ctrl.outdir,os.F_OK)):
      print ("Folders are not ok")
      print ("check that parent path of the output folder is OK")
      sys.exit(8)

   print ("Folders ok")



   chunksize = ctrl.nsino / (ctrl.nchunks-1)
   lastchunksize = ctrl.nsino - (chunksize * (ctrl.nchunks -1))
   firstchunk=1

   jobscript="%s/sinochunk_h5.qsh" % mypath
   jobprogram="doh5slice.py"
   jobflags="-i %s -o %s -m %i " %(ctrl.inpath,sinofolder,ctrl.memlimit)
   print "chunksize %i lastchunksize %i" %(chunksize,lastchunksize)

   sys.stdout = open(jobscript,"w")
   print("""\
#!/bin/bash 
set -x

#add the modules required 
source /dls_sw/i12/modulefiles/modules.sh
module add numpy/1.6.1-64
module add /dls_sw/i12/modulefiles/local-64
myjob=$JOB_ID
mytask=$SGE_TASK_ID
""") 

   print("""\
lc=%i
nc=%i
""") %(lastchunksize,chunksize)
   print("""\
if [[ $mytask -eq %i ]]
then
thisn=$lc
else
thisn=$nc
fi
((thisf = $nc * ($mytask - 1 ) ))
""") % ctrl.nchunks

   #assemble the command line that actually does the task
   print("""\
%s %s -f $thisf -n $thisn
set +x
""") % (jobprogram,jobflags)



#end of the queue script text
   sys.stdout.flush()
   sys.stdout=sys.__stdout__

   #set the queue environment
   qenviron=os.environ
   vprint (len(qenviron))
   vprint (qenviron.items())
   oldpath=""
   try :
      oldpath = qenviron["PATH"]
   except :
      oldpath = ""
   if ( "64bit" == platform.architecture()[0] ) :
      newpath="/dls_sw/apps/sge/SGE6.2/bin/lx24-amd64:/bin:/usr/bin:%s" % oldpath
   else:
      newpath="/dls_sw/apps/sge/SGE6.2/bin/lx24-x86/:/bin:/usr/bin:%s" % oldpath
   qenviron["SGE_CELL"]="DLS"
   qenviron["SGE_EXECD_PORT"]="60001"
   qenviron["SGE_QMASTER_PORT"]="60000"
   qenviron["SGE_ROOT"]="/dls_sw/apps/sge/SGE6.2"
   qenviron["PATH"]=newpath
   vprint (len(qenviron))
   vprint (qenviron.items())

   pyerr=open("%s/sino_listener_stderr.txt" % (mypath) ,"w")
   pyout=open("%s/sino_listener_stdout.txt" % (mypath) ,"w")
   pyenv_o=open("%s/python_stdout.txt" % (mypath),"w")
   pyenv_e=open("%s/python_stderr.txt" % (mypath),"w")
   jobname="SnH5"

   thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub", "-P","i12","-e",mypath, "-o", mypath, "-q",ctrl.myqueue,"-N",jobname,"-cwd","-pe","smp","4","-t","%i-%i" % (firstchunk,ctrl.nchunks),jobscript, qenviron)

#   try:
#         print ("Spawning the sinogram job ... ")
#         if (vflag):
#            subprocess.Popen("env",env=qenviron,shell=False,stdout=pyenv_o,stderr=pyenv_e)
#            print qenviron
#         thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub", "-P","i12","-e",mypath, "-o", mypath, "-q",ctrl.myqueue,"-N",jobname,"-cwd","-pe","smp","4","-t","%i-%i" % (firstchunk,ctrl.nchunks),jobscript, qenviron)
#         print ("return value was %s" % thispid)
#   except:
#         print "ERROR Spawning the sinogram job didn't work ",thispid
#         pyerr.close()
#         pyout.close()
#         pyenv_o.close()
#         pyenv_e.close()
#         sys.exit(7)


if __name__ == "__main__":
      print "Running main"
      main()

