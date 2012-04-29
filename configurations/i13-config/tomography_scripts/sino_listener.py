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

		self.chunk_ht = 167#default
		self.delflag = False
		self.firstchunk = 1#default
		self.ht = 2672#default
		self.idxflag = " "
		self.inflag = False
		self.infmt = "p_%05d.tif"
		self.interval = 1 #time interval when checking for a resource in seconds - controlled by z 
		self.lastchunk = 16
		self.lastflag = False
		self.lt = 10 # timeout when checking for a resource in seconds - - controlled by Z
		self.nchunks = 16 #default
		self.mypid = os.getpid()
		self.nperseg = 0
		self.nproj = 0
		self.outflag = False
		self.pidnums = []
		self.pnums = [0, 0, 0]
		self.pstrings = ['p', 'f', 'a']
		self.uniqueflag = False
		self.tifflag = False
		self.vflag = False
		self.testing = testing
		self.wd = 4008 #default


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
	 		self.out.write ( message )




	def run( self ):

	#width and height need to come from somewhere too ..
	#some defaults for testing

		self.indir = "projections"
		self.outdir = "sinograms"
		self.bytes = 2 #default
		self.firstchunk = 1#default
		self.nchunks = 16 #default
		self.nsegs = 1 #default
		self.nperseg = 6000#default
		self.jobbasename = "chunk" #default
		self.jobname = "chunk_sino"#default
		self.existflag = " " #default
		self.jobsuffix = ""#default
		self.myqueue = "low.q"#default
		self.uniqueid = "U"#default
		self.cropleft = 0
		self.cropright = 0
		self.hflag = 0
		if ( len( self.argv ) < 2 ):
			self.hflag = 1

		self.Wflag = 0
		try:
			opts, args = getopt.gnu_getopt( self.argv[1:], "1U:O:C:EGI:J:N:R:S:T:Z:b:cF:L:hi:j:l:n:o:p:s:vw:xz:Q:W:t" )
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
				self.inflag = True
			elif o == "-1":
				self.idxflag = "-1"
			elif o == "-I":
				self.infmt = a
				self.inflag = True
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
			else:
				self.errprint ( "Ignored option" )
				self.errprint ( "option %s value %s" % ( o, a ) )

		if ( len( self.argv ) == 2 and self.testing ):
			self.hflag = 1

		if ( self.hflag ):
			self.usage()
			return

		if ( self.uniqueflag ):
			self.mypid = uniqueid
		else:
			if self.testing:
		 		self.mypid = "testing_pid"
		 	else:
		 	 	self.mypid = os.getpid()

		if ( self.lastflag ):
			self.out.write( "Selecting last chunk to process: %i " % lastchunk )
		else:
			self.lastchunk = self.nchunks

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

		self.chunk_ht = self.ht / self.nchunks

		self.vprint( "ht %i chunk_ht: %i " % ( self.ht, self.chunk_ht ) )
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

		thisdir = os.getcwd()
		#chunkscript="sinochunk.qsh" % os.getpid()
		self.chunkscript = "%s/sinochunk.qsh" % self.settingsfolder
		self.finishscript = "%s/finishchunk.qsh" % self.settingsfolder
		self.chunkprogram = "sino_chunk_tiff_new.q"
		self.chunkflags = "-i %s -o %s -w %i -l %i -z %i  -Z %i  -s %i -p %i -b %i %s -S %s -I %s -T %i -R %i %s " % \
		( self.indir, self.outdir, self.wd, self.chunk_ht, self.interval, self.lt, self.nsegs, self.nperseg, self.bytes, self.existflag, self.settingsfolder, self.infmt, self.cropleft, self.cropright, self.idxflag )
		self.vprint( "Creating the queue script: %s" % self.chunkscript )
		self.vprint( "Using : %s" % self.chunkprogram )

		chunkscriptOut = open( self.chunkscript, "w" )

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
		chunkscriptOut.write( """mypid=%s""" % self.mypid )

		#set the output folder
		chunkscriptOut.write( """odir=%s""" % self.outdir )

		#check folder existance
		chunkscriptOut.write( """\
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
""" )

		#assemble the command line that actually does the task
		chunkscriptOut.write( """\
%s %s -m $mytask  -v -J %s${myjob}_t${mytask}
""" % ( self.chunkprogram, self.chunkflags, self.jobname ) )

		#check for error in return value
		chunkscriptOut.write( """\
retval=$?
if [[ retval -ne 0 ]]
then
  echo -e "job $myjob task $mytask return-value $retval\\n" >> %s/error_$mypid.txt  
fi
""" % self.settingsfolder )

		#end of the queue script text
		chunkscriptOut.flush()

		self.vprint( "Creating the finishing script: %s" % self.finishscript )

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

		#end of the finish script text
		finishscriptOut.flush()

		if self.testing:
			self.out.write( "Exiting after creating chunkscript file" )
			return


		#set the queue environment
		qenviron = os.environ
		self.vprint( len( qenviron ) )
		self.vprint( qenviron.items() )
		oldpath = ""
		try :
			oldpath = qenviron["PATH"]
		except :
			oldpath = ""
		if ( "64bit" == platform.architecture()[0] ) :
			newpath = "/dls_sw/apps/sge/SGE6.2/bin/lx24-amd64:/bin:/usr/bin:%s" % oldpath
		else:
			newpath = "/dls_sw/apps/sge/SGE6.2/bin/lx24-x86/:/bin:/usr/bin:%s" % oldpath
		qenviron["SGE_CELL"] = "DLS"
		qenviron["SGE_EXECD_PORT"] = "60001"
		qenviron["SGE_QMASTER_PORT"] = "60000"
		qenviron["SGE_ROOT"] = "/dls_sw/apps/sge/SGE6.2"
		qenviron["PATH"] = newpath
		self.vprint( len( qenviron ) )
		self.vprint( qenviron.items() )
		pyerr = open( "%s/sino_listener_stderr_%s.txt" % ( self.settingsfolder, jobname ) , "w" )
		pyout = open( "%s/sino_listener_stdout_%s.txt" % ( self.settingsfolder, jobname ) , "w" )
		pyenv_o = open( "%s/python_stdout_%s.txt" % ( self.settingsfolder, jobname ), "w" )
		pyenv_e = open( "%s/python_stderr_%s.txt" % ( self.settingsfolder, jobname ), "w" )

		try:
			self.out.write ( "Spawning the sinogram job ... " )
			if ( self.vflag ):
				subprocess.Popen( "env", env = qenviron, shell = False, stdout = pyenv_o, stderr = pyenv_e )
			self.out.write ( qenviron )
			if ( Wflag ):
				thispid = os.spawnlpe( os.P_WAIT, "qsub", "qsub", "-P", "i12", "-e", self.settingsfolder, "-o", self.settingsfolder, "-q", myqueue, "-N", jobname, "-hold_jid", mywait, "-cwd", "-pe", "smp", "4", "-t", "%i-%i" % ( self.firstchunk, self.lastchunk ), self.chunkscript, qenviron )
			else:
				thispid = os.spawnlpe( os.P_WAIT, "qsub", "qsub", "-P", "i12", "-e", self.settingsfolder, "-o", self.settingsfolder, "-q", myqueue, "-N", jobname, "-cwd", "-pe", "smp", "4", "-t", "%i-%i" % ( self.firstchunk, self.lastchunk ), self.chunkscript, qenviron )
			#thispid=os.spawnlpe(os.P_WAIT,"qsub","qsub", "-e",settingsfolder, "-o", settingsfolder, "-q",myqueue,"-N",jobname,"-cwd","-t","%i-%i" % (firstchunk,lastchunk),chunkscript, qenviron)
			self.out.write ( "return value was %s" % thispid )
		except:
			self.out.write ( "ERROR Spawning the sinogram job didn't work" )
			pyerr.close()
			pyout.close()
			pyenv_o.close()
			pyenv_e.close()
			raise Exception( 147 )

		try:
			self.out.write ( "Spawning the sinogram finishing job ... " )
			finishname = "f_%s" % self.jobname
			self.out.write( "JOB NAME IS %s\n" % finishname )
			thispid = os.spawnlpe( os.P_WAIT, "qsub", "qsub", "-P", "i12", "-e", self.settingsfolder, "-o", self.settingsfolder, "-q", "high.q", "-hold_jid", jobname, "-N", finishname, self.finishscript, qenviron )
			self.out.write ( "return value was %s" % thispid )

		except:
			out.write ( "Spawning the sinogram finishing job didn't work" )
			pyerr.close()
			pyout.close()
			raise Exception( 148 )

		pyerr.close()
		pyout.close()



if __name__ == "__main__":
	main( sys.argv )

import math
import unittest
import os

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
			self.assertEqual( linesActual[i], linesExpected[i], "line %d:%s " % ( i, linesActual[i] ) )
		if len( linesExpected ) == len( linesActual ):
			return
		extraLines = []
		if lastIndexToCompare == len( linesActual ):
			extraLines = linesExpected[lastIndexToCompare:]
		else:
			extraLines = linesActual[lastIndexToCompare:]
			self.assertEqual( "", `extraLines` )



class writer_newline:
	def __init__( self, pipe ):
		self.pipe = pipe
	def write( self, msg ):
		self.pipe.write( msg )
		self.pipe.write( "\n" )
		self.pipe.flush()

def suite():
	return unittest.TestSuite( ( unittest.TestLoader().loadTestsFromTestCase( Test1 ) ) )
