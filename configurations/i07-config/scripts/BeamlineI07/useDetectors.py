
#The ADC Card
from Diamond.PseudoDevices.AdcScaler import AdcScalerClass, AdcScalerChannelClass;


pvRootScaler   = "BL07I-EA-ADC-01";

adc = AdcScalerClass('adc',pvRootScaler);
ionc1 = AdcScalerChannelClass('ionc1',pvRootScaler, channel=0);
ionsc1=ionc1;

adc2 = AdcScalerChannelClass('adc2',pvRootScaler, channel=1);
adc3 = AdcScalerChannelClass('adc3',pvRootScaler, channel=2);
adc4 = AdcScalerChannelClass('adc4',pvRootScaler, channel=3);
adc5 = AdcScalerChannelClass('adc5',pvRootScaler, channel=4);
adc6 = AdcScalerChannelClass('adc6',pvRootScaler, channel=5);
adc7 = AdcScalerChannelClass('adc7',pvRootScaler, channel=6);
adc8 = AdcScalerChannelClass('adc8',pvRootScaler, channel=7);

DEFAULT_LEVEL = 100

ionc1.setLevel(DEFAULT_LEVEL)
adc2.setLevel(DEFAULT_LEVEL)
adc3.setLevel(DEFAULT_LEVEL)
adc4.setLevel(DEFAULT_LEVEL)
adc5.setLevel(DEFAULT_LEVEL)
adc6.setLevel(DEFAULT_LEVEL)
adc7.setLevel(DEFAULT_LEVEL)
adc8.setLevel(DEFAULT_LEVEL)



#The Struct Scaler Card
from Diamond.PseudoDevices.StruckScaler import StructScalerGdaClass, StructScalerGdaChannelClass;
from Diamond.PseudoDevices.Scaler8512DirectPV import ScalerChannelEpicsPVClass;

eh1sc = StructScalerGdaClass("eh1sc", struck1);

cttime = StructScalerGdaChannelClass("cttime", struck1, 0);
cyber = StructScalerGdaChannelClass("cyber", struck1, 1);
cyber.addShutter('fs')
apd = StructScalerGdaChannelClass("apd", struck1, 2);
apd.addShutter('fs');


eh1sc1 = cttime;
eh1sc2 = cyber;
eh1sc3 = apd;

eh1sc01 = StructScalerGdaChannelClass("eh1sc01", struck1, 0);
eh1sc02 = StructScalerGdaChannelClass("eh1sc02", struck1, 1);
eh1sc03 = StructScalerGdaChannelClass("eh1sc03", struck1, 2);
eh1sc04 = StructScalerGdaChannelClass("eh1sc04", struck1, 3);
eh1sc05 = StructScalerGdaChannelClass("eh1sc05", struck1, 4);
eh1sc06 = StructScalerGdaChannelClass("eh1sc06", struck1, 5);
eh1sc07 = StructScalerGdaChannelClass("eh1sc07", struck1, 6);
eh1sc08 = StructScalerGdaChannelClass("eh1sc08", struck1, 7);
eh1sc09 = StructScalerGdaChannelClass("eh1sc09", struck1, 8);
eh1sc10 = StructScalerGdaChannelClass("eh1sc10", struck1, 9);
eh1sc11 = StructScalerGdaChannelClass("eh1sc11", struck1, 10);
eh1sc12 = StructScalerGdaChannelClass("eh1sc12", struck1, 11);
eh1sc13 = StructScalerGdaChannelClass("eh1sc13", struck1, 12);
eh1sc14 = StructScalerGdaChannelClass("eh1sc14", struck1, 13);
eh1sc15 = StructScalerGdaChannelClass("eh1sc15", struck1, 14);
eh1sc16 = StructScalerGdaChannelClass("eh1sc16", struck1, 15);
eh1sc17 = StructScalerGdaChannelClass("eh1sc17", struck1, 16);
eh1sc18 = StructScalerGdaChannelClass("eh1sc18", struck1, 17);
eh1sc19 = StructScalerGdaChannelClass("eh1sc19", struck1, 18);
eh1sc20 = StructScalerGdaChannelClass("eh1sc20", struck1, 19);
eh1sc21 = StructScalerGdaChannelClass("eh1sc21", struck1, 20);
eh1sc22 = StructScalerGdaChannelClass("eh1sc22", struck1, 21);
eh1sc23 = StructScalerGdaChannelClass("eh1sc23", struck1, 22);
eh1sc24 = StructScalerGdaChannelClass("eh1sc24", struck1, 23);
eh1sc25 = StructScalerGdaChannelClass("eh1sc25", struck1, 24);
eh1sc26 = StructScalerGdaChannelClass("eh1sc26", struck1, 25);
eh1sc27 = StructScalerGdaChannelClass("eh1sc27", struck1, 26);
eh1sc28 = StructScalerGdaChannelClass("eh1sc28", struck1, 27);
eh1sc29 = StructScalerGdaChannelClass("eh1sc29", struck1, 28);
eh1sc30 = StructScalerGdaChannelClass("eh1sc30", struck1, 29);
eh1sc31 = StructScalerGdaChannelClass("eh1sc31", struck1, 30);
eh1sc32 = StructScalerGdaChannelClass("eh1sc32", struck1, 31);



#The Cyberstar Scintillation Card and APD device
from Diamond.Objects.EpicsUnit import EpicsApeAceDeviceClass;
from Diamond.Objects.EpicsUnit import EpicsCyberstarScintillationDeviceClass;

cyberstar=EpicsCyberstarScintillationDeviceClass('cyberstar', 'BL07I-EA-CYBER-01');
alias("cyberstar");

apdstar=EpicsApeAceDeviceClass('apdstar', 'BL07I-EA-APD-01');
alias("apdstar");

