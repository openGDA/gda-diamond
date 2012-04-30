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




def folderExistsWithTimeOut( dirToCheck, timeToWaitInS, sleepInterValInS , outStream ):
	"""
	Returns true if dirToCheck is found to exist within timeToWaitInS. Time interval between checks is  sleepInterValInS
	Else False
	Each check a . is written to outStream
	"""
	wtime = 0
	found = 0
	#wait for the directory to appear
	while ( ( wtime <= timeToWaitInS ) and ( found == 0 ) ):
		if not ( os.access ( dirToCheck, os.F_OK ) ):
			wtime += sleepInterValInS
			time.sleep( sleepInterValInS )
			outStream.write ( "." )
		else:
			found = 1
	#exit if it times out
	return os.access ( dirToCheck, os.F_OK )


def main( argv, out = sys.stdout, err = sys.stderr ):
	SinoListener( argv, out, err ).run()

class SinoListener():

	def __init__( self, argv, out, err, testing = False ):
		self.argv = argv
		self.out = out
		self.err = err

		self.firstchunk = 1 #number of first chunk
		self.ht = 2672#default. Length(height) of image controlled by l argument
		self.idxflag = " " #last argument to chunkprogram - either blank or -1, controlled by -1 argument
		self.infmt = "p_%05d.tif"
		self.interval = 1 #time interval when checking for a resource in seconds - controlled by z 
		self.lastchunk = 16 ## range end given in t argument to qsub. Controlled by -L argument otherwise set to nchunks
		#-t argument controls number of simultaneous jobs on the cluster firstchunk-lastchunk
		self.lastflag = False# indicates lastchunk is being controlled by -L command and that lastchunk is valid
		self.lt = 10 # timeout when checking for a resource in seconds - - controlled by Z
		self.mypid = os.getpid()
		self.nproj = 0
		self.outflag = False
		self.pidnums = []
		self.pnums = [0, 0, 0]
		self.pstrings = ['p', 'f', 'a']
		self.uniqueflag = False
		self.tifflag = False
		self.vflag = False #verbose flag default False controlled by -v
		self.testing = testing
		self.wd = 4008 #default
		self.indir = "projections"
		self.outdir = "sinograms"
		self.bytes = 2 #default
		self.nchunks = 16 #default number of chunks controlled by -n 
		self.nsegs = 1 #defaultb -s arg to chunkprogram - controlled by -s
		self.nperseg = 6000#default number of projections -p arg to chunk program controlled by -p
		self.jobbasename = "chunk" #default - -J
		self.jobname = "chunk_sino"#default - the finish job wait for the tasks with this naem to complete
		self.existflag = " " #default# 2nd part of -b flag to chunk program, controlled by -E
		self.jobsuffix = ""#default -j
		self.myqueue = "low.q" #default name of queue to use - controlled by -Q
		self.uniqueid = "U"#default if given replaces use of pid
		self.cropleft = 0
		self.cropright = 0
		self.hflag = 0 # show help and exit
		self.qsub_project="i12" # project name given to qsub
		


	def usage( self ):
		svnstring = "$Id: sino_listener.py 232 2012-04-11 13:21:04Z kny48981 $"
		self.out.write( "Version %s" % ( svnstring ) )
		self.out.write( "Usage:" )
		self.out.write( self.argv[0] )
		self.out.write ( "-i input dir (currently: projections)" )
		self.out.write ( "-o output dir (currently: sinograms)" )
		self.out.write ( "-p number of projections (currently %i )" % self.nperseg )
		self.out.write ( "    NOT automatically determined!" )
		self.out.write ( "-w width (currently %i )" % self.wd )
		self.out.write ( "-l length (height) of the image(currently %i)" % self.ht )
		self.out.write ( "-F number of first chunk (currently %i) " % self.firstchunk )
		self.out.write ( "-L number of last chunk (currently same as number of chunks) " )
		self.out.write ( "-n total number chunks (currently %i) " % self.nchunks )
		self.out.write ( "-J job hame " )
		self.out.write ( "-j suffix of job name " )
		self.out.write ( "-b bytes per pixel (currently 2)" )
		self.out.write ( "-s number of segments (currently 1) " )
		self.out.write ( "-Z timeout (currently %i)" % self.lt )
		self.out.write ( "-z check interval (currently %i)" % self.interval )
		self.out.write ( "-Q queue (currently medium.q) " )
		self.out.write ( "-U Unique ID (currently use PID) " )
		self.out.write ( "-I input filename format (C out.writef style) (currently %s) " % self.infmt )
		self.out.write ( "-1 start numbering of input files from 1 instead of 0 " )
		self.out.write ( "-t do nothing. Just create the bash script file" )

	def errprint( self, message = "none" ):
		self.out.write ( "errprint" )
		self.out.write ( "sino_listener.py: %s" % ( message ) )

	def vprint( self, message ):
		if self.vflag:
			self.out.write ( str( message ) )


	def createChunkScript( self ):
		"""
		nng28138@i13-ws001 ~]$ which sino_chunk_tiff_new.q
		/dls_sw/i12/software/tomography_scripts/sino_chunk_tiff_new.q
		"""		
		self.chunkscript = "%s/sinochunk.qsh" % self.settingsfolder
		chunkprogram = "sino_chunk_tiff_new.q"
		chunk_ht = self.ht / self.nchunks
		self.vprint( "Length(height) of image %i chunk_ht: %i " % ( self.ht, chunk_ht ) )
		
		chunkflags = "-i %s -o %s -w %i -l %i -z %i " % ( self.indir, self.outdir, self.wd, chunk_ht, self.interval)
		chunkflags += "-Z %i  -s %i -p %i -b %i %s " % ( self.lt, self.nsegs, self.nperseg, self.bytes, self.existflag)
		chunkflags += "-S %s -I %s -T %i -R %i %s " % (self.settingsfolder, self.infmt, self.cropleft, self.cropright, self.idxflag )
		self.vprint( "Creating the queue script: %s" % self.chunkscript )
		self.vprint( "Using : %s" % chunkprogram )



		chunkscriptOut = open( self.chunkscript, "w" )

		try:
			#output the introductory script section
			chunkscriptOut.write( """\
#!/bin/bash 
set -x

#add the modules required 
source /dls_sw/i12/modulefiles/modules.sh
module add /dls_sw/i12/modulefiles/local-64
myjob=$JOB_ID
mytask=$SGE_TASK_ID
""" )

			#set the unique identifier value
			chunkscriptOut.write( """mypid=%s\n""" % self.mypid )

			#set the output folder
			chunkscriptOut.write( """odir=%s\n""" % self.outdir )

			#check folder existance
			chunkscriptOut.write( """\
if [[ ! -e $odir ]]
then
mkdir -p $odir
fi
mynum=`printf "%%03d" $mytask`

echo PATH is $PATH

#ulimit -c unlimited
# UNCOMMENT  some of these lines to get more diagnostic information
# env > task${mytask}.env
#tracename=trace${myjob}_t${mytask}.trace
#trace execution all
""" )

			#assemble the command line that actually does the task
			chunkscriptOut.write( """\
%s %s -m $mytask  -v -J %s${myjob}_t${mytask}
""" 		 % ( chunkprogram, chunkflags, self.jobname ) )

			#check for error in return value
			chunkscriptOut.write( """\
retval=$?
if [[ retval -ne 0 ]]
then
  echo -e "job $myjob task $mytask return-value $retval\\n" >> %s/error_$mypid.txt  
fi
""" 		 % self.settingsfolder )


		finally:
			#end of the queue script text
			chunkscriptOut.flush()
			chunkscriptOut.close()

	def getArch(self):
		if  self.testing or (platform.architecture()[0] == "64bit")  :
			return "amd64"
		return "x86"
		
	def submitChunkScript(self):
		#set the queue environment
		if self.testing:
			qenviron = {}
		else:
			qenviron = os.environ
		qenviron["SGE_CELL"] = "DLS"
		qenviron["SGE_EXECD_PORT"] = "60001"
		qenviron["SGE_QMASTER_PORT"] = "60000"
		qenviron["SGE_ROOT"] = "/dls_sw/apps/sge/SGE6.2"
		oldpath = ""
		try :
			oldpath = qenviron["PATH"]
		except :
			oldpath = ""
		qenviron["PATH"] =  "/dls_sw/apps/sge/SGE6.2/bin/lx24-" + self.getArch() +":/bin:/usr/bin:" + oldpath
		self.vprint( `len( qenviron )` )
		self.vprint( qenviron.items() )
		pyerr = open( "%s/sino_listener_stderr_%s.txt" % ( self.settingsfolder, self.jobname ) , "w" )
		pyout = open( "%s/sino_listener_stdout_%s.txt" % ( self.settingsfolder, self.jobname ) , "w" )
		pyenv_o = open( "%s/python_stdout_%s.txt" % ( self.settingsfolder, self.jobname ), "w" )
		pyenv_e = open( "%s/python_stderr_%s.txt" % ( self.settingsfolder, self.jobname ), "w" )

		try:
			self.out.write ( "Spawning the sinogram job ... " )
			if ( self.vflag ):
				self.Popen( "env", env = qenviron, shell = False, stdout = pyenv_o, stderr = pyenv_e )
			self.out.write ( qenviron )
			args= ["qsub", "-P", self.qsub_project, "-e", self.settingsfolder, "-o", self.settingsfolder, "-q", self.myqueue, "-N", self.jobname]
			if ( self.Wflag ):
				args += ["-hold_jid", self.mywait]
			args +=  ["-cwd", "-pe", "smp", "4", "-t", "%i-%i" % ( self.firstchunk, self.lastchunk ), self.chunkscript ] 
			thispid = self.spawnlpe( os.P_WAIT, "qsub", tuple(args),qenviron)
			self.out.write ( "return value was %s" % thispid )
		except Exception, ex:
			self.out.write ( "ERROR Spawning the sinogram job didn't work " + str( ex ) )
			raise ex
		finally:
			pyerr.close()
			pyout.close()
			pyenv_o.close()
			pyenv_e.close()

	def submitFinishScript(self):
		#set the queue environment
		if self.testing:
			qenviron = {}
		else:
			qenviron = os.environ
		qenviron["SGE_CELL"] = "DLS"
		qenviron["SGE_EXECD_PORT"] = "60001"
		qenviron["SGE_QMASTER_PORT"] = "60000"
		qenviron["SGE_ROOT"] = "/dls_sw/apps/sge/SGE6.2"
		oldpath = ""
		try :
			oldpath = qenviron["PATH"]
		except :
			oldpath = ""
		qenviron["PATH"] =  "/dls_sw/apps/sge/SGE6.2/bin/lx24-" + self.getArch() +":/bin:/usr/bin:" + oldpath

		self.vprint( len( qenviron ) )
		self.vprint( qenviron.items() )
		pyerr = open( "%s/sino_listener_stderr_%s.txt" % ( self.settingsfolder, self.jobname ) , "w" )
		pyout = open( "%s/sino_listener_stdout_%s.txt" % ( self.settingsfolder, self.jobname ) , "w" )
		pyenv_o = open( "%s/python_stdout_%s.txt" % ( self.settingsfolder, self.jobname ), "w" )
		pyenv_e = open( "%s/python_stderr_%s.txt" % ( self.settingsfolder, self.jobname ), "w" )

		try:
			self.out.write ( "Spawning the sinogram finishing job ... " )
			finishname = "f_%s" % self.jobname
			self.out.write( "JOB NAME IS %s\n" % finishname )
			args = ["qsub", "-P", self.qsub_project, "-e", self.settingsfolder, "-o", self.settingsfolder, "-q", "high.q", "-hold_jid", self.jobname, "-N", finishname, self.finishscript]
			thispid = self.spawnlpe( os.P_WAIT, "qsub", tuple(args), qenviron )
			self.out.write ( "return value was %s" % thispid )

		except Exception, ex:
			self.out.write ( "Spawning the sinogram finishing job didn't work " + str( ex ) )
			raise ex
		finally:
			pyerr.close()
			pyout.close()


	def createFinishScript( self ):
		self.finishscript = "%s/finishchunk.qsh" % self.settingsfolder
		self.vprint( "Creating the finishing script: %s" % self.finishscript )

		try:
			finishscriptOut = open( self.finishscript, "w" )
			finishscriptOut.write( """\
#!/bin/bash 
set -x

#add the modules required 
source /dls_sw/i12/modulefiles/modules.sh
#add environment required by epics channel access (ezca) 

myjob=$JOB_ID
mytask=$SGE_TASK_ID
mypid=%s
jjname="%s"
""" % ( self.mypid, self.jobbasename ) )

			finishscriptOut.write( """\
ffolder="${jjname}_files"
errfile=%s/error_$mypid.txt
""" % self.settingsfolder )

			finishscriptOut.write( """\
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
""" % self.settingsfolder )

		finally:
			#end of the finish script text
			finishscriptOut.flush()
			finishscriptOut.close

	def spawnlpe( self, mode, file, args, env ):
		self.out.write( `mode`)
		self.out.write( `file`)
		self.out.write( `args`)
		self.out.write( `env` )
		if self.testing:
			return 0
		return os.spawnle( mode, file, args, env )

	def Popen( self, cmd, env, shell, stdout, stderr ):
		self.out.write( `cmd` )
		self.out.write( `env` )
		self.out.write( `shell` )
		if not self.testing:
			subprocess.Popen( cmd, env = env, shell = shell, stdout = stdout, stderr = stderr )

	def parseOptions(self):
	#width and height need to come from somewhere too ..
	#some defaults for testing

		if ( len( self.argv ) < 2 ):
			self.hflag = 1

		self.Wflag = 0  #wait for job mywait in qsub call, value controlled by W flag
		self.mywait = "" # default value of job id passed as argument to qsub if Wflag is 1
		try:
			opts, args = getopt.gnu_getopt( self.argv[1:], "1U:O:C:EGI:J:N:R:S:T:Z:b:cF:L:hi:j:l:n:o:p:s:vw:xz:Q:W:t", "qsub_project" )
		except getopt.GetoptError, err:
			self.errprint ( "Option parsing error" )
			self.errprint ( "Command line values: %s" % ( self.argv[1:] ) )
			self.errprint( "Message is %s" % ( str( err ) ) )
			self.usage()
			raise Exception( "Invalid usage" )

		if not ( len( args ) == 0 ):
			self.errprint ( "Option parsing error" )
			self.errprint ( "Command line values: %s" % ( self.argv[1:] ) )
			verrprint( "This program should not have non-flagged arguments" )
			self.out.write ( "unrecognized arguments: " + `args` )
			self.out.write ( `opts` + `args` )
			raise Exception( "Option parsing error" )

		for o, a in opts:
			if o == "-W":
				self.mywait = a
				self.Wflag = 1
			if o == "-Q":
				self.myqueue = a
			elif o == "-i":
				self.indir = a
			elif o == "-1":
				self.idxflag = "-1"
			elif o == "-I":
				self.infmt = a
			elif o == "-o":
				self.outdir = a
				self.outflag = True
			elif o == "-l":
				self.ht = int( a )
			elif o == "-w":
				self.wd = int( a )
			elif o == "-b":
				self.bytes = int( a )
			elif o == "-J":
				self.jobbasename = "%s" % a
			elif o == "-U":
				self.uniqueid = "%s" % a
				self.uniqueflag = True
			elif o == "-j":
				jobsuffix = "_%s" % a
			elif o == "-E":
				existflag = "-E"
			elif o == "-s":
				nsegs = int( a )
			elif o == "-p":
				self.nperseg = int( a )
			elif o == "-n":
				self.nchunks = int( a )
			elif o == "-L":
				self.lastchunk = int( a )
				self.lastflag = True
			elif o == "-F":
				self.firstchunk = int( a )
			elif o == "-R":
				self.cropright = int( a )
			elif o == "-T":
				self.cropleft = int( a )
			elif o == "-h":
				self.hflag = 1
			elif o == "-Z":
				self.lt = int( a )
			elif o == "-z":
				self.interval = int( a )
			elif o == "-v":
				self.vflag = True
			elif o == "-t":
				self.testing = True
			elif o == "--qsub_project":
				self.qsub_project = a
			else:
				self.errprint ( "Ignored option" )
				self.errprint ( "option %s value %s" % ( o, a ) )

		if ( len( self.argv ) == 2 and self.testing ):
			self.hflag = 1


		if ( self.uniqueflag ):
			self.mypid = uniqueid
		else:
			if self.testing:
		 		self.mypid = "testing_pid"
		 	else:
		 	 	self.mypid = os.getpid()

		if ( self.lastflag ):
			self.out.write( "Selecting last chunk to process: %i " % self.lastchunk )
		else:
			self.lastchunk = self.nchunks
		
	def run( self ):

		self.parseOptions()
		if ( self.hflag ):
			self.usage()
			return

		self.out.write ( "Using first chunk %i and last chunk %i" % ( self.firstchunk, self.lastchunk ) )

		self.jobname = "%s_sn_%s_%s" % ( self.jobbasename, self.jobsuffix, self.mypid )

		self.settingsbase = "sino_output"
		if self.testing:
			tstamp = "testing"
		else:
			tstamp = time.strftime( "%Y_%m%d_%H%M%S" )

		self.settingsfolder = "%s/sino_%s_files" % ( self.settingsbase, tstamp )
		self.out.write ( "Settings folder will be : %s " % self.settingsfolder )
		self.nproj = self.nperseg * self.nsegs

		self.out.write( "using input file format %s\n" % self.infmt )

		#check folder for the project
		self.out.write ( "Checking for input directory %s \nTimeout: %i seconds" % ( self.indir, self.lt ) )
		if not folderExistsWithTimeOut( self.indir, self.lt, self.interval, self.out ):
			msg = "Input directory %s is not available after %i seconds!" % ( self.indir, self.lt )
			self.errprint ( msg )
			raise Exception( msg )

		self.out.write ( "Input directory %s found...." % self.indir )

		#locate or create the output folders
		if not( os.access ( self.settingsbase, os.F_OK ) ):
			os.mkdir( self.settingsbase )

		if not( os.access ( self.settingsfolder, os.F_OK ) ):
			self.out.write ( "creating %s" % self.settingsfolder )
			os.mkdir( self.settingsfolder )

		#create the queue bash script for the queue task array

		self.createChunkScript()
		self.createFinishScript()

#For qsub doc see http://gridscheduler.sourceforge.net/htmlman/htmlman1/qsub.html

		self.submitChunkScript()
		self.submitFinishScript()




if __name__ == "__main__":
	main( sys.argv )

import math
import unittest
import os
import shutil
class Test1( unittest.TestCase ):
	def setUp( self ):
		if not os.path.exists( "testing_actual_output" ):
			os.mkdir( "testing_actual_output" )

	def tearDown( self ):
		pass

	def test_noArgs( self ):
		( out, err, errFileName, outputFileName ) = self.outAndErr( "test_noArgs" )
		main( ["program"], out = writer_newline( out ), err = writer_newline( err ) )
		out.close()
		err.close()
		self.checkFilesMatch( "expected_usage.txt", outputFileName )
		self.checkFilesMatch( "empty.txt" , errFileName )

	def test_testing( self ):
		( out, err, errFileName, outputFileName ) = self.outAndErr( "test_testing" )
		main( ["program", "-t"], out = writer_newline( out ), err = writer_newline( err ) )
		out.close()
		err.close()
		self.checkFilesMatch( "expected_usage.txt", outputFileName )
		self.checkFilesMatch( "empty.txt", errFileName )

	def test_help( self ):
		( out, err, errFileName, outputFileName ) = self.outAndErr( "test_help" )
		main( ["program", "-h"], out = writer_newline( out ), err = writer_newline( err ) )
		out.close()
		err.close()
		self.checkFilesMatch( "expected_usage.txt", outputFileName )
		self.checkFilesMatch( "empty.txt", errFileName )

	def test_i_no_parameter( self ):
		( out, err, errFileName, outputFileName ) = self.outAndErr( "test_i_no_parameter" )
		try:
			main( ["program", "-i"], out = writer_newline( out ), err = writer_newline( err ) )
		except Exception, ex:
			self.assertEquals( 'Invalid usage', str( ex ) )
		out.close()
		err.close()
		self.checkFilesMatch( outputFileName, outputFileName )
		self.checkFilesMatch( "empty.txt", errFileName )

	def test_i_nonExistentFolder( self ):
		( out, err, errFileName, outputFileName ) = self.outAndErr( "test_i_nonExistentFolder" )
		try:
			main( ["program", "-i", "nonExistent", "-Z", "2", "-t", "-v"], out = writer_newline( out ), err = writer_newline( err ) )
		except Exception, ex:
			self.assertEquals( 'Input directory nonExistent is not available after 2 seconds!', str( ex ) )
		finally:
			out.close()
			err.close()

	def test_i_cdw( self ):
		if os.path.exists("sino_output"):
			shutil.rmtree("sino_output")
		( out, err, errFileName, outputFileName ) = self.outAndErr( "test_i_cdw" )
		main( ["program", "-i", ".", "-t", "-v"], out = writer_newline( out ), err = writer_newline( err ) )
		out.close()
		err.close()
		self.checkFilesMatch( outputFileName, outputFileName )
		self.checkFilesMatch( "empty.txt", errFileName )
		sinochunkFile = "sino_output/sino_testing_files/sinochunk.qsh"
		self.checkFilesMatch1( "testing_expected_output/" + sinochunkFile, sinochunkFile )
		finishchunkFile = "sino_output/sino_testing_files/finishchunk.qsh"
		self.checkFilesMatch1( "testing_expected_output/" + finishchunkFile, finishchunkFile )

	def outAndErr( self, testName ):
		outputFileName = testName + "_output.txt"
		errFileName = testName + "_err.txt"
		out = open( "testing_actual_output" + '/' + outputFileName, "w" )
		err = open( "testing_actual_output" + '/' + errFileName, "w" )
		return ( out, err, errFileName, outputFileName )

	def checkFilesMatch( self, expectedFilePath, actualFilePath ):
		expectedFilePath = "testing_expected_output" + '/' + expectedFilePath
		actualFilePath = "testing_actual_output" + '/' + actualFilePath
		self.checkFilesMatch1( expectedFilePath, actualFilePath )

	def checkFilesMatch1( self, expectedFilePath, actualFilePath ):
		f = open( actualFilePath )
		linesActual = f.readlines()
		f.close
		f = open( expectedFilePath )
		linesExpected = f.readlines()
		f.close
		lastIndexToCompare = min( len( linesActual ), len( linesExpected ) )
		for i in range( lastIndexToCompare ):
			if linesActual[i] != linesExpected[i]:
				raise Exception( "File %s does not match %s " % ( expectedFilePath, actualFilePath ) )
		if len( linesExpected ) == len( linesActual ):
			return
		raise Exception( "File %s does not match %s " % ( expectedFilePath, actualFilePath ) )



class writer_newline:
	def __init__( self, pipe ):
		self.pipe = pipe
	def write( self, msg ):
		self.pipe.write( str( msg ) )
		self.pipe.write( "\n" )
		self.pipe.flush()

def suite():
	return unittest.TestSuite( ( unittest.TestLoader().loadTestsFromTestCase( Test1 ) ) )
