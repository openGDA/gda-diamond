from uk.ac.gda.beans.vortex import DetectorDeadTimeElement
from uk.ac.gda.beans.xspress import XspressDeadTimeParameters
from uk.ac.gda.util.beans.xml import XMLHelpers

# Return DetectorDeadTimeElement object containing deadtime correction parameters for channel of detector
# of Xspress3X, Xspress4 detector
def getDtcParams(basePv, channel): 
    allGoodGradName="C%d_DTC_AEG_RBV"
    allGoodOffsetName="C%d_DTC_AEO_RBV"
    inWindowGradientName="C%d_DTC_IWG_RBV"
    inWindowOffsetName="C%d_DTC_IWO_RBV"

    allGoodGradient = caget(basePv+allGoodGradName%(channel))
    allGoodOffset = caget(basePv+allGoodOffsetName%(channel))
    inWindowGrad = caget(basePv+inWindowGradientName%(channel))
    inWindowOffset = caget(basePv+inWindowOffsetName%(channel))
    
    print "Channel %d : %s  %s  %s  %s"%(channel, allGoodGradient, allGoodOffset ,inWindowGrad, inWindowOffset)
    
    return DetectorDeadTimeElement("Element"+str(channel-1), channel-1, float(allGoodGradient), float(allGoodOffset), float(inWindowOffset),  float(inWindowGrad))

# Collect deadtime correction parameters for all channels of a detector by
# calling getDtcParams(...) function in a loop
# Return XspressDeadTimeParameters object, containing list of DetectorDeadTimeElements, one for each channell of detector
def getAllDtcParams(basePv, numChannels) :
    
    allDeadtimeParameters = XspressDeadTimeParameters()
    
    for i in range(1, numChannels+1) :
        dtcParamsForChannel = getDtcParams(basePv, i)
        allDeadtimeParameters.addDetectorDeadTimeElement(dtcParamsForChannel)
        
    return allDeadtimeParameters

# Convert XspressDeadTimeParameters to XML string    
def createXmlString(allDtcParams): 
    return XMLHelpers.toXMLString(XspressDeadTimeParameters.mappingURL, allDtcParams)