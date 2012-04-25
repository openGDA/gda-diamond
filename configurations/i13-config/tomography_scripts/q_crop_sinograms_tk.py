#!/dls_sw/dasc/Python-2.4.4/bin/python
import sys
import os
import commands
import shutil
import time
import glob
import platform
import subprocess

from Tkinter import *
mwin = Tk()
vals=[]
labels=[]
entries=[]
medv = IntVar()
nrows=10

def runproc():
   global nrows
   global vals
   global medv
   chunkscript="runrotate.qsh"
   myqueue="medium.q"

   vfolder=vals[0].get()
   vnum=vals[1].get()
   snum=vals[2].get()
   jobname="r_%s" % snum
   try:
      angle=float(vals[3].get())
   except ValueError:
      print "Angle must be a number of degrees"
      return

   try:
      nchunks=int(vals[4].get())
   except ValueError:
      print "Number of chunks must be a positive integer!"
      return

   nfiles=1801

   if ( medv.get() == 0 ) :
      medflag="-median 1"
   else:
      medflag=" "
   vpath="%s/%s/" % (vfolder,vnum)
   infolder="%s/%s/processing/%s/sinograms/" %(vfolder,vnum,snum)
   pfolder="%s/%s/processing/%s" % (vfolder,vnum,snum)
   outfolder="%s/%s/processing/%s/csinograms/" % (vfolder,vnum,snum)
   flatname="%s/flat.tif" % (pfolder)
   cflatname="%s/cflat.tif" % (pfolder)

   if not (os.access (pfolder, os.F_OK)):
      print "creating %s " % pfolder
      os.mkdir(pfolder)

   if not (os.access (outfolder, os.F_OK)):
      print "creating %s " % outfolder
      os.mkdir(outfolder)

   chunksize=nfiles/nchunks
   lastchunk=nfiles-nchunks*chunksize
   lasttask=nchunks+1
   print chunksize,lastchunk,lasttask
   


   #create the script to submit to the queue
   sys.stdout = open(chunkscript,"w")
   print("""\
#!/bin/bash 
#modules don't work for gda user, use hacked module files 
      source /dls_sw/i12/modulefiles/modules.sh 
      #add the modules required  
      module add /dls_sw/i12/modulefiles/local-64 
      module add global/cluster 
      tasknum=$SGE_TASK_ID 
#variables set from the master python script
      if=%s
      of=%s
      chunksize=%i
      lasttask=%i
      lastchunk=%i
      medflag=\"%s\"
      angle=%f
#calculate the derived values
      (( zidx = $tasknum - 1 )) 
      (( start = $zidx * $chunksize )) 
      (( stop = $start + $chunksize ))  
      if [[ $tasknum -eq $lasttask ]] 
      then 
         (( stop = $start + $lastchunk )) 
      fi 
 
      for ((i=$start;i<$stop;i++)) 
      do 
         infile=`printf \"${if}/p_%%05d.tiff\" $i` 
         outfile=`printf \"${of}/p_%%05d.tiff\" $i` 
         echo $infile 
         echo $outfile 
         convert $medflag -crop ${xsize}x${ysize}+${xstart}+${ystart}  +matte $infile $outfile  
         if [[ $tasknum -eq $lasttask ]] 
         then 
            convert $medflag -crop ${xsize}x${ysize}+${xstart}+${ystart}  +matte $infile $outfile  
         fi 
      done 
   """) % (infolder,outfolder,chunksize,lasttask,lastchunk,medflag,angle) 

   sys.stdout.flush()
   sys.stdout=sys.__stdout__

   #set the queue environment
   qenviron=os.environ
   oldpath=""
   #check the architecture to get the right executable
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

   pyerr=open("q_rotate_err.txt" , "w")
   pyout=open("q_rotate_out.txt" , "w")

   try:
         print ("Spawning the rotation job ... ")
         queue_args="qsub -P i12 -q %s  -N %s -cwd -t 1-%i %s " % (myqueue,jobname,nchunks,chunkscript)
         print ("queue args are",queue_args)
         subprocess.Popen(queue_args,env=qenviron,shell=True,stdout=pyout,stderr=pyerr)
   except:
         print ("ERROR Spawning the rotation job didn't work")
         pyerr.close()
         pyout.close()
         sys.exit(147)

   pyerr.close()
   pyout.close()
#end of runproc()

#setting up the window
top = Frame(mwin,borderwidth=10)
for i in range(0,nrows):
        vals.append(StringVar())
        labels.append (Label(top,text="label %i" %i,padx=0))
        entries.append(Entry(top,width=30,relief="sunken",textvariable=vals[i]))
        labels[i].grid(row=i,column=0)
        entries[i].grid(row=i,column=1,sticky=N+E+S+W)

btrow=Frame(top,borderwidth=10);
medbt=Checkbutton(btrow,text="Median-1",variable=medv)
medbt.pack(side=LEFT)
runbt=Button(btrow,text="Run",command=runproc)
runbt.pack(side=LEFT)
exitbt=Button(btrow,text="Exit",command="exit")
exitbt.pack(side=LEFT)

btrow.grid(row=i+1,column=0,columnspan=2)

top.pack(fill=X,expand=1)
top.grid_columnconfigure(1,weight=1)

#set some defaults
entries[0].insert(0,"/dls/i12/data/2010/")
entries[1].insert(0,"ee2213-1")
entries[2].insert(0,"1020")
entries[3].insert(0,"0.15")
entries[4].insert(0,"64")
labels[0].config(text="Visit folder")
labels[1].config(text="Visit number")
labels[2].config(text="Scan number")
labels[3].config(text="Rotation Angle")
labels[4].config(text="Number of chunks")

mainloop()

