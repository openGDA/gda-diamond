
format = '%3.0f'
cambase = 'BL22I-DI-PHDGN-10:CAM'

d10xmax = DisplayEpicsPVClass('d10xmax',cambase+":XMAX",'V', format)
d10ymax = DisplayEpicsPVClass('d10ymax',cambase+":YMAX",'V', format)
