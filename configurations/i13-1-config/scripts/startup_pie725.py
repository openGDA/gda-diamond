from gdascripts.scan import rasterscans
print '=' * 80
print "running i13-1-config/scripts/startup_pie725.py"
print '=' * 80

# PIE725

pieX = pie.pieX  # @UndefinedVariable
pieY = pie.pieY  # @UndefinedVariable

# Pilatus


# Dummy detector

dd = rasterscans.DetectorDummy('dd')


# rasterscan

rasterscan = rasterscans.RasterScan()
#rasterscans.DEFAULT_SCANNABLES_FOR_RASTERSCANS = [meta]  # @UndefinedVariable
alias('rasterscan')  # @UndefinedVariable


# Doc

print
print '\n'.join(rasterscan.__doc__.split('\n')[2:])
print
# print "- rasterpil1 writing to $datadir$/tmp"
# print "- Change roi with e.g.:"
# print "     rasterpil1.roistats1.setRoi(10, 20, 470, 160, 'roi1') (startx, starty, sizex, sizey, name)"
# print "- raster map plotted on 'Plot 2' "
# 
# print
# print """
# - If restarted the MEDIPIX camera won't work. It will miss the fist exposure."
#  To fix this:"
#   $ rdesktop -g1200x1000 i16-xmap1
#  
#   The login is 'i16' and the password is stuck on the XMAP box. (On top of the experimental equipment tower)
#   
#   Then uncheck the checkbox labeled: 'Send Acq. Header' under the 'Advanced' tab.
# """

print '=' * 80
