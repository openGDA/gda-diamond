from gda.device.detector.mythen.client import TextClientMythenClient
from gda.device.detector.mythen import MythenDetectorImpl

mythen_client = TextClientMythenClient()
mythen_client.setHost("i11-mcs01")

mythen = MythenDetectorImpl()
mythen.setMythenClient(mythen_client)

print "done - Mythen detector is 'mythen'"
