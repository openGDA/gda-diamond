from gda.epics import CAClient
from gdascripts.messages import handle_messages
from gdascripts.scannable.epics.PvManager import PvManager
from gov.aps.jca.event import MonitorListener

class PvValueDictMonitorListener(MonitorListener):
    def __init__(self, pvValueDict, clientKey, caClient):
        self.clientKey=clientKey
        self.pvValueDict=pvValueDict
        self.pvValueDict[clientKey]=str(caClient.caget())

    def monitorChanged(self, ev):
        value = ev.getDBR().getValue()
        self.pvValueDict[self.clientKey]=str(value[0])

def testCAClient():
    pv='ws346-AD-SIM-01:CAM:ArrayCounter_RBV'
    cli=CAClient(pv)
    cli.configure()

    pv_values={}
    monitor=cli.camonitor(PvValueDictMonitorListener(pv_values, pv, cli))

    testMonitoring('pv_values', pv_values)

    cli.clearup()

    testNotMonitoring('pv_values', pv_values)

def testPvManager():
    adsim01=PvManager(pvroot='ws346-AD-SIM-01:')
    adsim01.configure()

    adsim01_values={}
    adsim01['CAM:ArrayCounter_RBV'].camonitor(PvValueDictMonitorListener(adsim01_values, 'CAM:ArrayCounter_RBV', adsim01['CAM:ArrayCounter_RBV']))
    adsim01['PROC:UniqueId_RBV'   ].camonitor(PvValueDictMonitorListener(adsim01_values, 'PROC:UniqueId_RBV'   , adsim01['PROC:UniqueId_RBV'   ]))

    testMonitoring('adsim01_values', adsim01_values)

    adsim01['CAM:ArrayCounter_RBV'].clearup()
    adsim01['PROC:UniqueId_RBV'   ].clearup()

    testNotMonitoring('adsim01_values', adsim01_values)

def testMonitoring(desc, pv_values):
    print "Monitoring..."
    print desc, '=', pv_values
    print "...Sleeping..."
    sleep(2)
    print desc, '=', pv_values
    print "...Sleeping..."
    sleep(2)
    print desc, '=', pv_values

def testNotMonitoring(desc, pv_values):
    print "Not monitoring..."
    print desc, '=', pv_values
    print "...Sleeping..."
    sleep(2)
    print desc, '=', pv_values
