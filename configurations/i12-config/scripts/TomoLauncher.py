from org.edna.tomov1 import Helpers
from org.edna.tomov1.xsdata import *
from org.edna.tomov1.launchers import *
from java.io import PrintStream
from java.io import FileOutputStream

print "rest up the input variable"

input = XSDataInputTomography()
input.setByteDepthOfImage(Helpers.createXSDataInteger(2))
input.setChunkHeight(Helpers.createXSDataInteger(10))
input.setImageDirectory(Helpers.createXSDataFile("/dls/i12/data/2010/ee0/91"))
input.setImageWidth(Helpers.createXSDataInteger(4006))
input.setJobName(Helpers.createXSDataString("mb01"))
input.setNumberOfChunks(Helpers.createXSDataInteger(16))
input.setNumberOfProjectionsPerSegment(Helpers.createXSDataInteger(128))
input.setNumberOfSegments(Helpers.createXSDataInteger(1))
input.setTimeoutLength(Helpers.createXSDataFloat(60.0))
input.setTimeoutPollingInterval(Helpers.createXSDataFloat(1.0))

print "new setup"

print "input set up"

print "Set up the stream to record the output"

ps = PrintStream(FileOutputStream("/dls/i12/data/2010/ee0/processing/out.tmp"))

print " stream set up, now running the plugin"

result = TomoLaunchers.LaunchEDPluginTomography(input,ps)


