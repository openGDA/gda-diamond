from mock import Mock
from exafsscripts.exafs.b18SamplePreparer import B18SamplePreparer
from gda.device import Scannable
from uk.ac.gda.beans.exafs.b18 import B18SampleParameters, XYThetaStageParameters, LN2CryoStageParameters, SXCryoStageParameters, PulseTubeCryostatParameters
import unittest
from gda.device.scannable import PulseTube

class TestB18SamplePreparer(unittest.TestCase):
    
    def setUp(self):
        self.mock_xytheta_scannable = Mock(spec=Scannable)
        self.mock_ln2cryo_scannable = Mock(spec=Scannable)
        self.mock_sxcryo_scannable = Mock(spec=Scannable)
        self.mock_lakeshore_scannable = Mock(spec=Scannable)
        self.mock_furnace_scannable = Mock(spec=Scannable)
        self.mock_pulsetube_scannable = Mock(spec=PulseTube)
        self.mock_xytheta_scannable.name = "mock_xytheta_scannable"
        self.mock_ln2cryo_scannable.name = "mock_ln2cryo_scannable"
        self.mock_sxcryo_scannable.name = "mock_sxcryo_scannable"
        self.mock_lakeshore_scannable.name = "mock_lakeshore_scannable"
        self.mock_pulsetube_scannable.name = "mock_pulsetube_scannable"
        self.sp = B18SamplePreparer(self.mock_sxcryo_scannable, self.mock_xytheta_scannable, self.mock_ln2cryo_scannable, self.mock_lakeshore_scannable, self.mock_furnace_scannable, self.mock_pulsetube_scannable)
        self.sp.setLoggingEnabled(False)
        
    def testPrepareXyThetaStage(self):
        mockXYTBean = Mock(spec=XYThetaStageParameters)
        mockXYTBean.getX.return_value = 1
        mockXYTBean.getY.return_value = 2
        mockXYTBean.getTheta.return_value = 3
        
        mockSpBean = Mock(spec=B18SampleParameters)
        mockSpBean.getStage.return_value = "xythetastage"
        mockSpBean.getXYThetaStageParameters.return_value = mockXYTBean
        
        self.sp.prepare(mockSpBean)
        self.mock_xytheta_scannable.assert_called_with([1,2,3])
        
    def testPrepareLn2CryoStage(self):
        mockLN2Bean = Mock(spec=LN2CryoStageParameters)
        mockLN2Bean.getHeight.return_value = 1
        mockLN2Bean.getAngle.return_value = 2
        
        mockSpBean = Mock(spec=B18SampleParameters)
        mockSpBean.getStage.return_value = "ln2cryostage"
        mockSpBean.getLN2CryoStageParameters.return_value = mockLN2Bean
        
        self.sp.prepare(mockSpBean)
        self.mock_ln2cryo_scannable.assert_called_with([1,2])
        
    def testPrepareSxCryoStage(self):
        mockSXCryoBean = Mock(spec=SXCryoStageParameters)
        mockSXCryoBean.getHeight.return_value = 1
        mockSXCryoBean.getRot.return_value = 2
        
        mockSpBean = Mock(spec=B18SampleParameters)
        mockSpBean.getStage.return_value = "sxcryostage"
        mockSpBean.getSXCryoStageParameters.return_value = mockSXCryoBean
        
        self.sp.prepare(mockSpBean)
        self.mock_sxcryo_scannable.assert_called_with([1,2])
        
    def testPulsetube(self):
        mockPulsetubeBean = Mock(spec=PulseTubeCryostatParameters)
        mockPulsetubeBean.getSetPoint.return_value = 1
        mockPulsetubeBean.getTolerance.return_value = 1
        
        self.mock_pulsetube_scannable.getPosition.return_value = [1,2,3,4,5,6,7,8,9,10,11,12]
        
        mockPulsetubeBean.isControlFlag.return_value = False
        mockSpBean = Mock(spec=B18SampleParameters)
        mockSpBean.getTemperatureControl.return_value = "pulsetubecryostat"
        mockSpBean.getPulseTubeCryostatParameters.return_value = mockPulsetubeBean
        
        self.sp.prepare(mockSpBean)
        print self.mock_pulsetube_scannable.method_calls
    
    