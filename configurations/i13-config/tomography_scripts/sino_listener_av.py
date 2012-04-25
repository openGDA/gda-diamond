#!/dls_sw/tools/bin/python2.4
#$Id: sino_listener.py 103 2010-08-11 11:03:44Z kny48981 $
import getopt
import sys
import os
import commands
import shutil
import time
import glob
import platform
import subprocess

interval=1
lt=10
vflag=False


def errprint(message="none"):
   print "errprint"
   print "sino_listener.py: %s" % (message)

def vprint(message):
    global vflag
    if vflag:
        print  message


def usage():
   svnstring="$Id: sino_listener.py 103 2010-08-11 11:03:44Z kny48981 $"
   global interval
   global lt
   print("%s version %s" %(sys.argv[0],svnstring))
   print("Usage:")
   print(sys.argv[0])
   print(" -i input dir")
   print ("-o output dir (relative to input dir )")
   print ("-w width")
   print ("-l length (height) of each chunk")
   print ("-n number of chunks ")
   print ("-J job hame ")
   print ("-j suffix of job name ")
   print ("-U Unique ID (REQUIRED) ")
   #print ("-E use existing data (bypassing epics)")
   #print ("-d Delete temporary files")
   print ("-b bytes per pixel")
   print ("-s number of segments")
   print ("-p number of projections per segment")
   #print ("-T convert to Tiff")
   print ("-Z timeout (default %i)" % lt)
   print ("-z check interval (default %i)" % interval )
   


def main():
   print "Entering main"
   global interval
   global lt
   global vflag
   inflag=False
   outflag=False
   delflag=False
   tifflag=False
   vflag=False
   pstrings=['p','f','a']
   pnums=[0,0,0]
   pidnums=[]

   #width and height need to come from somewhere too ..
   #some defaults for testing

   wd=4000                   #default
   ht=2000                   #default
   bytes=2                   #default
   nchunks=8                 #default
   nsegs=1                   #default
   nperseg=10                #default
   jobbasename="chunk"       #default
   jobname="chunk_sino"      #default
   existflag=" "             #default
   jobsuffix=""              #default
   myqueue="high.q"        #default
   uniqueid="undefined"      #default


   try:                                
      opts, args = getopt.gnu_getopt(sys.argv[1:],  "a:U:O:C:EGI:J:N:R:STZ:b:cdf:hi:j:l:n:o:p:s:vw:xz:")
   except getopt.GetoptError, err:           
      errprint ("Option parsing error")
      errprint ("Command line values: %s" % (sys.argv))
      errprint("Message is %s" % (str(err))) 
      usage()                          
      sys.exit(2)                     
   for o,a in opts:
      if o == "-i":
          indir=a
          inflag=True
      elif o == "-o":
           outdir=a
           outflag=True

      elif o == "-l":
           chunk_ht=int(a)
      elif o == "-a":
           avnum=int(a)
      elif o == "-w":
           wd=int(a)
      elif o == "-b":
           bytes=int(a)
      elif o == "-J":
           jobbasename="%s" % a
      elif o == "-U":
           uniqueid="%s" % a
           uniqueflag=True
      elif o == "-j":
           jobsuffix="_%s" % a 
      elif o == "-E":
           existflag="-E"
      elif o == "-s":
           nsegs=int(a)
      elif o == "-p":
           nperseg=int(a)
      elif o == "-n":
           nchunks=int(a)

      elif o == "-T":
           tifflag=True
      elif o == "-h":
           usage()
           sys.exit(0)
      elif o == "-d":
           delflag=True
      elif o == "-Z":
          lt=int(a)
      elif o == "-z":
          interval=int(a)
      elif o == "-v":
          vflag=True
      else:
           errprint ("Ignored option")
           errprint ("option %s value %s" % (o,a))
           #usage()
           #sys.exit(2)
   if ( not (inflag and outflag)):
      errprint("Input and Output directories must be specified")
      usage()
      sys.exit(3)

   # How to handle the last chunk?
   #for now we assume all chunks are the same height


   jobname="%s_sino%s" %(jobbasename,jobsuffix)
   nproj=nperseg*nsegs
   ht=chunk_ht * nchunks
   projnum=0
   size=wd*ht
   size_bytes=wd*ht*bytes
   chunk_size=wd*chunk_ht
   chunk_size_bytes = chunk_size * bytes 
   linebytes=wd*bytes
   chunkrange=range(1,nchunks+1)
   projrange=range(0,nproj)
   sinorange=range(0,chunk_ht)
   vprint ("chunk_ht: %i " % chunk_ht)
   vprint (sinorange)
   finishname="f_%s" % jobname
   print("JOB NAME IS %s\n") % finishname

#check folder for the project 
   print "Checking for input directory %s \nTimeout: %i seconds" % (indir,lt)
   wtime=0
   found=0
   #wait for the directory to appear
   while ( (wtime <= lt) and (found == 0) ):
      if not ( os.access (indir, os.F_OK)):
         wtime += interval
         time.sleep(interval)
         print "." 
      else:
         found=1
   #exit if it times out
   if not (os.access (indir, os.F_OK)):
         errprint ("Input directory %s is not available after %i seconds!" % (indir,wtime))
         sys.exit(5)
   else:
      print "Input directory %s found...." % indir

#check folders for the chunks

#   for i in chunkrange:
#      ipartdir="%s/%03i" % (indir,i) 
#      vprint ("Checking for chunk directory %s\n Timeout %i" % (ipartdir,lt))
#      wtime=0
#      found=0
#      #wait for the directory to appear
#      while (wtime <= lt and found == 0 ):
#         if not ( os.access (ipartdir, os.F_OK)):
#            wtime += interval 
#            time.sleep(interval)
#            vprint (".")
#         else:
#            found=1
#
#      #exit if it times out
#      if not ( os.access (ipartdir, os.F_OK)):
#         errprint ("Chunk directory %s is not available after %i seconds!" % (ipartdir,wtime))
#         sys.exit(6)
#      else:
#         print "Chunk directory %s found...." % indir
#
   print "All chunk directories found... " 

#locate or create the output folders
   print "output directory %s" % outdir
   if not (os.access (outdir, os.F_OK)):
      print "creating %s " % outdir
      os.mkdir(outdir)

   #create folders for the chunks

   for i in chunkrange:
      opartdir="%s/%03i" % (outdir,i) 
      print "chunk directory %s" % opartdir
      if not ( os.access (opartdir, os.F_OK)):
         print "creating %s " % opartdir
         os.mkdir(opartdir )

      #open the file

   #
   #
   #

   #create the queue bash script for the queue task array

   thisdir=os.getcwd()
   if (uniqueflag):
      mypid=uniqueid
   else:
      mypid=os.getpid()
   #chunkscript="sinochunk.qsh" % os.getpid()
   chunkscript="sinochunk.qsh" 
   finishscript="finishchunk.qsh" 
   #chunkprogram="/home/kny48981/progs/tomo_recon_pipe/scripts/sino_chunk_q.py"
   #chunkprogram="/dls_sw/i12/software/tomography_scripts/sino_chunk_ezca_tiff_q"
   chunkprogram="sino_chunk_avg.q" #use the path ... 
   chunkflags="-i %s -o %s -w %i -l %i -z %i  -Z %i  -s %i -p %i -b %i %s -a %i" % (indir,outdir,wd,chunk_ht,interval,lt,nsegs,nperseg,bytes,existflag,avnum) 
   myqueue="medium.q"
   vprint("Creating the queue script: %s" % chunkscript)
   vprint("Using : %s" % chunkprogram)

   sys.stdout = open(chunkscript,"w")
   print("""\
#!/bin/bash 
set -x

#add the modules required 
source /dls_sw/i12/modulefiles/modules.sh
#add environment required by epics channel access (ezca) 
module add /dls_sw/i12/modulefiles/local-64
module add /dls_sw/i12/modulefiles/epicstomo
myjob=$JOB_ID
mytask=$SGE_TASK_ID
mypid=%s

export PATH=$PATH:${EPICS_BASE}/bin/${EPICS_HOST_ARCH}:${EPICS_EXTENSIONS}/bin/${EPICS_HOST_ARCH}

echo PATH is $PATH
echo "caRepeater:"
which caRepeater
ulimit -c unlimited
# env > task${mytask}.env

%s %s -m $mytask  -v -J %s${myjob}_t${mytask}
retval=$?
if [[ retval -ne 0 ]]
then
  echo -e "job $myjob task $mytask return-value $retval\n" >> error_$mypid.txt  
fi


""") % (mypid,chunkprogram,chunkflags,jobname)
#end of the queue script text
   sys.stdout.flush()
   sys.stdout=sys.__stdout__

   vprint("Creating the finishing script: %s" % finishscript)

   sys.stdout = open(finishscript,"w")
   print("""\
#!/bin/bash 
set -x

#add the modules required 
source /dls_sw/i12/modulefiles/modules.sh
#add environment required by epics channel access (ezca) 

myjob=$JOB_ID
mytask=$SGE_TASK_ID
mypid=%s
jjname="%s"
ffolder="${jjname}_files"
if [[ -e error_$mypid.txt ]]
then
errtxt=`cat error_$mypid.txt`

		#send a mail message when completed
		/usr/sbin/sendmail -t $USER <<-ENDM
			Subject: [QUEUE] I12 job error from PID ${mypid}

                         The I12 data acquisition job has encountered a problem.
                         The error information is:

                         $errtxt

                         This  e-mail was automatically generated by
                         the tomographic reconstruction batch processing system

		ENDM

fi

mkdir -p ${ffolder}/job${myjob}
mv ${jjname}_sino* ${ffolder}/job${myjob}

""") % (mypid,jobbasename)
#end of the finish script text
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
   pyerr=open("sino_listener_stderr_%s" % jobname ,"w")
   pyout=open("sino_listener_stdout_%s" % jobname ,"w")
   pyenv_o=open("pyenv_o_%s" % jobname,"w")
   pyenv_e=open("pyenv_e_%s" % jobname,"w")

  # try:
  #    print ("Spawning the sinogram job ... ")
  #    thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub","-P","i12","-q",myqueue,"-N",jobname,"-cwd","-pe","smp","4","-t","1-%i" % nchunks,chunkscript,qenviron)
  #    print ("return value was %s" % thispid);
  # except:
  #    print ("ERROR Spawning the sinogram job didn't work")
  #    sys.exit(147)
   try:
         print ("Spawning the sinogram job ... ")
         #queue_args=["qsub","-P","i12","-q",myqueue,"-N",jobname,"-cwd","-pe","smp","4","-t","1-%i" % nchunks,chunkscript]
         #queue_args="qsub -P i12 -q %s  -N %s -cwd -pe smp 4 -t 1-%i %s " % (myqueue,jobname,nchunks,chunkscript)
         #queue_args=["which qsub","-x"]
         #print ("queue args are",queue_args)
         #subprocess.Popen(queue_args,env=qenviron,stout=pyout,stderr=pyerr)
         if (vflag):
            subprocess.Popen("env",env=qenviron,shell=False,stdout=pyenv_o,stderr=pyenv_e)
            print qenviron
         #thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub", "-q",myqueue,"-N",jobname,"-cwd","-pe","smp","4","-t","1-%i" % nchunks,chunkscript, qenviron)
         thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub", "-P","i12","-q",myqueue,"-N",jobname,"-cwd","-pe","smp","4","-t","1-%i" % nchunks,chunkscript, qenviron)
         #subprocess.Popen(queue_args,env=qenviron,shell=True,stdout=pyout,stderr=pyerr)
         #(queue_args,env=qenviron,shell=True,stdout=pyout,stderr=pyerr)
         print ("return value was %s" % thispid)
   except:
         print ("ERROR Spawning the sinogram job didn't work")
         pyerr.close()
         pyout.close()
         pyenv_o.close()
         pyenv_e.close()
         sys.exit(147)

   try:
         print ("Spawning the sinogram finishing job ... ")
         thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub","-P","i12","-q","high.q","-hold_jid",jobname,"-N",finishname,finishscript,qenviron)
         print ("return value was %s" % thispid)

   except:
         print ("Spawning the sinogram finishing job didn't work")
         pyerr.close()
         pyout.close()
         sys.exit(148)

   pyerr.close()
   pyout.close()

   sys.exit(0)
   

if __name__ == "__main__":
      print "Running main"
      main()
