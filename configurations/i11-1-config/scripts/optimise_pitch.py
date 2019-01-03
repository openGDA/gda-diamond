# this is the start position
start = -10
# this is the coarse step of the piezo
step = 1.0
# this is the maximum number of steps we should take
n = ((10 - start) / step) + 1
# this is the y size of S4
ysize = 0.8
# this is the y centre of S4
ycentre = -1.226
# this is the pc for the fast feedback
ffb = "BL11I-OP-DCM-01:FP:S4FB"
# this is the pv for DCM pitch
fp = "BL11I-OP-DCM-01:FB:DAC:02"

# make sure we use builtin python sum
try:
 del(sum)
except:
 pass

# wait for topup to complete if it will interrupt us
topup_time = float(caget("SR-CS-FILL-01:COUNTDOWN"))
# assume it will take 0.6 seconds per point, a position will be found
# halfway through each scan, and we need 3 scan iterations
needed_time = n*0.7*0.5*3
if needed_time > topup_time:
 waiting_time = topup_time + 10
 print "Waiting %.2fs for topup to complete..." % waiting_time
 sleep(waiting_time)
print "Starting Optimisation"

# setup scaler and disable fast feedback
caput("BL11I-EA-COUNT-02.TP",0.5)
caput(ffb+":AUTO", 0)
caput(ffb+".FBON", 0)

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
 caput(fp, start)
 sleep(1)
 less = 0
 for i in range(n):
  posn = start + step * i
  caput(fp, posn)
  sleep(0.12)
  posns.append(posn)
  caput("BL11I-EA-COUNT-02.CNT", 1)
  sleep(0.52)
  izero = Io.getPosition()
  izeros.append(izero)
  if len(izeros) < 3:
   continue
  if izeros[-1] > izeros[-2]:
   less = 0
  else:
   less += 1
  if less > 3:
   break
 return (posns, izeros)

# scan fine pitch (coarse)
posns, izeros = scan_fpitch(start, step, n)
pxs = [p for p, x in zip(posns,izeros) if x > 0.95*max(izeros)]
maximum = sum(pxs) / len(pxs)
print "maximum1", maximum

# scan fine pitch (fine)
caput(fp, -10)
sleep(2)
step = step / 10.0
start = maximum - (n * 0.5 * step)
posns, izeros = scan_fpitch(start, step, n)
pxs = [p for p, x in zip(posns,izeros) if x > 0.95*max(izeros)]
maximum = sum(pxs) / len(pxs)
print "maximum2", maximum

# scan fine pitch (v fine)
caput(fp, -10)
sleep(2)
step = step / 10.0
start = maximum - (n * 0.5 * step)
posns, izeros = scan_fpitch(start, step, n)
pxs = [p for p, x in zip(posns,izeros) if x > 0.95*max(izeros)]
maximum = sum(pxs) / len(pxs)
print "maximum3", maximum

# move to maximum
caput(fp, -10)
sleep(2)
caput(fp, maximum)
print "Optimisation max Izero: %d cts" % (max(izeros)*2)
print "Optimisation fpitch2 value: %.3f mdeg" % maximum
'''
print "Moving slit blades in"
pos s4ygap ysize
diff = float(caget("BL11I-AL-SLITS-04:Y:MINUS:I"))
sum = abs(float(caget("BL11I-AL-SLITS-04:Y:PLUS:I"))) + abs(float(caget("BL11I-AL-SLITS-04:Y:MINUS:I"))) / 2
while abs(diff) > 0.02:
 print diff / sum * 0.2
 p = s4ycentre.getPosition() + (diff / sum * 0.2)
 pos s4ycentre p
 diff = float(caget("BL11I-AL-SLITS-04:Y:PLUS:I")) - float(caget("BL11I-AL-SLITS-04:Y:MINUS:I"))
 sum = abs(float(caget("BL11I-AL-SLITS-04:Y:PLUS:I")) + float(caget("BL11I-AL-SLITS-04:Y:MINUS:I"))) / 2
'''
sleep(2)
PPOS = float(caget(fp+".RVAL"))
print "Enabling fast feedback around", PPOS
caput("BL11I-DI-IAMP-04:SETRANGE", 1)
caput(ffb+":LIMITS.DISA", 1)
caput(ffb+".DRVL", PPOS - 1000)
caput(ffb+".DRVH", PPOS + 1000)
caput(ffb+".I", PPOS)
caput(ffb+".KP", 0.01)
caput(ffb+".KI", 150)
caput(ffb+".VAL", 0)
caput(ffb+".DT", 0.03)
'''
caput(ffb+".FBON", 1)
caput(ffb+":AUTO", 1)
'''

# tidy up
caput("BL11I-EA-COUNT-01.TP1",1.0)
caput("BL11I-EA-COUNT-01.CONT", "AutoCount")
caput("BL11I-EA-COUNT-02.CONT", "AutoCount")
caput("BL11I-EA-COUNT-02.CNT", 1)
print "Optimisation Complete"
print "Now you need to centre the slits, then enable feedback"
