print '=' * 80
print "running i16/config/scripts/startup_pie725.py"
print '=' * 80

from gdascripts.utils import caput_wait
import pie725


# PIE725

pieX = pie.pieX  # @UndefinedVariable
pieY = pie.pieY  # @UndefinedVariable

# Pilatus

try:
    pie725.setup_overlay_plugin(pvbase_det='BL16I-EA-PILAT-01:')
    caput_wait('BL16I-EA-PILAT-01:MJPG:MinCallbackTime', .2) # limit MJPG stream rate to prevent IOC overload and dropped frames
    #rasterpil1.filewriter.filePathTemplate='$datadir$/tmp/$scan$-rasterpil1-files'  # @UndefinedVariable
    #rasterpil1.tifwriter.filePathTemplate='/ramdisk'  # @UndefinedVariable
except:
    print "* Could not setup_overlay_plugin on pie725 with det='BL16I-EA-PILAT-01:'"

# Medipix
try:
    pie725.setup_overlay_plugin(pvbase_det='BL16I-EA-DET-13:')
    caput_wait('BL16I-EA-DET-13:MJPG:MinCallbackTime', .2) # limit MJPG stream rate to prevent IOC overload and dropped frames
except java.lang.IllegalStateException:
    print "* Could not connect to Medipix camera on 'BL16I-EA-DET-13"

# Dummy detector

dd = pie725.DetectorDummy('dd')


# rasterscan

rasterscan = pie725.RasterScan()
pie725.DEFAULT_SCANNABLES_FOR_RASTERSCANS = [meta]  # @UndefinedVariable
alias('rasterscan')  # @UndefinedVariable


# Doc

print
print '\n'.join(rasterscan.__doc__.split('\n')[2:])
print
print "- rasterpil1 writing to $datadir$/tmp"
print "- Change roi with e.g.:"
print "     rasterpil1.roistats1.setRoi(10, 20, 470, 160, 'roi1') (startx, starty, sizex, sizey, name)"
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
