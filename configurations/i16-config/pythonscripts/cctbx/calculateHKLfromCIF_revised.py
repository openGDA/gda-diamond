import sys
from cctbx import xray

if __name__ == '__main__':
        xrayStructure = xray.structure.from_cif(file_path=sys.argv[1])
        wavelength = float(sys.argv[2])
        
        xrayStructure.expand_to_p1()
        
        f_calc = xrayStructure.structure_factors(anomalous_flag=True, d_min=wavelength / 2).f_calc()
        f_calc.show_summary().show_array()

