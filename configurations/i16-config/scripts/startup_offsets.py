import pd_offset; reload(pd_offset)

########create new device by adding to this list and move to a position"


# polariser offsets
tthp_detoffset=pd_offset.Offset('tthp_detoffset') 
thp_offset=pd_offset.Offset('thp_offset') 
thp_offset_sigma=pd_offset.Offset('thp_offset_sigma') 
thp_offset_pi=pd_offset.Offset('thp_offset_pi') 
tthp_offset=pd_offset.Offset('tthp_offset')
cry_offset=pd_offset.Offset('cry_offset')
ref_offset=pd_offset.Offset('ref_offset')

#
phi_offset=pd_offset.Offset('phi_offset') 
gam_offset=pd_offset.Offset('gam_offset')



# 
eta_offset=pd_offset.Offset('eta_offset') 
delta_offset=pd_offset.Offset('delta_offset') #used in th2th
mu_offset=pd_offset.Offset('mu_offset') 
#try:
#    # RJW 8/4/11 Namespace confusion: at this point delta is the ScannableMotor, but
#    # what we really need to offset is the delta field in the euler object???
#    delta_axis_offset = pd_offset.Offset('delta_axis_offset', euler.delta)
#except NameError:

delta_axis_offset = pd_offset.Offset('delta_axis_offset', kdelta)
    
idgap_offset=pd_offset.Offset('idgap_offset')
bragg_offset=pd_offset.Offset('bragg_offset')
uharmonic = pd_offset.Offset('Uharmonic'); uharmonic.setOutputFormat(['%.0f'])
dcmharmonic = pd_offset.Offset('DCMharmonic'); dcmharmonic.setOutputFormat(['%.0f'])
ppp_xtal1_111_offset=pd_offset.Offset('ppp_xtal1_111_offset') 
ppp_xtal1_220_offset=pd_offset.Offset('ppp_xtal1_220_offset') 
ppp_xtal1_m220_offset=pd_offset.Offset('ppp_xtal1_m220_offset')
ppp_xtal1_440_offset=pd_offset.Offset('ppp_xtal1_440_offset') 
ppp_xtal2_111_offset=pd_offset.Offset('ppp_xtal2_111_offset') 
ppp_xtal2_220_offset=pd_offset.Offset('ppp_xtal2_220_offset') 


m1y_offset=pd_offset.Offset('m1y_offset') 
m2y_offset=pd_offset.Offset('m2y_offset') 
base_z_offset=pd_offset.Offset('base_z_offset') 
ztable_offset=pd_offset.Offset('ztable_offset') 



delta_virtual=pd_offset.Offset('delta_virtual')
#tthp_detoffset=pd_offset.Offset('tthp_detoffset')

andor_file_number=pd_offset.Offset('andor_file_number')

m2_coating_offset= pd_offset.Offset('m2_coating_offset'); m2_coating_offset.rh=0; m2_coating_offset.si=11;


