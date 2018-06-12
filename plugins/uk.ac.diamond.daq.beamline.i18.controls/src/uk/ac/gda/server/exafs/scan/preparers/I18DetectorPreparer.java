package uk.ac.gda.server.exafs.scan.preparers;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.jython.InterfaceProvider;
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
import uk.ac.gda.server.exafs.scan.QexafsDetectorPreparer;

public class I18DetectorPreparer implements QexafsDetectorPreparer {

	private static final Logger logger = LoggerFactory.getLogger(I18DetectorPreparer.class);

	private final Scannable[] sensitivities;
	private final Scannable[] sensitivityUnits;
	private final TfgScalerWithFrames counterTimer01;

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;
	private BufferedDetector qexafsCounterTimer01;
	private Xspress3BufferedDetector qexafsXspress3;
	private Xspress3 xspress3;
	private Xspress3FFoverI0BufferedDetector qexafsFFI0Xspress3;

	public I18DetectorPreparer(Scannable[] sensitivities, Scannable[] sensitivityUnits, TfgScalerWithFrames ionchambers,
			Xspress3 xspress3, BufferedDetector qexafsCounterTimer01,
			Xspress3BufferedDetector qexafsXspress3,
			Xspress3FFoverI0BufferedDetector qexafsFFI0Xspress3) {
		this.sensitivities = sensitivities;
		this.sensitivityUnits = sensitivityUnits;
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
			controlIonc(ionChambersBean, index);
		}
	}

	private void controlIonc(List<IonChamberParameters> ionChambersBean, int ionChamberNum) throws DeviceException {
		IonChamberParameters ionChamber = ionChambersBean.get(ionChamberNum);
		setupAmpSensitivity(ionChamber, ionChamberNum);
	}

	private void setupAmpSensitivity(IonChamberParameters ionChamberParams, int index) throws DeviceException {
		if (ionChamberParams.getChangeSensitivity()) {
			if (ionChamberParams.getGain() == null || ionChamberParams.getGain().equals("")) {
				return;
			}

			try {
				InterfaceProvider.getTerminalPrinter().print(
						"Changing sensitivity of " + ionChamberParams.getName() + " to " + ionChamberParams.getGain());
				String[] gain = ionChamberParams.getGain().split(" ");
				sensitivities[index].moveTo(gain[0]);
				sensitivityUnits[index].moveTo(gain[1]);
			} catch (DeviceException e) {
				logger.error("Exception while trying to change the sensitivity of ion chamber {}", ionChamberParams.getName(), e);
				InterfaceProvider
						.getTerminalPrinter()
						.print("Set the ion chamber sensitivity manually, uncheck the box in the Detector Parameters editor and restart the scan");
				InterfaceProvider.getTerminalPrinter().print("Please report this problem to Data Acquisition");
				throw e;
			}
		}
	}

}
