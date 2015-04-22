package uk.ac.gda.server.exafs.scan.preparers;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.NXDetector;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xspress.Xspress2Detector;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.jython.InterfaceProvider;

import java.util.List;

import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.client.microfocus.scan.RasterMapDetectorPreparer;
import uk.ac.gda.devices.detector.xspress3.Xspress3;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;
import uk.ac.gda.devices.detector.xspress3.Xspress3FFoverI0BufferedDetector;
import uk.ac.gda.server.exafs.scan.QexafsDetectorPreparer;

public class I18DetectorPreparer implements QexafsDetectorPreparer, RasterMapDetectorPreparer {

	private final Scannable[] gains;
	private final TfgScalerWithFrames counterTimer01;
	private final Xspress2Detector xspress2system;

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;
	private BufferedDetector qexafs_counterTimer01;
	private Xspress3BufferedDetector qexafs_xspress3;
	private BufferedDetector qexafs_xspress;
	private BufferedDetector qexafsFFI0;
	private BufferedDetector buffered_cid;
	private NXDetector hardwareTriggeredCmos;
	private Xspress3 xspress3;
	private Xspress3FFoverI0BufferedDetector qexafs_FFI0_xspress3;

	public I18DetectorPreparer(Scannable[] gains, TfgScalerWithFrames ionchambers, Xspress2Detector xspressSystem,
			Xspress3 xspress3, BufferedDetector qexafs_counterTimer01, BufferedDetector qexafs_xspress,
			BufferedDetector QexafsFFI0, Xspress3BufferedDetector qexafs_xspress3,
			Xspress3FFoverI0BufferedDetector qexafs_FFI0_xspress3, BufferedDetector buffered_cid,
			NXDetector hardwareTriggeredCmos) {
		this.gains = gains;
		this.counterTimer01 = ionchambers;
		this.xspress2system = xspressSystem;
		this.xspress3 = xspress3;
		this.qexafsFFI0 = QexafsFFI0;
		this.qexafs_xspress3 = qexafs_xspress3;
		this.qexafs_counterTimer01 = qexafs_counterTimer01;
		this.qexafs_xspress = qexafs_xspress;
		this.qexafs_FFI0_xspress3 = qexafs_FFI0_xspress3;
		this.buffered_cid = buffered_cid;
		this.hardwareTriggeredCmos = hardwareTriggeredCmos;
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
			if (detType.compareTo(FluorescenceParameters.GERMANIUM_DET_TYPE) == 0) {
				xspress2system.setConfigFileName(xmlFileName);
				xspress2system.configure();
			} else if (detType.compareTo(FluorescenceParameters.XSPRESS3_DET_TYPE) == 0) {
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
		if (microFocusParameters.isRaster()) {
			double rowLength = microFocusParameters.getXEnd() - microFocusParameters.getXStart();
			long pointsPerRow = Math.round(Math.floor((rowLength / microFocusParameters.getXStepSize()))) + 1;
			double collectionTime = microFocusParameters.getRowTime() / pointsPerRow;
			hardwareTriggeredCmos.setCollectionTime(collectionTime);
		} else {
			hardwareTriggeredCmos.setCollectionTime(microFocusParameters.getCollectionTime());
		}
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
		String expt_type = detectorBean.getExperimentType();
		if (expt_type.equals("Transmission")) {
			return new BufferedDetector[] { qexafs_counterTimer01 };
		}
		// else Fluo
		String det_type = detectorBean.getFluorescenceParameters().getDetectorType();
		if (det_type.compareTo(FluorescenceParameters.XSPRESS3_DET_TYPE) == 0) {
			return new BufferedDetector[] { qexafs_counterTimer01, qexafs_xspress3, qexafs_FFI0_xspress3 };
		} // else Ge
		return new BufferedDetector[] { qexafs_counterTimer01, qexafs_xspress, qexafsFFI0 };
	}

	@Override
	public BufferedDetector[] getRasterMapDetectors() throws Exception {

		String expt_type = detectorBean.getExperimentType();
		if (expt_type.equals("Transmission")) {
			return new BufferedDetector[] { qexafs_counterTimer01, buffered_cid };
		}

		// else Fluo
		String det_type = detectorBean.getFluorescenceParameters().getDetectorType();
		if (det_type.compareTo(FluorescenceParameters.XSPRESS3_DET_TYPE) == 0) {
			return new BufferedDetector[] { qexafs_counterTimer01, buffered_cid, qexafs_xspress3, qexafs_FFI0_xspress3 };
		}// else Ge
		return new BufferedDetector[] { qexafs_counterTimer01, qexafs_xspress };
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
			if (ionChamberParams.getGain() == null || ionChamberParams.getGain() == "") {
				return;
			}

			try {
				InterfaceProvider.getTerminalPrinter().print(
						"Changing sensitivity of " + ionChamberParams.getName() + " to " + ionChamberParams.getGain());

				gains[index].moveTo(ionChamberParams.getGain());
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
				MicroFocusScanParameters microParams = (MicroFocusScanParameters) scanBean;
				if (!microParams.isRaster()) {
					return new Detector[] { hardwareTriggeredCmos };
				}
			}
		}

		return null;
	}

}