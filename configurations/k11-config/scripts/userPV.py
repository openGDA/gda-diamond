from gdascripts.pd.epics_pds import EpicsReadWritePVClass

'''
    m1_temp_mask1 = DisplayEpicsPVClass('m1_temp_mask1', 'BL11K-OP-MR-01:TEMP:X1', 'degC', '%.1f')
    m1_temp_mask2 = DisplayEpicsPVClass('m1_temp_mask2', 'BL11K-OP-MR-01:TEMP:X2', 'degC', '%.1f')
    m1_temp_fin1 = DisplayEpicsPVClass('m1_temp_fin1', 'BL11K-OP-MR-01:TEMP:GFNU', 'degC', '%.1f')
    m1_temp_fin2 = DisplayEpicsPVClass('m1_temp_fin2', 'BL11K-OP-MR-01:TEMP:GFND', 'degC', '%.1f') 
   
    m2_temp_mask1 = DisplayEpicsPVClass('m2_temp_mask1', 'BL11K-OP-MR-02:TEMP:X1', 'degC', '%.1f')
    m2_temp_mask2 = DisplayEpicsPVClass('m2_temp_mask2', 'BL11K-OP-MR-02:TEMP:X2', 'degC', '%.1f')   
    
    m3_temp_mask1 = DisplayEpicsPVClass('m3_temp_mask1', 'BL11K-OP-MR-03:TEMP:X1', 'degC', '%.1f')
    m3_temp_mask2 = DisplayEpicsPVClass('m3_temp_mask2', 'BL11K-OP-MR-03:TEMP:X2', 'degC', '%.1f')  
    m3_temp_fin1 = DisplayEpicsPVClass('m3_temp_fin1', 'BL11K-OP-MR-03:TEMP:GFNU', 'degC', '%.1f')
    m3_temp_fin2 = DisplayEpicsPVClass('m3_temp_fin2', 'BL11K-OP-MR-03:TEMP:GFND', 'degC', '%.1f')
   
    m4_temp_mask1 = DisplayEpicsPVClass('m4_temp_mask1', 'BL11K-OP-MR-04:TEMP:X1', 'degC', '%.1f')
    m4_temp_mask2 = DisplayEpicsPVClass('m4_temp_mask2', 'BL11K-OP-MR-04:TEMP:X2', 'degC', '%.1f') 
   ''' 

bsel = EpicsReadWritePVClass('bsel', 'BL11K-MO-BSEL-01:R.VAL', 'mm', '%.1f')