import subprocess
def makeLinks(scanNumber, lastImage, firstImage=2,visit="mt8511-1"):
    """
    Command to make soft links for of projections into current folder
    scanNumber - the scan number e.g. 510
    lastImage   - last image number 
    firstImage - first image number. default(2)
    visit - your visit to I13 default(mt8511-1)
    """
    for i in range(firstImage,lastImage+1):
		filename="pco1"+`scanNumber` + ("-%05d.tif" % (i-firstImage))
		cmd="ln -s /dls/i13/data/2012/" + visit + "/" + `scanNumber` + "/pco1/"+filename + " " + filename
		subprocess.call(cmd, shell=True)



makeLinks(scanNumber=513, lastImage=1202, firstImage=2,visit="mt5811-1")
