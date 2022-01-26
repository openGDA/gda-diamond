print '=' * 80
print "running b16/config/scripts/startup_pie725.py"
print '=' * 80

from gdascripts.utils import caput_wait
#import pie725
from epics_scripts.device.scannable.detector.addetector.link_overlay_to_roi import setup_overlay_plugin
from gdascripts.scan import rasterscans
# PIE725

pieX = pie.pieX  # @UndefinedVariable
pieY = pie.pieY  # @UndefinedVariable

# Pilatus

#pie725.setup_overlay_plugin(pvbase_det='BL16I-EA-PILAT-01:')
caput_wait('BL16B-EA-DET-04:MJPG:MinCallbackTime', .2) # limit MJPG stream rate to prevent IOC overload and dropped frames

# To change back then comment out and restart the servers
#rasterpil.tifwriter.filePathTemplate='/ramdisk'  # @UndefinedVariable
#rasterpil.tifwriter.filePathInaccessibleFromServer=True



from epics_scripts.device.scannable.detector.addetector.link_overlay_to_roi import setup_overlay_plugin

#try:
setup_overlay_plugin(pvbase_det='BL16B-EA-DET-04:')
#    caput_wait('BL16I-EA-DET-12:MJPG:MinCallbackTime', .2) # limit MJPG stream rate to prevent IOC overload and dropped frames
#except java.lang.IllegalStateException:
#    print "* Could not connect to Medipix camera on 'BL16I-EA-DET-12"

# Dummy detector

#dd = pie725.DetectorDummy('dd')


# rasterscan


rasterscan = rasterscans.RasterScan()
rasterscans.DEFAULT_SCANNABLES_FOR_RASTERSCANS = [meta]  # @UndefinedVariable
alias('rasterscan')  # @UndefinedVariable


# Doc

print
print '\n'.join(rasterscan.__doc__.split('\n')[2:])
print
print "- rasterpil1 writing to $datadir$/tmp"
print "- Change roi with e.g.:"
print "     rasterpil.roistats1.setRoi(10, 20, 470, 160, 'roi1') (startx, starty, sizex, sizey, name)"
print "- raster map plotted on 'Plot 2' "

print
print """
- If restarted the MEDIPIX camera won't work. It will miss the fist exposure."
 To fix this:"
  $ rdesktop -g1200x1000 i16-xmap1
 
  The login is 'i16' and the password is stuck on the XMAP box. (On top of the experimental equipment tower)
  
  Then uncheck the checkbox labeled: 'Send Acq. Header' under the 'Advanced' tab.
"""

print '=' * 80
