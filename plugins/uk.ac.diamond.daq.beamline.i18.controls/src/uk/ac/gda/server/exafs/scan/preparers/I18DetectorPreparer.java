package uk.ac.gda.server.exafs.scan.preparers;

import java.util.List;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.devices.detector.xspress3.Xspress3;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;
import uk.ac.gda.devices.detector.xspress3.Xspress3FFoverI0BufferedDetector;
import uk.ac.gda.server.exafs.scan.DetectorPreparerFunctions;
import uk.ac.gda.server.exafs.scan.QexafsDetectorPreparer;

public class I18DetectorPreparer implements QexafsDetectorPreparer {

	private final TfgScalerWithFrames counterTimer01;

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;
	private BufferedDetector qexafsCounterTimer01;
	private Xspress3BufferedDetector qexafsXspress3;
	private Xspress3 xspress3;
	private Xspress3FFoverI0BufferedDetector qexafsFFI0Xspress3;
	private DetectorPreparerFunctions detectorPreparerFunctions = new DetectorPreparerFunctions();

	public I18DetectorPreparer(Scannable[] sensitivities, Scannable[] sensitivityUnits, TfgScalerWithFrames ionchambers,
			Xspress3 xspress3, BufferedDetector qexafsCounterTimer01,
			Xspress3BufferedDetector qexafsXspress3,
			Xspress3FFoverI0BufferedDetector qexafsFFI0Xspress3) {
		detectorPreparerFunctions.setSensitivities(sensitivities);
		detectorPreparerFunctions.setSensitivityUnits(sensitivityUnits);
		this.counterTimer01 = ionchambers;
		this.xspress3 = xspress3;
		this.qexafsXspress3 = qexafsXspress3;
		this.qexafsCounterTimer01 = qexafsCounterTimer01;
		this.qexafsFFI0Xspress3 = qexafsFFI0Xspress3;
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		this.scanBean = scanBean;
		this.detectorBean = detectorBean;

		if (detectorBean.getExperimentType().equals(DetectorParameters.FLUORESCENCE_TYPE)) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getFluorescenceParameters();
			String detType = fluoresenceParameters.getDetectorType();
			String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
			if (detType.compareTo(FluorescenceParameters.XSPRESS3_DET_TYPE) == 0) {
				xspress3.setConfigFileName(xmlFileName);
				xspress3.loadConfigurationFromFile();
			}
		}

		controlAllIonC(detectorBean.getIonChambers());
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		Double[] times = getScanTimeArray();
		if (times.length > 0) {
			counterTimer01.setTimes(times);
		}
	}

	@Override
	public void completeCollection() {
		// nothing here
	}

	@Override
	public BufferedDetector[] getQEXAFSDetectors() throws Exception {
		((BufferedScaler) qexafsCounterTimer01).setTtlSocket(0);
		String exptType = detectorBean.getExperimentType();
		if (exptType.equals(DetectorParameters.TRANSMISSION_TYPE)) {
			return new BufferedDetector[] { qexafsCounterTimer01 };
		}
		// else Fluo
		String detType = detectorBean.getFluorescenceParameters().getDetectorType();
		if (detType.compareTo(FluorescenceParameters.XSPRESS3_DET_TYPE) == 0) {
			return new BufferedDetector[] { qexafsCounterTimer01, qexafsXspress3, qexafsFFI0Xspress3 };
		}
		throw new UnsupportedOperationException("Detector type not supported");
	}

	@Override
	public Detector[] getExtraDetectors() {
		return new Detector[0];
	}

	private Double[] getScanTimeArray() throws Exception {
		if (scanBean instanceof XasScanParameters) {
			return ExafsScanPointCreator.getScanTimeArray((XasScanParameters) scanBean);
		} else if (scanBean instanceof XanesScanParameters) {
			return XanesScanPointCreator.getScanTimeArray((XanesScanParameters) scanBean);
		}
		return new Double[0];
	}

	private void controlAllIonC(List<IonChamberParameters> ionChambersBean) throws DeviceException {
		for (int index = 0; index < ionChambersBean.size(); index++) {
			detectorPreparerFunctions.setupAmplifierSensitivity(ionChambersBean.get(index), index);
		}
	}
}
