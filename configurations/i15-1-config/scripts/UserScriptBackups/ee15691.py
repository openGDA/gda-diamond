from time import sleep
from gda.data import NumTracker

samXYposns = {"spin":[-6.,144.785],
              "empty":[-6.,141.785],
              #"spinDark":[-4.5,144.785],
              #"spinLight":[-13.,144.785]}
              "spinDark":[-4.5,144.785],
              "spinLight":[-12.,144.785]}

def ee15691_collection_01():
    spinOn
    samSelect("spinLight")
    peCollectDark(600,"011_dark_60x10s")
    peCollectData(600,"012_SB-Basolite_LightBlue_60x10s")
    samSelect("spinDark")
    sleep(600)
    peCollectData(600,"013_SB-Basolite_DarkBlue_60x10s")
    
def ee15691_collection_02():
    spinOn
    samSelect("spinLight")
    sleep(300)
    peCollectDark(600,"014_dark_60x10s")
    peCollectData(10,"015_SB-Basolite_LightBlue_1x10s")
    peCollectData(600,"016_SB-Basolite_LightBlue_60x10s")
#     samSelect("spinDark")
#     sleep(600)
#     peCollectData(10,"017_SB-Basolite_DarkBlue_1x10s")
#     peCollectData(600,"018_SB-Basolite_DarkBlue_60x10s")

def ee15691_collection_03():
    spinOn
    samSelect("spinDark")
    #sleep(300)
    eh3close
    peCollectDark(600,"017_dark_60x10s")
    d1in
    eh3open
    peCollectData(600,"018_EmptyCapillary_60x10s")

def ee15691_collection_03():
    spinOn
    samSelect("spinDark")
    #sleep(300)
    eh3close
    peCollectDark(600,"019_dark_60x10s")
    d1in
    eh3open
    peCollectData(600,"020_EmptyXPDF_60x10s")

def ee15691_collection_04():
    spinOn
    samSelect("spinDark")
    d1in
    eh3open
    sleep(10)
    peCollectData(10,"021_SB1-3070_1x10s")
    peCollectData(600,"022_SB1-3070_60x10s")
    spinOff

def ee15691_collection_05():
    spinOn
    samSelect("spinDark")
    eh3close
    peCollectDark(600,"023_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(10,"024_SB2-4060_1x10s")
    peCollectData(600,"025_SB2-4060_60x10s")
    spinOff
    eh3close

def ee15691_collection_06():
    spinOn
    samSelect("spinDark")
    #eh3close
    #peCollectDark(600,"023_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(10,"026_SB3-5050_1x10s")
    peCollectData(600,"027_SB3-5050_60x10s")
    spinOff
    eh3close

def ee15691_collection_07():
    spinOn
    samSelect("spinDark")
    #eh3close
    #peCollectDark(600,"023_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(10,"028_SB4-5545_1x10s")
    peCollectData(600,"029_SB4-5545_60x10s")
    spinOff
    eh3close
    peMonitorStability()

def ee15691_collection_08():
    spinOn
    samSelect("spinDark")
    #eh3close
    #peCollectDark(600,"023_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(10,"030_SB5-6337_1x10s")
    peCollectData(600,"031_SB5-6337_60x10s")
    spinOff
    eh3close
    peMonitorStability()
    
def ee15691_collection_09():
    spinOn
    samSelect("spinDark")
    #eh3close
    #peCollectDark(600,"023_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(10,"032_SB6-8020_1x10s")
    peCollectData(600,"033_SB6-8020_60x10s")
    spinOff
    eh3close
    peMonitorStability(preWait=10)

def ee15691_collection_10():
    spinOn
    samSelect("spinDark")
    eh3close
    peCollectDark(600,"034_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(10,"035_SB7-100Et_1x10s")
    peCollectData(600,"036_SB7-100Et_60x10s")
    spinOff
    eh3close
    peMonitorStability(preWait=10)

def ee15691_collection_11():
    spinOn
    samSelect("spinDark")
    #eh3close
    #peCollectDark(600,"034_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(10,"037_SB8-Cuace_1x10s")
    peCollectData(600,"038_SB8-Cuace_60x10s")
    spinOff
    eh3close
    peMonitorStability(preWait=10)
print "ee15691 scripts loaded"
