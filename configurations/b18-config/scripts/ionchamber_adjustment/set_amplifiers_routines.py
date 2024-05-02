###########
'''
last_edit 20180214 DG
tested release
Adjusting amplifiers in the minimum number of steps possible, included possiblity to select an element and edge to do the adjustment
'''

from time import sleep
from warnings import warn
import random

# lists for convert between value and index (0~35)
val_list=['1','2','5','10','20','50','100','200','500']
scale_list=['pA/V','nA/V','uA/V','mA/V']

def valueToIndex(val, scale): # val is actual value from val_list, same as scale from scale_list
    ampl=int(val_list.index(val))+int(scale_list.index(scale))*9
    return ampl

def indexToValue(ampl): # ampl is 0~35
    def scale():
        return int(ampl/9)
    def val():
        return int(ampl-scale()*9)
   
    #return [val_list[val()],scale_list[scale()]]
    return [val(),scale()]



def get_amp_txt(amp_int):

    scale_int=amp_int//9
    val_int=amp_int%9
    scale_txt=scale_list[scale_int]
    val_txt=val_list[val_int]
    return val_txt+scale_txt

def get_amp_factor(amp_int):
    scale_index=amp_int//9
    val_index=amp_int%9
 
    #counts as if 1A current measured: 500mA/v -> 2, 20uA/V -> 1e4 1pA/V -> 1e12
    amp_factor=10**(3*(4-scale_index))/int(val_list[val_index])
    return amp_factor

def get_ic_status(amps,ints,max_I):
    ic_status=['','','']
    for ic in range(3):
        lowest_acceptable_value=0.8*max_I/2.5
        if ints[ic]>max_I:
            ic_status[ic]='high'
        elif lowest_acceptable_value<=ints[ic]<=max_I:
            ic_status[ic]='ok'
        elif ints[ic]<lowest_acceptable_value:
            ic_status[ic]='low'
        else:
            ic_status[ic]='error_reading_detector_values'
    return ic_status

def get_rand_counts(amp_int,amp_opt,counts_opt=20000000,counts_min_limit=1,counts_max_limit=35000000,counts_tol_limit=1000):
    norm_factor=get_amp_factor(amp_opt)
    current=counts_opt/norm_factor
    amp_factor=get_amp_factor(amp_int)
    min_range=int(max(counts_min_limit,min(current*amp_factor*0.8,counts_max_limit-counts_tol_limit)))
    max_range=int(max(counts_min_limit+counts_tol_limit,min(current*amp_factor*1.2,counts_max_limit)))
    counts=    random.randrange(min_range,max_range)
    return counts

def read_chambers_test(amp_array,amp_opt_array):
    ints=[0,0,0,0]
    for i in range(len(amp_array)):
        amp_int=amp_array[i]
        amp_opt=amp_opt_array[i]
        ints[i+1]=get_rand_counts(amp_int,amp_opt)
    return ints

def read_ampl_test(amps_to_set=[]):
    if len(amps_to_set)==0:
        amps=[random.randrange(0,36) for i in range(3)]
    else:
        amps=amps_to_set
    return amps
    
    
def isalive():  #determines if b18 detector rates is running
    status_alive=detectorMonitorDataProvider.getCollectionIsRunning()    
    return status_alive

def read_from_alive():
    #here b18 detector rates is running
    ok=True
    while ok:
        a=counterTimer01.getStatus()
        if(a==0):
            result=counterTimer01.readout()
            ok=False
        else:
            sleep(0.1)
    return result

def read_from_stopped():
    #here b18 detector rates is not running so read directly
    counterTimer01.setCollectionTime(1.0)
    counterTimer01.collectData()
    sleep(1.1)
    result=counterTimer01.readout()
    #counterTimer01.getExtraNames()
    return result

def read_chambers():
    result=read_from_stopped()
    return result

def read_ampl(): # index
    #note present implementation dos not have much sense 

    val1= i0_stanford_sensitivity.getPosition() 
    val2= it_stanford_sensitivity.getPosition()
    val3= iref_stanford_sensitivity.getPosition()
    scale1= i0_stanford_sensitivity_units.getPosition()
    scale2= it_stanford_sensitivity_units.getPosition()
    scale3= iref_stanford_sensitivity_units.getPosition()
    
    #convert the text code for amplification+scale into a number 
    ampl1=valueToIndex(val1, scale1)
    ampl2=valueToIndex(val2, scale2)
    ampl3=valueToIndex(val3, scale3)

    print 'amplifiers:',[ampl1,ampl2,ampl3]
    return [ampl1,ampl2,ampl3]

def set_ampl(ampl_arr): #ampl_arr is index array
    #sets amplifications according to read_ampl code i.e. integers starting from 0=1pa/v
    
    ampl1=ampl_arr[0]
    ampl2=ampl_arr[1]
    ampl3=ampl_arr[2]
      
    #convert the text code for amplification+scale into a number 
    scale1=indexToValue(ampl1)[1]
    scale2=indexToValue(ampl2)[1]
    scale3=indexToValue(ampl3)[1]
    
    val1=indexToValue(ampl1)[0]
    val2=indexToValue(ampl2)[0]
    val3=indexToValue(ampl3)[0]

    print 'set_ampl:',ampl_arr
    print '\tscales and values:',scale1,val1, scale2,val2,scale3,val3
    print '\tI0:',val_list[val1], scale_list[scale1]
    print '\tIt:',val_list[val2], scale_list[scale2]
    print '\tIref:',val_list[val3], scale_list[scale3]
    
    ampl1=int(val1)+int(scale1)*9
    ampl2=int(val2)+int(scale2)*9
    ampl3=int(val3)+int(scale3)*9
    
    if(val1>=0)and(val1<9):
        i0_stanford_sensitivity.moveTo(val_list[val1])
    if(val2>=0)and(val2<9):
        it_stanford_sensitivity.moveTo(val_list[val2])
    if(val3>=0)and(val3<9):
        iref_stanford_sensitivity.moveTo(val_list[val3])
    if(scale1>=0)and(scale1<4):
        i0_stanford_sensitivity_units.moveTo(scale_list[scale1])
    if(scale2>=0)and(scale2<4):
        it_stanford_sensitivity_units.moveTo(scale_list[scale2])
    if(scale3>=0)and(scale3<4):
        iref_stanford_sensitivity_units.moveTo(scale_list[scale3])

    return [ampl1,ampl2,ampl3]

def adjust_sensitivities(amp_opt_array=[8,12,15]):
    def keep_values(ic):
        amps_to_set[ic]=amps[ic]
        exp_counts[ic]=counts[ic]
    def optimise_low_counts(ic,max_I=22000000):
        current=counts[ic]/get_amp_factor(amps[ic])
        max_amp=max_I/current
        amps_to_set[ic]=min(range(36), key=lambda i: abs(get_amp_factor(i)-max_amp))
        exp_counts[ic]=current*get_amp_factor(amps_to_set[ic])    
    def optimise_high_counts(ic):
        amps_to_set[ic]=min(amps[ic]+9,35)
        current=counts[ic]/get_amp_factor(amps[ic])
        exp_counts[ic]=current*get_amp_factor(amps_to_set[ic])    
    def reduce_to_keep_safe_counts(ic):
        amps_to_set[ic]=min(amps[ic]+1,35)
        current=counts[ic]/get_amp_factor(amps[ic])
        exp_counts[ic]=current*get_amp_factor(amps_to_set[ic]) 
    max_I=22000000
    amps_ok=[False]*3
    ic_status=['','','']
    old_status=['','','']
    amps_to_set=[]
    loop_counter=0
    while amps_ok.count(True) is not 3:
        loop_counter=loop_counter+1
        print('loop : '+str(loop_counter))
        amps_ok=[False]*3
        sleep(0.1)
        amps=read_ampl()
        print('amplifications integer = ',amps)
        print('amplifications = ',[get_amp_txt(amp_int) for amp_int in amps])
        counts=read_chambers()[1:4] #only reading values from I0,It,Iref in position 1,2,3 of the array
        print('counts = ',counts)        
        ic_status=get_ic_status(amps,counts,max_I)
        print('ion chambers status = ',ic_status)
        amps_to_set=[1,1,1] 
        for a in range(len(amps)):
            amps_to_set[a]=amps[a]
        exp_counts=counts 
        if loop_counter>20:
            amps_ok=[True]*3
            ic_status=['ok','ok','ok']
        #loop on each ionchamber
        for ic in range(3):
            print('ion chamber : ',ic)
            if ic_status[ic]=='ok':
                    keep_values(ic)
                    amps_ok[ic]=True
            elif ic_status[ic]=='low':
                if amps[ic]==0:
                    print('amps reached 0 limit')
                    keep_values(ic)
                    amps_ok[ic]=True
                    warn("\n Ionchamber "+str(ic)+"; Amplification at minimum value, intensities cannot be further optimised")
                elif 'ok' in old_status[ic]:    
                    print('counts were ok and then decreased')
                    #counts oscillating around lowest_acceptable_I, no changes in amplification needed
                    keep_values(ic)
                    amps_ok[ic]=True
                else :
                    #run a loop that optimizes the amplifications to be as close as possible to max_I without saturation
                    print('running loop to optimize low counts')
                    optimise_low_counts(ic,max_I)
                    old_status[ic]=old_status[ic]+'_optimized'                
            elif ic_status[ic]=='high':
                if amps[ic]==35:
                    print('amps reached 35 limit')
                    keep_values(ic)
                    amps_ok[ic]=True
                    warn("\n Ionchamber "+str(ic)+"; Amplification at maximum value, detector saturation cannot be avoided")
                elif 'ok' in old_status[ic]:
                    print('counts were ok and then increased')
                    #counts oscillating around max_I value, one step change applied to stay in a safe count region
                    #ok, no need to double check counts
                    reduce_to_keep_safe_counts(ic)
                    amps_ok[ic]=True    
                elif 'optimized' in old_status[ic]:
                    print('counts were optimised from low and then saturated')
                    # previous optimization loop did not work, avoid going in infinite loop 
                    #goes down step by step until not saturated
                    reduce_to_keep_safe_counts(ic)
                    amps_ok[ic]=True
                else:    
                    #changes scale unit and optimize during next loop 
                    print('running loop to optimize high counts')        
                    optimise_high_counts(ic)
            old_status[ic]=old_status[ic]+'_'+ic_status[ic]
        print('old_status: ',old_status)
        print(amps_to_set,'\n',exp_counts,'\n',amps_ok)
        set_ampl(amps_to_set)
    print(amps_ok)
    print('amplifications to set :',amps_to_set)
    print('intensities expected :',exp_counts)
    return amps_to_set


def adjust_sensitivities_edge(element='',line='K',pre_edge=50,post_edge=1000):
    import ionchamber_adjustment.Xray_edges as xe
    if element in xe.At_names:
        atnum_edge=xe.At_names.index(element)
    else:
        warn("element not recognized, check format! (first letter has to be capital e.g. Fe for iron)")
        lst=xe.Edge_K
    
    if   line in ['k','K']:           lst=xe.Edge_K
    elif line in ['l1','L1']:         lst=xe.Edge_L1
    elif line in ['l2','L2']:         lst=xe.Edge_L2 
    elif line in ['l3','L3','l','L']: lst=xe.Edge_L3
    elif line in ['m1','M1']:         lst=xe.Edge_M1
    elif line in ['m2','M2']:         lst=xe.Edge_M2
    elif line in ['m3','M3']:         lst=xe.Edge_M3
    elif line in ['m4','M4']:         lst=xe.Edge_M4
    elif line in ['m5','M5','m','M']: lst=xe.Edge_M5
    else: 
        warn("line not recognized (should be K, L1, L2, L3, L, M1, M2, M3, M4, M5, M)\n by default, the calculations will be performed at K edge")
        lst=xe.Edge_K
    
    en_edge=lst[atnum_edge]
    if 2000<en_edge<36000:
        E1=en_edge-pre_edge
        E2=en_edge+post_edge
        print ' adjusting amplifier settings at ',E1,' ev...'
        pos energy E1
        ampl_E1=adjust_sensitivities()
        print ' adjusting amplifier settings at ',E2,'ev...'
        pos energy E2
        ampl_E2=adjust_sensitivities()
        #now setting lower sensitivity measured
        ampl_to_set=[max(ampl_E1[0],ampl_E2[0]),max(ampl_E1[1],ampl_E2[1]),max(ampl_E1[2],ampl_E2[2])]
        warn_amplifiers(ampl_to_set)
        set_ampl(ampl_to_set)
        print 'done'
    else:
        warn('energy out of the range allowed on B18 beamline 2-36KeV, check again element and line')

def adjust_sensitivities_element_edge(element_edge='Fe_K'):
    element,line=element_edge.split('_')
    adjust_sensitivities_edge(element,line)

def warn_amplifiers(ampl):
    #Sends a wargning i f amplifiers not great
    ok=True
    for i in range(len(ampl)):
        if ampl[i]<9:
            warn("\n Ionchamber "+str(i)+"; amplifier in pA range, low flux")
            ok=False
        elif ampl[i]>17:
            warn("\n Ionchamber "+str(i)+"; amplifier over nA range, high flux")
            ok=False
    return ok

def adjust_sensitivities_2E(E1,E2):
    print 'DG_edit_2018'
    print ' adjusting amplifier settings at ',E1,' ev...'
    pos energy E1
    ampl_E1=adjust_sensitivities()
    print ' adjusting amplifier settings at ',E2,'ev...'
    pos energy E2
    ampl_E2=adjust_sensitivities()

    #now setting lower sensitivity measured
    ampl=[max(ampl_E1[0],ampl_E2[0]),max(ampl_E1[1],ampl_E2[1]),max(ampl_E1[2],ampl_E2[2])]
    warn_amplifiers(ampl) #sends a warning message if amplifiers are out of nA regime
    set_ampl(ampl)
    print 'done'
    return


def adjust_sensitivities_xE(Earr):
    ampl_list=[]
    for iene in Earr:
        print ' adjusting amplifier settings at ',iene,' ev...'
        pos energy iene
        energy.waitWhileBusy()  #added 2015.02.20
        ampl_tmp=adjust_sensitivities()
        ampl_list.append(ampl_tmp)
    
    transposed_list=map(list, zip(*ampl_list)) #Note trick!
    print transposed_list
    #now setting lower sensitivity measured
    ampl=[max(transposed_list[0]),max(transposed_list[1]),max(transposed_list[2])]
    set_ampl(ampl)
    print 'done'
    return

def check_beam_on():
    beam_on=True
    d1=0
    d2=0
    d3=0
    a3=0
    d7=0
    d9=0
    Shtr0=0
    Shtr1=0
    ca1=CAClient()    
    warn_msg=''
    if ca1.caget('BL18B-DI-PHDGN-01:STA')!='1':
        d1=1
        warn_msg=warn_msg+'\nD1 closed - diagnostic in'
    if ca1.caget('BL18B-DI-PHDGN-02:STA')!='1':
        d2=1
        warn_msg=warn_msg+'\nD2 closed - diagnostic in'
    if ca1.caget('BL18B-DI-PHDGN-03:STA')!='1':
        d3=1
        warn_msg=warn_msg+'\nD3 closed - diagnostic in'
    if ca1.caget('BL18B-OP-ATTN-03:P1:UPD.D')!='0.0':
        a3=1
        warn_msg=warn_msg+'\nA3 closed - fluorescence screen in'
    if ca1.caget('BL18B-DI-PHDGN-07:STA')!='3':
        d7=1
        warn_msg=warn_msg+'\nD7 closed - front laser in'
    if ca1.caget('BL18B-DI-PHDGN-09:STA')!='3':
        d9=1
        warn_msg=warn_msg+'\nD9 closed - camera in'
    if ca1.caget('FE18B-PS-SHTR-02:STA')=='3':
        Shtr0=1
        warn_msg=warn_msg+'\nExperimental Shutter closed'
    if ca1.caget('BL18B-PS-SHTR-01:STA')=='3':
        Shtr1=1
        warn_msg=warn_msg+'\nOptic Shutter closed'
    on=[d1,d2,d3,a3,d7,d9,Shtr0,Shtr1]
    if sum(on) is not 0:
        beam_on=False
        warn('X-ray beam not on:'+warn_msg)
    return beam_on
