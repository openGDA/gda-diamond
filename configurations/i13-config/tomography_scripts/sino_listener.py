#!/dls_sw/tools/bin/python2.4
#$Id: sino_listener.py 232 2012-04-11 13:21:04Z kny48981 $
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
wd=4008                   #default
ht=2672                    #default
firstchunk=1              #default
lastchunk=16
nchunks=16                #default
chunk_ht=167              #default
vflag=False
nproj=0
nperseg=0
infmt="p_%05d.tif"


def errprint(out, message="none"):
   out.write ("errprint")
   out.write ( "sino_listener.py: %s" % (message))

def vprint(out, message):
    global vflag
    if vflag:
        out.write (message)

def usage(out):
   svnstring="$Id: sino_listener.py 232 2012-04-11 13:21:04Z kny48981 $"
   global interval
   global infmt
   global lt
   global wd
   global ht
   global chunk_ht
   global firstchunk
   global lastchunk
   global nchunks
   global nperseg
   global nproj
   global chunk_ht
   out.write("Version %s" %(svnstring))
   out.write("Usage:")
   out.write(sys.argv[0])
   out.write ("-i input dir (currently: projections)")
   out.write ("-o output dir (currently: sinograms)")
   out.write ("-p number of projections (currently %i )" % nperseg)
   out.write ("    NOT automatically determined!")
   out.write ("-w width (currently %i )" % wd)
   out.write ("-l length (height) of the image(currently %i)" % ht)
   out.write ("-F number of first chunk (currently %i) " % firstchunk)
   out.write ("-L number of last chunk (currently same as number of chunks) " )
   out.write ("-n total number chunks (currently %i) " % nchunks)
   out.write ("-J job hame ")
   out.write ("-j suffix of job name ")
   #out.write ("-E use existing data (bypassing epics)")
   #out.write ("-d Delete temporary files")
   out.write ("-b bytes per pixel (currently 2)")
   out.write ("-s number of segments (currently 1) ")
   #out.write ("-T convert to Tiff")
   out.write ("-Z timeout (currently %i)" % lt)
   out.write ("-z check interval (currently %i)" % interval )
   out.write ("-Q queue (currently medium.q) ")
   out.write ("-U Unique ID (currently use PID) ")
   out.write ("-I input filename format (C out.writef style) (currently %s) " % infmt)
   out.write ("-1 start numbering of input files from 1 instead of 0 ")
   out.write ("-t do nothing. Just create the bash script file")
   


def main(argv, out=sys.stdout, err=sys.stderr ):
   global chunk_ht
   global firstchunk
   global ht
   global infmt
   global interval
   global lastchunk
   global lt
   global nchunks
   global nperseg
   global nproj
   global vflag
   global testing # if true just produce the basj script file
   global wd
   uniqueflag=False
   inflag=False
   idxflag=" "
   outflag=False
   lastflag=False
   delflag=False
   tifflag=False
   vflag=False
   testing=False
   pstrings=['p','f','a']
   pnums=[0,0,0]
   pidnums=[]
   mypid=os.getpid()

   #width and height need to come from somewhere too ..
   #some defaults for testing

   indir="projections"
   outdir="sinograms"
   bytes=2                   #default
   firstchunk=1              #default
   nchunks=16                #default
   nsegs=1                   #default
   nperseg=6000              #default
   jobbasename="chunk"       #default
   jobname="chunk_sino"      #default
   existflag=" "             #default
   jobsuffix=""              #default
   myqueue="low.q"        #default
   uniqueid="U"              #default
   cropleft=0
   cropright=0
   hflag=0
   if (len(argv) < 2):
      hflag=1

   Wflag=0
   try:                                
      opts, args = getopt.gnu_getopt(argv[1:],  "1U:O:C:EGI:J:N:R:S:T:Z:b:cF:L:hi:j:l:n:o:p:s:vw:xz:Q:W:t")
   except getopt.GetoptError, err:           
      errprint (out, "Option parsing error")
      errprint (out, "Command line values: %s" % (argv[1:]))
      errprint(out, "Message is %s" % (str(err))) 


      usage(out)                          
      raise Exception("Invalid usage")                     
   if not (len(args) == 0 ):
      errprint (out, "Option parsing error")
      errprint (out, "Command line values: %s" % (argv[1:]))
      errprint(out, "This program should not have non-flagged arguments") 
      out.write ("unrecognized arguments: " + `args`)
      out.write ( `opts` + `args`)
      sys.exit(2)

   for o,a in opts:
      if o == "-W":
          mywait=a
          Wflag=1
      if o == "-Q":
          myqueue=a
      elif o == "-i":
          indir=a
          inflag=True
      elif o == "-1":
          idxflag="-1"
      elif o == "-I":
          infmt=a
          inflag=True
      elif o == "-o":
           outdir=a
           outflag=True
      elif o == "-l":
           ht=int(a)
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
      elif o == "-L":
           lastchunk=int(a)
           lastflag=True
      elif o == "-F":
           firstchunk=int(a)
      elif o == "-R":
           cropright=int(a)
      elif o == "-T":
           cropleft=int(a)
      elif o == "-h":
           hflag=1
      elif o == "-Z":
          lt=int(a)
      elif o == "-z":
          interval=int(a)
      elif o == "-v":
          vflag=True
      elif o == "-t":
          testing=True
      else:
           errprint (out, "Ignored option")
           errprint (out, "option %s value %s" % (o,a))

   if (len(argv) ==2 and testing):
      hflag=1

   if (hflag):
      usage(out)
      return

   if (uniqueflag):
      mypid=uniqueid
   else:
      if testing:
          mypid="testing_pid"
      else:
          mypid=os.getpid()

   if (lastflag):
      out.write("Selecting last chunk to process: %i " % lastchunk )
   else:
      lastchunk=nchunks

   out.write ("Using first chunk %i and last chunk %i" %(firstchunk,lastchunk))

   


   jobname="%s_sn_%s_%s" %(jobbasename,jobsuffix,mypid)

   settingsbase="sino_output"
   if testing:
       tstamp = "testing"
   else:
       tstamp=time.strftime("%Y_%m%d_%H%M%S")
   settingsfolder="%s/sino_%s_files" % (settingsbase, tstamp)
   out.write ("Settings folder will be : %s " % settingsfolder)
   nproj=nperseg*nsegs

   chunk_ht = ht/nchunks

   projnum=0
   size=wd*ht
   size_bytes=wd*ht*bytes
   chunk_size=wd*chunk_ht
   chunk_size_bytes = chunk_size * bytes 
   linebytes=wd*bytes
   chunkrange=range(1,nchunks+1)

   projrange=range(0,nproj)
   sinorange=range(0,chunk_ht)
   vprint(out,"ht %i chunk_ht: %i " % (ht, chunk_ht))
   vprint(out,sinorange)
   finishname="f_%s" % jobname
   out.write("JOB NAME IS %s\n" % finishname)
   out.write("using input file format %s\n" % infmt)

#check folder for the project 
   out.write ("Checking for input directory %s \nTimeout: %i seconds" % (indir,lt))
   wtime=0
   found=0
   #wait for the directory to appear
   while ( (wtime <= lt) and (found == 0) ):
      if not ( os.access (indir, os.F_OK)):
         wtime += interval
         time.sleep(interval)
         out.write (".") 
      else:
         found=1
   #exit if it times out
   if not (os.access (indir, os.F_OK)):
         errprint (out, "Input directory %s is not available after %i seconds!" % (indir,wtime))
         sys.exit(5)
   else:
      out.write ("Input directory %s found...." % indir)

#locate or create the output folders
   if not(os.access (settingsbase,os.F_OK)):
      os.mkdir(settingsbase)

   if not(os.access (settingsfolder,os.F_OK)):
      out.write ("creating %s" % settingsfolder)
      os.mkdir(settingsfolder)

   #create the queue bash script for the queue task array

   thisdir=os.getcwd()
   #chunkscript="sinochunk.qsh" % os.getpid()
   chunkscript="%s/sinochunk.qsh" % settingsfolder
   finishscript="%s/finishchunk.qsh" % settingsfolder
   chunkprogram="sino_chunk_tiff_new.q"
   chunkflags="-i %s -o %s -w %i -l %i -z %i  -Z %i  -s %i -p %i -b %i %s -S %s -I %s -T %i -R %i %s " % (indir,outdir,wd,chunk_ht,interval,lt,nsegs,nperseg,bytes,existflag,settingsfolder,infmt,cropleft,cropright,idxflag) 
   vprint(out,"Creating the queue script: %s" % chunkscript)
   vprint(out,"Using : %s" % chunkprogram)

   chunkscriptOut = open(chunkscript,"w")

   #output the introductory script section
   chunkscriptOut.write("""\
#!/bin/bash 
set -x

#add the modules required 
source /dls_sw/i12/modulefiles/modules.sh
module add /dls_sw/i12/modulefiles/local-64
myjob=$JOB_ID
mytask=$SGE_TASK_ID
""") 

   #set the unique identifier value
   chunkscriptOut.write("""mypid=%s""" % mypid)

   #set the output folder
   chunkscriptOut.write("""odir=%s""" % outdir)

   #check folder existance
   chunkscriptOut.write("""\
if [[ ! -e $odir ]]
then
mkdir -p $odir
fi
mynum=`out.writef "%%03d" $mytask`

echo PATH is $PATH

#ulimit -c unlimited
# UNCOMMENT  some of these lines to get more diagnostic information
# env > task${mytask}.env
#tracename=trace${myjob}_t${mytask}.trace
#trace execution all
""") 

   #assemble the command line that actually does the task
   chunkscriptOut.write("""\
%s %s -m $mytask  -v -J %s${myjob}_t${mytask}
""" % (chunkprogram,chunkflags,jobname) )

   #check for error in return value
   chunkscriptOut.write("""\
retval=$?
if [[ retval -ne 0 ]]
then
  echo -e "job $myjob task $mytask return-value $retval\\n" >> %s/error_$mypid.txt  
fi
""" % settingsfolder)

#end of the queue script text
   chunkscriptOut.flush()
   
   if testing:
       out.write( "Exiting after creating chunkscript file")
       return
   


   vprint(out,"Creating the finishing script: %s" % finishscript)

   finishscriptOut = open(finishscript,"w")
   finishscriptOut.write("""\
#!/bin/bash 
set -x

#add the modules required 
source /dls_sw/i12/modulefiles/modules.sh
#add environment required by epics channel access (ezca) 

myjob=$JOB_ID
mytask=$SGE_TASK_ID
mypid=%s
jjname="%s"
""" % (mypid,jobbasename) )

   finishscriptOut.write("""\
ffolder="${jjname}_files"
errfile=%s/error_$mypid.txt
""" % settingsfolder )

   finishscriptOut.write("""\
if [[ -e $errfile ]]
then
errtxt=`cat $errfile`

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

#mkdir -p ${ffolder}/job${myjob}
#mv ${jjname}_sino* ${ffolder}/job${myjob}

mv *.trace %s
""" % settingsfolder )

#end of the finish script text
   finishscriptOut.flush()



   #set the queue environment
   qenviron=os.environ
   vprint(out,len(qenviron))
   vprint(out,qenviron.items())
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
   vprint(out,len(qenviron))
   vprint(out,qenviron.items())
   pyerr=open("%s/sino_listener_stderr_%s.txt" % (settingsfolder,jobname) ,"w")
   pyout=open("%s/sino_listener_stdout_%s.txt" % (settingsfolder,jobname) ,"w")
   pyenv_o=open("%s/python_stdout_%s.txt" % (settingsfolder,jobname),"w")
   pyenv_e=open("%s/python_stderr_%s.txt" % (settingsfolder,jobname),"w")

   try:
         out.write ("Spawning the sinogram job ... ")
         if (vflag):
            subprocess.Popen("env",env=qenviron,shell=False,stdout=pyenv_o,stderr=pyenv_e)
            out.write (qenviron)
         if (Wflag):
            thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub", "-P","i12","-e",settingsfolder, "-o", settingsfolder, "-q",myqueue,"-N",jobname,"-hold_jid",mywait,"-cwd","-pe","smp","4","-t","%i-%i" % (firstchunk,lastchunk),chunkscript, qenviron)
         else:
            thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub", "-P","i12","-e",settingsfolder, "-o", settingsfolder, "-q",myqueue,"-N",jobname,"-cwd","-pe","smp","4","-t","%i-%i" % (firstchunk,lastchunk),chunkscript, qenviron)
         #thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub", "-e",settingsfolder, "-o", settingsfolder, "-q",myqueue,"-N",jobname,"-cwd","-t","%i-%i" % (firstchunk,lastchunk),chunkscript, qenviron)
         out.write ("return value was %s" % thispid)
   except:
         out.write ("ERROR Spawning the sinogram job didn't work")
         pyerr.close()
         pyout.close()
         pyenv_o.close()
         pyenv_e.close()
         raise Exception(147)

   try:
         out.write ("Spawning the sinogram finishing job ... ")
         thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub","-P","i12","-e",settingsfolder,"-o",settingsfolder,"-q","high.q","-hold_jid",jobname,"-N",finishname,finishscript,qenviron)
         out.write ("return value was %s" % thispid)

   except:
         out.write ("Spawning the sinogram finishing job didn't work")
         pyerr.close()
         pyout.close()
         raise Exception(148)

   pyerr.close()
   pyout.close()

   return
   

if __name__ == "__main__":
      main(sys.argv)

import math
import unittest

class Test1(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_noArgs(self):
        (out, err,  errFileName, outputFileName) = self.outAndErr("test_noArgs")
        main(["program"], out=writer_newline(out), err=writer_newline(err))
        out.close()
        err.close()
        self.checkFilesMatch("expected_usage.txt", outputFileName )
        self.checkFilesMatch("empty.txt" , errFileName)

    def test_testing(self):
        (out, err,  errFileName, outputFileName) = self.outAndErr("test_testing")
        main(["program","-t"], out=writer_newline(out), err=writer_newline(err))
        out.close()
        err.close()
        self.checkFilesMatch("expected_usage.txt", outputFileName)
        self.checkFilesMatch( "empty.txt", errFileName)

    def test_help(self):
        (out, err, errFileName, outputFileName) = self.outAndErr("test_help")
        main(["program","-h"], out=writer_newline(out), err=writer_newline(err))
        out.close()
        err.close()
        self.checkFilesMatch( "expected_usage.txt", outputFileName)
        self.checkFilesMatch("empty.txt", errFileName)

    def test_i_no_parameter(self):
        (out, err, errFileName, outputFileName) = self.outAndErr("test_i_no_parameter")
        try:
            main(["program","-i"], out=writer_newline(out), err=writer_newline(err))
        except Exception, ex:
           self.assertEquals('Invalid usage', str(ex))             
        out.close()
        err.close()
        self.checkFilesMatch(outputFileName, outputFileName)
        self.checkFilesMatch("empty.txt", errFileName)

    def test_i_cdw(self):
        (out, err, errFileName, outputFileName) = self.outAndErr("test_i_cdw")
        main(["program","-i",".","-t"], out=writer_newline(out), err=writer_newline(err))
        out.close()
        err.close()
        self.checkFilesMatch(outputFileName, outputFileName)
        self.checkFilesMatch("empty.txt", errFileName)
    
    def outAndErr(self,testName):
        outputFileName = testName + "_output.txt"
        errFileName = testName + "_err.txt"
        out=open( "testing_actual_output" + '/' + outputFileName,"w")
        err=open( "testing_actual_output" + '/' + errFileName,"w")
        return (out, err, errFileName, outputFileName)

    def checkFilesMatch(self, expectedFilePath, actualFilePath):
        expectedFilePath = "testing_expected_output" + '/' + expectedFilePath
        actualFilePath = "testing_actual_output" + '/' + actualFilePath
        f = open(actualFilePath)
        linesActual =  f.readlines()
        f.close
        f = open(expectedFilePath)
        linesExpected =  f.readlines()
        f.close
        lastIndexToCompare = min(len(linesActual), len(linesExpected) ) 
        for i in range(lastIndexToCompare):
            self.assertEqual(linesActual[i], linesExpected[i])
        if len(linesExpected) == len(linesActual):
            return
        extraLines = []
        if lastIndexToCompare == len(linesActual):
            extraLines = linesExpected[lastIndexToCompare:]
        else:
            extraLines = linesActual[lastIndexToCompare:]
        self.assertEqual("",`extraLines`)
        
            
        
class writer_newline:
    def __init__(self, pipe):
        self.pipe = pipe
    def write(self, msg):
        self.pipe.write(msg)
        self.pipe.write("\n")
        self.pipe.flush()

def suite():
    return unittest.TestSuite(( unittest.TestLoader().loadTestsFromTestCase(Test1)))
