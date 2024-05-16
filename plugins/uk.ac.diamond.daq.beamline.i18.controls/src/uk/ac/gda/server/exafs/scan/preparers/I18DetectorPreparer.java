package uk.ac.gda.server.exafs.scan.preparers;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.factory.Finder;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.devices.detector.FluorescenceDetector;
import uk.ac.gda.devices.detector.FluorescenceDetectorParameters;
import uk.ac.gda.server.exafs.scan.DetectorPreparerFunctions;
import uk.ac.gda.server.exafs.scan.QexafsDetectorPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class I18DetectorPreparer implements QexafsDetectorPreparer {

	private final TfgScalerWithFrames counterTimer01;

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;
	private BufferedDetector qexafsCounterTimer01;
	private DetectorPreparerFunctions detectorPreparerFunctions = new DetectorPreparerFunctions();
	private Map<String, List<BufferedDetector>> qexafsDetectorsMap = new HashMap<>();

	public I18DetectorPreparer(Scannable[] sensitivities, Scannable[] sensitivityUnits, TfgScalerWithFrames ionchambers,
			BufferedDetector qexafsCounterTimer01) {
		detectorPreparerFunctions.setSensitivities(sensitivities);
		detectorPreparerFunctions.setSensitivityUnits(sensitivityUnits);
		this.counterTimer01 = ionchambers;
		this.qexafsCounterTimer01 = qexafsCounterTimer01;
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		this.scanBean = scanBean;
		this.detectorBean = detectorBean;

		if (detectorBean.getExperimentType().equals(DetectorParameters.FLUORESCENCE_TYPE)) {
			// Get the fluorescence detector parameters bean
			FluorescenceParameters fluorescenceParameters = detectorBean.getFluorescenceParameters();
			FluorescenceDetectorParameters params = (FluorescenceDetectorParameters) XMLHelpers.getBeanObject(experimentFullPath, fluorescenceParameters.getConfigFileName());

			// Check the detector object referenced by the bean exists on the server
			String detName = params.getDetectorName();
			FluorescenceDetector detObject = Finder.findOptionalOfType(detName, FluorescenceDetector.class).orElse(null);

			if (detObject == null) {
				String xmlFileName = experimentFullPath + fluorescenceParameters.getConfigFileName();
				throw new IllegalArgumentException("Cannot configure detector using "+xmlFileName+" : No server side object called "+detName+" can be found!");
			}

			// Configure the detector
			detObject.applyConfigurationParameters(params);
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
		if (!qexafsDetectorsMap.containsKey(detType) ) {
			throw new UnsupportedOperationException("Detector type "+detType+" not supported");
		}
		return qexafsDetectorsMap.get(detType).toArray(new BufferedDetector[] {});
	}

	@Override
	public Detector[] getExtraDetectors() {
		return new Detector[0];
	}

	private Double[] getScanTimeArray() throws Exception {
		if (scanBean instanceof XasScanParameters xasParams) {
			return ExafsScanPointCreator.getScanTimeArray(xasParams);
		} else if (scanBean instanceof XanesScanParameters xanesParams) {
			return XanesScanPointCreator.getScanTimeArray(xanesParams);
		}
		return new Double[0];
	}

	private void controlAllIonC(List<IonChamberParameters> ionChambersBean) throws DeviceException {
		for (int index = 0; index < ionChambersBean.size(); index++) {
			detectorPreparerFunctions.setupAmplifierSensitivity(ionChambersBean.get(index), index);
		}
	}

	public Map<String, List<BufferedDetector>> getQexafsDetectorsMap() {
		return qexafsDetectorsMap;
	}

	public Map<String, List<BufferedDetector>> setQexafsDetectorsMap(Map<String, List<BufferedDetector>> qexafsDetectorMap) {
		return this.qexafsDetectorsMap = new HashMap<>(qexafsDetectorMap);
	}

	public void addQexafsDetectors(String detectorType, List<BufferedDetector> detectors) {
		qexafsDetectorsMap.put(detectorType, detectors);
	}
}
