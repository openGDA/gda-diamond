from gdaserver import ecva1, ecva2, ecva3, ecva4, ecva5, ecva6, ecva7, ecva8, ecva9, ecva10

VALVES = {
    1: ecva1,
    2: ecva2,
    3: ecva3,
    4: ecva4,
    5: ecva5,
    6: ecva6,
    7: ecva7,
    8: ecva8,
    9: ecva9,
    10: ecva10,
          }


def openvalve(valve_num, opening_time):
    valve = VALVES[valve_num]
    pos(valve, "Open")
    sleep(opening_time)
    pos(valve, "Close")


def closevalve(valve_num):
    valve = VALVES[valve_num]
    pos(valve, "Close")

alias(openvalve)
alias(closevalve)
