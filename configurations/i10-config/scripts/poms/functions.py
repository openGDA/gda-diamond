def testIntensity():
    #pos tth 0 th 0 sy -5
    pos s4xsize 0.1 s4ysize 0.12
    pos s1xsize 1 s1ysize 1
    pos pol pc
    pos energy 700
    pimteShOpen()
    scan dummy 1 100 1 refl 0.1


# rasor diode
#500771 # light
#500772, 773 #dark


#rasor diode 12/12/18
#502835 #light
#502836, 837, 838 #dark


#rasor 503065 on wednesday when struggeling with 




def logMirrorPositions():
    # measure at 700 eV
    
    f=open("/dls_sw/i10/software/gda/config/scripts/poms/logs/mirror_positions.dat", 'a')
    timeStr = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    line = "%s" % timeStr
    line += "\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%2.2f" % (m4_x.getPosition(), m4_y.getPosition(), m4_z.getPosition(), m4_yaw.getPosition(), m4_pitch.getPosition(), m4_roll.getPosition(), m4fpitch.getPosition())
    line += "\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%2.2f" % (m3m5_x.getPosition(), m3m5_y.getPosition(), m3m5_z.getPosition(), m3m5_yaw.getPosition(), m3m5_pitch.getPosition(), m3m5_roll.getPosition(), m3m5fpitch.getPosition())
    line += "\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%2.2f" % (m1_x.getPosition(), m1_y.getPosition(), m1_z.getPosition(), m1_yaw.getPosition(), m1_pitch.getPosition(), m1_roll.getPosition(), m1fpitch.getPosition())
    line += "\t%6.3f\t%6.3f" % (pgm_grat_pitch.getPosition()/1000.0, pgm_m2_pitch.getPosition()/1000.0)
    line += "\n"
    f.write(line); f.flush(); f.close()









# align for transmission
# works well for S4 x=0.2, y=1.2
def alignSample():
    pos vmag 0
    scan dummy 1 1 1 pixistiff 0.002 pixisSum
    cscan user1_axis2 0.3 0.05 pixistiff 0.5 pixisSum
    go peak
    scan dummy 1 1 1 pixistiff 0.002 pixisSum
    cscan user1_axis1 0.3 0.05 pixistiff 0.5 pixisSum
    go peak
    scan dummy 1 1 1 pixistiff 0.5 pixisSum
    
    """ saves log """
    f=open("/dls_sw/i10/software/gda/config/scripts/poms/logs/cryo_position.dat", 'a')
    timeStr = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    line = "%s\t%03.1f\t%1.2f\t%02.2f\t%1.2f \n" % (timeStr, pomsTemp.getPosition(), user1_axis1.getPosition(), user1_axis2.getPosition(), user1_axis3.getPosition() )
    f.write(line); f.flush(); f.close()
    


def fieldCycle():
    for i in range(20): #field cycling
        pos vmag 120
        time.sleep(1)
        pos vmag 0
        time.sleep(1)
        
        
