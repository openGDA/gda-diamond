import os
from datetime import date
from gda.configuration.properties import LocalProperties
from datacollection.CollectionMode import COLLECT_MODE

class DatasetMetadata():

	SUMMARY_SUBFOLDER = "summary"
	SCRATCH_PATH = "/tmp/"

	def __init__(self):
		self._directory = self.SCRATCH_PATH
		self._mode = COLLECT_MODE[0]
		self._prefix = "test" #prefix
		self._num_runs = 0
		self._start_run_number = 1
		self._visit_folder = ""
		self._detector_write_path = ""
		self.config()


	def _check_directory(self,path):
		try:
			if os.path.isdir(path):
				return
		except:
			raise
		try:
			os.makedirs(path)
		except OSError:
			if not os.path.isdir(path):
				raise


	def config(self):
		year = str(date.today().year)
		folder = str(LocalProperties.get("gda.data.scan.datawriter.datadir"))
		self._visit_folder = folder.replace("$year$",year)


	def detectorWritePath(self):
		return self._detector_write_path


	def directory(self):
		return self._directory


	def mode(self):
		return self._mode


	def numRuns(self):
		return self._num_runs


	def prefix(self):
		return self._prefix


	def setDetectorWritePath(self, value):
		self._detector_write_path = value


	def setDirectory(self, value):
		self._directory = value


	def setMode(self, value):
		self._mode = value


	def setNumRuns(self, value):
		self._num_runs = value


	def setPrefix(self, value):
		self._prefix = value


	def setStartRunNumber(self, value):
		self._start_run_number = value


	def startRunNumber(self):
		return self._start_run_number


	def visitFolder(self):
		return self._visit_folder


	def _write_header(self,filepath,filename):
		f = open(filepath+filename,"w")
		try:
			f.write("File = %s\n" % (filename))
			f.write("Prefix = %s\n" % (self.prefix()))
			f.write("Visit Folder = %s\n" % (self.visitFolder()))
			f.write("numRuns = %d\n" % (self.numRuns()))
			f.write("startRunNumber = %d\n" % (self.startRunNumber()))
			f.write("Mode = %s\n" % (self.mode()))
			f.write("[Run Log]\n")
		except:
			print("Failed to process header for data set with prefix: %s" % self.prefix())
		finally:
			f.close()


	def _write_run(self,filepath,filename,rundata):
		f = open(filepath+filename,"a")
		run_number = rundata.runNumber()
		try:
			f.write("Run(%d).numImages = %d\n" % (run_number,rundata.numImages()))
			f.write("Run(%d).startImageNumber = %d\n" % (run_number,rundata.startImageNumber()))
			f.write("Run(%d).step = %5.4f\n" % (run_number,rundata.step()))
			if self.mode() == COLLECT_MODE[1]:
				f.write("Run(%d).userStep = %5.4f\n" % (run_number,rundata.userStep()))
		except:
			print("Unable to complete log entry for run %d" % run_number)
		finally:
			f.close()


	def writeRun(self, rundata):
		filename = ""
		filepath = ""
		try:
			filepath = self.visitFolder()+self.SUMMARY_SUBFOLDER+"/"
			filename = self.prefix()+"log.txt"
		except:
			print("Unable to access run parameters")
			return
		try: 	# Quietly update copy in scratch
			self._write_run(self.SCRATCH_PATH, filename)
		except:
			print("writeRun: Unable to access file %s%s" % (self.SCRATCH_PATH,filename))
			return
		try:
			print("--------------------------------------------------------")
			print("Writing run (%d) parameters to %s in %s" % (rundata.runNumber(),filename,filepath))
			self._write_run(filepath,filename,rundata)
		except:
			print("writeRun: Unable to access file %s%s" % (filepath,filename))


	def writeHeader(self):
		filename = ""
		filepath = ""
		try:
			filename = self.prefix()+"log.txt"
			filepath = self.visitFolder()+self.SUMMARY_SUBFOLDER+"/"
		except:
			print("Unable to access header parameters")
			return
		try:	# Quietly write a copy to scratch
			self._write_header(self.SCRATCH_PATH, filename)
		except:
			print("Unable to access file %s%s" % (self.SCRATCH_PATH,filename))
			return
		print("Visit Folder: %s" % self.visitFolder())
		try:
			print("---------------------------------------------------------")
			print("Writing header for data set (prefix=%s) in %s%s" % (self.prefix(),filepath,filename))
			self._check_directory(filepath)
			self._write_header(filepath,filename)
		except:
			print("Unable to access file %s%s" % (filepath,filename))

