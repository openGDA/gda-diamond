package uk.ac.gda.server.exafs.scan.preparers;

import java.util.List;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.NXDetector;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.jython.InterfaceProvider;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.devices.detector.xspress3.Xspress3;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;
import uk.ac.gda.devices.detector.xspress3.Xspress3FFoverI0BufferedDetector;
import uk.ac.gda.server.exafs.scan.QexafsDetectorPreparer;

public class I18DetectorPreparer implements QexafsDetectorPreparer {

	private final Scannable[] sensitivities;
	private final Scannable[] sensitivityUnits;
	private final TfgScalerWithFrames counterTimer01;

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;
	private BufferedDetector qexafs_counterTimer01;
	private Xspress3BufferedDetector qexafs_xspress3;
	private BufferedDetector buffered_cid;
	private NXDetector hardwareTriggeredCmos;
	private Xspress3 xspress3;
	private Xspress3FFoverI0BufferedDetector qexafs_FFI0_xspress3;
	private boolean isBuffered_cid;

	public I18DetectorPreparer(Scannable[] sensitivities, Scannable[] sensitivityUnits, TfgScalerWithFrames ionchambers,
			Xspress3 xspress3, BufferedDetector qexafs_counterTimer01,
			Xspress3BufferedDetector qexafs_xspress3,
			Xspress3FFoverI0BufferedDetector qexafs_FFI0_xspress3, BufferedDetector buffered_cid,
			NXDetector hardwareTriggeredCmos) {
		this.sensitivities = sensitivities;
		this.sensitivityUnits = sensitivityUnits;
		this.counterTimer01 = ionchambers;
		this.xspress3 = xspress3;
		this.qexafs_xspress3 = qexafs_xspress3;
		this.qexafs_counterTimer01 = qexafs_counterTimer01;
		this.qexafs_FFI0_xspress3 = qexafs_FFI0_xspress3;
		this.buffered_cid = buffered_cid;
		this.hardwareTriggeredCmos = hardwareTriggeredCmos;
		// by default should be false as not used with users, only beamline staff
		this.isBuffered_cid = false;
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		this.scanBean = scanBean;
		this.detectorBean = detectorBean;

		if (detectorBean.getExperimentType().equalsIgnoreCase("Fluorescence")) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getFluorescenceParameters();
			String detType = fluoresenceParameters.getDetectorType();
			String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
			if (detType.compareTo(FluorescenceParameters.XSPRESS3_DET_TYPE) == 0) {
				xspress3.setConfigFileName(xmlFileName);
				xspress3.loadConfigurationFromFile();
			}
			control_all_ionc(fluoresenceParameters.getIonChamberParameters());
			if (fluoresenceParameters.isCollectDiffractionImages() && scanBean instanceof MicroFocusScanParameters) {
				control_cmos((MicroFocusScanParameters) scanBean);
			}
		} else if (detectorBean.getExperimentType().equalsIgnoreCase("Transmission")) {
			TransmissionParameters transmissionParameters = detectorBean.getTransmissionParameters();
			control_all_ionc(transmissionParameters.getIonChamberParameters());
		}
	}

	private void control_cmos(MicroFocusScanParameters microFocusParameters) throws DeviceException {
		hardwareTriggeredCmos.setCollectionTime(microFocusParameters.getCollectionTime());
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		Double[] times = new Double[] {};
		if (scanBean instanceof XasScanParameters) {
			times = ExafsScanPointCreator.getScanTimeArray((XasScanParameters) scanBean);
		} else if (scanBean instanceof XanesScanParameters) {
			times = XanesScanPointCreator.getScanTimeArray((XanesScanParameters) scanBean);
		}
		if (times.length > 0) {
			counterTimer01.setTimes(times);
		}
		return;
	}

	@Override
	public void completeCollection() {
		// nothing here
	}

	@Override
	public BufferedDetector[] getQEXAFSDetectors() throws Exception {
		((BufferedScaler) qexafs_counterTimer01).setTtlSocket(0);
		String expt_type = detectorBean.getExperimentType();
		if (expt_type.equals("Transmission")) {
			return new BufferedDetector[] { qexafs_counterTimer01 };
		}
		// else Fluo
		String det_type = detectorBean.getFluorescenceParameters().getDetectorType();
		if (det_type.compareTo(FluorescenceParameters.XSPRESS3_DET_TYPE) == 0) {
			return new BufferedDetector[] { qexafs_counterTimer01, qexafs_xspress3, qexafs_FFI0_xspress3 };
		}
		throw new UnsupportedOperationException("Detector type not supported");
	}

	protected void control_all_ionc(List<IonChamberParameters> ion_chambers_bean) throws Exception {
		for (int index = 0; index < ion_chambers_bean.size(); index++) {
			control_ionc(ion_chambers_bean, index);
		}
	}

	protected void control_ionc(List<IonChamberParameters> ion_chambers_bean, int ion_chamber_num) throws Exception {
		IonChamberParameters ion_chamber = ion_chambers_bean.get(ion_chamber_num);
		setup_amp_sensitivity(ion_chamber, ion_chamber_num);
	}

	protected void setup_amp_sensitivity(IonChamberParameters ionChamberParams, int index) throws Exception {
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
			} catch (Exception e) {
				InterfaceProvider.getTerminalPrinter().print(
						"Exception while trying to change the sensitivity of ion chamber" + ionChamberParams.getName());
				InterfaceProvider
						.getTerminalPrinter()
						.print("Set the ion chamber sensitivity manually, uncheck the box in the Detector Parameters editor and restart the scan");
				InterfaceProvider.getTerminalPrinter().print("Please report this problem to Data Acquisition");
				throw e;
			}
		}
	}

	@Override
	public Detector[] getExtraDetectors() {

		// add the cmos when asked for diffraction during step fluo maps. This is for XRD maps.
		if (detectorBean.getExperimentType().equalsIgnoreCase("Fluorescence")) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getFluorescenceParameters();
			if (fluoresenceParameters.isCollectDiffractionImages() && scanBean instanceof MicroFocusScanParameters) {
				return new Detector[] { hardwareTriggeredCmos };
			}
		}

		return null;
	}

	public boolean isBuffered_cid() {
		return isBuffered_cid;
	}

	public void setBuffered_cid(boolean isBuffered_cid) {
		this.isBuffered_cid = isBuffered_cid;
	}

}
