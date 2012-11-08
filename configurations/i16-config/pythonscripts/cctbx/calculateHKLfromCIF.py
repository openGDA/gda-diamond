import sys
import re

from cctbx import uctbx
from cctbx import xray
from cctbx import crystal
from cctbx.array_family import flex


from PyCifRW.CifFile import CifFile
from cctbx.uctbx import unit_cell

from cctbx.sgtbx import space_group
from cctbx.sgtbx import space_group_symbols
from cctbx import sgtbx


def read_cif_return_cell_plus_scatterers(cif_file):
     
        cif_file = CifFile(cif_file)
        for k in cif_file.dictionary:
            cif_global = cif_file[k]
            break
        unit_cell = [cif_global[param]
                for param in [
                "_cell_length_a", "_cell_length_b", "_cell_length_c",
                "_cell_angle_alpha", "_cell_angle_beta", "_cell_angle_gamma"]]
        space_group_info = sgtbx.space_group_info(
                 symbol=cif_global["_symmetry_space_group_name_H-M"])
        
        # regex to remove standard error on unit cell dimentions
        i = 0
        numre = re.compile('(\d+\.\d+)(\(\d+\))')
        
        for value in unit_cell:
            numre_match = numre.match(value)
            if(numre_match != None):
                unit_cell[i] = float(numre_match.group(1))
            else:
                unit_cell[i] = float(value)
            i += 1
        uc = uctbx.unit_cell(unit_cell)
        crystal_symmetry = crystal.symmetry(
                unit_cell=uc,
                space_group_info=space_group_info)       
        structure = xray.structure(crystal_symmetry=crystal_symmetry)
        coord_list = []
        for label, x, y, z, so in zip(cif_global["_atom_site_label"],
                                   cif_global["_atom_site_fract_x"],
                                   cif_global["_atom_site_fract_y"],
                                   cif_global["_atom_site_fract_z"],
                                   cif_global["_atom_site_occupancy"]):
               coord_list.append(xray.scatterer(label=label, site=[float(s) for s in [x, y, z]], u=float(so)))
        scatterers = flex.xray_scatterer(coord_list)
        return   structure, scatterers

if __name__ == '__main__':
        structure, scatterer = read_cif_return_cell_plus_scatterers(sys.argv[1])
        wavelength = float(sys.argv[2])
        
        xrayStructure = xray.structure(structure, scatterer)
        xrayStructure.expand_to_p1()
        
        f_calc = xrayStructure.structure_factors(anomalous_flag=True, d_min=wavelength / 2).f_calc()
        f_calc.show_summary().show_array()

