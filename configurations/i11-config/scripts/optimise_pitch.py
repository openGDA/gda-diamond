from gdascripts.utils import caget, caput
from time import sleep 
from gda.jython.commands.ScannableCommands import pos
from localStation import finder

fpitch2=finder.find("fpitch2")
Io=finder.find("Io")
# setup parameters for the scans
#start = -10
#step = 0.2
start = -4
step = 0.2
n = 176
ysize = 0.8
ycentre = -1.226

# wait for topup to complete if it will interrupt us
topup_time = float(caget("SR-CS-FILL-01:COUNTDOWN"))
needed_time = n*0.29 + 20.0
if needed_time > topup_time:
    waiting_time = topup_time + 10
    print "Waiting %.2fs for topup to complete..." % waiting_time
    sleep(waiting_time)
print "Starting Optimisation"

# setup scaler and disable fast feedback
caput("BL11I-EA-COUNT-01.TP",0.1)
caput("BL11I-OP-DCM-01:PID:AUTO", 0)
caput("BL11I-OP-DCM-01:PID.FBON", 0)
'''
s4yplus.asynchronousMoveTo(1.4)
s4yminus.asynchronousMoveTo(-2.4)
s4yplus.waitWhileBusy()
s4yminus.waitWhileBusy()
'''
# moving function
def scan_fpitch(start, step, n):
    posns = []
    izeros = []
    pos(fpitch2, start)
    sleep(1)
    less = 0
    for i in range(n):
        posn = start + step * i
        pos(fpitch2, posn)
        sleep(0.12)
        posns.append(posn)
        caput("BL11I-EA-COUNT-01.CNT", 1)
        sleep(0.12)
        izero = Io.getPosition()
        izeros.append(izero)
        if len(izeros) < 3:
            continue
        if izeros[-1] > izeros[-2]:
            less = 0
        else:
            less += 1
        if less > 5:
            break
    return (posns, izeros)

# scan fine pitch (coarse)
posns, izeros = scan_fpitch(start, step, n)

# scan fine pitch (fine)
step = step / 20.0
index = izeros.index(max(izeros))
start = posns[index] - (n * step * 0.8)
posns, izeros = scan_fpitch(start, step, n)

# move to maximum
maximum = posns[izeros.index(max(izeros))]
pos(fpitch2, maximum)
print "Optimisation max Izero: %.1f cts" % max(izeros)
print "Optimisation fpitch2 value: %.3f mDeg" % maximum

'''
print "Moving slit blades in"
pos s4ygap ysize
diff = float(caget("BL11I-AL-SLITS-04:Y:PLUS:I")) - float(caget("BL11I-AL-SLITS-04:Y:MINUS:I"))
sum = abs(float(caget("BL11I-AL-SLITS-04:Y:PLUS:I"))) + abs(float(caget("BL11I-AL-SLITS-04:Y:MINUS:I"))) / 2
while abs(diff) > 0.02:
 print diff / sum * 0.2
 p = s4ycentre.getPosition() + (diff / sum * 0.2)
 pos s4ycentre p
 diff = float(caget("BL11I-AL-SLITS-04:Y:PLUS:I")) - float(caget("BL11I-AL-SLITS-04:Y:MINUS:I"))
 sum = abs(float(caget("BL11I-AL-SLITS-04:Y:PLUS:I")) + float(caget("BL11I-AL-SLITS-04:Y:MINUS:I"))) / 2
'''
sleep(2)
print "Enabling fast feedback"
PPOS = float(caget("BL11I-OP-DCM-01:FPITCH2.RVAL"))
caput("BL11I-OP-DCM-01:PID:LIMITS.A", PPOS * 0.95)
caput("BL11I-OP-DCM-01:PID:LIMITS.B", PPOS * 1.05)
caput("BL11I-OP-DCM-01:PID.I", PPOS)
caput("BL11I-OP-DCM-01:PID.KP", 0.01)
caput("BL11I-OP-DCM-01:PID.KI", 1500)
caput("BL11I-OP-DCM-01:PID.VAL", 32768)
caput("BL11I-OP-DCM-01:PID.DT", 0.03)
caput("BL11I-OP-DCM-01:PID.FBON", 1)
caput("BL11I-OP-DCM-01:PID:AUTO", 1)

# tidy up
caput("BL11I-EA-COUNT-01.TP1",1.0)
print "Optimisation Complete"
