

#Example images from : "/dls/i06/data/2010/si0/28431_UViewImage" or "/home/xr56/testData/28431_UViewImage/"

from gda.analysis import RCPPlotter
import scisoftpy.plot as dpl

run "scisoft/peem_analysis"

pp=RCPPlotter()
sourceDir = "/dls/i06/tmp/test"
targetDir = "/dls/i06/tmp/test"

#To load image
#pp.scanForImages("Image Explorer", "/dls/i06/data/2010/cm1895-1/demoImages")
#pp.scanForImages("Image Explorer", sourceDir)

load_peem(sourceDir);

#Users need to select the images and send them to server.
[cdMap, positiveImage, negativeImage, averageImages] = process_peem(targetDir)


#to plot cd map
dpl.image(cdMap, name="PEEM Image")

#to plot the positive image
dpl.image(positiveImage, name="PEEM Image")

#to plot the negative image
dpl.image(negativeImage, name="PEEM Image")

#to plot the average images
dpl.image(averageImages[0], name="PEEM Image")
dpl.image(averageImages[1], name="PEEM Image")
dpl.image(averageImages[2], name="PEEM Image")
dpl.image(averageImages[3], name="PEEM Image")


