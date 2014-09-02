from beamline.average import Average

d2camtotal=DisplayEpicsPVClass('d2camtotal', 'BL05I-DI-PHDGN-02:DCAM:STAT:Total_RBV', '', '%5.5g')
d3camtotal=DisplayEpicsPVClass('d3camtotal', 'BL05I-DI-PHDGN-03:DCAM:STAT:Total_RBV', '', '%5.5g')
dj6camtotal=DisplayEpicsPVClass('dj6camtotal', 'BL05J-DI-PHDGN-01:DCAM:STAT:Total_RBV', '', '%5.5g')
d6camtotal=DisplayEpicsPVClass('d6camtotal', 'BL05I-DI-PHDGN-06:DCAM:STAT:Total_RBV', '', '%5.5g')
d5camtotal=DisplayEpicsPVClass('d5camtotal', 'BL05I-DI-PHDGN-05:DCAM:STAT:Total_RBV', '', '%5.5g')
DiagOntotal=DisplayEpicsPVClass('DiagOntotal', 'BL05I-DI-PHDGN-91:DCAM:STAT:Total_RBV', '', '%5.5g')
average_d7current=Average("average_d7current", d7current)
average_dj7current=Average("average_dj7current", dj7current)
average_d3current=Average("average_d3current", d3current)