from gda.configuration.properties import LocalProperties
from gda.observable import IObserver
from gdaserver import ncddetectors, eh_shutter, det_shutter
from uk.ac.gda.server.ncd.plotting import DetectorRates

class DetGuard(IObserver):
    def __init__(self, detsys, *shutters):
        self.detsys = detsys
        self.limits = {}
        self.checks = {"peak" : (lambda x: x.maxCounts/x.countingTime),
                  "peakcounts" : (lambda x: x.maxCounts),
                  "sum" : (lambda x: x.integratedCounts/x.countingTime) }
        self.severities = {"hard" : self.hardAction, "soft" : self.softAction }
        self.shutters = shutters
        self.detsys.addIObserver(self)
        
    def update(self, observed, message):
        try:
            for rate in message:
                detname = rate.detName
                for type in self.checks.keys():
                    for severity in self.severities.keys():
                        if detname+type+severity in self.limits:
                            current_value = self.checks[type](rate)
                            limit = self.limits[detname+type+severity]
                            if current_value > limit:
                                self.severities[severity](detname, current_value, limit, rate.highCounts)
        except:
            pass
        
    def softAction(self, message, current_value, limit, *other):
        print "INFO: detector %s is operating close to the maximum allowed count rate (current value %g, limit %g)" % (message, current_value, limit)
        
    def hardAction(self, message, current_value, limit, high_counts=()):
        print "ERROR: count rate %g exceeds limit %g on detector %s intolerable, closing shutter" % (current_value, limit, message)
        if (high_counts):
            print "High count pixels: " + ', '.join(str(hc) for hc in high_counts)
        for shutter in self.shutters:
            shutter("Close")


DETGUARD_CREATED_PROPERTY = 'i22.rate.detguard.created'
if not LocalProperties.check(DETGUARD_CREATED_PROPERTY):
    detguard=DetGuard(ncddetectors, eh_shutter, det_shutter)

    P2M_LIMIT = 1000000

    DetectorRates.setThreshold("Pilatus2M_SAXS", P2M_LIMIT)
    DetectorRates.setThreshold("Pilatus2M_WAXS", P2M_LIMIT)

    detguard.limits["Pilatus2M_SAXSpeakcountssoft"] = 0.75*P2M_LIMIT
    detguard.limits["Pilatus2M_SAXSpeakcountshard"] = P2M_LIMIT

    detguard.limits["Pilatus2M_WAXSpeakcountssoft"]= 0.75*P2M_LIMIT
    detguard.limits["Pilatus2M_WAXSpeakcountshard"]= P2M_LIMIT

    LocalProperties.set(DETGUARD_CREATED_PROPERTY, "True")
