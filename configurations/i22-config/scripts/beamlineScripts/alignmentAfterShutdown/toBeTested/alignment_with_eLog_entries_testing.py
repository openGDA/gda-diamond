import scisoftpy as dnp
import time
from gda.util import ElogEntry
from gda.configuration.properties import LocalProperties

elog = Elog("Beam Alignment", "i22user", LocalProperties.get(LocalProperties.GDA_DEF_VISIT), "BLI22", "BLI22")

s1xc = s1_xcentre.getPosition()
s1yc = s1_ycentre.getPosition()
s2xc = s2_xcentre.getPosition()
s2yc = s2_ycentre.getPosition()
ax = feaptr_x.getPosition()
ay = feaptr_y.getPosition()

s1y_requiredgap = 1.178
s1x_requiredgap = 1.226
s2y_requiredgap = 1.317
s2x_requiredgap = 1.381
s1_opengap = 5.000
s2_opengap = 15.000


# According to Dr Malfois, alignment works best at 7.5keV
# and the Femto amp at D4 is much better than the OD amp at D3
# so we get the mirrors out of the way.
# texts is an array to store comments and results in

pos energy 7.5
pos hfm_x 10
pos vfm_y 10
pos d4filter 'IL Diode HFM'

# S1 gaps are set for 600mm mirrors at both HFM and VFM positions
# S2 gaps are set out of the way
pos s1_ygap s1y_requiredgap
pos s1_xgap s1x_requiredgap
pos s2_ygap s2_opengap
pos s2_xgap s2_opengap

# Mono pitch is optimised. We get nicer rocking curves using finepitch piezo with motor fixed
elog.addText("Mono pitch scan: rscan finepitch -100 100 0.5 d4d1")
pos pitch -230
rscan finepitch -100 100 0.5 d4d1
inc finepitch -100
go peak
elog.addPeak("Peak flux found at finepitch: "+peak.result.pos)

#Calibrate S1 x and y
pos s1_xgap s1_opengap
pos s1_ygap s1_opengap

scan s1_yplus 2.5 -2.0 0.05 d4d1
s1ypluspos = edge.result.pos
s1ypluswidth = edge.result.fwhm
pos s1_yplus (s1_opengap/2.0)

scan s1_yminus -2.5 2.0 0.05 d4d1
s1yminuspos = edge.result.pos
s1yminuswidth = edge.result.fwhm
pos s1_yminus -(s1_opengap/2.0)

scan s1_xplus 2.5 -2.0 0.05 d4d1
s1xpluspos = edge.result.pos
s1xpluswidth = edge.result.fwhm
pos s1_xplus (s1_opengap/2.0)

scan s1_xminus -2.5 2.0 0.05 d4d1
s1xminuspos = edge.result.pos
s1xminuswidth = edge.result.fwhm
pos s1_xminus -(s1_opengap/2.0)

pos s1_yplus s1ypluspos
pos s1_yminus s1yminuspos

while d4d1.getPosition() > 200:
	inc s1_ygap -0.01
	sleep(2)

s1ypos = s1_ycentre.getPosition()
text = "New s1_ycentre position: "+ str(s1ypos)
texts.append( text )
print text
text = "Old s1_ycentre position was: "+ str(s1yc)
texts.append( text )
print text
text = "Apparent vertical beam motion at S1: "+ str(s1ypos - s1yc )
texts.append( text )
print text

caput("BL22I-AL-SLITS-01:Y:ZERO.PROC", 1)
text = "S1 Y calibrated! Moving s1_ygap to "+str(s1y_requiredgap)
texts.append( text )
print text
pos s1_ygap s1y_requiredgap

pos s1_xplus s1xpluspos
pos s1_xminus s1xminuspos

while d4d1.getPosition() > 200:
	inc s1_xgap -0.01
	sleep(2)

s1xpos = s1_xcentre.getPosition()

text = "New s1_xcentre position: "+ str(s1xpos)
texts.append( text )
print text
text = "Old s1_xcentre position was: "+ str(s1xc)
texts.append( text )
print text
text = "Apparent horizontal beam motion at S1: "+ str(s1xpos - s1xc )
texts.append( text )
print text

caput("BL22I-AL-SLITS-01:X:ZERO.PROC", 1)
text = "S1 X calibrated! Moving s1_xgap to "+str(s1x_requiredgap)
texts.append( text )
print text
pos s1_xgap s1x_requiredgap

scan feaptr_y -4 4 0.1 d4d1
go peak
text = "New feaptr_y position: "+ str(feaptr_y.getPosition())
texts.append( text )
print text
text = "Old feaptr_y position was: "+ str(ay)
texts.append( text )
print text
text = "Apparent vertical beam motion at FE aperture: "+ str(feaptr_y.getPosition() - ay )
texts.append( text )
print text

scan feaptr_x -4 4 0.1 d4d1
go peak
text = "New feaptr_x position: "+ str(feaptr_x.getPosition())
texts.append( text )
print text
text = "Old feaptr_x position was: "+ str(ax)
texts.append( text )
print text
text = "Apparent horizontal beam motion at FE aperture: "+ str(feaptr_x.getPosition() - ax )
texts.append( text )
print text


#Calibrate S2 x and y

scan s2_yplus 1.5 -1 0.02 d4d1
s2ypluspos = edge.result.pos
s2ypluswidth = edge.result.fwhm
pos s2_yplus (s2_opengap/2.0)

scan s2_yminus -1.5 1.0 0.02 d4d1
s2yminuspos = edge.result.pos
s2yminuswidth = edge.result.fwhm
pos s2_yminus -(s2_opengap/2.0)

scan s2_xplus 1.5 -1.0 0.02 d4d1
s2xpluspos = edge.result.pos
s2xpluswidth = edge.result.fwhm
pos s2_xplus (s2_opengap/2.0)

scan s2_xminus -1.5 1.0 0.02 d4d1
s2xminuspos = edge.result.pos
s2xminuswidth = edge.result.fwhm
pos s2_xminus -(s2_opengap/2.0)

pos s2_yplus s2ypluspos
pos s2_yminus s2yminuspos

while d4d1.getPosition() > 200:
	inc s2_ygap -0.005
	sleep(2)

s2ypos = s2_ycentre.getPosition()
text = "New s2_ycentre position: "+ str(s2ypos)
texts.append( text )
print text
text = "Old s2_ycentre position was: "+ str(s2yc)
texts.append( text )
print text
text = "Apparent vertical beam motion at S2: "+ str(s2ypos - s2yc )
texts.append( text )
print text

caput("BL22I-AL-SLITS-01:Y:ZERO.PROC", 1)
text = "S1 Y calibrated! Moving s1_ygap to "+str(s1y_requiredgap)
texts.append( text )
print text
pos s1_ygap s1y_requiredgap






pos s2_xplus s2xpluspos
pos s2_xminus s2xminuspos

while d4d1.getPosition() > 200:
	inc s2_xgap -0.005
	sleep(2)

s2xpos = s2_xcentre.getPosition()

text = "New s2_ycentre position: "+ str(s2_ypos)
texts.append( text )
print text
text = "Old s2_ycentre position was: "+ str(s2yc)
texts.append( text )
print text
text = "Apparent vertical beam motion at S2: "+ str(s2_ypos - s2yc )
texts.append( text )
print text

text = "New s2_xcentre position: "+ str(s2xpos)
texts.append( text )
print text
text = "Old s2_xcentre position was: "+ str(s2xc)
texts.append( text )
print text
text = "Apparent horizontal beam motion at S2: "+ str(s2xpos - s2xc )
texts.append( text )
print text

caput("BL22I-AL-SLITS-02:Y:ZERO.PROC", 1)
caput("BL22I-AL-SLITS-02:X:ZERO.PROC", 1)
print "S2 calibrated!"

pos s2_ygap 1.319
pos s2_xgap 1.365

scan idgap_mm 6 10 0.01 d4d1

pos energy 12.4

nTexts = len(texts)
for i in range(nTexts) :
	print texts[i]

print "All done..."