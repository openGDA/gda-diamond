#!/dls_sw/prod/tools/RHEL5/bin/python2.6
import sys
import os
import time
import getopt
import subprocess
import platform
from xml.dom.minidom import parse
from math import log10, floor


def ndigits(N):
#lambda N: ((N==0) and 1) or floor(log10(abs(N)))+1    
   ndig=0    
   if N==0:
      ndig=1
   else:
      ndig=floor(log10(abs(N)))+1
   return ndig

def setenvironment():
   global qenviron

   #set the queue environment
   qenviron=os.environ
   oldpath=""
   try :
      oldpath = qenviron["PATH"]
   except :
      oldpath = ""
   if ( "64bit" == platform.architecture()[0] ) :
      newpath="/dls_sw/apps/sge/UGE8.3.1/bin/lx-amd64/:/bin:/usr/bin:%s" % oldpath
   else:
      newpath="/dls_sw/apps/sge/UGE8.3.1/bin/lx-amd64/:/bin:/usr/bin:%s" % oldpath
   qenviron["SGE_CELL"]="DLS_SCIENCE"
   qenviron["SGE_EXECD_PORT"]="60031"
   qenviron["SGE_QMASTER_PORT"]="60030"
   qenviron["SGE_ROOT"]="/dls_sw/apps/sge/UGE8.3.1"
   qenviron["PATH"]=newpath
   
def printusage():
   print(sys.argv[0])
   desc = "\nDesc: To create a queued batch for testing a range of values for reconstruction parameters R and NumSeries (NS).\n"
   desc += "For parameter R, two modes are available for creating a range: arithmetic series (a) and geometric series (g).\n"
   desc += "For parameter NS, arithmetic series is always applied.\n"
   print(desc)
   print("Usage: %s Rstart [Rsteps Rstep NSstart NSsteps NSstep Rmode SLICEstart SLICEsteps SLICEstep SETTINGSxml]") % (sys.argv[0])
   #print("Usage: %s Rstart Rtot Rinc NSstart NStot NSinc mode SLICEstart SLICEtot SLICEinc") % (sys.argv[0])
   print("REQUIRED: Rstart")
   print("defaults: Rsteps=16, Rstep=1, NSstart=1, NSsteps=1, NSstep=1, Rmode=g, SLICEstart=500, SLICEsteps=1, SLICEstep=1, SETTINGSxml=\"./settings.xml\"")
   print("inputs: settings XML file in current directory, and sinograms in 'sinograms' sub-directory of current directory")
   print("pre-requisite: input settings XML file must have RingArtefacts set to 'AML'")
   print("pre-requisite: input settings XML file must have ImageCentre set to the optimal centre of rotation already found")
   print("outputs: stored in 'param_output' directory, containing two time-stamped sub-directories: one for text files and the other for images\n")
   print("example 1: q2paramxml.py 1e-2 4 1e-1 1 1 1") 
   print("   generates Rsteps*NSsteps=4*1=4 reconstructions of default slice 500, corresponding to parameter pairs: (R, NS) = (0.01, 1), (0.001, 1), (0.0001, 1), (0.00001, 1)")
   print("example 2: q2paramxml.py 1e-2 4 1e-1 1 2 1")
   print("   generates Rsteps*NSsteps=4*2=8 reconstructions of default slice 500, corresponding to parameter pairs: (R, NS) = (0.01, 1), (0.001, 1), (0.0001, 1), (0.00001, 1), (0.01, 2), (0.001, 2), (0.0001, 2), (0.00001, 2)")
   print("example 3: q2paramxml.py 1e-2 4 1e-1 1 2 1 a")
   print("   generates Rsteps*NSsteps=4*2=8 reconstructions of default slice 500, corresponding to parameter pairs: (R, NS) = (0.01, 1), (0.02, 1), (0.03, 1), (0.04, 1), (0.01, 2), (0.02, 2), (0.03, 2), (0.04, 2)")
   
def main():
   global qenviron
   argc=len(sys.argv)
   print"Number of args supplied on the command line: %i" %argc
   if (argc <= 1 ):
      printusage()
      return

   proj="i12"
   #proj="i13"
   myqueue="low.q"

   #set the queue environment
   setenvironment()
   reconprogram="dt64n -v 4"
   obasefolder="param_output"
   tstamp=time.strftime("%Y_%m%d_%H%M%S")
   myfolder="par_%s_files" % tstamp
   imfolder="par_%s_images" % tstamp
   mypath="%s/%s" % (obasefolder,myfolder)
   impath="%s/%s" % (obasefolder,imfolder)

   if not(os.access (obasefolder,os.F_OK)):
      os.mkdir(obasefolder)

   if not(os.access (mypath,os.F_OK)):
      os.mkdir(mypath)

   if not(os.access (impath,os.F_OK)):
      os.mkdir(impath)

   rstart=0.005
   rstep=1.0

   rstart=float(sys.argv[1])


   if (argc >= 3 ):
      rsteps = int(sys.argv[2])
   else:
      rsteps  = 16

   if (argc >= 4 ):
      rstep = float(sys.argv[3])
   else:
      rstep = 1.0
#
   if (argc >= 5 ):
      nsstart = float(sys.argv[4])
   else:
      nsstart = 1.0

   if (argc >= 6 ):
      nssteps = int(sys.argv[5])
   else:
      nssteps = 1

   if (argc >= 7 ):
      nsstep = float(sys.argv[6])
   else:
      nsstep = 1.0

   if (argc >= 8 ):
      rmode = sys.argv[7]
   else:
      rmode = "g"
#
   if (argc >= 5+4 ):
      slicestart = int(sys.argv[4+4])
   else:
      slicestart = 500

   if (argc >= 6+4 ):
      nslices = int(sys.argv[5+4])
   else:
      nslices = 1

   if (argc >= 7+4 ):
      slicestep = int(sys.argv[6+4])
   else:
      slicestep = 1

   if (argc >= 8+4 ):
      xmlinfile = (sys.argv[7+4])
   else:
      xmlinfile = "settings.xml" 


   print("rstart: %f" % rstart)
   print("rsteps: %i" % rsteps)
   print("rstep: %f" % rstep)
   
#
   print("nsstart: %f" % nsstart)
   print("nssteps: %i" % nssteps)
   print("nsstep: %f" % nsstep)

   print("rmode: %s" % rmode)

   if rmode=="a":
      print("\t In this mode, 'a', values of R parameter form arithmetic series: R = Rstart + Rstep*i, where i=0, 1,... , Rsteps-1")
   else:
      print("\t In this mode, 'g', values of R parameter form geometric series: R = Rstart * Rstep^i, where i=0, 1,... , Rsteps-1")

   print("\t In this, and any other other, mode values of NumSeries parameter form arithmetic series: NS = NSstart + NSstep*j, where j=0, 1,... , NSsteps-1")

   slicestop=slicestart + ((nslices - 1 ) * slicestep)

   print("slicestart: %i" % slicestart)
   print("slicestop: %i" % slicestop)
   print("slicestep: %i" % slicestep)
   print("xmlinfile: %s" % xmlinfile)

   print("proj: %s" % proj)
   print("queue: %s" % myqueue)

   mydoc=parse(xmlinfile)

   #set the slice range and input folder which is constant for all different centre values

   bptag=mydoc.getElementsByTagName("InputData")
   valtag=bptag[0].getElementsByTagName("FileFirst")
   valtag[0].childNodes[0].data=slicestart

   valtag=bptag[0].getElementsByTagName("FileLast")
   valtag[0].childNodes[0].data=slicestop

   valtag=bptag[0].getElementsByTagName("FileStep")
   valtag[0].childNodes[0].data=slicestep

   valtag=bptag[0].getElementsByTagName("Folder")
   valtag[0].childNodes[0].data="sinograms"

   #set the output folder and path for this job
   bptag=mydoc.getElementsByTagName("OutputData")

   valtag=bptag[0].getElementsByTagName("Folder")
   valtag[0].childNodes[0].data=impath
   mycpu=0

   print("\n")

   # figure out number of digits to be used in ns-tag in output filename
   nsstop = nsstart + nsstep*(nssteps-1)
   print("nsstop: %i" % nsstop)
   # count number of digits in nsstop!
   nsstop_ndigits = ndigits(nsstop)
   print("nsstop_ndigits: %i" % nsstop_ndigits)
   nsnametag = "NS%%0%ii_" %(max(2,ndigits(nsstop)))
   print("nsnametag: %s" % nsnametag) # eg NS%02i_

   # figure out number of digits to be used in sgetask-tag in XML log filename
   
   #return
   #create a separate xml for each centre value
   sgetasks=0
   for rloop in range(0,rsteps,1):
      # calc next value of parameter R
      if rmode=="a":
         r=round(rstart+float(rloop)*rstep,5)
      else:
         r=round(rstart*pow(rstep,rloop),10) 

      for nsloop in range(0,nssteps,1):
	 # calc next value of parameter NS
         ns=nsstart+(nsloop*nsstep)

	 #advance sgetask index
         sgetasks+=1
         #print("rloop: %i" % rloop)
         #print("nsloop: %i" % nsloop)
         #print("sgetask: %i" % sgetasks)
         print("rloop: %i; nsloop: %i; task %i; parameter R: %f; parameter NS: %i" % (rloop,nsloop,sgetasks,r,ns))

         #change the values in the xml tags 
         #create the file prefix for this job
         outputs=mydoc.getElementsByTagName("OutputData")
         prefix=outputs[0].getElementsByTagName("Prefix")
         prefix[0].childNodes[0].data="param_R%08.5g_NS%02i_" % (r,ns)

         #set ring-suppression params as specified
         bptag=mydoc.getElementsByTagName("Preprocessing")
         ntag=bptag[0].getElementsByTagName("RingArtefacts")
         ir=ntag[0].getElementsByTagName("ParameterR")
         ir[0].childNodes[0].data=r

	 ins=ntag[0].getElementsByTagName("NumSeries")
         ins[0].childNodes[0].data=ns

         bptag=mydoc.getElementsByTagName("LogFile")
         bptag[0].childNodes[0].data="%s/log_%03i.xml" %(mypath,sgetasks)

         #use the task number for file name to simplify queue script

         f=file("%s/param_%03d.xml" % (mypath,(sgetasks)),"w")
         f.write(mydoc.toxml())
         f.close()


   print("\n sgetasks tot: %i (expected %i)" % (sgetasks, (rsteps*nssteps)))
   #print("\n sgetasks tot: %i" % sgetasks)
   #create a little bash script to run in the queue
   myscript="%s/param.qsh" % mypath
   sys.stdout = open(myscript,"w")

   #output the introductory script section
   print("""\
#!/bin/bash 
#parameter script
set -x
#add the modules required 
#source /dls_sw/i12/modulefiles/modules.sh
source /etc/profile.d/modules.sh
module add /dls_sw/i12/modulefiles/local-64
myjob=$JOB_ID
mytask=$SGE_TASK_ID
myxmlfile=`printf "param_%03d.xml" $mytask`
""")

   #create the correct path for the input file
   print("""\
mypath=%s
myxmlpath=$mypath/$myxmlfile
""") % mypath

   #section to implement the cuda locking

   print("""\
mycuda=0
cudafound=0
tries=0
mylockdir=/tmp/tomo-i12-$USER/lock

mydate=`date`
mkdir -p $mylockdir
#try to acquire a lock representing one of the cuda cards
while [[ $cudafound -eq 0 ]]
do

   for mycuda in 0 1 
   do
       mylockf=$mylockdir/cuda$mycuda
       exec 8>>$mylockf

       if  flock -w 5 -x 8
       then
          cudafound=1
          echo "host $HOSTNAME date $mydate job $myjob task $tasknum"  >> $mylockf
          echo "Got lock on $mylockf"
          break
       else
          echo "Did not get lock on $mylockf"
       fi
   done
    if [[ $cudafound -eq 0 ]]
    then
       (( tries ++ ))
       if [[ $tries -gt 10 ]]
       then
            echo "Could not acquire the lock on a CUDA device lock-file!"
            echo "Check $mylockdir "
            exit
       fi
     sleep 5
     fi

done
echo "using cuda $mycuda" 
#change the input file to change the device ... aaargh ... 
sed -i "s|^.*GPUDeviceNumber.*$|<GPUDeviceNumber>$mycuda</GPUDeviceNumber>|" $myxmlpath
""")

   #actually run the program at last
   print("""\
%s $myxmlpath
""") % (reconprogram)



#end of the queue script text
   sys.stdout.flush()
   sys.stdout=sys.__stdout__

   #run the script in the queue
   #myqueue="medium.q"
   #myqueue="low.q"
   jobname="param"
   pyenv_o=open("%s/python_stdout_%s.txt" % (mypath,jobname),"w")
   pyenv_e=open("%s/python_stderr_%s.txt" % (mypath,jobname),"w")
   try:
         print ("Spawning the job ... ")
         thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub", "-P",proj,"-e",mypath, "-o", mypath, "-q",myqueue,"-N",jobname,"-cwd","-pe","smp","4","-t","%i-%i" % (1,sgetasks),myscript, qenviron)
         print ("return value was %s" % thispid)
   except:
         print ("ERROR Spawning the job didn't work")
         pyerr.close()
         pyout.close()
         pyenv_o.close()
         pyenv_e.close()
         sys.exit(147)
   



if __name__ == "__main__":
      #print "Running main"
      main()
