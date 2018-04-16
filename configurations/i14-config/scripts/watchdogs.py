# Manage scanning watchdogs
from __future__ import print_function
from org.eclipse.scanning.sequencer import ServiceHolder

watchdogService = ServiceHolder.getWatchdogService()
topupWatchdog = watchdogService.getWatchdog("TopupWatchdog")
expressionWatchdog = watchdogService.getWatchdog("ExpressionWatchdog")

def enableWatchdogs():
    topupWatchdog.setEnabled(True)
    expressionWatchdog.setEnabled(True)

def disableWatchdogs():
    topupWatchdog.setEnabled(False)
    expressionWatchdog.setEnabled(False)

def listWatchdogs():
    registered_names = watchdogService.getRegisteredNames()
    if registered_names is None or len(registered_names) == 0:
        print('No watchdogs are defined')
    else:
        print('The following watchdogs are defined. Watchdogs marked with an asterisk are currently enabled.')
        for name in sorted(registered_names):
            if watchdogService.getWatchdog(name).isEnabled():
                print('  *', name, sep = '')
            else:
                print('   ', name, sep = '')