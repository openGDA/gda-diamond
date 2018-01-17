'''
Created on 10 Jan 2018

@author: fy65
'''
from gdaserver import pgmGratingSelect
def idgap_calc(Ep, polarisation):
    gap=19.9
    # Linear Horizontal
    if (polarisation=="LH"):
        if (Ep>910 and Ep < 970):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15
                #gap = 23.271 + 0.01748*Ep #Corrected for VPG1 on 2016/10/06
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                gap = 18.669193 + 0.02350180*Ep  #Corrected for VPG2 at 930 eV on 2017/08/08
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 18.5611846 + 0.02369966*Ep #Corrected for VPG3 on 2017/09/20
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>500 and Ep<600):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15
                #gap = 23.271 + 0.01748*Ep #Corrected for VPG1 on 2016/10/06
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                gap = 18.669193 + 0.02350180*Ep  #Corrected for VPG2 at 930 eV on 2017/08/08
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/09/20
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")
        elif (Ep>690 and Ep<750):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 19.2998231 + 0.02285595*Ep #Corrected for VPG1 on 2017/02/15
                #raise Exception("No calibration available for VPG1 in LH mode")
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 12.2144937 + 0.01746779*Ep  #Corrected for VPG2 on 2017/11/30
                raise Exception("No calibration available for VPG2 in LH mode")
            elif pgmGratingSelect.getPosition()=="VPG3":
                #gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/09/20
                raise Exception("No calibration available for VPG3 in LH mode")
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")    
        elif (Ep>=820 and Ep<=910):
            if pgmGratingSelect.getPosition()=="VPG1":
                #gap = 19.2998231 + 0.02285595*Ep #Corrected for VPG1 on 2017/02/15
                raise Exception("No calibration available for VPG1 in LH mode")
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap = 18.9330761 + 0.02318578*Ep  #Corrected for VPG2 on 2018/01/10
                #raise Exception("No calibration available for VPG2 in LH mode")
            elif pgmGratingSelect.getPosition()=="VPG3":
                #gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/09/20
                raise Exception("No calibration available for VPG3 in LH mode")
            else:
                raise ValueError("Unknown Grating select in LH polarisationMode")    
        else:
            raise ValueError("Energy demand %feV is outside calibrated ranges") % (Ep)
    # Linear Vertical
    elif polarisation=="LV":
        if (Ep>910 and Ep < 970):
            if pgmGratingSelect.getPosition()=="VPG1":
                # gap = 11.1441137 + 0.01881376*Ep #Corrected for VPG1 on 2017/07/31 ---> Linear Vertical
                # gap = 11.6401974 + 0.01819208*Ep #Corrected for VPG1 on 2017/07/07 ---> Linear Vertical
                gap = 11.0806699 + 0.01891585*Ep #Corrected for VPG1 at 930 eV on 2017/08/03 ---> Linear Vertical
            elif pgmGratingSelect.getPosition()=="VPG2":
                # gap = 11.3014613 + 0.01856236*Ep #Corrected for VPG2 on 2017/08/02 ---> Linear Vertical
#                 gap = 11.2363888 + 0.01864200*Ep #Corrected for VPG2 at 930 eV on 2017/08/03 ---> Linear Vertical
                gap = 11.3838749 + 0.01844212*Ep #Corrected for VPG2 at 930 eV on 2017/10/08 ---> Linear Vertical
            elif pgmGratingSelect.getPosition()=="VPG3":
                # gap = 11.2972185 + 0.01862358*Ep #Corrected for VPG3 on 2017/07/27 ---> Linear Vertical
                gap = 11.3218637 + 0.01860144*Ep #Corrected for VPG3 at 930 eV on 2017/08/03 ---> Linear Vertical
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>500 and Ep<600):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15
                #gap = 23.271 + 0.01748*Ep #Corrected for VPG1 on 2016/10/06
            elif pgmGratingSelect.getPosition()=="VPG2":
                #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                gap = 18.669193 + 0.02350180*Ep  #Corrected for VPG2 at 930 eV on 2017/08/08
            elif pgmGratingSelect.getPosition()=="VPG3":
                gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/10/09
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>690 and Ep<750):
            if pgmGratingSelect.getPosition()=="VPG1":
                gap = 12.1996757 + 0.01755656*Ep #Corrected for VPG1 on 2017/02/15
                #raise Exception("No calibration available for VPG1 in LV mode")
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap = 12.2144937 + 0.01746779*Ep  #Corrected for VPG2 on 2017/11/30
            elif pgmGratingSelect.getPosition()=="VPG3":
                #gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/09/20
                raise Exception("No calibration available for VPG1 in LV mode")
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        elif (Ep>=820 and Ep<=910):
            if pgmGratingSelect.getPosition()=="VPG1":
                #gap = 12.1996757 + 0.01755656*Ep #Corrected for VPG1 on 2017/02/15
                raise Exception("No calibration available for VPG1 in LV mode")
            elif pgmGratingSelect.getPosition()=="VPG2":
                gap = 11.8230212 + 0.01793526*Ep  #Corrected for VPG2 on 2018/01/10
            elif pgmGratingSelect.getPosition()=="VPG3":
                #gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/09/20
                raise Exception("No calibration available for VPG3 in LV mode")
            else:
                raise ValueError("Unknown Grating select in LV polarisationMode")
        else:
            raise ValueError("Energy demand %feV is outside calibrated ranges") % (Ep)
    # Circular left
    elif polarisation=="CL":
        raise ValueError("CL polarisationMode is not yet implemented")
    
    # Circular right
    elif polarisation=="CR":
        raise ValueError("CR polarisationMode is not yet implemented")
    
    # Linear 
    elif polarisation=="L1":
        raise ValueError("L1 polarisationMode is not yet implemented")
 
    # Unsupported        
    else:
        raise ValueError("Unsupported polarisationMode mode")
       
    if (gap<20 or gap>70):
        raise ValueError("Required Soft X-Ray ID idgap is out side allowable bound (20, 70)!")
    return gap
