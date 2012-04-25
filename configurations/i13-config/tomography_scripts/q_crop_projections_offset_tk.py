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
nrows=11

def runproc():
   global nrows
   global vals
   global medv
   chunkscript="runcrop.qsh"
   myqueue="medium.q"

   vfolder=vals[0].get()
   vnum=vals[1].get()
   snum=vals[2].get()
   jobname="crop_%s" % snum
   try:
      xstart=int (vals[5].get())
      ystart=int (vals[6].get())
      xsize=int(vals[7].get())
      ysize=int(vals[8].get())
      offstart=int(vals[9].get())
      offset=int(vals[10].get())
   except ValueError:
      print "Crop parameters  must be positive integers"
      return

   offx=xstart+offset
   try:
      nchunks=int(vals[4].get())
   except ValueError:
      print "Number of chunks must be a positive integer!"
      return

   try:
      nfiles=int(vals[3].get())
   except ValueError:
      print "Number of files must be a positive integer!"
      return

   if ( medv.get() == 1 ) :
      medflag="-median 1"
   else:
      medflag=" "
   vpath="%s/%s/" % (vfolder,vnum)
   infolder="%s/%s/default/%s/projections/" %(vfolder,vnum,snum)
   pfolder="%s/%s/processing/%s" % (vfolder,vnum,snum)
   outfolder="%s/%s/processing/%s/cprojections/" % (vfolder,vnum,snum)
   flatname="%s/flat.tif" % pfolder
   cflatname="%s/cflat.tif" % pfolder

   if not (os.access (pfolder, os.F_OK)):
      print "creating %s " % pfolder
      os.mkdir(pfolder)

   if not (os.access (outfolder, os.F_OK)):
      print "creating %s " % outfolder
      os.mkdir(outfolder)

   chunksize=nfiles/(nchunks-1)
   lastchunk=nfiles-(nchunks-1)*chunksize
   lasttask=nchunks
   print "chunksize %i lastchunk %i lasttask %i" %( chunksize,lastchunk,lasttask)
   


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
      fn=%s
      cfn=%s
      chunksize=%i
      lasttask=%i
      lastchunk=%i
      medflag=\"%s\"
      xstart=%i
      ystart=%i
      xsize=%i
      ysize=%i
      offstart=%i
      offx=%i
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
         if [[ $i -ge $offstart ]]
         then
            xstart=$offx
         fi
         convert +repage $medflag -crop ${xsize}x${ysize}+${xstart}+${ystart}  +matte $infile $outfile  
      done 
      if [[ $tasknum -eq $lasttask ]] 
      then 
         convert +repage $medflag -crop ${xsize}x${ysize}+${xstart}+${ystart}  +matte $fn $cfn  
      fi 
   """) % (infolder,outfolder,flatname,cflatname,chunksize,lasttask,lastchunk,medflag,xstart,ystart,xsize,ysize,offstart,offx) 

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

   pyerr=open("q_crop_err.txt" , "w")
   pyout=open("q_crop_out.txt" , "w")

   try:
         print ("Spawning the projections crop job ... ")
         queue_args="qsub -P i12 -q %s  -N %s -cwd -t 1-%i %s " % (myqueue,jobname,lasttask,chunkscript)
         print ("queue args are",queue_args)
         subprocess.Popen(queue_args,env=qenviron,shell=True,stdout=pyout,stderr=pyerr)
   except:
         print ("ERROR Spawning the cropping job didn't work")
         pyerr.close()
         pyout.close()
         sys.exit(147)

   pyerr.close()
   pyout.close()
#end of runproc()

#setting up the window
#using tkinter
top = Frame(mwin,borderwidth=10)
#several rows of label/value pairs
for i in range(0,nrows):
        vals.append(StringVar())
        labels.append (Label(top,text="label %i" %i,padx=0))
        entries.append(Entry(top,width=30,relief="sunken",textvariable=vals[i]))
        labels[i].grid(row=i,column=0)
        entries[i].grid(row=i,column=1,sticky=N+E+S+W)

#tickbox for optional median filter
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

#assign the labels
labels[0].config(text="Visit folder")
labels[1].config(text="Visit number")
labels[2].config(text="Scan ID")
labels[3].config(text="Number of Files")
labels[4].config(text="Number of queue jobs")
labels[5].config(text="xstart")
labels[6].config(text="ystart")
labels[7].config(text="xsize")
labels[8].config(text="ysize")
labels[9].config(text="offset start")
labels[10].config(text="x offset")
#set the default values
entries[0].insert(0,"/dls/i12/data/2010/")
entries[1].insert(0,"cm1898-4")
entries[2].insert(0,"2090")
entries[3].insert(0,"3600")
entries[4].insert(0,"56")
entries[5].insert(0,"0")
entries[6].insert(0,"0")
entries[7].insert(0,"400")
entries[8].insert(0,"400")
entries[9].insert(0,"1000")
entries[10].insert(0,"40")


mainloop()

