'''
Created on 5 Feb 2018

@author: fy65
'''


def stopJythonScannablesExceptExcluded():
    print("!!! Stopping Jython scannables")
    from gda.factory import Finder
    from gda.device.scannable import ScannableMotionBase, ScannableBase
    from gda.device import Scannable
    command_server = Finder.find("command_server")
    scannables = command_server.getNamesForAllObjectsOfType(Scannable)

    excluded_scannables = scannables["STOP_ALL_EXCLUSIONS"]
    dontuse = None
    for dontuse in scannables.values():
        if isinstance(dontuse, (ScannableMotionBase, ScannableBase)):
            if excluded_scannables is not None and dontuse not in excluded_scannables:
                try:
                    print('    Stopping ' + dontuse.getName())
                    dontuse.stop()
                except:
                    print('    problem stopping ' + dontuse.getName())
            else:
                print('    ' + dontuse.getName() + ' is excluded from Stop All.')

    del dontuse
    print('\n')
