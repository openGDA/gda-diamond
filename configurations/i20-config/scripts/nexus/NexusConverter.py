from gda.analysis import ScanFileHolder
from gda.analysis.io import NexusLoader

for i in range(18):
    
    index = 691+i
    path = "/dls/i20/data/2009/0-0/nexus/i20_"+str(index)

    sfh = ScanFileHolder()


    sfh.load(NexusLoader(path+".nxs"))

    s1_voffset_dataset = sfh.getAxis("s1_voffset")
    d3_up_dataset      = sfh.getAxis("d3_up")
    d3_updrain_dataset = sfh.getAxis("d3_updrain")


    file = open(path+".dat", "w")

    file.write("s1_voffset\td3_up\t\td3_updrain\n")

    try:
        for (index, val) in enumerate(s1_voffset_dataset):
            file.write(str(val)+"\t\t"+str(d3_up_dataset[index])+"\t\t"+str(d3_updrain_dataset[index])+"\n");

    finally:
        file.close();
    
    print "Written "+path+".dat"