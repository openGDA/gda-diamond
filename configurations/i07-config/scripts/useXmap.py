

def disable_nexus():
        LocalProperties.set("gda.data.scan.datawriter.dataFormat", "SixdSrsDataWriter")

def enable_nexus():
        LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusDataWriter")

try:
        caput("ME13C-EA-DET-01:CollectMode", 0) #MCA Spectra
        caput("ME13C-EA-DET-01:PresetMode", 1) #Real mode
        caput("ME13C-EA-DET-01:MCA1.NUSE", 2048) #binning
        caput("ME13C-EA-DET-01:DXP1:MaxEnergy", 20.48)
        caput("ME13C-EA-DET-01:DXP2:MaxEnergy", 20.48)
        caput("ME13C-EA-DET-01:DXP3:MaxEnergy", 20.48)
        caput("ME13C-EA-DET-01:DXP4:MaxEnergy", 20.48)
except:
        print "WARNING: Could not ensure xmapMca settings are correct"


enable_nexus()
print('INFO: Nexus file writing has been enabled - required for Xmap')
print('nxs data files will be written in addition to dat')
print('This can be disabled with disable_nexus()')

