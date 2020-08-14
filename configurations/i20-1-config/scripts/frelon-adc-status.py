# Print adc status of the frelon to the Jython console.
# Command and labels taken from text strings in myfrelon_GUI.py on frelon control machine.
# imh 16/6/2020

ADC_Register_Camera=['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG',
                             'AH', 'AI', 'AJ', 'AK']
ADC_Status_Camera_labels=['CCD_TEMP (deg) ',
        'PELTCUR (Amp)  ',
        'PRESSURE (mbar)',
        'PCBTEMP (deg)  ',
        'VDR1 (V)       ',
        'VDR2 (V)       ',
        'VDR3 (V)       ',
        'VDR4 (V)       ',
        'IN8            ',
        'IN9            ',
        'IN10           ']

ADC_Register_Power=['aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag',
        'ah', 'ai', 'aj', 'ak']
ADC_Status_Power_labels=['+ 5   V ',
        '+ 3.3 V ',
        '+15   V ',
        '-15   V ',
        '+ 6   V ',
        '- 6   V ',
        '-22   V ',
        '+ 3.6 V ',
        'TEMP1   ',
        'TEMP2   ',
        'TPELTIER']


def showStatus(commands, labels) :
    frelonDevice = frelon.getFrelon()
    for i in range(len(commands)) :
        command = ">" + commands[i] + "?"
        val = frelonDevice.execSerialCommand(command)
        val[0] = val[0].replace("!OK:","")
        print labels[i] + " : "+val[0]


def showFrelonAdcStatus() :
    showStatus(ADC_Register_Camera, ADC_Status_Camera_labels)
    showStatus(ADC_Register_Power, ADC_Status_Power_labels)


print "Use showFrelonAdcStatus() function to print frelon ADC status to Jython console"

