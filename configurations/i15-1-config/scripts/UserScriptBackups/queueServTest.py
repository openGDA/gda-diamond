from org.eclipse.scanning.event.queues import ServicesHolder as srvho

from org.eclipse.scanning.api.event.queues.beans import TaskBean
from org.eclipse.scanning.api.event.queues.beans import SubTaskAtom
from org.eclipse.scanning.api.event.queues.beans import MoveAtom

qServ = srvho.getQueueService()
qctrl = srvho.getQueueControllerService()

#ActiveMQ can be viewed by going to http://i15-1-control.diamond.ac.uk:8161
#1. Log in as admin, admin
#2. Go back to the main page and browse the available queues

qServ.setQueueRoot("uk.ac.diamond.i15-1.test")
qServ.setUri("failover:(tcp://i15-1-control.diamond.ac.uk:61616)?startupMaxReconnectAttempts=3")

qctrl.init()
qctrl.startQueueService()

#=== TESTING A SIMPLE MOVE ===
tb = TaskBean("Test")
sta = SubTaskAtom("MoveTestParent")
mva = MoveAtom("Movement", "s5gapX", 0, 10) #0 is request position, 10 is run time, which is not used atm

sta.addAtom(mva)
tb.addAtom(sta)

qctrl.submit(tb, qctrl.getJobQueueID())

#=== TESTING A MULTI-MOTOR MOVE ===
cplxmv = { "s5gapX" : 5, "s5gapY" : 3 } #This time there are two request positions
mvb = MoveAtom("ComplexMove", cplxmv, 10) #Again 10 is not used
stb = SubTaskAtom("NewTestSub")
stb.addAtom(mvb)
tb = TaskBean("newtest")
tb.addAtom(stb)
qctrl.submit(tb, qctrl.getJobQueueID())