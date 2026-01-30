'''
Created on 30 Jan 2026

@author: fy65
'''
from i06shared.commands.flatFieldAcqusition import acquire_flat_field,\
    create_nxlink
from gdascripts.scan.miscan import miscan

def flatField(num_images, exposure_time, driver_mode = "SRW"):
    if driver_mode =="SRW":
        from gdaserver import medipix  # @UnresolvedImport
        acquire_flat_field(num_images, medipix, exposure_time)
    elif driver_mode == "CRW":
        from gdaserver import mpx  # @UnresolvedImport
        miscan(mpx, num_images, exposure_time)
        create_nxlink(mpx)
    else:
        raise ValueError("drive mode given %s is not supported!" % driver_mode)

from gda.jython.commands.GeneralCommands import alias
alias("flatField")