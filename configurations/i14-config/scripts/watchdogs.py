# Manage scanning watchdogs
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
