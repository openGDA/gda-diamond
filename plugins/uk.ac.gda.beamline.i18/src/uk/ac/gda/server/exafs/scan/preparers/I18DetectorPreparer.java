package uk.ac.gda.server.exafs.scan.preparers;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.NXDetector;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.device.scannable.BeamMonitor;
import gda.device.scannable.DetectorFillingMonitorScannable;
import gda.device.scannable.TopupChecker;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.jython.InterfaceProvider;
import gda.jython.commands.ScannableCommands;

import java.util.List;

import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.QEXAFSParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.client.microfocus.scan.RasterMapDetectorPreparer;
import uk.ac.gda.server.exafs.scan.QexafsDetectorPreparer;

public class I18DetectorPreparer implements QexafsDetectorPreparer, RasterMapDetectorPreparer {

	private final Scannable[] gains;
	private final TfgScalerWithFrames counterTimer01;
	private final Xspress2Detector xspress2system;
	private final Xmap xmpaMca;

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;
	private TopupChecker topupMonitor;
	private BeamMonitor beam;
	private DetectorFillingMonitorScannable detectorFillingMonitor;
	private BufferedDetector qexafs_counterTimer01;
	private BufferedDetector qexafs_xmap;
	private BufferedDetector qexafs_xspress;
	private BufferedDetector qexafsFFI0;
	private BufferedDetector buffered_cid;
	private NXDetector hardwareTriggeredCmos;

	public I18DetectorPreparer(Scannable[] gains, TfgScalerWithFrames ionchambers, Xspress2Detector xspressSystem,
			Xmap vortexConfig, BufferedDetector qexafs_counterTimer01, BufferedDetector qexafs_xspress,
			BufferedDetector QexafsFFI0, BufferedDetector qexafs_xmap, BufferedDetector buffered_cid,
			NXDetector hardwareTriggeredCmos) {
		this.gains = gains;
		this.counterTimer01 = ionchambers;
		this.xspress2system = xspressSystem;
		this.xmpaMca = vortexConfig;
		this.qexafsFFI0 = QexafsFFI0;
		this.qexafs_xmap = qexafs_xmap;
		this.qexafs_counterTimer01 = qexafs_counterTimer01;
		this.qexafs_xspress = qexafs_xspress;
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
			if (detType == "Germanium") {
				xspress2system.setConfigFileName(xmlFileName);
				xspress2system.configure();
			} else if (detType == "Silicon") {
				xmpaMca.setConfigFileName(xmlFileName);
				xmpaMca.configure();
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
			// print "points per row",str(pointsPerRow)
			double collectionTime = microFocusParameters.getRowTime() / pointsPerRow;
			// print "time per point",str(collectionTime)
			// print "Setting cmos to collect for",str(collectionTime),"s"
			hardwareTriggeredCmos.setCollectionTime(collectionTime);
		} else {
			// print "Setting cmos to collect for",microFocusParameters.getCollectionTime(),"s"
			hardwareTriggeredCmos.setCollectionTime(microFocusParameters.getCollectionTime());
		}
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		configureMonitors();
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

		// this was written before xspress3 added and implemented on the beamline (this was done for 8.4 in November
		// 2014)
		String expt_type = detectorBean.getExperimentType();
		if (expt_type.equals("Transmission")) {
			return new BufferedDetector[] { qexafs_counterTimer01 };
		}

		if (detectorBean.getFluorescenceParameters().getDetectorType().equals("Silicon")) {
			return new BufferedDetector[] { qexafs_counterTimer01, qexafs_xmap, qexafsFFI0 };
		} /*
		 * else if (detectorBean.getFluorescenceParameters().getDetectorType().equals("Xspress3")) { return
		 * createBufferedDetArray(new String[] { "qexafs_counterTimer01", "qexafs_xspress3", "qexafs_FFI0_xspress3" });
		 * }
		 */

		return new BufferedDetector[] { qexafs_counterTimer01, qexafs_xspress, qexafsFFI0 };
	}

	@Override
	public BufferedDetector[] getRasterMapDetectors() throws Exception {

		String expt_type = detectorBean.getExperimentType();
		if (expt_type.equals("Transmission")) {
			return new BufferedDetector[] { qexafs_counterTimer01, buffered_cid };
		}

		if (detectorBean.getFluorescenceParameters().getDetectorType().equals("Silicon")) {
			return new BufferedDetector[] { qexafs_counterTimer01, buffered_cid, qexafs_xmap };
		} /*
		 * else if (detectorBean.getFluorescenceParameters().getDetectorType().equals("Xspress3")) { return
		 * createBufferedDetArray(new String[] { "qexafs_counterTimer01", "qexafs_xspress3", "qexafs_FFI0_xspress3" });
		 * }
		 */

		return new BufferedDetector[] { qexafs_counterTimer01, buffered_cid, qexafs_xspress };
	}

	public void addMonitors(TopupChecker topupMonitor, BeamMonitor beam,
			DetectorFillingMonitorScannable detectorFillingMonitor) {
		this.topupMonitor = topupMonitor;
		this.beam = beam;
		this.detectorFillingMonitor = detectorFillingMonitor;
	}

	private void configureMonitors() {
		double collectionTime = 0.0;
		if (scanBean instanceof XanesScanParameters) {
			List<Region> regions = ((XanesScanParameters) scanBean).getRegions();
			for (Region region : regions) {
				if (collectionTime < region.getTime()) {
					collectionTime = region.getTime();
				}
			}
		} else if (scanBean instanceof QEXAFSParameters) {
			// pass
		} else if (scanBean instanceof MicroFocusScanParameters) {
			// pass
		} else {
			// # EXAFS
			collectionTime = ((XasScanParameters) scanBean).getExafsTime();
			if (((XasScanParameters) scanBean).getExafsToTime() > collectionTime) {
				collectionTime = ((XasScanParameters) scanBean).getExafsToTime();
			}
		}
		// print "setting collection time to " + str(collectionTime)

		if (topupMonitor != null) {
			topupMonitor.setPauseBeforePoint(true);
			topupMonitor.setPauseBeforeLine(false);
			topupMonitor.setCollectionTime(collectionTime);
		}

		if (beam != null) {
			beam.setPauseBeforePoint(true);
			beam.setPauseBeforeLine(true);
		}

		if (detectorFillingMonitor != null && detectorBean.getExperimentType().equals("Fluorescence")
				&& detectorBean.getFluorescenceParameters().getDetectorType().equals("Germanium")) {
			detectorFillingMonitor.setPauseBeforePoint(true);
			detectorFillingMonitor.setPauseBeforeLine(false);
			// print "Adding the detectorFillingMonitor to the list of defaults";
			ScannableCommands.add_default(new Object[] { detectorFillingMonitor });
		} else {
			ScannableCommands.remove_default(new Object[] { detectorFillingMonitor });
		}
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
			// String[] gainStringParts = ionChamberParams.getGain().split(" ");
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

		// add the cmos when asked for diffraction during step fluo maps.  This is for XRD maps.
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