import arpes, shutil

# script to be run as part of acceptance testing a newly installed GDA on I05
# performs one fixed & one swept scan

nexusValidationTestsDir = "/dls/science/groups/das/NeXusAudit/I05"
xtn = ".nxs"
xtnLen = len(xtn)

arpes.ARPESRun("/dls_sw/i05/software/gda/config/scripts/nexusValidationFixedScan.arpes").run() # editor.getPath()<-beanfile for swept scan <- variant of 
lastScanFile = lastScanDataPoint().currentFilename                                             # get path of last file
shutil.copy(lastScanFile, nexusValidationTestsDir+"/"+lastScanFile[:-xtnLen]+"_fixed"+xtn)     # copy resulting nexus file to validation area

arpes.ARPESRun("/dls_sw/i05/software/gda/config/scripts/nexusValidationSweptScan.arpes").run() # editor.getPath()<-beanfile for swept scan <- variant of 
lastScanFile = lastScanDataPoint().currentFilename                                             # get path of last file
shutil.copy(lastScanFile, nexusValidationTestsDir+"/"+lastScanFile[:-xtnLen]+"_swept"+xtn)     # copy resulting nexus file to validation area

# Notes
# ARPESRun.run() ends up calling gda.jython.commands.ScannableCommands.staticscan([self.scienta]) after the scienta analyser is configured
# so excute ARPESRun.run() config-only and then and extended command to exercise the nexus file
# e.g. scan sapolar -20 24 0.25 say -0.293 0.00428 analyser                                         # with a bit of movement
# e.g. scan sapolar -20 24 0.25 say -0.293 0.00428 analyser es1 es2                                 # with camera images
# TBD scan exit_slit 0.2 0.1 -0.01 analyser


