from time import sleep

samXYposns = {"spin":[-4.5,144.785],
              "out":[15.,144.785]}

def ee15676_collection_01():
    spinOn
    eh3close
    samSelect("spin")
    peCollectDark(600,"001_dark_60x10s")
    d1in
    eh3open
    peCollectData(600,"002_Si_SRM640c_60x10s")
    eh3close

def ee15676_collection_02():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"003_EmptyXPDF_60x10s")
    eh3close
    peMonitorStability()

def ee15676_collection_03():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"004_Glassy_ZIF-4_60x10s")
    eh3close
    spinOff
    peMonitorStability(preWait=10)

def ee15676_collection_04():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"005_Empty_Capillary_60x10s")
    eh3close
    spinOff
    peMonitorStability(preWait=10)
    
def ee15676_collection_05():
    spinOn
    eh3close
    peCollectDark(600,"006_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"007_BM_ZIF-4_60x10s")
    eh3close
    spinOff
    peMonitorStability(preWait=20)
    
def ee15676_collection_06():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"008_TIA_ZIF-4_60x10s")
    eh3close
    spinOff
    peMonitorStability(preWait=20)
    
def ee15676_collection_07():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"009_Katoite_exGEM_60x10s")
    eh3close
    spinOff
    peMonitorStability(preWait=20)
    
def ee15676_collection_08():
    peCollectDark(600,"010_dark_60x10s")
    
def ee15676_collection_09():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"009_Katoite_exGEM_90p1K_60x10s")
    eh3close
    spinOff
    peMonitorStability(preWait=20)
    
def ee15676_collection_10():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"010_Katoite_exGEM_100p0K_60x10s")
    eh3close
    peMonitorStability(preWait=20)
    
def ee15676_collection_11():
    spinOn
    eh3close
    peCollectDark(600,"011_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"012_Katoite_exGEM_110p0K_60x10s")
    eh3close
    peMonitorStability(preWait=20)

def ee15676_collection_12():
    spinOn
    eh3close
    peCollectDark(600,"013_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"014_Katoite_exGEM_120p0K_60x10s")
    eh3close
    peMonitorStability(preWait=20)

def ee15676_collection_13():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"015_Katoite_exGEM_150p0K_60x10s")
    eh3close
    peMonitorStability(preWait=20)

def ee15676_collection_14():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"016_Katoite_exGEM_220p0K_60x10s")
    eh3close
    peMonitorStability(preWait=20)

def ee15676_collection_15():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"017_Empty_Capillary_120p0K_60x10s")
    eh3close
    peMonitorStability(preWait=20)
    
def ee15676_collection_16():
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"018_Empty_Capillary_91K_60x10s")
    eh3close
    peMonitorStability(preWait=20)
    
    
print "ee15676 scripts loaded"
