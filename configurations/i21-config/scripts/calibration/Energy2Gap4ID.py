'''
Created on 10 Jan 2018

@author: fy65
'''
from gdaserver import pgmGratingSelect
def idgap_calc(Ep, polarisation):
    gap=19.9
    # Linear Horizontal
    if (polarisation=="LH"):
        if (Ep>915 and Ep < 1050):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15: SHOULD BE CHECKED: MAY NEED CORRECTING
                #gap = 23.271 + 0.01748*Ep #Corrected for VPG1 on 2016/10/06
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                #gap = 18.669193 + 0.02350180*Ep  #Corrected for VPG2 at 930 eV on 2017/08/08
                gap = 18.04823999 + 0.02423148*Ep  #Corrected for VPG2 at 930 eV on 2019/07/21

            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 18.5611846 + 0.02369966*Ep #Corrected for VPG3 on 2017/09/20
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>500 and Ep<=600):
            if pgmGratingSelect.getPosition()=="VPG1":
                #gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15
                gap = 18.0359889 + 0.02485902*Ep #Corrected for VPG1 on 2018/04/19
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                #gap = 18.669193 + 0.02350180*Ep  #Corrected for VPG2 at 930 eV on 2017/08/08
                #gap = 18.0444241 + 0.02478207*Ep  #Corrected for VPG2 around 550 eV on 2018/01/16
                #gap = 18.0784061 + 0.02466737*Ep  #Corrected for VPG2 on 2019/02/11
                gap = 17.94704524 + 0.02501413*Ep  #Corrected for VPG2 on 2019/07/21
            elif pgmGratingSelect.getPosition()=="VPG3":
                #gap = 18.0112254 + 0.02490918*Ep #Corrected for VPG3 on 2018/01/20
                gap = 18.0365707 + 0.02483224*Ep  #Corrected for VPG3 on 2019/02/11
                
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>600 and Ep<=700):
            if pgmGratingSelect.getPosition()=="VPG1":
                #gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15
                gap = 18.9610065 + 0.02329706*Ep #Corrected for VPG1 on 2018/06/22
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                #gap = 18.669193 + 0.02350180*Ep  #Corrected for VPG2 at 930 eV on 2017/08/08
                #gap = 18.9256730 + 0.02327420*Ep  #Corrected for VPG2 around 550 eV on 2018/06/22
                gap = 19.10375129 + 0.02309419*Ep  #Corrected for VPG2 around 680 eV on 2019/07/28
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 18.9464110 + 0.02331950*Ep #Corrected for VPG3 on 2018/06/22                
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>700 and Ep<=820):
            if pgmGratingSelect.getPosition()=="VPG1":
                #gap = 19.2998231 + 0.02285595*Ep #Corrected for VPG1 on 2017/12/01
                #gap = 19.2309878 + 0.02296267*Ep #Corrected for VPG1 on 2018/4/23
                gap = 19.315 + 0.022716*Ep #Corrected for VPG1 on 2020/01/24
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 18.7769565 + 0.02352715*Ep  #Corrected for VPG2 on 2018/03/07
                #gap = 19.2185231 + 0.02287568*Ep  #Corrected for VPG2 on 2018/04/23
                #gap = 19.5776100 + 0.02231282*Ep  #Corrected for VPG2 on 2019/02/27
                gap = 19.23029473 + 0.02293361*Ep  #Corrected for VPG2 on 2019/07/14

            elif pgmGratingSelect.getPosition()=="VPG3":
                #gap = 19.0918751 + 0.02313526*Ep #Corrected for VPG3 on 2018/03/07
                gap = 18.5124072 + 0.02393300*Ep #Corrected for VPG3 on 2018/04/23
                
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>820 and Ep<=915):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 18.8476189 + 0.02339853*Ep #Corrected for VPG3 on 2018/01/11
#                 raise Exception("No calibration available for VPG1 in LH mode")
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 18.9330761 + 0.02318578*Ep  #Corrected for VPG2 on 2018/01/10
                gap = 19.11675168 + 0.02302911*Ep  #Corrected for VPG2 on 2019/07/15
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 18.8476189 + 0.02339853*Ep #Corrected for VPG3 on 2018/01/11
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")    
        elif (Ep>=325 and Ep<=410):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 15.0738470 + 0.03168032*Ep #Corrected for VPG1 on 2018/04/16
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap = 15.0331831 + 0.03165627*Ep  #Corrected for VPG2 on 2018/04/16
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 15.1190608 + 0.03150392*Ep #Corrected for VPG3 on 2018/04/16
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>=450 and Ep<=500):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 17.1120838 + 0.02661410*Ep #Corrected for VPG2 on 2018/08/03
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap = 17.1120838 + 0.02661410*Ep #Corrected for VPG2 on 2018/08/03
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 17.1120838 + 0.02661410*Ep #Corrected for VPG2 on 2018/08/03
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>=1050 and Ep<=1220):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 8.60527040 + 0.03287279*Ep  #Corrected for VPG1 on 2018/06/21
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap = 9.05139093 + 0.03235159*Ep  #Corrected for VPG2 on 2018/06/19
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 8.90762510 + 0.03261594*Ep #Corrected for VPG3 on 2018/06/19
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>=1295 and Ep<=1430):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap =-46.1543877 + 0.07416048*Ep  #Corrected for VPG1 on 2018/06/21
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap =-43.2421160 + 0.07174397*Ep  #Corrected for VPG2 on 2018/06/19
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap =-48.2489975 + 0.07562796*Ep #Corrected for VPG3 on 2018/06/19
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>1430 and Ep<=1680):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap =17.25681236 + 0.00867844*Ep  #Corrected for VPG1 on 2019/03/05
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap =17.60728471 + 0.00842455*Ep  #Corrected for VPG2 on 2019/03/05
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap =17.75147390 + 0.00840392*Ep  #Corrected for VPG3 on 2019/03/05
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>=1990 and Ep<=2010):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 34.45  #Corrected for VPG1 at 2000 eV on 2019/03/05
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap = 34.30  #Corrected for VPG2 at 2000 eV on 2019/03/05
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 34.35  #Corrected for VPG3 at 2000 eV on 2019/03/05
        elif (Ep>=250 and Ep<325):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 13.02256252 + 0.03789791*Ep #Corrected for VPG1 on 2019/05/12
            elif pgmGratingSelect.getPosition()=="VPG2":
                raise ValueError("Unknown Grating select in LH polarisationMode")
            elif pgmGratingSelect.getPosition()=="VPG3":
                raise ValueError("Unknown Grating select in LH polarisationMode")
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        else:
            raise ValueError("Energy demand %feV is outside calibrated ranges") % (Ep)
    # Linear Vertical
    elif polarisation=="LV":
        if (Ep>915 and Ep < 1050):
            if pgmGratingSelect.getPosition()=="VPG1":
                # gap = 11.1441137 + 0.01881376*Ep #Corrected for VPG1 on 2017/07/31 ---> Linear Vertical
                # gap = 11.6401974 + 0.01819208*Ep #Corrected for VPG1 on 2017/07/07 ---> Linear Vertical
                # gap = 11.0806699 + 0.01891585*Ep #Corrected for VPG1 at 930 eV on 2017/08/03 ---> Linear Vertical
                # gap = 10.8954430 + 0.01901698*Ep #Corrected for VPG1 at 930 eV on 2018/04/21 ---> Linear Vertical
                gap = 11.11762667 + 0.01899187*Ep #Corrected for VPG1 at 930 eV on 2019/07/05 ---> Linear Vertical
                
            elif pgmGratingSelect.getPosition()=="VPG2":
                # gap = 11.3014613 + 0.01856236*Ep #Corrected for VPG2 on 2017/08/02 ---> Linear Vertical
#                 gap = 11.2363888 + 0.01864200*Ep #Corrected for VPG2 at 930 eV on 2017/08/03 ---> Linear Vertical
#                 gap = 11.3838749 + 0.01844212*Ep #Corrected for VPG2 at 930 eV on 2017/10/08 ---> Linear Vertical
#                 gap = 10.9848979 + 0.01883657*Ep #Corrected for VPG2 at 930 eV on 2018/12/0 ---> Linear Vertical
#                 gap = 10.99339638 + 0.01885432*Ep #Corrected for VPG2 at 930 eV on 2019/07/11 ---> Linear Vertical
                gap = 11.25886216 + 0.01860659*Ep #Corrected for VPG2 at 930 eV on 2019/07/13 ---> Linear Vertical
                
            elif pgmGratingSelect.getPosition()=="VPG3":
                # gap = 11.2972185 + 0.01862358*Ep #Corrected for VPG3 on 2017/07/27 ---> Linear Vertical
                #gap = 11.3218637 + 0.01860144*Ep #Corrected for VPG3 at 930 eV on 2017/08/03 ---> Linear Vertical
                gap = 11.42918054 + 0.01841707*Ep #Corrected for VPG3 at 930 eV on 2019/07/10 ---> Linear Vertical
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>500 and Ep<=600):
            if pgmGratingSelect.getPosition()=="VPG1":
                #gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15
                gap = 11.4929059 +  0.01866740*Ep #Corrected for VPG1 on 2018/04/19
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                #gap = 11.5139582 + 0.01858746*Ep  #Corrected for VPG2 around 550 eV on 2018/01/15
                #gap = 11.5248060 + 0.01849955*Ep  #Corrected for VPG2 on 2019/02/11
                gap = 11.40989969 + 0.01877971*Ep  #Corrected for VPG3 on 2019/07/21
            elif pgmGratingSelect.getPosition()=="VPG3":
                #gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/10/09
                #gap = 11.4922997 + 0.01867722*Ep #Corrected for VPG3 on 2018/01/20
                gap = 11.4819971 + 0.01864219*Ep  #Corrected for VPG3 on 2019/02/11
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>600 and Ep<=700):
            if pgmGratingSelect.getPosition()=="VPG1":
                #gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15
                gap = 12.0417084 + 0.01768560*Ep #Corrected for VPG1 on 2018/06/22
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                #gap = 18.669193 + 0.02350180*Ep  #Corrected for VPG2 at 930 eV on 2017/08/08
                #gap = 12.0417084 + 0.01768560*Ep  #Corrected for VPG2 around 550 eV on 2018/06/22
                gap = 11.97497963 + 0.01783092*Ep  #Corrected for VPG2 around 660 eV on 2019/07/28
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 12.0035701 + 0.01780733*Ep #Corrected for VPG3 on 2018/06/22
                
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>700 and Ep<=820):
            if pgmGratingSelect.getPosition()=="VPG1":
                #gap = 12.1996757 + 0.01755656*Ep #Corrected for VPG1 on 2017/12/01
                #gap = 12.1751464 + 0.01759710*Ep #Corrected for VPG1 on 2018/04/23
                gap = 12.188 + 0.017466*Ep #Corrected for VPG1 on 2020/01/24
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 12.2144937 + 0.01746779*Ep  #Corrected for VPG2 on 2017/11/30
                #gap = 12.1515345 + 0.01754967*Ep  #Corrected for VPG2 on 2017/04/23
                #gap = 12.30554589 + 0.017280755*Ep  #Corrected for VPG2 on 2019/02/27
                gap = 12.07751729 + 0.01766240*Ep  #Corrected for VPG2 on 2019/07/14
            elif pgmGratingSelect.getPosition()=="VPG3":
                #gap = 12.1109048 + 0.01766378*Ep #Corrected for VPG3 on 2018/03/07
                gap = 12.0099896 + 0.01781198*Ep #Corrected for VPG3 on 2018/04/23
                #raise Exception("No calibration available for VPG1 in LV mode")
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>820 and Ep<=915):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 11.7160683 + 0.01814283*Ep #Corrected for VPG3 on 2018/01/11
#                 raise Exception("No calibration available for VPG1 in LV mode")
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 11.8230212 + 0.01793526*Ep  #Corrected for VPG2 on 2018/01/10
                gap = 11.82038503 + 0.01797192*Ep  #Corrected for VPG2 on 2019/07/15
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 11.7160683 + 0.01814283*Ep #Corrected for VPG3 on 2018/01/11
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>=1050 and Ep<=1220):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 2.89323404 + 0.02633185*Ep  #Corrected for VPG1 on 2018/06/21
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap = 2.51074540 + 0.02653346*Ep  #Corrected for VPG2 on 2018/06/19
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 2.82442703 + 0.02637886*Ep #Corrected for VPG3 on 2018/06/19
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")    
        elif (Ep>=450 and Ep<=500):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 11.0197952 + 0.01953697*Ep #Corrected for VPG2 on 2018/08/03
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap = 11.0197952 + 0.01953697*Ep #Corrected for VPG2 on 2018/08/03
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 11.0197952 + 0.01953697*Ep #Corrected for VPG2 on 2018/08/03
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>=1295 and Ep<=1430):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap =-40.0707586 + 0.05886600*Ep  #Corrected for VPG1 on 2018/06/21
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap =-45.2788260 + 0.06229816*Ep  #Corrected for VPG2 on 2018/06/19
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap =-43.8399100 + 0.06151759*Ep #Corrected for VPG3 on 2018/06/19
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>1430 and Ep<=1680):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap =10.92236351 + 0.00650547*Ep  #Corrected for VPG1 on 2019/03/05
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap =11.19292000 + 0.00630086*Ep  #Corrected for VPG2 on 2019/03/05
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap =11.45065675 + 0.00618820*Ep  #Corrected for VPG3 on 2019/03/05
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>=1990 and Ep<=2010):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 23.82  #Corrected for VPG1 at 2000 eV on 2019/03/05
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap = 23.72  #Corrected for VPG2 at 2000 eV on 2019/03/05
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 23.74  #Corrected for VPG3 at 2000 eV on 2019/03/05
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")    
        else:
            raise ValueError("Energy demand %feV is outside calibrated ranges") % (Ep)
    # Circular left
    elif polarisation=="CL":
        if (Ep>695 and Ep<=720):
            if pgmGratingSelect.getPosition()=="VPG1":
                raise Exception("No calibration available for VPG1 in CL mode")
            elif pgmGratingSelect.getPosition()=="VPG2":
#                 gap = 13.4952116 + 0.0200068*Ep #Corrected for VPG2 on 2019/02/28 with a phase of -19.36
#                 gap = 13.6675300 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.10
#                 gap = 13.6103300 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.20
#                 gap = 13.5531300 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.30
#                 gap = 13.52453 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.35
#                 gap = 13.4902100 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.41
#                 gap = 13.4787700 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.43
#                 gap = 13.4616100 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.46
#                 gap = 13.38153 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.60
                gap = 13.43873 + 0.0200600*Ep #Corrected for VPG2 on 2019/11/20 with a phase of -19.5
#                 gap = 13.15273 + 0.0200600*Ep #Corrected for VPG2 on 2019/11/20 with a phase of -20.0
            elif pgmGratingSelect.getPosition()=="VPG3":
                raise Exception("No calibration available for VPG3 in CL mode")
            else:
                raise ValueError("Unknown Grating select in CL polarisationMode")
        elif (Ep>720 and Ep<=740):
            if pgmGratingSelect.getPosition()=="VPG1":
                raise Exception("No calibration available for VPG1 in CL mode")
            elif pgmGratingSelect.getPosition()=="VPG2":
#                 gap = 13.9018119 + 0.0194255*Ep #Corrected for VPG2 on 2019/02/28 with a phase of -19.39
#                 gap = 13.6675300 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.10
#                 gap = 13.6103300 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.20
#                 gap = 13.5531300 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.30
#                 gap = 13.52453 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.35
#                 gap = 13.4902100 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.41
#                 gap = 13.4787700 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.43
#                 gap = 13.4616100 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.46
#                 gap = 13.38153 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.60
                gap = 13.43873 + 0.0200600*Ep #Corrected for VPG2 on 2019/11/20 with a phase of -19.5
#                 gap = 13.15273 + 0.0200600*Ep #Corrected for VPG2 on 2019/11/20 with a phase of -20.0
            elif pgmGratingSelect.getPosition()=="VPG3":
                raise Exception("No calibration available for VPG3 in CL mode")
            else:
                raise ValueError("Unknown Grating select in CL polarisationMode")
        else:
            raise ValueError("CL polarisationMode is not yet implemented for this energy")
    # Circular right
    elif polarisation=="CR":
        if (Ep>695 and Ep<=716):
            if pgmGratingSelect.getPosition()=="VPG1":
                raise Exception("No calibration available for VPG1 in CR mode")
            elif pgmGratingSelect.getPosition()=="VPG2":
#                 gap = 13.4790812 + 0.0200014*Ep #Corrected for VPG2 on 2019/02/28 with a phase of +19.36
#                 gap = 13.5276700 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.10
#                 gap = 13.5039300 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.20
#                 gap = 13.4801900 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.30
#                 gap = 13.46832 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.35
#                 gap = 13.4540800 + 0.0200900*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.41
#                 gap = 13.4493300 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.43
#                 gap = 13.4422100 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.46
#                 gap = 13.40897 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.60
                gap = 13.43271 + 0.0200600*Ep #Corrected for VPG2 on 2019/11/20 with a phase of -19.5
#                 gap = 13.31401 + 0.0200600*Ep #Corrected for VPG2 on 2019/11/20 with a phase of -20.0
            elif pgmGratingSelect.getPosition()=="VPG3":
                raise Exception("No calibration available for VPG3 in CR mode")
            else:
                raise ValueError("Unknown Grating select in CR polarisationMode")
        elif (Ep>716 and Ep<=740):
            if pgmGratingSelect.getPosition()=="VPG1":
                raise Exception("No calibration available for VPG1 in CR mode")
            elif pgmGratingSelect.getPosition()=="VPG2":
#                 gap = 13.4572041 + 0.0200039*Ep #Corrected for VPG2 on 2019/02/28 with a phase of +19.39
#                 gap = 13.5276700+ 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.10
#                 gap = 13.5039300 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.20
#                 gap = 13.4801900+ 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.30
#                 gap = 13.46832 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.35
#                 gap = 13.4540800 + 0.0200900*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.41
#                 gap = 13.4493300+ 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.43
#                 gap = 13.4422100 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of +19.46
#                 gap = 13.40897 + 0.0200600*Ep #Corrected for VPG2 on 2019/09/30 with a phase of -19.60
                gap = 13.43271 + 0.0200600*Ep #Corrected for VPG2 on 2019/11/20 with a phase of -19.5
#                 gap = 13.31401 + 0.0200600*Ep #Corrected for VPG2 on 2019/11/20 with a phase of -20.0
            elif pgmGratingSelect.getPosition()=="VPG3":
                raise Exception("No calibration available for VPG3 in CR mode")
            else:
                raise ValueError("Unknown Grating select in CR polarisationMode")
        else:
            raise ValueError("CR polarisationMode is not yet implemented for this energy")
    # Linear 
    elif polarisation=="L1":
        raise ValueError("L1 polarisationMode is not yet implemented")
 
    # Unsupported        
    else:
        raise ValueError("Unsupported polarisationMode mode")
       
    if (gap<20 or gap>70):
        raise ValueError("Required Soft X-Ray ID idgap is out side allowable bound (20, 70)!")
    return gap
