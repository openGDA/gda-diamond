'''
Created on 1 Dec 2025

@author: fy65
'''
import __main__  # @UnresolvedImport
from gdascripts.utils import caput
from time import sleep
from gda.jython.commands.GeneralCommands import alias

print('\n')
print("-"*80)
print("load commands to setup zacscan detector PVs:")
print("      switch_to_magnet_pvs_for_zacscan")
print("      switch_to_xabs_or_dd_pvs_for_zacscan")
print("\n")

idd_dd_xabs_pv_map = {"det1": ("BL06J-MO-FSCAN-01:DET1:PV", "BL06J-EA-USER-01:SC1-RAW"),
          "det2": ("BL06J-MO-FSCAN-01:DET2:PV", "BL06J-EA-USER-01:SC2-RAW"),
          "det3": ("BL06J-MO-FSCAN-01:DET3:PV", "BL06J-EA-USER-01:SC3-RAW"),
          "det4": ("BL06J-MO-FSCAN-01:DET4:PV", "BL06J-EA-USER-01:SC4-RAW"),
          "det5": ("BL06J-MO-FSCAN-01:DET5:PV", "BL06I-OP-IDD-01:ENERGY.RBV"),
          "det6": ("BL06J-MO-FSCAN-01:DET6:PV", "BL06I-OP-PGM-01:ENERGY.RBV"),
          "det7": ("BL06J-MO-FSCAN-01:DET7:PV", "BL06J-EA-USER-01:SC5-RAW"),
          "det8": ("BL06J-MO-FSCAN-01:DET8:PV", "BL06J-EA-USER-01:SC6-RAW")
          }

idd_magnet_pv_map = {"det1": ("BL06J-MO-FSCAN-01:DET1:PV", "BL06J-EA-MAG-01:TEYC-RAW"),
          "det2": ("BL06J-MO-FSCAN-01:DET2:PV", "BL06J-EA-USER-01:SC2-RAW"),
          "det3": ("BL06J-MO-FSCAN-01:DET3:PV", "BL06J-EA-MAG-01:FDUC-RAW"),
          "det4": ("BL06J-MO-FSCAN-01:DET4:PV", "BL06J-EA-MAG-01:FDDC-RAW"),
          "det5": ("BL06J-MO-FSCAN-01:DET5:PV", "BL06I-OP-IDD-01:ENERGY.RBV"),
          "det6": ("BL06J-MO-FSCAN-01:DET6:PV", "BL06I-OP-PGM-01:ENERGY.RBV"),
          "det7": ("BL06J-MO-FSCAN-01:DET7:PV", "BL06J-EA-MAG-01:90DC-RAW"),
          "det8": ("BL06J-MO-FSCAN-01:DET8:PV", "BL06J-EA-MAG-01:FIELDC-RAW")
          }

idu_dd_xabs_pv_map = {"det1": ("BL06J-MO-FSCAN-02:DET1:PV", "BL06J-EA-USER-01:SC1-RAW"),
          "det2": ("BL06J-MO-FSCAN-02:DET2:PV", "BL06J-EA-USER-01:SC2-RAW"),
          "det3": ("BL06J-MO-FSCAN-02:DET3:PV", "BL06J-EA-USER-01:SC3-RAW"),
          "det4": ("BL06J-MO-FSCAN-02:DET4:PV", "BL06J-EA-USER-01:SC4-RAW"),
          "det5": ("BL06J-MO-FSCAN-02:DET5:PV", "BL06I-OP-IDU-01:ENERGY.RBV"),
          "det6": ("BL06J-MO-FSCAN-02:DET6:PV", "BL06I-OP-PGM-01:ENERGY.RBV"),
          "det7": ("BL06J-MO-FSCAN-02:DET7:PV", "BL06J-EA-USER-01:SC5-RAW"),
          "det8": ("BL06J-MO-FSCAN-02:DET8:PV", "BL06J-EA-USER-01:SC6-RAW")
          }

idu_magnet_pv_map = {"det1": ("BL06J-MO-FSCAN-02:DET1:PV", "BL06J-EA-MAG-01:TEYC-RAW"),
          "det2": ("BL06J-MO-FSCAN-02:DET2:PV", "BL06J-EA-USER-01:SC2-RAW"),
          "det3": ("BL06J-MO-FSCAN-02:DET3:PV", "BL06J-EA-MAG-01:FDUC-RAW"),
          "det4": ("BL06J-MO-FSCAN-02:DET4:PV", "BL06J-EA-MAG-01:FDDC-RAW"),
          "det5": ("BL06J-MO-FSCAN-02:DET5:PV", "BL06I-OP-IDU-01:ENERGY.RBV"),
          "det6": ("BL06J-MO-FSCAN-02:DET6:PV", "BL06I-OP-PGM-01:ENERGY.RBV"),
          "det7": ("BL06J-MO-FSCAN-02:DET7:PV", "BL06J-EA-MAG-01:90DC-RAW"),
          "det8": ("BL06J-MO-FSCAN-02:DET8:PV", "BL06J-EA-MAG-01:FIELDC-RAW")
          }

def switch_to_magnet_pvs_for_zacscan():
    if str(__main__.smode.getPosition()) == "idd":
        for pv, value in idd_magnet_pv_map.values():
            caput(pv, value)
            sleep(0.1)
    elif str(__main__.smode.getPosition()) == "idu":
        for pv, value in idu_magnet_pv_map.values():
            caput(pv, value)
            sleep(0.1)
    else:
        print("\nzacscan is not supported in smode %s\n" % str(__main__.smode.getPosition()))

alias("switch_to_magnet_pvs_for_zacscan")
 
def switch_to_xabs_or_dd_pvs_for_zacscan():
    if str(__main__.smode.getPosition()) == "idd":
        for pv, value in idd_dd_xabs_pv_map.values():
            caput(pv, value)
            sleep(0.1)
    elif str(__main__.smode.getPosition()) == "idu":
        for pv, value in idu_dd_xabs_pv_map.values():
            caput(pv, value)
            sleep(0.1)
    else:
        print("\nzacscan is not supported in smode %s\n" % str(__main__.smode.getPosition()))

alias("switch_to_xabs_or_dd_pvs_for_zacscan")

if __name__ == '__main__':
    pass